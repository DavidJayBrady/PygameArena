import pygame
from pygame.locals import *

from SpriteSheet import SpriteSheet

from math import atan
from math import degrees
from random import randrange

# If you get add_internal error, make sure you inherit from pygame.sprite.Sprite
pygame.font.init()
FONT = pygame.font.Font(None, 26)


MELEE_COLOR = (220, 20, 60)
MELEE_INFO_COLOR = (220, 100, 120)

RANGE_COLOR = (20, 200, 60)
RANGE_INFO_COLOR = (80, 170, 110)

MAGIC_COLOR = (90, 140, 220)
MAGIC_INFO_COLOR = (70, 120, 220)

PASSIVE_COLOR = (200, 150, 100)
PASSIVE_INFO_COLOR = (180, 160, 110)


def adjust(detail_box, x):
    return list(map(lambda x, y: x + y, x, detail_box))

class Ability(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

    @staticmethod
    def gather_statistics(type, ability_level, detail_box):
        stats = {}
        stats[FONT.render(type.name, True, type.name_color)] = adjust(detail_box, (10, 10))
        stats[FONT.render("Level: "+str(ability_level), True, type.info_color)] = adjust(detail_box, (110, 10))
        stats[FONT.render("Type: " +str(type.ability_type), True, type.info_color)] = adjust(detail_box, (250, 50))
        stats[FONT.render("Damage: "+str(type.calc_damage(ability_level, True)), True, type.info_color)] = adjust(detail_box, (225, 10))
        stats[FONT.render("Energy: "+str(type.calc_energy_consume(ability_level, True)), True, type.info_color)] = adjust(detail_box, (10, 50))
        stats[FONT.render("Cooldown: "+str(type.calc_cooldown(ability_level, True)), True, type.info_color)] = adjust(detail_box, (110, 50))
        stats[FONT.render(type.description, True, type.info_color)] = adjust(detail_box, (10, 80))
        return stats


class ToughenUp(Ability):
    name = "Toughen Up"
    ability_type = "Passive"
    description = "Increases HP capacity and regeneration."
    name_color = PASSIVE_COLOR
    info_color = PASSIVE_INFO_COLOR

    def __init__(self):
        Ability.__init__(self)

    @staticmethod
    def calc_damage(ability_level, from_player):
        return None

    @staticmethod
    def calc_cooldown(ability_level, from_player):
        return None

    @staticmethod
    def calc_energy_consume(ability_level, from_player):
        return None

    @staticmethod
    def gather_statistics(type, ability_level, detail_box):
        stats = {}
        stats[FONT.render(type.name, True, type.name_color)] = adjust(detail_box, (10, 10))
        stats[FONT.render("Level: "+str(ability_level), True, type.info_color)] = adjust(detail_box, (130, 10))
        stats[FONT.render("Type: " +str(type.ability_type), True, type.info_color)] = adjust(detail_box, (215, 10))
        stats[FONT.render(type.description, True, type.info_color)] = adjust(detail_box, (10, 80))
        return stats


class Attack(Ability):

    name = "Strike"
    ability_type = "Melee"
    description = "Strike in front of character"
    name_color = MELEE_COLOR
    info_color = MELEE_INFO_COLOR

    def __init__(self, player_to_click, sprite_cord, from_player, ability_level):
        Ability.__init__(self)

        self.unit_vect = player_to_click.normalize()

        self.from_player = from_player
        self.sprite_cord = sprite_cord

        self.angle = self.find_angle(self.unit_vect)

        self.move_image(self.unit_vect, sprite_cord)

        self.dead = True

        self.damage = self.calc_damage(ability_level, from_player)
        self.cooldown = self.calc_cooldown(ability_level, from_player)
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

    @staticmethod
    def calc_damage(ability_level, from_player):
        return 15 + (ability_level * 5) if from_player else 10 + (ability_level * 5)

    @staticmethod
    def calc_cooldown(ability_level, from_player):
        return 400 if from_player else 600

    @staticmethod
    def calc_energy_consume(ability_level, from_player):
        return 10


class Sweep(Attack):

    name = "Sweep"
    ability_type = "Melee"
    description = "Melee attack around player."
    name_color = MELEE_COLOR
    info_coor = MELEE_INFO_COLOR

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

    @staticmethod
    def calc_damage(ability_level, from_player):
        return 10 + (ability_level * 5)

    @staticmethod
    def calc_cooldown(ability_level, from_player):
        return 800

    @staticmethod
    def calc_energy_consume(ability_level, from_player):
        return 25


class Arrow(Attack):

    name = "SingleShot"
    ability_type = "Range"
    description = "Fires a single arrow."
    name_color = RANGE_COLOR
    info_color = RANGE_INFO_COLOR

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

    @staticmethod
    def calc_damage(ability_level, from_player):
        return 10 + (ability_level * 5)

    @staticmethod
    def calc_cooldown(ability_level, from_player):
        return 450 if from_player else 2500

class SplitShot(Arrow):

    name = "SplitShot"
    ability_type = "Range"
    description = "Fires 3 arrows in a cone."
    name_color = RANGE_COLOR
    info_color = RANGE_INFO_COLOR

    def __init__(self, player_to_click, sprite_cord, from_player, ability_level):
        Arrow.__init__(self, player_to_click, sprite_cord, from_player, ability_level)
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

    name = "Lightning"
    ability_type = "Magic"
    description = "Fast and and varied damage"
    name_color = MAGIC_COLOR
    info_color = MAGIC_INFO_COLOR

    def __init__(self, player_to_click,  sprite_cord, from_player, ability_level):
        Arrow.__init__(self, player_to_click, sprite_cord, from_player, ability_level)

        self.damage = Lightning.calc_damage(ability_level, from_player)
        self.cooldown = self.calc_cooldown(ability_level, from_player)
        self.energy_consume = Lightning.calc_energy_consume(ability_level, from_player)

        self.x_move_ratio = self.unit_vect[0] * 70
        self.y_move_ratio = self.unit_vect[1] * 70

    def load_transform_image(self):
        self.image = pygame.image.load('Other Art/Lightning.jpg')
        self.image = pygame.transform.smoothscale(self.image, [80, 48])

        # Rotate sword to go in direction of click. Minus 90 because sword originally points upwards.
        self.image = pygame.transform.rotate(self.image, self.angle)

    @staticmethod
    def calc_damage(ability_level, from_player):
        return randrange(3, 35) + (ability_level * (randrange(2,6)))

    @staticmethod
    def calc_cooldown(ability_level, from_player):
        return 350

    @staticmethod
    def calc_energy_consume(ability_level, from_player):
        return 10


class FireStorm(Ability):

    name = "FireStorm"
    ability_type = "Magic"
    description = "Burn an area, damage over time"
    name_color = MAGIC_COLOR
    info_color = MAGIC_INFO_COLOR

    def __init__(self, player_to_click, sprite_cord, from_player, ability_level):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.smoothscale(pygame.image.load('Other Art/LavaGround.png'), [120, 120])
        self.image.set_colorkey((0, 0, 0))

        if player_to_click.length() > 500:
            return None

        self.from_player = from_player

        # 608, 368 is Center of character
        self.rect = Rect(list(map(lambda x, y: x + y, (608, 368), player_to_click)) + [64, 64])

        self.cooldown = FireStorm.calc_cooldown(ability_level, from_player)

        self.energy_consume = FireStorm.calc_energy_consume(ability_level, from_player)

        self.damage = FireStorm.calc_damage(ability_level, from_player)

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

    @staticmethod
    def calc_damage(ability_level, from_player):
        return 1 + (ability_level * .5)

    @staticmethod
    def calc_cooldown(ability_level, from_player):
        return 600

    @staticmethod
    def calc_energy_consume(ability_level, from_player):
        return 30

# Spell idea, put lightning thorns around player.
# So that walking around a monster would do damage, or weird armor buff,
# Spells can cause + buffs on player.

# Spell idea,  ice wall in front of player. Chill enemies near wall. Blocks attacks till it "dies".