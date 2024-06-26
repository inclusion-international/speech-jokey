from kivy.lang import Builder
from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.card import MDCard

KV = '''
<MyCard>
    padding: "4dp"
    size_hint: None, None
    size: "240dp", "100dp"

    MDRelativeLayout:

        MDIconButton:
            icon: "dots-vertical"
            pos_hint: {"top": 1, "right": 1}

        MDLabel:
            text: root.text
            adaptive_size: True
            color: "grey"
            pos: "12dp", "12dp"
            bold: True


MDScreen:
    theme_bg_color: "Custom"
    md_bg_color: self.theme_cls.backgroundColor

    MDBoxLayout:
        id: box
        adaptive_size: True
        spacing: "12dp"
        pos_hint: {"center_x": .5, "center_y": .5}
'''


class MyCard(MDCard): # Hey, I also wanted to do changes here
# This is my code line that I changed
    '''Implements a material card.'''

    text = StringProperty()


class Example(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        for style in ("elevated", "filled", "outlined"):
            self.root.ids.box.add_widget(
                MyCard(style=style, text=style.capitalize())
            )


Example().run()