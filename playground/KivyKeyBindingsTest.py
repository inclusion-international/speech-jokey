from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window

class KeyDown(App):
    def build(self):
        # bind any key press to the window
        Window.bind(on_keyboard=self.key_action)
        return Widget()

    # Will be called if any key is pressed
    def key_action(self,  *args):
        #print(len(args))
        print("got a key event: %s" % list(args))
        # codepoint seems to be the unicode character
        codepoint = args[2]
        # key is the key character like with string
        key = args[3]
        # The list of modifiers contains information, if keys like ctrl, shift, alt,... are pressed
        # This can also be in combination with other keys.
        modifiers = args[4]

        # check if ctrl+p is pressed
        if "ctrl" in modifiers and key == "p":
            print("ctrl+p pressed")

if __name__ == '__main__':
    KeyDown().run()