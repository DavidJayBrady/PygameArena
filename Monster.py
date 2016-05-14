import pygame
from pygame.locals import *
from random import randrange


from SpriteSheet import SpriteSheet
from Sword import Attack
from Sword import Arrow
from Sword import FireStorm
from Character import Character
from Mover import Mover
from HUD import Bar


class Monster(Mover):
    def __init__(self):
        Mover.__init__(self)
        monsters = SpriteSheet('instant_dungeon_artpack/By Scott Matott/monsters.png')
        pick_monster = monsters.image_at([0, 112, 16, 16]).convert()

        self.exp_value = 100

        self.level = 2

        self.scale_factor = [64, 64]

        self.enlarge = lambda x: pygame.transform.smoothscale(x, self.scale_factor)

        self.image = self.enlarge(pick_monster) # pygame.Surface
        self.image.set_colorkey((0, 0, 0))

        monster_images = monsters.load_strip([0, 112, 16, 16, 8], 8)
        self.load_images(monster_images)

        self.rect = self.image.get_rect() # pygame.Rect
        self.rect = self.rect.move([randrange(700, 3670), randrange(700, 2160)]) # Random spawn location

        self.direction = randrange(1, 9) # Refer to Mover.update method
        self.walk_counter = 0            # Keep monsters from changing directions constantly

        # Speed is used for finding direction. Velocity already contains that direction.
        self.speed = [2, 2]
        self.velocity = pygame.math.Vector2(self.speed)

        self.health = 90 + (25 * self.level)
        self.max_health = self.health

        self.timer = pygame.time.get_ticks()

        self.cooldown = 800

        self.uses_caps = False

        self.offset = [5, -15]

        self.healthbar = Bar(self.offset, self.uses_caps, False, 'health')

    def load_images(self, monster_images):
        self.down_image = self.enlarge(monster_images[0]).convert()
        self.up_image = self.enlarge(monster_images[2]).convert()
        self.right_image = self.enlarge(monster_images[4]).convert()
        self.left_image = self.enlarge(monster_images[6]).convert()

        self.image.set_colorkey((0, 0, 0))
        self.down_image.set_colorkey((0, 0, 0))
        self.up_image.set_colorkey((0, 0, 0))
        self.right_image.set_colorkey((0, 0, 0))
        self.left_image.set_colorkey((0, 0, 0))


    def attack(self, char_cord):
        if pygame.time.get_ticks() - self.timer > self.cooldown: # Limit attacks per second.
            if self.player_around(char_cord, 100, '<'):
                self.timer = pygame.time.get_ticks()
                monster_to_player = pygame.math.Vector2(list(map(lambda x, y: x - y,
                                                                 list(char_cord)[:2], self.rect.center)))
                unit_vect = monster_to_player.normalize()
                sword = Attack(unit_vect, self.rect, False, self.level)
                return sword

    def walk_random(self):
        '''
        :param monster_list: List of monsters
        :actions: Move the monsters in random directions at random speeds
        '''
        find_speed = {1: [-self.speed[0], 0], 2: [self.speed[0], 0], # + on x direction is right, - is left
                          3: [0, self.speed[1]], 4: [0, -self.speed[1]], # + on y is down, - is up
                           5: [-self.speed[0], -self.speed[1]], 6: [self.speed[0], -self.speed[1]],
                           7: [-self.speed[0], self.speed[1]], 8: [self.speed[0], self.speed[1]]}
        if self.walk_counter > 100:
            self.direction = randrange(1, 9) # 1 left, 2 right, 3 down, 4 up, 5 northwest
            self.walk_counter = 0            # 6 northeast, 7 southwest, 8 southeast
        self.velocity = find_speed[self.direction]
        self.walk_counter += 1

    def update(self, char_velocity, char_rect, elapsed_time):
        Mover.update(self, char_velocity, char_rect, elapsed_time)
        if not self.player_around(char_rect, 700, '<'):
            self.walk_random()
        else:
            self.walk_to_player(char_rect)
        self.change_image()
        self.rect = self.rect.move(self.velocity)

    def change_image(self):
        if self.velocity[0] < 0 and abs(self.velocity[0]) >= abs(self.velocity[1]):
            self.image = self.left_image
        elif self.velocity[0] > 0 and abs(self.velocity[0]) >= abs(self.velocity[1]):
            self.image = self.right_image
        elif self.velocity[1] > 0 and abs(self.velocity[1]) >= abs(self.velocity[0]):
            self.image = self.down_image
        elif self.velocity[1] < 0 and abs(self.velocity[1] >= abs(self.velocity[0])):
            self.image = self.up_image

    def player_around(self, char_rect: Rect, tolerance: int, less_or_greater: str) -> bool:
        '''
        :param char_rect: Player rectangle, used to get player coordinates.
        :param tolerance: The length in pixels to have around player.
        :return: True if monster is within tolerance range, False otherwise.
        '''
        # Note that while we subtract the entire Rects, we only use the first 2 elements, which are the coordinates.
        dist_vect = pygame.math.Vector2(list(map(lambda player, monster: player - monster, char_rect, self.rect))[:2])
        mag_dist_vect = dist_vect.length()
        if less_or_greater == '<':
            return mag_dist_vect < tolerance
        else:
            return mag_dist_vect > tolerance


    def walk_to_player(self, char_rect):
        dist_vect = pygame.math.Vector2(list(map(lambda player, monster: player - monster, char_rect, self.rect))[:2])
        unit_vect = dist_vect.normalize()
        self.velocity = list(map(lambda speed, unit: speed * unit, unit_vect, self.speed))

    @staticmethod # This method is used for ALL classes of monsters, thus the "monster_info"
    def spawn_monsters(character: Character, walls, monster_info: tuple) -> list:
        '''
        :param character:Duh
        :param walls: Duh
        :param monster_info: Tuple containing monster type and number to make.
        :return: Monsters!
        '''
        monster_list = []
        for monster_class, number in monster_info:
            for i in range(number - 1):
                monster = monster_class()
                if pygame.sprite.spritecollideany(monster, monster_list) == None and\
                                pygame.sprite.collide_rect(monster, character) == False and\
                                    pygame.sprite.spritecollideany(monster, walls) == None:
                    monster_list.append(monster)

        return monster_list

    def handle_collision(self, collided_sprites):
        ''' If collided with any sort of attack, take damage. Else, bounce off thing monster collided with. '''
        for sprite in collided_sprites:
            if (isinstance(sprite, Attack) or isinstance(sprite, FireStorm)) and sprite.from_player:
                self.take_damage(sprite.damage)
            else:
                self.rect = self.rect.move(-self.velocity[0], -self.velocity[1])
                self.walk_counter += 100

    def take_damage(self, damage: int):
        self.health -= damage

    def is_dead(self):
        return self.health <= 0

    def draw_health_bar(self, screen):
        if not self.is_dead():
            self.healthbar.draw_health_bar(screen, self.rect, self.health, self.max_health)

class ChampionMeleeMonster(Monster):
    def __init__(self):
        Monster.__init__(self)

        self.level = 3

        self.exp_value = 250

        monsters = SpriteSheet('instant_dungeon_artpack/By Scott Matott/monsters.png')

        self.image = self.enlarge(monsters.image_at([0, 128, 16, 16]).convert()) # pygame.Surface
        self.image.set_colorkey((0, 0, 0))

        monster_images = monsters.load_strip([0, 128, 16, 16, 8], 8)

        self.load_images(monster_images)

        # Speed is used for finding direction. Velocity already contains that direction.
        self.speed = [3, 3]
        self.velocity = pygame.math.Vector2(self.speed)

        self.health = 150 + (30 * self.level)
        self.max_health = 150 + (30 * self.level)

        self.cooldown = 500

        self.uses_caps = True

        self.offset = (-40, -30)

        self.healthbar = Bar(self.offset, self.uses_caps, False, 'health')

class RangeMonster(Monster):

    detect_range = 800
    attack_range = 450
    run_to_range = 450
    run_away_range = 200


    def __init__(self):
        Monster.__init__(self)
        monsters = SpriteSheet('instant_dungeon_artpack/By Scott Matott/monsters.png')
        pick_monster = monsters.image_at([0, 64, 16, 16]).convert()

        self.scale_factor = [64, 64]

        self.enlarge = lambda x: pygame.transform.smoothscale(x, self.scale_factor)

        self.image = self.enlarge(pick_monster) # pygame.Surface
        self.image.set_colorkey((0, 0, 0))

        monster_images = monsters.load_strip([0, 64, 16, 16, 8], 8)
        self.load_images(monster_images)

        self.direction = randrange(1, 9) # Refer to Mover.update method
        self.walk_counter = 0            # Keep monsters from changing directions constantly

        # Speed is used for finding direction. Velocity already contains that direction.
        self.speed = [2, 2]
        self.velocity = pygame.math.Vector2(self.speed)

        self.health = 80 + (10 * self.level)
        self.max_health = self.health

    def update(self, char_speed, char_rect, elapsed_time):
        ''' Overriding for range monster to maintain a distance from the player. '''
        Mover.update(self, char_speed, char_rect, elapsed_time)

        # Walk to player if more than 800 pixels away.
        if self.player_around(char_rect, RangeMonster.detect_range, '>') and self.player_around(char_rect, 900, '<'):
            self.walk_to_player(char_rect)

        # Walk from player if less than 150 pixels away.
        if self.player_around(char_rect, 150, '<'):
            self.walk_from_player(char_rect, char_speed)

        else:
            self.walk_random()

        self.change_image()
        self.rect = self.rect.move(self.velocity)

    def walk_from_player(self, char_rect, char_speed):
        ''' Make velocity in direction away from player. '''
        dist_vect = pygame.math.Vector2(list(map(lambda player, monster: monster - player, char_rect, self.rect))[:2])
        unit_vect = dist_vect.normalize()
        self.velocity = list(map(lambda speed, unit: speed * unit, unit_vect, self.speed))

    def attack(self, char_cord):
        if self.player_around(char_cord, RangeMonster.attack_range, '<'):
            monster_to_player = pygame.math.Vector2(list(map(lambda x, y: x - y,
                                                             list(char_cord)[:2], self.rect.center)))
            unit_vect = monster_to_player.normalize()
            arrow = Arrow(unit_vect, self.rect, False, self.level)
            if pygame.time.get_ticks() - self.timer > arrow.cooldown and self.player_around(char_cord, 800, '<'): # Limit attacks per second.
                    self.timer = pygame.time.get_ticks()
                    return arrow
