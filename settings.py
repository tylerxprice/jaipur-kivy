from kivy.core.text import LabelBase

KIVY_FONTS = [
    {
        "name": "Constantia",
        "fn_regular": "data/fonts/constan.ttf",
        "fn_bold": "data/fonts/constanb.ttf",
        "fn_italic": "data/fonts/constani.ttf",
        "fn_bolditalic": "data/fonts/constanz.ttf"
    },
]

for font in KIVY_FONTS:
    LabelBase.register(**font)
