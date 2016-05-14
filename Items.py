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
        stats[FONT.render("Level: "+str(ability_level), True, type.info_color)] = adjust(detail_box, (110, 10))
        stats[FONT.render("Type: " +str(type.ability_type), True, type.info_color)] = adjust(detail_box, (250, 50))
        stats[FONT.render("Damage: "+str(type.calc_damage(ability_level, True)), True, type.info_color)] = adjust(detail_box, (225, 10))
        stats[FONT.render("Energy: "+str(round(type.calc_energy_consume(ability_level, True))), True, type.info_color)] = adjust(detail_box, (10, 50))
        stats[FONT.render("Cooldown: "+str(type.calc_cooldown(ability_level, True)), True, type.info_color)] = adjust(detail_box, (110, 50))
        stats[FONT.render(type.description, True, type.info_color)] = adjust(detail_box, (10, 80))
        return stats


class Armor(Item):
    name = "Armor"
    ability_type = "Defensive"
    description = "Not sure yet"
    name_color = MELEE_COLOR
    info_color = MELEE_INFO_COLOR

    ability_to_buff = S.ToughenUp
    levels_to_buff = 3

    def on_active_enter(self, ability_levels):
        ability_levels[Armor.ability_to_buff] += Armor.levels_to_buff

    def on_active_leave(self, ability_levels):
        ability_levels[Armor.ability_to_buff] -= Armor.levels_to_buff
