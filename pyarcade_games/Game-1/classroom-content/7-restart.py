import arcade
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "My Awesome Game")
        self.background_color = arcade.color.AMAZON
        self.setup()                                   ## NEW ##
                                                       ## NEW ##
    def setup(self):                                   ## NEW ##
        self.player = arcade.Sprite(":resources:/images/animated_characters/robot/robot_idle.png")
        self.player.center_x = SCREEN_WIDTH / 2
        self.player.center_y = SCREEN_HEIGHT / 2

        self.coin_list = arcade.SpriteList()
        for n in range(50):
            coin = arcade.Sprite(":resources:/images/items/coinGold.png", 0.5)
            coin.center_x = random.randint(0, SCREEN_WIDTH)
            coin.center_y = random.randint(0, SCREEN_HEIGHT)
            self.coin_list.append(coin)

        self.score = 0

    def on_draw(self):
        self.clear()
        self.coin_list.draw()
        arcade.draw_sprite(self.player)
        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 50, font_size=30)

        if self.score >= 50:                                           ## NEW ##
            arcade.draw_text(                                          ## NEW ##
                "GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,      ## NEW ##
                font_size=80, anchor_x="center"                        ## NEW ##
            )                                                          ## NEW ##
            arcade.draw_text(                                          ## NEW ##
                "Press R to restart",                                  ## NEW ##
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50,              ## NEW ##
                font_size=30, anchor_x="center"                        ## NEW ##
            )

    def on_update(self, delta_time):
        self.player.update()

        hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in hit_list:
            self.score += 1
            coin.kill()

        if self.player.right > SCREEN_WIDTH:
            self.player.right = SCREEN_WIDTH
        if self.player.left < 0:
            self.player.left = 0
        if self.player.top > SCREEN_HEIGHT:
            self.player.top = SCREEN_HEIGHT
        if self.player.bottom < 0:
            self.player.bottom = 0

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_SPEED
        if key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_SPEED
        if key == arcade.key.UP:
            self.player.change_y = PLAYER_SPEED
        if key == arcade.key.DOWN:
            self.player.change_y = -PLAYER_SPEED
        if key == arcade.key.R:                      ## NEW ##
            self.setup()                             ## NEW ##

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.change_x = 0
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0

MyGame()
arcade.run()