import sys
from Map_elements import *
from Player import *
from Enemy import *
from pygame_widgets import Button
import random
import numpy as np


class BoatGame:  # todo fare cartella img
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)

    def init_game(self):
        # initialize all variables and do all the setup for a new game
        self.reset()

        # fire button
        self.button_x = GRIDWIDTH + 60
        self.button_y = GRIDHEIGHT - 100
        self.button_width = 93
        self.button_height = 45
        self.button_fire = Button(
            self.screen, self.button_x, self.button_y, self.button_width, self.button_height,
            text='Fire', fontSize=50, margin=20, inactiveColour=(0, 255, 0), hoverColour=(255, 255, 255),
            pressedColour=(255, 0, 0), radius=5, onRelease=lambda: pg.event.post(pg.event.Event(PLAYER_SHOOT_EVENT))
        )

    def reset(self):
        # sprites
        self.all_sprites = pg.sprite.Group()
        self.walls_sprites = pg.sprite.Group()
        self.enemies_sprites = pg.sprite.Group()
        self.exit_sprites = pg.sprite.Group()
        self.power_ups_sprites = pg.sprite.Group()

        self.enemies = []
        self.walls = []
        self.power_ups = []
        # walls
        self.generateMap()

        # player
        print("player generating:")
        rand_px, rand_py = random.randint(1, GRIDWIDTH / TILESIZE - 1), random.randint(1, GRIDHEIGHT / TILESIZE - 1)
        while any(rand_px == w.x and rand_py == w.y for w in self.walls):
            rand_px, rand_py = random.randint(0, GRIDWIDTH / TILESIZE), random.randint(0, GRIDHEIGHT / TILESIZE)
        print("    " + str(rand_px) + " " + str(rand_py))
        self.player = Player(self, rand_px, rand_py)

        # enemies
        print("enemies generating:")
        rand_ex, rand_ey = random.randint(1, GRIDWIDTH / TILESIZE - 1), random.randint(1, GRIDHEIGHT / TILESIZE - 1)
        try:
            while any(rand_ex == w.x and rand_ey == w.y for w in self.walls + [self.player]) and np.linalg.norm((rand_ex, rand_ey), (self.player.getX(), self.player.getY()) ) > MIN_START_DISTANCE_PLAYER_ENEMY:
                rand_ex, rand_ey = random.randint(0, GRIDWIDTH / TILESIZE), random.randint(0, GRIDHEIGHT / TILESIZE)
        except:
            print("Something else went wrong")
        print("    " + str(rand_ex) + " " + str(rand_ey))
        self.enemies.append(Enemy(self, rand_ex, rand_ey))

        # exit
        print("exit generating:")
        rand_exit_x, rand_exit_y = random.randint(0, GRIDWIDTH / TILESIZE), random.randint(0, GRIDHEIGHT / TILESIZE)
        try:
            while any(rand_exit_x == w.x and rand_exit_y == w.y for w in self.walls + [self.player] + self.enemies) and np.linalg.norm((rand_exit_x, rand_exit_y), (self.player.getX(), self.player.getY())) > MIN_START_DISTANCE_PLAYER_EXIT:
                rand_exit_x, rand_exit_y = random.randint(0, GRIDWIDTH / TILESIZE), random.randint(0, GRIDHEIGHT / TILESIZE)
        except:
            print("Something else went wrong")
        print("    " + str(rand_exit_x) + " " + str(rand_exit_y))
        self.exit = [Exit(self, rand_exit_x, rand_exit_y)]

        # power ups
        print("power ups generating:")
        num_powerup = random.randint(MIN_NUM_POWERUP, MAX_NUM_POWERUP)
        for i in range(num_powerup):
            rand_pow_x, rand_pow_y = random.randint(0, GRIDWIDTH / TILESIZE), random.randint(0, GRIDHEIGHT / TILESIZE)
            rand_effect = random.randint(0, 1)
            while any(rand_pow_x == w.x and rand_pow_y == w.y for w in
                      self.walls + [self.player] + self.enemies + self.power_ups):
                rand_pow_x, rand_pow_y = random.randint(0, GRIDWIDTH / TILESIZE), random.randint(0, GRIDHEIGHT / TILESIZE)
            self.power_ups.append(PowerUps(self, rand_pow_x, rand_pow_y, rand_effect))
            print("    " + str(rand_pow_x) + " " + str(rand_pow_y))

        return self.enemies[0].calc_observation()

    def generateMap(self):
        # walls
        num_obstacles = random.randint(MIN_NUM_OBSTACLE, MAX_NUM_OBSTACLE)
        print("wall generating:")
        for o in range(num_obstacles):
            rand_center_x = random.randint(3, GRIDWIDTH / TILESIZE-13)
            rand_center_y = random.randint(3, GRIDHEIGHT / TILESIZE-3)
            num_lines = random.randint(MIN_LINES_FOR_OBSTACLES, MAX_LINES_FOR_OBSTACLES)
            for l in range(num_lines):
                rand_x = int(np.random.normal(scale=3)) + rand_center_x
                rand_y = int(np.random.normal(scale=3)) + rand_center_y
                direct = random.randint(0, 3)
                lenght = random.randint(MIN_LENGHT_LINE, MAX_LENGHT_LINE)
                for x in range(lenght):
                    pos_x, pos_y = 0, 0
                    if direct == 0:
                        pos_x, pos_y = rand_x + x - int(lenght / 2), rand_y - int(lenght / 2)
                    elif direct == 1:
                        pos_x, pos_y = rand_x + int(lenght / 2), rand_y + x + int(lenght / 2)
                    elif direct == 2:
                        pos_x, pos_y = rand_x + x + int(lenght / 2), rand_y + x + int(lenght / 2)
                    elif direct == 3:
                        pos_x, pos_y = rand_x - x + int(lenght / 2), rand_y + x + int(lenght / 2)

                    if 0 < pos_x < int(GRIDWIDTH / TILESIZE) and 0 < pos_y < int(GRIDHEIGHT / TILESIZE) :
                        print("    " + str(pos_x) + " " + str(pos_y))
                        self.walls.append(Wall(self, pos_x, pos_y))

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def close(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()

    def draw_grid(self):
        for x in range(0, GRIDWIDTH + TILESIZE, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, GRIDHEIGHT))
        for y in range(0, GRIDHEIGHT + TILESIZE, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (GRIDWIDTH, y))

    def draw(self):
        self.screen.fill(BGCOLOR)
        pg.draw.rect(self.screen, SETTING_COLOR, (GRIDWIDTH, 0, SETTING_WIDTH, SETTING_HEIGHT))
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        self.button_fire.draw()
        pg.display.flip()

    def events(self):

        # check hover mouse
        events = pg.event.get()
        for block in self.player.feasible_move:
            if block.rect.collidepoint(pg.mouse.get_pos()):
                block.image.fill(GREEN)
            else:
                block.image.fill(LIGHTGREY)

        # catch all events here
        for event in events:
            # quit
            if event.type == pg.QUIT:
                self.close()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.close()
            # player turn
            if event.type == pg.MOUSEBUTTONUP:
                # check feasible player move
                for block in self.player.feasible_move:
                    if block.rect.collidepoint(pg.mouse.get_pos()):
                        dx = int(block.rect.x / TILESIZE) - self.player.x
                        dy = int(block.rect.y / TILESIZE) - self.player.y
                        self.player.move(dx, dy)
                        # check powerup
                        for powerup in self.power_ups:
                            if self.player.x == powerup.x and self.player.y == powerup.y:
                                powerup.acquired_by(self.player)
                        # check win
                        for exit in self.exit:
                            if self.player.x == exit.x and self.player.y == exit.y:
                                print("win")
            if event.type == PLAYER_SHOOT_EVENT:
                self.player.shoot_fire()

            # enemy turn
            if event.type == ENEMY_TURN_EVENT:
                pg.time.delay(100)
                for enemy in self.enemies:
                    enemy_action = enemy.random_action()
                    enemy.step(enemy_action)
                    for powerup in self.power_ups:
                        if enemy.getX() == powerup.x and enemy.getY() == powerup.y:
                            powerup.acquired_by(enemy)
                    self.player.move_shoot_and_moves()
                    for enemy in self.enemies:
                        enemy.move_shoot_and_moves()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass