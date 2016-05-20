

import pygame
from pygame.locals import *
from sys import exit

from Collisions import Collider
from Mover import Mover
from Background import Background
from Background import Wall
from Character import Character
from Monster import Monster
from Monster import ChampionMeleeMonster
from Monster import RangeMonster
from HUD import AbilityManager
from HUD import Inventory
from Sword import Attack
from Sword import FRAME_RATE

'''
Some things to take a next step:
    - Change how recovering is calculated. Currently in ToughenUp,
        but it belongs in chaacter, because both ToughenUp level and items may affect health/health regen.
            - ToughenUp need not show total regen, only regen from ability. Total regen can be in something else,
            say, a character sheet.

    - Put some thought into FireStorm. Something is off about it.
        - Probably needs to work similar to PoE's fire trap, it's too powerful if you can spam it.
            - But also sucks too much with just a normal long cooldown?


    - Controls. Right click to level up just isn't worth the right click.
        - Consider transfering game to PoE system of movement and using abilities.
    - Ability to hold left click on monster to attack.
    - Equipment
        - Handling inventory
            - Reuse ability manager to hold equipment.
    - Bug Fixes
        - Monsters should always be above the FireStorm

    - Feedback
        - Melee underpowered, range op. Monsters too easy.
        - Aadit
            - Range underpowered, he likes lightning, increase range of attack/sweep.


    - Make this games positions not hardcoded. Only set for 1280 by 800 pixels right now.
'''



class PgGroup(pygame.sprite.Group):
    def __init__(self, *args):
        pygame.sprite.Group.__init__(self, *args)

    @staticmethod
    def monster_attack(monsters: 'PgGroup', char_chord):
        monster_swords = []
        for monster in monsters:
            monster_weapon = monster.attack(char_chord)
            if isinstance(monster_weapon, Attack):
                monster_swords.append(monster_weapon)
        return monster_swords

    @staticmethod
    def draw_monster_bars(monsters, screen):
        for monster in monsters:
            monster.draw_health_bar(screen)

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

        self.monsters = Monster.spawn_monsters(self.character, self.walls, ((ChampionMeleeMonster, 15), (Monster, 30),
                                                                            (RangeMonster, 25)))

        self.ability_manager = AbilityManager()

        # So we can call each monster's attack method.
        self.monster_group = PgGroup(self.monsters)

        # Used to update everything to screen.
        self.all_sprites = PgGroup((self.character, self.monsters, self.background, self.walls))

        # Used to draw. We separate background so we can ensure it gets pictured before other things.
        self.all_but_background.add(self.monsters)

        self.time_test = False # Changed things in while loop so need to recreate timetest.
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
                        exit()

    def main(self):
        elapsed_time = 0
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    if self.time_test:
                        for key, value in self.time_dict.items():
                            print(key, value/self.loop_counter)
                    pygame.quit()
                    exit()
                if event.type == KEYUP:
                    Mover.handle_character_event(event, False)
                elif event.type == KEYDOWN:
                    if event.key == K_1 or event.key == K_2 or event.key == K_3 or event.key == K_4:
                        hotkey = event.key - 49 # printing out event.key gives 49, 50, 51, 52; for K_1, K_2...
                        if self.ability_manager.elements[hotkey] is not None:
                            self.ability_manager.ability = self.ability_manager.elements[hotkey]
                    elif event.key == K_i:
                        self.character.inventory.menu_up = not self.character.inventory.menu_up
                    else:
                        Mover.handle_character_event(event, True)
                elif event.type == MOUSEBUTTONDOWN:
                    if Rect(30, 640, 370, 100).collidepoint(event.pos) or (self.ability_manager.menu_up and Rect(30, 360, 370, 300).collidepoint(event.pos)):
                         ability_leveled =  self.ability_manager.handle_click(event)
                         if ability_leveled:
                             self.character.ability_levels[ability_leveled] += 1
                             self.character.increment_maxes()
                    elif Rect(880, 640, 370, 115).collidepoint(event.pos) or (self.character.inventory.menu_up and Rect(880, 280, 370, 360).collidepoint(event.pos)):
                         self.character.inventory.handle_click(event, self.character.ability_levels)
                         self.character.increment_maxes() # If Item that boost ToughenUp is equipped, health needs to change.
                    else:
                        self.ability_manager.menu_up = False
                        self.character.inventory.menu_up = False
                        weapon = self.character.attack(event.pos, self.ability_manager.ability)
                        if weapon != None:
                            self.all_but_background.add(weapon) # For collisions
                            self.all_sprites.add(weapon) # For movement


            self.screen.fill((0, 0, 0))

            self.character.calc_velocity(elapsed_time)

            monster_weapons = PgGroup.monster_attack(self.monster_group, self.character.rect.center)
            self.all_but_background.add(monster_weapons)
            self.all_sprites.add(monster_weapons)

            Collider.check_collision_group(self.all_but_background, self.screen)

            self.all_sprites.update(self.character.velocity, self.character.rect, elapsed_time)

            # Collisions should be after update so can check for collisions between sword/monster/player.


            PgGroup.draw(self.screen, self.background, self.all_but_background)
            self.clear_weapon() # Must be after draw. Keep at end of loop, since attack happens in event for loop.
            self.clear_dead()

            self.character.recover(elapsed_time)

            # Draw the HUD
            self.character.draw_bars(self.screen)

            PgGroup.draw_monster_bars(self.monsters, self.screen)

            self.ability_manager.draw(self.screen, self.character.ability_levels)
            self.character.inventory.draw(self.screen, self.character.ability_levels)

            pygame.display.update()
            elapsed_time = self.my_clock.tick(FRAME_RATE)

if __name__ == '__main__':
    gamestate = GameState()
    gamestate.main()