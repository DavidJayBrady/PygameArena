import pygame
from pygame.locals import *

import Sword as S

class Bar:
    def __init__(self, offset, uses_caps: bool, from_player: bool, type: str):
        self.offset = offset
        self.uses_caps = uses_caps
        self.from_player = from_player

        shrink = lambda x: pygame.transform.smoothscale(x, [40, 40])
        self.left_cap = shrink(pygame.image.load('Health Bars/Left-Cap.png'))
        self.right_cap = shrink(pygame.image.load('Health Bars/Right-Cap.png'))

        self.type = type

        if type == 'health':
            self.bar = shrink(pygame.image.load('Health Bars/Health.png'))
        elif type == 'energy':
            self.bar = shrink(pygame.image.load('Health Bars/Energy.png'))
        elif type == 'experience':
            self.bar = shrink(pygame.image.load('Health Bars/Experience.png'))

        self.empty_bar = shrink(pygame.image.load('Health Bars/Empty-Health.png'))

    def draw_health_bar(self, screen, rect, current, max):
        if self.uses_caps and (self.type == 'health' or self.type == 'energy') and self.from_player:
            current_scale = int(current/2)
            max_scale = int(max/2)
            self.blit_caps(screen, rect, current_scale, max_scale)

        elif self.uses_caps and (self.type == 'health') and not self.from_player:
            max_scale = 70
            current_scale = int((current/max) * max_scale)
            self.blit_caps(screen, rect, current_scale, max_scale)

        elif self.type == 'experience':
            max_scale = 770
            current_scale = int(((current/max) * max_scale))
            self.blit_caps(screen, rect, current_scale, max_scale)
        else:
            max_scale = 60
            current_scale = int((current/max) * max_scale) # 60  is the number in the self.empty bar line
            self.left_cap_end = [rect.topleft[0] + self.offset[0], rect.topleft[1] + self.offset[1]]
            self.bar = pygame.transform.smoothscale(self.bar, [current_scale, 15])
            self.empty_bar = pygame.transform.scale(self.empty_bar, [max_scale, 15])

        if current > 0 or self.uses_caps:
            screen.blit(self.empty_bar, self.left_cap_end)
            screen.blit(self.bar, self.left_cap_end)

    def blit_caps(self, screen, rect, current_scale, max_scale):
        left_cap_start = [rect.topleft[0] + self.offset[0], rect.topleft[1] + self.offset[1]]
        self.left_cap_end = [rect.topleft[0] + self.offset[0] + 40, rect.topleft[1] + self.offset[1]]

        screen.blit(self.left_cap, left_cap_start)
        screen.blit(self.right_cap, [max_scale + self.left_cap_end[0], self.left_cap_end[1]])

        self.bar = pygame.transform.scale(self.bar, [(current_scale if current_scale != 0 else 1), 40])
        self.empty_bar = pygame.transform.scale(self.empty_bar, [max_scale, 40])

class AbilityManager:
    def __init__(self):

        ability_background = pygame.image.load('Other Art/Ability_Background.png')
        self.ability_background_image = pygame.transform.smoothscale(ability_background, [370, 100])
        self.ability_background_rect = Rect(30, 640, 370, 100)

        load_and_scale = lambda x: pygame.transform.smoothscale(pygame.image.load(x), [80, 80])

        toughen_image = load_and_scale('Other Art/ToughenUp.png')
        attack_image = load_and_scale('Other Art/Sword_Ability.png')
        sweep_image = load_and_scale('Other Art/Sweep_Ability.png')
        arrow_image = load_and_scale('Other Art/BowArrow.png')
        splitshot_image = load_and_scale('Other Art/Splitshot.png')
        lightning_image = load_and_scale('Other Art/Lightning.jpg')
        lightning_image.set_colorkey((0, 0 ,0))
        firestorm_image = load_and_scale('Other Art/Fireball.png')
        firestorm_image.set_colorkey((0, 0 , 0))

        self.ability_images = {S.ToughenUp: toughen_image, S.Attack: attack_image,
                               S.Sweep: sweep_image, S.Arrow: arrow_image,
                               S.SplitShot: splitshot_image, S.Lightning: lightning_image,
                               S.FireStorm: firestorm_image}

        self.ability_names = {S.ToughenUp: "Toughen Up", S.Attack: "Strike", S.Sweep: "Sweep", S.Arrow: 'SingleShot',
                              S.SplitShot: "Splitshot", S.Lightning: "Lightning", S.FireStorm: "FireStorm"}

        self.ability_points = 3

        # Used to draw the ability menu popup. Position is determined by menu_rects. 1 is bottom left, 2 is right of 1.
        self.ability_list = [S.Attack, S.Sweep, S.Arrow, S.SplitShot,
                             S.Lightning, S.FireStorm, S.ToughenUp, None, None, None, None, None]

        # Controls what spell goes on which hotkey, and the image that shows up. These are defaults.
        self.ability_hotkeys = {0: S.Attack, 1: S.Sweep, 2: S.Arrow, 3: S.SplitShot, 4: S.Attack, 5: S.Sweep,
                                6: S.Arrow, 7: S.SplitShot, 8: S.Lightning, 9: S.FireStorm, 10: S.ToughenUp,
                                11: None, 12: None, 13: None, 14: None, 15: None}

        # Default starting ability.
        self.ability = S.Attack

        # Use these to detect click and house hovering. Do not change.
        self.ability_rect_list = [Rect(40 + (x*90), 650, 80, 80) for x in range(4)]

        self.ability_menu_background_image = pygame.transform.smoothscale(self.ability_background_image, [370, 300])
        self.ability_menu_background_rect = (30, 360, 350, 300)

        self.menu_up = False
        self.index_clicked = None


        # Make numbers for ability hotkeys.
        self.font = pygame.font.Font(None, 26)
        self.hotkey_texts = [self.font.render(str(i), True, (100, 200, 200)) for i in range(1, 5)]

        # Gather rectangles for ability menu. 1 is bottom left, 2 is to the right of 1, and 4 is above 1.
        self.menu_rects = {}
        for i in range(3):
            for j in range(4):
                self.menu_rects[j + (i*4)] = Rect([40 + (j*90), 550 - (i*90), 80, 80])


        self.all_rects = {x: Rect(40+(x*90), 650, 80, 80) for x in range(4)}
        for i in range(3):
            for j in range(4):
                self.all_rects[4 + j + (i*4)] = Rect([40 + (j*90), 550 - (i*90), 80, 80])


    def draw(self, screen, ability_levels):

        self._paint_ability_info(screen, self.ability_rect_list, ability_levels, True)

        if self.menu_up:
            #self._paint_ability_info(screen, self.menu_rects, ability_levels, False)
            self._draw_abilities(screen, self.ability_menu_background_image,
                                 self.ability_menu_background_rect, self.ability_list, self.menu_rects)


        if self.ability_points > 0:
            extra_text = ' ability point to spend' if self.ability_points == 1 else ' ability points to spend'
            screen.blit(self.font.render(str(self.ability_points) + extra_text, True, (120, 200, 160)),[50, 140])


        self._draw_abilities(screen, self.ability_menu_background_image, self.ability_background_rect,
                             self.ability_hotkeys, self.ability_rect_list)

        self._draw_hotkey_details(screen, ability_levels)


    def ability_image_clicked(self, click_pos: tuple):
        for index in range(4):
            if self.all_rects[index].collidepoint(click_pos):
                self.index_clicked = index
                return (True, self.ability_hotkeys[index])


    def menu_ability_clicked(self, click_pos: tuple):
        for index in range(4, len(self.all_rects)):
            if self.all_rects[index].collidepoint(click_pos):
                return (True, self.ability_hotkeys[index])
        return (False,)


    def change_hotkey(self, weapon):
        self.ability_hotkeys[self.index_clicked] = weapon


    def _draw_hotkey_details(self, screen, ability_levels):
        for i in range(4): # Draw ability details. Hotkey at top left, "Level x" at bottom mid.
            try:
                text = self.font.render("Level " + str(ability_levels[self.ability_hotkeys[i]]), True, (100, 200, 200))
                text_pos = list(map(lambda x, y: x - y, self.ability_rect_list[i].bottomright, [70, 0]))
                screen.blit(self.hotkey_texts[i], self.ability_rect_list[i].topleft)
                screen.blit(text, text_pos)
            except KeyError:
                pass # So we can have abilities be empty.


    def _paint_ability_info(self, screen, rect_container, ability_levels, from_hotkeys: bool):
        # Highlight scrolled over picture in menu and paint their details above.
        iterate_part = 4 if not self.menu_up else len(self.all_rects)
        for index in range(iterate_part):
            if self.all_rects[index].collidepoint(pygame.mouse.get_pos()):
                self._draw_ability_details(screen, index, ability_levels, from_hotkeys)
                pygame.draw.rect(screen, (0, 200, 200), self.all_rects[index])

    def _draw_abilities(self, screen, image, image_rect, abilities, rect_container):
        screen.blit(image, image_rect)
        for i in range(len(rect_container)):
            self._square_image_blit(screen, abilities[i], (0, 100, 200) if not
                                   abilities[i] == self.ability else (100, 200, 200), rect_container[i])


    def _square_image_blit(self, screen, weapon: 'weapon class', color: tuple, ability_rect):
        pygame.draw.rect(screen, color, ability_rect, 1)
        if weapon is not None:
            screen.blit(self.ability_images[weapon], ability_rect)

    def _draw_ability_details(self, screen, index, ability_levels, from_hotkey):
        position = Rect(30, 540, 300, 50) if not self.menu_up else Rect(30, 260, 300, 50)

        if from_hotkey:
            highlighted_ability = self.ability_hotkeys[index]

        else:
            highlighted_ability = self.ability_list[index]

        try:
            ability_statistics = highlighted_ability.gather_statistics(
                highlighted_ability,ability_levels[highlighted_ability], list(position)[:2])

            screen.blit(self.ability_background_image, position)
            for text, position in ability_statistics.items():
                screen.blit(text, position)
        except (KeyError, AttributeError):
            pass