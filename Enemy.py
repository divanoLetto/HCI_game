from Base_classes import Character, table_feasible_directions
from settings import *
from Utils import isClose


class Enemy(pg.sprite.Sprite, Character):
    #  Actions:
    # Type: Discrete(2)
    #   0 Fire
    #   1

    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.enemies_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.player = game.player
        self.alive = True

        self.image_N = pg.image.load('images/player_N.png')
        self.image_E = pg.image.load('images/player_E.png')
        self.image_S = pg.image.load('images/player_S.png')
        self.image_O = pg.image.load('images/player_O.png')
        self.image_NE = pg.image.load('images/player_NE.png')
        self.image_SE = pg.image.load('images/player_SE.png')
        self.image_SO = pg.image.load('images/player_SO.png')
        self.image_NO = pg.image.load('images/player_NO.png')
        self.image_broken = pg.image.load('images/explosion.png')
        Character.__init__(self, x, y, self.image_NE, game)

    #  def reset(self):  game responsability
    #      return self.game.restart()

    def step(self, action):
        if action == 0:
            self.shoot_fire()
        else:
            feasible_dir = [table_feasible_directions[str((table_feasible_directions[str(self.direction)] + d.id) % 8)] for d in self.feasible_move if
                            d.no_collision()]
            choose_move = feasible_dir[action-1]
            self.move(choose_move[0], choose_move[1])
        return self.calc_observation()

    def calc_observation(self):
        observation = {}
        observation["global_obs"] = self.calculate_global_observation_matrix()
        observation["local_maps"] = self.calculate_local_observation_matrix(observation["global_obs"])
        observation["vector_properties"] = self.calculate_vector_properties()
        return observation

    def calculate_global_observation_matrix(self):
        #  Map Observations
        #     0 = free
        #     1 = wall
        #     2 = player
        #     3 = agents/enemies - self if alone
        #     4 = exit
        #     5 = power-up_1
        #     6 = power-up_2
        w, h = int(GRIDWIDTH / TILESIZE) + 1, int(GRIDHEIGHT / TILESIZE) + 1
        global_matrix = [[0 for y in range(h)] for x in range(w)]
        #  walls
        for wall in self.game.walls:
            global_matrix[wall.x][wall.y] = 1
        #  player
        global_matrix[self.player.x][self.player.y] = 2
        #  self agent
        for enemy in self.game.enemies:
            global_matrix[enemy.x][enemy.y] = 3
        #  exits
        for ex in self.game.exit:
            global_matrix[ex.x][ex.y] = 4
        #  powerups
        for powerup in self.game.power_ups:
            if powerup.effect == 0:
                global_matrix[powerup.x][powerup.y] = 5
            else:
                global_matrix[powerup.x][powerup.y] = 6
        return global_matrix

    def calculate_local_observation_matrix(self, global_matrix):
        #  Map Observations
        #     0 = free
        #     1 = wall
        #     2 = player
        #     3 = agents/enemies - self if alone
        #     4 = exit
        #     5 = power-up_1
        #     6 = power-up_2
        local_observations = {}
        print("local observation map:")
        #  3x3 local map
        matricx_local_3x3 = [[0 for x in range(3)] for y in range(3)]
        for y in [-1, 0, 1]:
            for x in [-1, 0, 1]:
                mx, my = self.game.enemies[0].x + x, self.game.enemies[0].y + y  # just 1 enemy
                if 0 <= mx <= GRIDWIDTH / TILESIZE and 0 <= my <= GRIDHEIGHT / TILESIZE:
                    print("   x,y: " + str(x) + " " + str(y) + "and mx,my: " + str(mx) + " " + str(my))
                    matricx_local_3x3[x+1][y+1] = global_matrix[mx][my]
                else:
                    matricx_local_3x3[x+1][y+1] = 1
        local_observations["3x3"] = matricx_local_3x3

        #  5x5 local map
        matricx_local_5x5 = [[0 for x in range(5)] for y in range(5)]
        for y in [-2, -1, 0, 1, 2]:
            for x in [-2, -1, 0, 1, 2]:
                mx, my = self.game.enemies[0].x + x, self.game.enemies[0].y + y  # just 1 enemy
                if 0 <= mx <= GRIDWIDTH / TILESIZE and 0 <= my <= GRIDHEIGHT / TILESIZE:
                    matricx_local_5x5[x+2][y+2] = global_matrix[mx][my]
                else:
                    matricx_local_5x5[x+2][y+2] = 1
        local_observations["5x5"] = matricx_local_5x5

        return local_observations

    def calculate_vector_properties(self):
        # alive         0 1 2
        # direction --> 8 x 4
        # range         7 6 5
        vector_properties = {}
        if self.alive:
            vector_properties["alive"] = 1
        else:
            vector_properties["alive"] = 0
        vector_properties["direction"] = table_feasible_directions[str(self.direction)]
        vector_properties["range"] = self.range_fire
        return vector_properties

    def move(self, dx, dy):
        if self.alive:
            self.setDirection(dx, dy)
            self.x += dx
            self.y += dy

    def setDirection(self, dx, dy):
        self.direction = [dx, dy]
        if dx == -1 and dy == -1:
            self.image = self.image_NO
        elif dx == 0 and dy == -1:
            self.image = self.image_N
        elif dx == 1 and dy == -1:
            self.image = self.image_NE
        elif dx == 1 and dy == 0:
            self.image = self.image_E
        elif dx == 1 and dy == 1:
            self.image = self.image_SE
        elif dx == 0 and dy == 1:
            self.image = self.image_S
        elif dx == -1 and dy == 1:
            self.image = self.image_SO
        elif dx == -1 and dy == 0:
            self.image = self.image_O

    def shoot_fire(self):
        for shoot in self.fire_shoots:
            wx = self.player.x
            wy = self.player.y
            if isClose(wx, shoot.getX(), 0.5) and isClose(wy, shoot.getY(), 0.5):
                self.player.destroid()

    def isCollision(self, dx, dy):
        not_collision = True
        for wall in self.game.walls:
            if isClose(wall.getX(), self.x + dx, 0.5) and isClose(wall.getY(), self.y+dy, 0.5):
                not_collision = False
        return not_collision

    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

    def destroid(self):
        print("Enemy died")
        self.kill()
        self.image = self.image_broken
        pg.sprite.Sprite.__init__(self, self.game.all_sprites, self.game.walls_sprites)
        self.alive = False



