from Base_classes import Character
from settings import *
from Utils import isClose


class Player(pg.sprite.Sprite, Character):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)

        self.image_N = pg.image.load('images/player_N.png')
        self.image_E = pg.image.load('images/player_E.png')
        self.image_S = pg.image.load('images/player_S.png')
        self.image_O = pg.image.load('images/player_O.png')
        self.image_NE = pg.image.load('images/player_NE.png')
        self.image_SE = pg.image.load('images/player_SE.png')
        self.image_SO = pg.image.load('images/player_SO.png')
        self.image_NO = pg.image.load('images/player_NO.png')
        Character.__init__(self, x, y, self.image_NE, game)

    def move(self, dx=0, dy=0):
        Character.move(self, dx, dy)
        pg.event.post(pg.event.Event(ENEMY_TURN_EVENT))

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
            for enemy in self.game.enemies:
                wx = enemy.x
                wy = enemy.y
                if isClose(wx, shoot.getX(), 0.5) and isClose(wy, shoot.getY(), 0.5):
                    enemy.destroid()
        pg.event.post(pg.event.Event(ENEMY_TURN_EVENT))

    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

    def destroid(self):
        print("game over")






