from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty

class MyClass(EventDispatcher):
    a = NumericProperty(1)
    other=None

    def __init__(self, a, **kwargs):
        super(MyClass, self).__init__(**kwargs)
        self.a=a

    def callback(self, instance, value):
        print('MyClass callback is call from', instance)
        print('and the a value changed to', value)

class SecondClass(EventDispatcher):
    b = NumericProperty(2)
    other=None

    def __init__(self, b, **kwargs):
        super(SecondClass, self).__init__(**kwargs)
        self.b = b

    def callback(self, instance, value):
        print('SecondClass callback is called from', instance)
        print('and the a value changed to', value)


my = MyClass(2)
other = SecondClass(4)
my.other=other
other.other=my
my.bind(a=my.other.callback)
other.bind(b=other.other.callback)


# At this point, any change to the a property will call your callback.
my.a = 5
other.b = 3