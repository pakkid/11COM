import arcade

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "My Awesome Game")
        self.background_color = arcade.color.AMAZON

    def on_draw(self):
        self.clear()

    def on_update(self, delta_time):
        ...

MyGame()
arcade.run()