from kivy.lang import Builder

from kivymd.app import MDApp
from kivymd.uix.tab import (
    MDTabsItem,
    MDTabsItemIcon,
    MDTabsItemText,
    MDTabsBadge,
)

KV = '''
MDScreen:
    md_bg_color: self.theme_cls.backgroundColor

    MDTabsPrimary:
        id: tabs
        pos_hint: {"center_x": .5, "center_y": .5}

        MDDivider:
'''


class Example(MDApp):
    def on_start(self):
        for tab_icon, tab_name in {
            "airplane": "Flights",
            "treasure-chest": "Trips",
            "compass-outline": "Explore",
        }.items():
            if tab_icon == "treasure-chest":
                self.root.ids.tabs.add_widget(
                    MDTabsItem(
                        MDTabsItemIcon(
                            MDTabsBadge(
                                text="99",
                            ),
                            icon=tab_icon,
                        ),
                        MDTabsItemText(
                            text=tab_name,
                        ),
                    )
                )
            else:
                self.root.ids.tabs.add_widget(
                    MDTabsItem(
                        MDTabsItemIcon(
                            icon=tab_icon,
                        ),
                        MDTabsItemText(
                            text=tab_name,
                        ),
                    )
                )
            self.root.ids.tabs.switch_tab(icon="airplane")

    def build(self):
        self.theme_cls.primary_palette = "Olive"
        return Builder.load_string(KV)


Example().run()