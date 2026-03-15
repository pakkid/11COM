import arcade

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "My Awesome Game")
        self.background_color = arcade.color.AMAZON

        self.player = arcade.Sprite(":resources:/images/animated_characters/robot/robot_idle.png")
        self.player.center_x = 400
        self.player.center_y = 300
        self.player.change_x = 5

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.player)

    def on_update(self, delta_time):
        self.player.update()

        if self.player.right > 800:
            self.player.change_x = -5
        if self.player.left < 0:
            self.player.change_x = 5

MyGame()
arcade.run()