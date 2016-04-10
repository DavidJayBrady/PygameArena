import pygame
from pygame.locals import *

from Sword import Arrow
from Sword import FireStorm

class Mover(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.is_player = False

    set_up = False     # Booleans used for character movement
    set_left = False
    set_down = False
    set_right = False

    @staticmethod
    def handle_character_event(event, setting: bool):
        '''
        :param event: Type of event is either KEYDOWN or KEYUP.
        :param setting: True or False depending on KEYDOWN or KEYUP.
        :action: Change the right setting to the right boolean.
        '''
        if event.key == K_w:
            Mover.set_up = setting
        if event.key == K_s:
            Mover.set_down = setting
        if event.key == K_a:
            Mover.set_left = setting
        if event.key == K_d:
            Mover.set_right = setting

    def update(self, character_velocity, char_rect):
        '''
        :param items: List of rectangles, representing locations
        :param sprite_list: All of the sprites we need to move
        :param character_speed: How fast we need to move the sprites, to make illusion of player moving.
        :action: Move all rectangles according to input and player speed.
        '''
        self.rect.move_ip(character_velocity[0], character_velocity[1])


    @staticmethod
    def check_collision_group(most_sprites: pygame.sprite.Group, screen):
        for sprite in most_sprites:
            most_sprites.remove(sprite)

            removed_friendlies = []
            if type(sprite) is Arrow: # To prevent friendly projectiles from colliding with each other.
                for sprite2 in most_sprites:
                    if type(sprite2) is Arrow and sprite.from_player == sprite.from_player:
                        most_sprites.remove(sprite2); removed_friendlies.append(sprite2)

            # Try to get this working to prevent monster arrows colliding with other monsters.
            #if type(sprite) is Arrow and sprite.from_player is False:
            #    for sprite2 in most_sprites:
            #        if isinstance(sprite2, Monster):
            #            most_sprites.remove(sprite2)
            #            removed_friendlies.append(sprite2)


            collided_sprite = pygame.sprite.spritecollideany(sprite, most_sprites)
            most_sprites.add(removed_friendlies)
            if collided_sprite is not None:
                sprite.handle_collision(collided_sprite)
            most_sprites.add(sprite)

