import pygame
from pygame.locals import *

from SpriteSheet import SpriteSheet

from math import atan
from math import degrees
from random import randrange

# If you get add_internal error, make sure you inherit from pygame.sprite.Sprite


class ToughenUp:

    def __init__(self, player_to_click, sprite_cord, from_player, ability_level):
        self.coodown = 10000
        self.energy_consume = 0
        self.damage = 0

class Attack(pygame.sprite.Sprite):

    def __init__(self, player_to_click, sprite_cord, from_player, ability_level):
        pygame.sprite.Sprite.__init__(self)

        self.unit_vect = player_to_click.normalize()

        self.from_player = from_player
        self.sprite_cord = sprite_cord

        self.angle = self.find_angle(self.unit_vect)

        self.move_image(self.unit_vect, sprite_cord)

        self.dead = True

        self.damage = 10 + (ability_level * 5) if from_player else 10
        self.cooldown = 400 if from_player else 600
        self.energy_consume = 10

    def find_angle(self, unit_vect: pygame.math.Vector2) -> int:  # Make better name sometime
        try:
            angle = degrees(atan(-unit_vect[1]/unit_vect[0])) # Negative the y cord since + y is down.
        except ZeroDivisionError:
            if -unit_vect[1] > 0:
                angle = 90
            else:
                angle = 270
        if unit_vect[0] < 0:
            angle += 180
        return angle

    def move_image(self, unit_vect, sprite_cord):
        '''
        :param unit_vect: Directional vector from player to click.
        :param sprite_cord: Coordinate of sprite that made the Attack.
        :action: Make the new rectangle, load the right image. Moves the weapon on screen.
        '''
        self.load_transform_image()
        self.new_rect(unit_vect, sprite_cord)

    def load_transform_image(self):
        '''
        :action: Loads image of sword and scales it accordingly, and rotates it in the correct direction.
        '''
        sword_images = SpriteSheet('instant_dungeon_artpack/By Voytek Falendysz/shield_knife_and_scrolls.png')
        image = sword_images.image_at([86, 0, 5, 16])
        self.image = pygame.transform.smoothscale(image, [20, 64])

        # Rotate sword to go in direction of click. Minus 90 because sword originally points upwards.
        self.image = pygame.transform.rotate(self.image, self.angle - 90)

    def new_rect(self, unit_vect, sprite_cord):
        '''
        :param unit_vect: Directional vector from player to click.
        :param sprite_cord: Coordinates of sprite that made the attack. (Player or monster)
        :action: Move the sprite_cord in the direction of the unit_vect.
        '''
        vector = list(map(lambda x: 80 * x, unit_vect))
        self.image.set_colorkey((0, 0, 0))

        # Get rect of image, move image to center of character, then start it right in front of player.
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(sprite_cord[0], sprite_cord[1])
        self.rect = self.rect.move(vector)

    def handle_collision(self, collided_sprite):
        pass

    def weapon_update(self):
        pass

    def is_dead(self):
        return self.dead


class Sweep(Attack):


    def __init__(self, player_to_click, sprite_cord, from_player, ability_level):
        Attack.__init__(self, player_to_click, sprite_cord, from_player, ability_level)

        self.from_player = from_player

        self.rotated = 0
        self.dead = False

        self.damage = 10 + (ability_level * 5)

        self.energy_consume = 25

        self.cooldown = 800

        # Makes Sweep start right at click.
        self.unit_vect = self.unit_vect.rotate(-20)
        self.angle += 20

    def weapon_update(self):
        self.rotated += 40 # Keep rotating until 360 has happened.

        self.angle -= 40 # Rotates picture
        self.unit_vect = self.unit_vect.rotate(40) # Changes the unit vector.

        self.move_image(self.unit_vect, self.sprite_cord) # move_image inherited from Attack
        if self.rotated >= 360:
            self.dead = True

class Arrow(Attack):

    def __init__(self, player_to_click, sprite_cord, from_player, ability_level):
        Attack.__init__(self, player_to_click, sprite_cord, from_player, ability_level)


        self.x_move_ratio = self.unit_vect[0] * 20
        self.y_move_ratio = self.unit_vect[1] * 20

        self.move_image(self.unit_vect, sprite_cord)

        self.dead = False

        self.cooldown = 450 if from_player else 2500

        self.damage = 10 + (ability_level * 5)

    def load_transform_image(self):
        self.image = pygame.image.load('Other Art/arrow.png')
        self.image = pygame.transform.smoothscale(self.image, [64, 32])

        # Rotate sword to go in direction of click. Minus 90 because sword originally points upwards.
        self.image = pygame.transform.rotate(self.image, self.angle)

    def weapon_update(self):
        ''' Move projectile forward. '''
        self.rect = self.rect.move(self.x_move_ratio, self.y_move_ratio)

    def update(self, character_velocity, char_rect):
        '''
        :action: Move projectile with character, so its path is normal.
        '''
        self.rect.move_ip(character_velocity[0], character_velocity[1])

    def handle_collision(self, collided_sprite):
        if not isinstance(collided_sprite, Arrow):
            self.dead = True


class SplitShot:


    def __init__(self, player_to_click, sprite_cord, from_player, ability_level):
        unit_vect = player_to_click.normalize()

        mag_vect = player_to_click.length()

        self.arrow1 = Arrow(unit_vect, sprite_cord, from_player, ability_level)

        unit_vect2 = unit_vect.rotate(1500/mag_vect*2)
        self.arrow2 = Arrow(unit_vect2, sprite_cord, from_player, ability_level)

        unit_vect3 = unit_vect.rotate(-1500/mag_vect*2)
        self.arrow3 = Arrow(unit_vect3, sprite_cord, from_player, ability_level)

        self.cooldown = self.arrow1.cooldown

        self.energy_consume = self.arrow1.energy_consume * 3


class Lightning(Arrow):


    def __init__(self, player_to_click,  sprite_cord, from_player, ability_level):
        Arrow.__init__(self, player_to_click, sprite_cord, from_player, ability_level)

        self.cooldown = 350
        self.damage = randrange(3, 17)  + (ability_level * (randrange(2, 6)))

        self.x_move_ratio = self.unit_vect[0] * 70
        self.y_move_ratio = self.unit_vect[1] * 70

    def load_transform_image(self):
        self.image = pygame.image.load('Other Art/Lightning.jpg')
        self.image = pygame.transform.smoothscale(self.image, [80, 48])

        # Rotate sword to go in direction of click. Minus 90 because sword originally points upwards.
        self.image = pygame.transform.rotate(self.image, self.angle)


class FireStorm(pygame.sprite.Sprite):


    def __init__(self, player_to_click, sprite_cord, from_player, ability_level):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.smoothscale(pygame.image.load('Other Art/LavaGround.png'), [120, 120])
        self.image.set_colorkey((0, 0, 0))

        if player_to_click.length() > 500:
            return None

        self.from_player = from_player

        # 608, 368 is Center of character
        self.rect = Rect(list(map(lambda x, y: x + y, (608, 368), player_to_click)) + [64, 64])

        self.cooldown = 600

        self.energy_consume = 30

        self.damage = 4 + (ability_level * .5)

        self.dead = False

        self.lifetime = 4000 # Milliseconds

        self.current_time = pygame.time.get_ticks()

    def weapon_update(self):
        self.lifetime -= (pygame.time.get_ticks() - self.current_time)
        self.current_time = pygame.time.get_ticks()
        if self.lifetime < 0:
            self.dead = True

    def handle_collision(self, collided_sprite):
        pass

    def update(self, character_velocity, char_rect):
        '''
        :action: Move fire with character, so its path is normal.
        '''
        self.rect.move_ip(character_velocity[0], character_velocity[1])

    def is_dead(self):
        return self.dead

# Spell idea, put lightning thorns around player.
# So that walking around a monster would do damage, or weird armor buff,
# Spells can cause + buffs on player.

# Spell idea,  ice wall in front of player. Chill enemies near wall. Blocks attacks till it "dies".