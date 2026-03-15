import arcade

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "My Awesome Game")
        self.background_color = arcade.color.AMAZON

        self.player = arcade.Sprite(":resources:/images/animated_characters/robot/robot_idle.png")
        self.player.center_x = 400
        self.player.center_y = 300

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.player)

    def on_update(self, delta_time):
        self.player.update()

        if self.player.right > 800:
            self.player.right = 800
        if self.player.left < 0:
            self.player.left = 0
        if self.player.top > 600:
            self.player.top = 600
        if self.player.bottom < 0:
            self.player.bottom = 0

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.change_x = -5
        if key == arcade.key.RIGHT:
            self.player.change_x = 5
        if key == arcade.key.UP:
            self.player.change_y = 5
        if key == arcade.key.DOWN:
            self.player.change_y = -5

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.change_x = 0
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0

MyGame()
arcade.run()