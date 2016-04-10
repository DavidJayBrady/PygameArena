global LEFT
LEFT = 1
global RIGHT
RIGHT = 3



import pygame
from pygame.locals import *
from sys import exit

from Mover import Mover
from Background import Background
from Background import Wall
from Character import Character
from Monster import Monster
from Monster import ChampionMeleeMonster
from Monster import RangeMonster
from HUD import AbilityManager
from Sword import Attack
from Sword import FireStorm
from Sword import ToughenUp


'''
Some things to take a next step:
    - Equipment
        - Handling inventory
            - Sort of Skyrim STyle
                - Menu on right side of screen above experirence bar, 3 tabs (main hand, armor, offhand)
                - Items will be represented as text, can have picture show up when scrolling over.
    - Bug Fixes
        - Monsters should always be above the LavaGround.
        - Monsters should not block friendly arrows.
    - Make this games positions not hardcoded. Only set for 1280 by 800 pixels right now.
'''

class PgGroup(pygame.sprite.Group):
    def __init__(self, *args):
        pygame.sprite.Group.__init__(self, *args)

    @staticmethod
    def update_attacks(all_sprites):
        for sprite in all_sprites:
            if isinstance(sprite, Attack) or isinstance(sprite, FireStorm):
                sprite.weapon_update()


    @staticmethod
    def monster_attack(monsters: 'PgGroup', char_chord):
        monster_swords = []
        for monster in monsters:
            monster_weapon = monster.attack(char_chord)
            if isinstance(monster_weapon, Attack):
                monster_swords.append(monster_weapon)
        return monster_swords

    @staticmethod
    def draw(screen, background, rest_of_sprites):
        screen.blit(background.image, background.rect)
        for sprite in rest_of_sprites:
            screen.blit(sprite.image, sprite.rect)


class GameState:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 800))
        self.area = self.screen.get_rect()
        self.walls = Wall.gather_walls()

        self.my_clock = pygame.time.Clock()     # Utility object

        self.background = Background()          # Objects we put on screen
        self.character = Character(self.area)

        self.all_but_background = PgGroup((self.character, self.walls))

        self.monsters = Monster.spawn_monsters(self.character, self.walls, ((ChampionMeleeMonster, 10), (Monster, 20),
                                                                            (RangeMonster, 20)))

        self.ability_manager = AbilityManager()

        # So we can call each monster's attack method.
        self.monster_group = PgGroup(self.monsters)

        # Used to update everything to screen.
        self.all_sprites = PgGroup((self.character, self.monsters, self.background, self.walls))

        # Used to draw. We separate background so we can ensure it gets pictured before other things.
        self.all_but_background.add(self.monsters)

        self.time_test = False
        self.time_dict = {'drawmove': 0, 'abilitydraw': 0, 'eventloop': 0, 'attacks': 0, 'collisions': 0,
                          'move': 0, 'clear/recover': 0, 'drawbars': 0}
        self.loop_counter = 0

    def clear_weapon(self):
        # If sword is on screen, clear it off.
        for sprite in self.all_but_background:
            if isinstance(sprite, Attack) and sprite.is_dead():
                sprite.kill()

    def clear_dead(self):
        # Remove dead monsters/players from game.
        for sprite in self.all_but_background:
            if type(sprite) is Monster or Character:
                if sprite.is_dead():
                    sprite.kill()
                    if isinstance(sprite, Monster):
                        self.character.experience += sprite.exp_value
                        if self.character.level_up():
                            self.ability_manager.ability_points += 1
                    elif type(sprite) is Character:
                        #self.print_credits()
                        exit()

    def main(self):
        elapsed_time = 0
        while True:
            a = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == QUIT:
                    if self.time_test:
                        for key, value in self.time_dict.items():
                            print(key, value/self.loop_counter)
                    pygame.quit()
                    #self.print_credits()
                    exit()
                if event.type == KEYUP:
                    Mover.handle_character_event(event, False)
                elif event.type == KEYDOWN:
                    if event.key == K_1 or event.key == K_2 or event.key == K_3 or event.key == K_4:
                        hotkey = event.key - 49 # printing out event.key gives 49, 50, 51, 52; for K_1, K_2...
                        if self.ability_manager.ability_hotkeys[hotkey] is not None:
                            self.ability_manager.ability = self.ability_manager.ability_hotkeys[hotkey]
                    else:
                        Mover.handle_character_event(event, True)
                elif event.type == MOUSEBUTTONDOWN and event.button == LEFT:
                    if self.ability_manager.menu_up:
                        test_index = self.ability_manager.menu_ability_clicked(event.pos)
                        if test_index[0]:
                            self.ability_manager.change_hotkey(test_index[1])
                    if self.ability_manager.ability_image_clicked(event.pos):
                        self.ability_manager.set_menu_up(True) if not self.ability_manager.menu_up else self.ability_manager.set_menu_up(False)
                    else:
                        self.ability_manager.set_menu_up(False)
                        weapon = self.character.attack(event.pos, self.ability_manager.ability)
                        if weapon != None:
                            self.all_but_background.add(weapon) # For collisions
                            self.all_sprites.add(weapon) # For movement
                elif event.type == MOUSEBUTTONDOWN and event.button == RIGHT:
                    if self.ability_manager.menu_up:
                        test_index = self.ability_manager.menu_ability_clicked(event.pos)
                        if test_index[0] and self.ability_manager.ability_points > 0:
                            self.ability_manager.ability_list[test_index[1]].level_up()
                            self.ability_manager.ability_points -= 1
                            self.character.increment_maxes(ToughenUp.ability_level)
            b = pygame.time.get_ticks() - a
            self.screen.fill((0, 0, 0))

            self.character.calc_velocity(elapsed_time)

            PgGroup.update_attacks(self.all_but_background)

            monster_weapons = PgGroup.monster_attack(self.monster_group, self.character.rect.center)
            self.all_but_background.add(monster_weapons)
            self.all_sprites.add(monster_weapons)
            c = pygame.time.get_ticks() - (b + a)
            # Collisions, must be after attack so can check for collisions between sword/monser/player.
            Mover.check_collision_group(self.all_but_background, self.screen)
            d = pygame.time.get_ticks() - (c + b + a)
            # Move and show everything.
            self.all_sprites.update(self.character.velocity, self.character.rect)
            e = pygame.time.get_ticks() - (d + c + b + a)

            PgGroup.draw(self.screen, self.background, self.all_but_background)
            z = pygame.time.get_ticks() - (e + d+ c + b + a)
            self.clear_weapon() # Must be after draw. Keep at end of loop, since attack happens in event for loop.
            self.clear_dead()

            self.character.recover(ToughenUp.ability_level)

            f = pygame.time.get_ticks() - (e + d + c + b + a + z)

            # Draw the HUD
            self.character.draw_bars(self.screen)

            for monster in self.monsters:
                monster.draw_health_bar(self.screen)
            g = pygame.time.get_ticks() - (f + e + d + c + b + a + z)
            self.ability_manager.draw(self.screen)
            h = pygame.time.get_ticks() - (g + f + e + d + c + b + a + z)

            if self.time_test:
                self.time_dict['eventloop'] += b
                self.time_dict['attacks'] += c
                self.time_dict['collisions'] += d
                self.time_dict['move'] += e
                self.time_dict['drawmove'] += z
                self.time_dict['clear/recover'] += f
                self.time_dict['drawbars'] += g
                self.time_dict['abilitydraw'] += h
                self.loop_counter += 1

            pygame.display.update()
            elapsed_time = self.my_clock.tick(20)

    def print_credits(self):
        print("Thanks to Ryan Ward for helping me learn object oriented programming with this project.")
        print("Thanks to opengameart.org, most images used in this game were from there..")
        print("The ToughenUp ability picture was found on google images, but it originated from *Fable: The Lost Chapters.*")

if __name__ == '__main__':
    gamestate = GameState()
    gamestate.main()