import kivy
kivy.require('1.9.1')  # update with your current version

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import *
from kivy.core.window import Window

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.vector import Vector
from kivy.config import Config

import random

import settings #TODO better packaging


class ImageButton(Image, Button):
  pass


class BoardArea(Widget):
  pass


class Card(ImageButton):
  LOCATION_ON_DECK = 0
  LOCATION_IN_MARKET = 1
  LOCATION_IN_DISCARD = 2
  LOCATION_IN_HAND = 3
  LOCATION_IN_HERD = 4

  is_face_up = BooleanProperty(False)
  is_selected = BooleanProperty(False)
  is_animating = BooleanProperty(False)
  location = NumericProperty(LOCATION_ON_DECK)
  face_source = StringProperty()
  back_source = StringProperty('images/cards/deck.png')

  def __init__(self, face_source, **kwargs):
    super(Card, self).__init__(**kwargs)
    self.face_source = face_source

  def flip_card(self):
    self.is_face_up = not self.is_face_up
    self.source = self.face_source if self.is_face_up else self.back_source

  def set_location(self, new_location):
    self.location = new_location

  def select(self, *ignore):
    if self.is_animating:
      return

    if self.location in (Card.LOCATION_ON_DECK, Card.LOCATION_IN_DISCARD):
      return

    self.is_selected = not self.is_selected

    if self.location is Card.LOCATION_IN_MARKET:
      self.animate(y=(self.y - 20 if self.is_selected else self.y + 20), duration=0.25)

    if self.location in (Card.LOCATION_IN_HAND, Card.LOCATION_IN_HERD):
      self.animate(y=(self.y + 20 if self.is_selected else self.y - 20), duration=0.25)

  def reorder(self):
    parent = self.parent
    parent.remove_widget(self)
    parent.add_widget(self)

  def animate(self, **kwargs):
      self.is_animating = True
      a = Animation(**kwargs)
      a.bind(on_complete=Card.complete_animation)
      a.start(self)

  def complete_animation(animation, widget):
    widget.is_animating = False

class DiamondCard(Card):
  def __init__(self, **kwargs):
    super(DiamondCard, self).__init__('images/cards/diamonds.png', **kwargs)

class GoldCard(Card):
  def __init__(self, **kwargs):
    super(GoldCard, self).__init__('images/cards/gold.png', **kwargs)

class SilverCard(Card):
  def __init__(self, **kwargs):
    super(SilverCard, self).__init__('images/cards/silver.png', **kwargs)

class ClothCard(Card):
  def __init__(self, **kwargs):
    super(ClothCard, self).__init__('images/cards/cloth.png', **kwargs)

class SpiceCard(Card):
  def __init__(self, **kwargs):
    super(SpiceCard, self).__init__('images/cards/spice.png', **kwargs)

class LeatherCard(Card):
  def __init__(self, **kwargs):
    super(LeatherCard, self).__init__('images/cards/leather.png', **kwargs)

class CamelCard(Card):
  def __init__(self, **kwargs):
    super(CamelCard, self).__init__('images/cards/camel.png', **kwargs)


class DrawDeck(BoardArea):
  NUM_DIAMOND_CARDS = 6
  NUM_GOLD_CARDS    = 6
  NUM_SILVER_CARDS  = 6
  NUM_CLOTH_CARDS   = 8
  NUM_SPICE_CARDS   = 8
  NUM_LEATHER_CARDS = 10
  NUM_CAMEL_CARDS   = 11
  NUM_CARDS         = NUM_DIAMOND_CARDS + NUM_GOLD_CARDS + NUM_SILVER_CARDS + \
                      NUM_CLOTH_CARDS + NUM_SPICE_CARDS + NUM_LEATHER_CARDS + \
                      NUM_CAMEL_CARDS

  cards = ListProperty([])
  def __init__(self, **kwargs):
    super(DrawDeck, self).__init__(**kwargs)

    for _ in xrange(DrawDeck.NUM_DIAMOND_CARDS):
      self.cards.append(DiamondCard());
    for _ in xrange(DrawDeck.NUM_GOLD_CARDS):
      self.cards.append(GoldCard());
    for _ in xrange(DrawDeck.NUM_SILVER_CARDS):
      self.cards.append(SilverCard());
    for _ in xrange(DrawDeck.NUM_CLOTH_CARDS):
      self.cards.append(ClothCard());
    for _ in xrange(DrawDeck.NUM_SPICE_CARDS):
      self.cards.append(SpiceCard());
    for _ in xrange(DrawDeck.NUM_LEATHER_CARDS):
      self.cards.append(LeatherCard());
    for _ in xrange(DrawDeck.NUM_CAMEL_CARDS):
      self.cards.append(CamelCard());

  def draw_camel_card(self):
    camel = self.cards.pop()
    assert isinstance(camel, CamelCard)
    return camel

  def draw_card(self):
    assert len(self.cards) > 0
    return self.cards.pop()

  def shuffle_cards(self):
    assert len(self.cards) == (DrawDeck.NUM_CARDS - 3) # three camels have been removed
    random.shuffle(self.cards)

  def add_cards_to_table(self, table):
    assert len(self.cards) == DrawDeck.NUM_CARDS
    for card in self.cards:
      table.add_widget(card)
      card.pos = self.pos


class DiscardPile(BoardArea):
  pass


class Market(BoardArea):
  MAX_CARDS_IN_MARKET = 5
  cards = {0: None, 1: None, 2: None, 3: None, 4: None}

  def __init__(self, **kwargs):
    super(Market, self).__init__(**kwargs)

  def add_card(self, card):
    if card.location is Card.LOCATION_ON_DECK:
      card.flip_card()

    card.location = Card.LOCATION_IN_MARKET

    for key, item in self.cards.items():
      if item is None:
        self.cards[key] = card
        return (self.pos[0] + card.width * key, self.pos[1])

    return (None, None)


class TokenBank(BoardArea):
  pass


class PlayerArea(BoardArea):
  pass


class Hand(Widget):
  STARTING_HAND_SIZE = 5
  END_OF_TURN_MAX_HAND_SIZE = 7

  cards = ListProperty([])

  def add_card(self, card):
    card.set_location(Card.LOCATION_IN_HAND)
    self.cards.append(card)

  def remove_camels(self):
    camels = list()
    for card in list(self.cards):
      if isinstance(card, CamelCard):
        self.cards.remove(card)
        camels.append(card)
    return camels

  def get_count(self):
    return len(self.cards)

  def draw_cards(self, x, y):
    if self.get_count() > 3:
      overlap_factor = 3.0 / self.get_count()
    else:
      overlap_factor = 1.0

    for card in self.cards:
      card.flip_card()
      card.opacity = 1.0
      card.pos = (x, y)
      card.reorder()
      x += card.width * overlap_factor


class Herd(Widget):
  camels = ListProperty([])

  def add_camels(self, new_camels):
    self.camels.extend(new_camels)
    for card in new_camels:
      card.set_location(Card.LOCATION_IN_HERD)

  def get_count(self):
    return len(self.camels)

  def draw_cards(self, x, y):
    if self.get_count() > 2:
      overlap_factor = 2.0 / self.get_count()
    else:
      overlap_factor = 1.0

    for card in self.camels:
      card.flip_card()
      card.opacity = 1.0
      card.pos = (x, y)
      card.reorder()
      x -= card.width
      x += card.width * overlap_factor


class Player(Widget):
  hand = ObjectProperty(None)
  herd = ObjectProperty(None)
  money = NumericProperty(0)
  num_wins = NumericProperty(0)
  hand_label = ObjectProperty(None)
  herd_label = ObjectProperty(None)
  avatar_source = StringProperty()
  shaded_avatar_source = StringProperty()

  def __init__(self, avatar_source, shaded_avatar_source, **kwargs):
    super(Player, self).__init__(**kwargs)
    self.hand = Hand()
    self.herd = Herd()
    self.avatar_source = avatar_source
    self.shaded_avatar_source = shaded_avatar_source

  def deal_card(self, card):
    self.hand.add_card(card)
    #TODO card.animate(callback=self.card_dealt, x=x_dest, y=y_dest, duration=2.)
    card.opacity = 0 #TODO animate shrinking into player label
    self.hand_label.text = str(self.hand.get_count())
    return (self.x if self.player_number is 1 else self.right - card.width, self.y)

  def form_herd(self):
    camels = self.hand.remove_camels()
    self.herd.add_camels(camels)
    self.hand_label.text = str(self.hand.get_count())
    self.herd_label.text = str(self.herd.get_count())

  def start_turn(self, player_area):
    self.avatar.source = self.avatar_source
    self.money_label.text = str(self.money)
    self.money_label.opacity = 1.

    self.hand.draw_cards(player_area.x, player_area.y)
    self.herd.draw_cards(player_area.right - 162, player_area.y)

  def end_turn(self):
    self.avatar.source = self.shaded_avatar_source
    self.money_label.text = "??"
    self.money_label.opacity = 0.5
    # hide hand & herd
    pass

class PlayerOne(Player):
  def __init__(self, **kwargs):
    super(PlayerOne, self).__init__('images/player_one_avatar.png',
                                    'images/player_one_avatar_shaded.png',
                                    **kwargs)

class PlayerTwo(Player):
  def __init__(self, **kwargs):
    super(PlayerTwo, self).__init__('images/player_two_avatar.png',
                                    'images/player_two_avatar_shaded.png',
                                    **kwargs)


class GameTable(Widget):
  player_one = ObjectProperty(None)
  player_two = ObjectProperty(None)
  current_player = ObjectProperty(None)
  idle_player = ObjectProperty(None)
  draw_deck = ObjectProperty(None)
  discard_pile = ObjectProperty(None)
  market = ObjectProperty(None)
  token_bank = ObjectProperty(None)
  player_area = ObjectProperty(None)

  def __init__(self, **kwargs):
    super(GameTable, self).__init__(**kwargs)
    self.current_player = random.choice((self.player_one, self.player_two))
    self.idle_player = self.player_two if self.current_player is self.player_one else self.player_one

  def deal_camel_to_market(self):
    card = self.draw_deck.draw_camel_card()
    x, y = self.market.add_card(card)
    card.animate(x=x, y=y, duration=1., t='out_sine')

  def deal_card_to_market(self):
    card = self.draw_deck.draw_card()
    x, y = self.market.add_card(card)
    card.animate(x=x, y=y, duration=1., t='out_sine')

  def deal_card_to_player(self, player):
    card = self.draw_deck.draw_card()
    x, y = player.deal_card(card)
    #card.animate(x=x, y=y, duration=1.,  t='out_sine')
    card.pos = (x, y)

  def deal(self):
    self.draw_deck.add_cards_to_table(self)

    for _ in xrange(3):
      self.deal_camel_to_market()

    self.draw_deck.shuffle_cards()

    for _ in xrange(Hand.STARTING_HAND_SIZE):
      self.deal_card_to_player(self.current_player)
      self.deal_card_to_player(self.idle_player)

    self.deal_card_to_market()
    self.deal_card_to_market()

    self.current_player.form_herd()
    self.idle_player.form_herd()

  def prompt_player(self):
    # clear player area
    # show modal that says who's turn it is
    # populate player area
    self.current_player.start_turn(self.player_area)
    pass


class JaipurApp(App):
  texture = ObjectProperty(None)
  game_table = ObjectProperty(None)

  def build(self):
    self.texture = Image(source='images/bg_tile.png').texture
    self.texture.wrap = 'repeat'
    self.texture.uvsize = (1280/63, 720/62)

    self.game_table = GameTable()

    Window.size = (1280, 720)
    Config.set('graphics', 'resizable', 0) #don't make the app re-sizeable
    Window.clearcolor = (0,0,0,1.) #Graphics fix for issues on some phones



    return self.game_table

  def on_start(self):
    self.game_table.deal()
    self.game_table.prompt_player()

if __name__ == '__main__':
  JaipurApp().run()
