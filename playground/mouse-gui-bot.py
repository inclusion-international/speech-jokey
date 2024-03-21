import mouse
def on_move(event):
    print(event.x, event.y)

mouse.hook(on_move)
mouse.wait()

