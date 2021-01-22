from settings import *
from Utils import isClose
from random import randint


class Object:
    def __init__(self, x, y, image, game):
        self.x = x
        self.y = y
        self.game = game
        self.image = image
        self.rect = self.image.get_rect()
        super().__init__()

    def getX(self):
        return self.x

    def getY(self):
        return self.y


table_feasible_directions = {
        "0": [-1, -1],
        "1": [0, -1],
        "2": [1, -1],
        "3": [1, 0],
        "4": [1, 1],
        "5": [0, 1],
        "6": [-1, 1],
        "7": [-1, 0],
        "[-1, -1]": 0,
        "[0, -1]": 1,
        "[1, -1]": 2,
        "[1, 0]": 3,
        "[1, 1]": 4,
        "[0, 1]": 5,
        "[-1, 1]": 6,
        "[-1, 0]": 7
    }


class Character(Object):
    def __init__(self, x, y, image, game):
        Object.__init__(self, x, y, image, game)
        self.direction = [1, -1]
        self.feasible_move = []
        for id in [-1, 0, 1]:
            self.feasible_move.append(FeasibleMove(self.game, self, id))
        self.range_fire = 2
        self.fire_shoots = self.fire_x_init()

    def fire_x_init(self):
        fire_xs = []
        start_fire_dir = [-2, +2]
        for i in range(2):
            fire_xs.append(FireX(self.game, self, i, start_fire_dir[i]))
        return fire_xs

    def move_shoot_and_moves(self):
        for block in self.feasible_move:
            block.move()
        for fire_shoot in self.fire_shoots:
            fire_shoot.move()

    def move(self,dx, dy):
        self.setDirection(dx, dy)
        self.x += dx
        self.y += dy

    def step(self, action):
        pass

    def random_action(self):
        feasible_dir = [table_feasible_directions[str((table_feasible_directions[str(self.direction)] + d.id) % 8)] for d in self.feasible_move if
                        d.no_collision()]
        return randint(0, len(feasible_dir))

    def destroid(self):
        pass

    def setDirection(self, dx, dy):
        pass
    def getDirection(self):
        return self.direction
    def shoot_fire(self):
        pass


class FeasibleMove(pg.sprite.Sprite, Object):
    def __init__(self, game, player, id):
        Object.__init__(self, None, None,  pg.Surface((TILESIZE - 3, TILESIZE - 3)), game)
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.player = player
        self.id = id

        self.image.fill(LIGHTGREY)
        self.move()

        self.fix_dxdy = 2
        self.any_collision = True
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

    def move(self):
        d = self.player.getDirection()
        dx, dy = table_feasible_directions[str((table_feasible_directions[str(d)] + self.id) % 8)]
        self.x = self.player.getX() + dx
        self.y = self.player.getY() + dy
        self.any_collision = True
        for wall in self.game.walls:
            if isClose(wall.getX(), self.x, 0.5) and isClose(wall.getY(), self.y, 0.5):
                self.any_collision = False
        if self.x >= GRIDWIDTH / TILESIZE or self.x < 0 or self.y >= GRIDHEIGHT / TILESIZE or self.y < 0:
            self.any_collision = False

    def no_collision(self):
        return self.any_collision

    def update(self):
        if self.any_collision:
            self.rect.x = self.x * TILESIZE + self.fix_dxdy
            self.rect.y = self.y * TILESIZE + self.fix_dxdy
        else:
            self.rect.x = -10  # todo fix this
            self.rect.y = -10


class FireX(pg.sprite.Sprite, Object):
    def __init__(self, game, player,  id, traj):
        Object.__init__(self, None, None, pg.image.load('images/fire_x.png'), game)
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.player = player
        self.id = id
        self.trajectory_offset = traj
        self.move()

    def move(self):
        traj = table_feasible_directions[str((table_feasible_directions[str(self.player.getDirection())] + self.trajectory_offset) % 8)]
        range_fire = self.player.range_fire
        stop = False
        for i in range(1, range_fire + 1):
            x = self.player.getX() + traj[0] * i
            y = self.player.getY() + traj[1] * i
            #  check collision with walls or enemy
            for coll in self.game.walls + self.game.enemies:
                if isClose(x, coll.x, 0.5) and isClose(y, coll.y, 0.5):
                    if isinstance(coll, Character):
                        range_fire = i
                    else:
                        range_fire = i - 1
                    stop = True
                    break
            #  check out-of-map problem
            if x >= GRIDWIDTH / TILESIZE or x < 0 or y >= GRIDHEIGHT / TILESIZE or y < 0:
                range_fire = i - 1
                stop = True
            if stop:
                break
        if range_fire > 0:
            self.x = self.player.getX() + traj[0] * range_fire
            self.y = self.player.getY() + traj[1] * range_fire
        else:
            self.x = -10  # todo fix this
            self.y = -10

    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE


