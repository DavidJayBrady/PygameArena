import pygame
from pygame.locals import *
import Sword as S
import Items

# Used for determining if MOUSEBUTTONDOWN was a left or right click.
LEFT = 1
RIGHT = 3

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
            max_scale = 380
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


class Menu:
    def __init__(self, left_boundary, background_image):

        self.menu_up = False
        self.index_clicked = None

        self.left_boundary = left_boundary

        ability_background = pygame.image.load(background_image)
        self.menu_background_image = pygame.transform.smoothscale(ability_background, [370, 120])

        self.menu_background_rect = Rect(left_boundary-10, 630, 370, 115)
        self.menu_up_background_image = pygame.transform.smoothscale(ability_background, [370, 285])
        self.menu_up_background_rect = (left_boundary-10, 350, 370, 285)

        # Make numbers for ability hotkeys.
        self.font = pygame.font.Font(None, 22)

        text = ["Sft", "Spc", "Ml", "Mr"]
        self.hotkey_texts = [self.font.render(text[i], True, (100, 200, 200)) for i in range(4)]

        # Generate a dictionary, keys 0-15, with each value being a Rect, or a location.
        # Shape is as follows.
        #
        # 12  13  14  15
        # 8   9   10  11
        # 4   5   6   7
        # 0   1   2   3
        # Only the bottom row is usually visible, but self.menu_up means the rest will show.
        self.positions = {}
        self.rows = 4
        self.columns = 4
        for i in range(self.rows):
            for j in range(self.columns):
                self.positions[j + (i*4)] = Rect([left_boundary + (j*90), 650 - (i*90), 80, 80])

    def active_image_clicked(self, click_pos: tuple):
        for index in range(4):
            if self.positions[index].collidepoint(click_pos):
                self.index_clicked = index
                return (True, index)

    def draw(self, screen, ability_levels):
        self._paint_ability_info(screen, ability_levels)
        self._draw_abilities(screen)

    def menu_ability_clicked(self, click_pos: tuple):
        for index in range(4, len(self.positions)):
            if self.positions[index].collidepoint(click_pos):
                return (True,  index)
        return (False,)

    def _change_element(self, index):
        self.elements[self.index_clicked] = self.elements[index]

    def _paint_ability_info(self, screen, ability_levels):
        # Highlight scrolled over picture in menu and paint their details above.
        iterate_part = 4 if not self.menu_up else len(self.positions)
        for index in range(iterate_part):
            if self.positions[index].collidepoint(pygame.mouse.get_pos()):
                self._draw_ability_details(screen, index, ability_levels)
                pygame.draw.rect(screen, (0, 200, 200), self.positions[index]) # highlights the ability

    def _draw_abilities(self, screen):
        screen.blit(self.menu_background_image, self.menu_background_rect)
        if self.menu_up:
            screen.blit(self.menu_up_background_image, self.menu_up_background_rect)

        iterate_part = 4 if not self.menu_up else len(self.positions)
        for index in range(iterate_part):
            self._square_image_blit(screen, self.elements[index], (0, 100, 200) if not
                                   self.elements[index] == self.ability else (100, 200, 200), self.positions[index])

    def _square_image_blit(self, screen, weapon: 'weapon class', color: tuple, ability_rect):
        pygame.draw.rect(screen, color, ability_rect, 1)
        if weapon is not None:
            screen.blit(self.element_images[weapon], ability_rect)

    def _draw_ability_details(self, screen, index, ability_levels):
        position = Rect(self.left_boundary-10, 225 + ((self.rows - 1) * 100), 300, 50) if not self.menu_up else Rect(self.left_boundary-10, 235, 300, 50)

        highlighted_element = self.elements[index]

        try:
            element_statistics = highlighted_element.gather_statistics(
                highlighted_element, ability_levels[highlighted_element], list(position)[:2])

            screen.blit(self.menu_background_image, position)
            for text, position in element_statistics.items():
                screen.blit(text, position)
        except (KeyError, AttributeError):
            pass

class Inventory(Menu):
    def __init__(self, left_boundary):
        Menu.__init__(self, left_boundary, "Other Art/Ability_Background.png")

        self.element_to_move = None
        self.ready_to_swap = False

        self.ability = None

        self.elements = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None,
                                6: None, 7: None, 8: None, 9: None, 10: None,
                                11: Items.Armor, 12: None, 13: None, 14: None, 15: None,
                                16: None, 17: None, 18: None, 19: None}

        load_and_scale = lambda x: pygame.transform.smoothscale(pygame.image.load(x), [80, 80])
        # This image just doesn't fit the theme well.
        armor_image = load_and_scale("Items/Light_Armor_Leather.png")

        self.element_images = {Items.Armor: armor_image}

    def draw(self, screen, ability_levels):
        self._highlight_element_to_move(screen)
        Menu.draw(self, screen, ability_levels)

    def _highlight_element_to_move(self, screen):
        if self.element_to_move is not None and self.menu_up:
            pygame.draw.rect(screen, (100, 200, 100), self.positions[self.element_to_move], 0)

    # The following 2 methods prevent Attribute errors from calling a method on None.
    def _call_safe_enter(self, index, ability_levels):
        try:
            self.elements[index].on_active_enter(ability_levels)
        except AttributeError:
            pass

    def _call_safe_leave(self, index, ability_levels):
        try:
            self.elements[index].on_active_leave(ability_levels)
        except AttributeError:
            pass

    def _draw_item_details(self, screen, ability_levels):
        pass

    def handle_click(self, event, ability_levels):
        if event.button == LEFT:
            if self.menu_up:
                test_index = self.menu_ability_clicked(event.pos)
                if not test_index[0]:
                    test_index = self.active_image_clicked(event.pos)
                if test_index is not None and test_index[0]:
                    if not self.ready_to_swap:
                        self.ready_to_swap = True
                        self.element_to_move = test_index[1]
                    else:
                        if self.element_to_move in (0, 1, 2, 3) and test_index[1] not in (0, 1, 2, 3):
                            self._call_safe_leave(self.element_to_move, ability_levels)
                            self._call_safe_enter(test_index[1], ability_levels)
                        elif self.element_to_move not in (0, 1, 2, 3) and test_index[1] in (0, 1, 2, 3):
                            self._call_safe_enter(self.element_to_move, ability_levels)
                            self._call_safe_leave(test_index[1], ability_levels)

                        self.elements[self.element_to_move], self.elements[test_index[1]]\
                            = self.elements[test_index[1]], self.elements[self.element_to_move]
                        self.ready_to_swap = False
                        self.element_to_move = None
            else:
                if self.active_image_clicked(event.pos):
                    self.menu_up = not self.menu_up

class AbilityManager(Menu):
    def __init__(self, left_boundary):
        Menu.__init__(self, left_boundary, "Other Art/Ability_Background.png")

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

        wisen_image = load_and_scale("Other Art/Wisen.png")

        self.element_images = {S.ToughenUp: toughen_image, S.Attack: attack_image,
                               S.Sweep: sweep_image, S.Arrow: arrow_image,
                               S.SplitShot: splitshot_image, S.Lightning: lightning_image,
                               S.FireStorm: firestorm_image, S.Wisen: wisen_image}

        self.element_names = {S.ToughenUp: "Toughen Up", S.Attack: "Strike", S.Sweep: "Sweep", S.Arrow: 'SingleShot',
                              S.SplitShot: "Splitshot", S.Lightning: "Lightning", S.FireStorm: "FireStorm",
                              S.Wisen: "Wisen"}

        # Belongs in character, but only single player game, so does not matter and is more convenient here.
        self.ability_points = 3

        self.ability = S.Attack

        self.elements = {0: S.Attack, 1: S.Sweep, 2: S.Arrow, 3: S.SplitShot, 4: S.Attack, 5: S.Sweep,
                                6: S.Arrow, 7: S.SplitShot, 8: S.Lightning, 9: S.FireStorm, 10: S.ToughenUp,
                                11: S.Wisen, 12: None, 13: None, 14: None, 15: None}

    def draw(self, screen, ability_levels):
        self._grey_out(screen, ability_levels)

        Menu.draw(self, screen, ability_levels)

        self._draw_hotkey_details(screen, ability_levels)

        if self.ability_points > 0:
            extra_text = ' ability point to spend' if self.ability_points == 1 else ' ability points to spend'
            screen.blit(self.font.render(str(self.ability_points) + extra_text, True, (120, 200, 160)),[50, 140])

    def _grey_out(self, screen, ability_levels):
        # Slightly grey unleveled abilities, marking them unusable.
        iterate_part = 4 if not self.menu_up else len(self.positions)
        for index in range(iterate_part):
            if self.elements[index] and ability_levels[self.elements[index]] == 0:
                pygame.draw.rect(screen, (180, 75, 75), self.positions[index], 0)

    def _draw_hotkey_details(self, screen, ability_levels):

        for i in range(4): # Draw ability details. Hotkey at top left, "Level x" at bottom mid.
            try:
                text = self.font.render("Level " + str(ability_levels[self.elements[i]]), True, (100, 200, 200))
                text_pos = list(map(lambda x, y: x - y, self.positions[i].bottomright, [70, -3]))
                screen.blit(self.hotkey_texts[i], self.positions[i].topleft)
                screen.blit(text, text_pos)
            except KeyError:
                pass # So we can have abilities be empty.

    def handle_click(self, event):
        if event.button == LEFT:
            if self.menu_up:
                test_index = self.menu_ability_clicked(event.pos)
                if test_index[0]:
                    self._change_element(test_index[1])
            if self.active_image_clicked(event.pos):
                self.menu_up = not self.menu_up
            else:
                self.menu_up = not self.menu_up
        elif event.button == RIGHT:
            test_index = self.active_image_clicked(event.pos)
            if self.menu_up:
                test_index2 = self.menu_ability_clicked(event.pos)
                test_index = test_index2 if test_index2[0] else test_index
            if test_index is not None and test_index[0] and test_index[1] and self.ability_points > 0:
                self.ability_points -= 1
                return self.elements[test_index[1]]
