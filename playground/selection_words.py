import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class MyGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.cols = 1

        self.inside = GridLayout()
        self.inside.cols = 2

        self.inside.add_widget(Label(text="First Name: "))
        self.name = TextInput(multiline=True)
        self.name.bind(cursor = self.cursor_control)
        self.inside.add_widget(self.name)

        self.add_widget(self.inside)

        self.cursor_left = Button(text = "Cursor Left", font_size=40)
        self.cursor_left.bind(on_press = self.cursor_pressed_left)
        self.add_widget(self.cursor_left)

        self.cursor_right = Button(text="Cursor Right", font_size=40)
        self.cursor_right.bind(on_press=self.cursor_pressed_right)
        self.add_widget(self.cursor_right)

        self.cnt_button = 0
        self.old_cnt_button = 0
        self.old_cursor_index = self.name.cursor_index()

    def cursor_control(self, instance, value):
        new_cursor_index = self.name.cursor_index()
        old_cursor_index = self.old_cursor_index
        cnt_button = self.cnt_button
        old_cnt_button = self.old_cnt_button

        if abs(cnt_button-old_cnt_button) >= 1 and abs(new_cursor_index - old_cursor_index) <= 1:
            print('Using buttons to move cursor')
        elif abs(cnt_button-old_cnt_button) == 0 and abs(new_cursor_index - old_cursor_index) == 1:
            print('Writing')
        elif abs(cnt_button-old_cnt_button) == 0 and abs(new_cursor_index - old_cursor_index) > 1:
            print('moved cursor randomly')
            #set cursor to the end of the word
            cursor_in_row_index = self.name._cursor[0]
            row = self.name._cursor[1]
            text_row = self.name._lines[row]

            spaces = []
            for index in range(cursor_in_row_index,len(text_row)):
                char = text_row[index]
                if char == " ":
                    spaces.append(index)
            if spaces:
                end_word_index = spaces[0]
                self.name.cursor = (end_word_index, row)
            else:
                self.name.do_cursor_movement('cursor_end')

        self.new_cursor_index = self.name.cursor_index()
        self.save_old_cursor_index(new_cursor_index)
        self.save_old_cnt_button(cnt_button)

    def save_old_cursor_index(self, cursor_index):
        self.old_cursor_index = cursor_index

    def save_old_cnt_button(self, cnt_button):
        self.old_cnt_button = cnt_button

    def cursor_pressed_left(self, instance):
        self.name.do_cursor_movement('cursor_left')
        self.cnt_button = self.cnt_button + 1
        Clock.schedule_once(self.set_focus, 0.5)

    def cursor_pressed_right(self, instance):
        self.name.do_cursor_movement('cursor_right')
        self.cnt_button = self.cnt_button + 1
        Clock.schedule_once(self.set_focus, 0.5)

    def set_focus(self, dt):
        self.name.focus = True

class MyApp(App):
    def build(self):
        return MyGrid()

if __name__ == "__main__":
    MyApp().run()