import pygame
import Sword as S

FONT = pygame.font.Font(None, 26)

MELEE_COLOR = (220, 50, 60)
MELEE_INFO_COLOR = (220, 100, 120)

RANGE_COLOR = (20, 200, 60)
RANGE_INFO_COLOR = (80, 170, 70)

MAGIC_COLOR = (100, 180, 220)
MAGIC_INFO_COLOR = (90, 140, 220)

PASSIVE_COLOR = (200, 150, 100)
PASSIVE_INFO_COLOR = (180, 160, 110)

def adjust(detail_box, x):
    return list(map(lambda x, y: x + y, x, detail_box))


class Item:
    @staticmethod
    def gather_statistics(type, ability_level, detail_box):
        stats = {}
        stats[FONT.render(type.name, True, type.name_color)] = adjust(detail_box, (10, 10))
        stats[FONT.render("Type: " +str(type.ability_type), True, type.info_color)] = adjust(detail_box, (10, 45))
        stats[FONT.render("Enhances: " + type.ability_to_buff_str, True, type.info_color)] = adjust(detail_box, (10, 80))
        stats[FONT.render("Increases levels by: " + str(type.levels_to_buff), True, type.info_color)] = adjust(detail_box, (80, 10))
        return stats


class Armor(Item):
    name = "Armor"
    ability_type = "Defensive"
    description = "Not sure yet"
    name_color = MELEE_COLOR
    info_color = MELEE_INFO_COLOR

    ability_to_buff_str = "Toughen Up"
    ability_to_buff = S.ToughenUp
    levels_to_buff = 3

    @staticmethod
    def on_active_enter(ability_levels):
        ability_levels[Armor.ability_to_buff] = Armor.levels_to_buff

    @staticmethod
    def on_active_leave(ability_levels):
        ability_levels[Armor.ability_to_buff] -= Armor.levels_to_buff
