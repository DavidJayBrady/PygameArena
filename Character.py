import pygame
from SpriteSheet import SpriteSheet
from HUD import Bar
from Mover import Mover
import Sword as S

class Character(Mover):
    def __init__(self, gamestate_area):
        Mover.__init__(self)

        self.level = 1
        self.experience = 1
        self.level_experience = 1000

        self.ability_levels = {S.Attack: 1, S.Sweep: 1, S.Arrow: 1, S.SplitShot: 1, S.Lightning: 1,
                               S.FireStorm: 1, S.ToughenUp: 1}

        self.is_player = True

        scale_factor = [64, 64]
        enlarge = lambda x: pygame.transform.smoothscale(x, scale_factor)

        characters = SpriteSheet('instant_dungeon_artpack/By JosВ Luis Peirв Lima/players-mages.png')
        self.image = enlarge(characters.image_at([64, 0, 16, 16])).convert() # pygame.Surface
        self.rect = self.image.get_rect() # pygame.Rect

        # Start character at center of screen.
        center_character = list(gamestate_area.center)
        center_character = list(map(lambda x, y: x - (y/2), center_character, scale_factor))
        self.rect = self.rect.move(center_character[0], center_character[1])

        # Used to face different direction when walking that way.
        player_images = characters.load_strip([0, 0, 16, 16], 8)
        self.down_image = enlarge(player_images[0]).convert()
        self.up_image = enlarge(player_images[2]).convert()
        self.right_image = enlarge(player_images[4]).convert()
        self.left_image = enlarge(player_images[6]).convert()

        # Get rid of green box around player.
        self.image.set_colorkey((0, 255, 0))
        self.down_image.set_colorkey((0, 255, 0))
        self.up_image.set_colorkey((0, 255, 0))
        self.right_image.set_colorkey((0, 255, 0))
        self.left_image.set_colorkey((0, 255, 0))

        # Used for movement.
        self.speed = [.1, .1]   # pixels per millisecond
        self.velocity = [0, 0]

        # Used to limit attacks per second.
        self.timer = pygame.time.get_ticks()

        self.max_health = 700
        self.health = 700
        self.max_energy = 300
        self.energy = 200

        self.uses_caps = True # Drawing health bar utility.

        health_bar_offset = [-570, -320]
        energy_bar_offset = [-570, -280]
        experience_bar_offset = [-200, 330]

        self.healthbar = Bar(health_bar_offset, self.uses_caps, 'health')
        self.energybar = Bar(energy_bar_offset, self.uses_caps, 'energy')
        self.experiencebar = Bar(experience_bar_offset, self.uses_caps, 'experience')

    def attack(self, event_position, attack_type):

        player_to_click = pygame.math.Vector2(list(map(lambda x, y: x - y, list(event_position), self.rect.center)))

        weapon = attack_type(player_to_click, self.rect, True, self.ability_levels[attack_type])

        try: # For when FireStorm is too far and returns None when weapon is created.
            if pygame.time.get_ticks() - self.timer > weapon.cooldown: # Limit attacks per second based on ability.
                if not self.energy - weapon.energy_consume < 0:
                    self.timer = pygame.time.get_ticks()
                    self.energy -= weapon.energy_consume

                    if isinstance(weapon, S.Attack) and type(weapon) is not S.SplitShot or isinstance(weapon, S.FireStorm):
                        return weapon
                    # For Splitshot.
                    else:
                        return (weapon.arrow1, weapon.arrow2, weapon.arrow3)
        except AttributeError:
            return None

    def update(self, character_speed, char_rect):
        '''
        :param character_speed: Not used, have to pass here to pass to monster. Char cord not used either.
        :action: Change image of character to moving direction.
        '''
        if Mover.set_up:
            self.image = self.up_image
        elif Mover.set_left:
            self.image = self.left_image
        elif Mover.set_down:
            self.image = self.down_image
        elif Mover.set_right:
            self.image = self.right_image

    def handle_collision(self, collided_sprite):
        if not isinstance(collided_sprite, S.Attack) and not isinstance(collided_sprite, S.FireStorm):
                self.velocity = list(map(lambda x : -2 * x, self.velocity))

        if isinstance(collided_sprite, S.Attack) or isinstance(collided_sprite, S.FireStorm):
            if not collided_sprite.from_player:
                self.take_damage(collided_sprite.damage)

    def calc_velocity(self, elapsed_time):
        self.velocity = [0, 0]
        if Mover.set_up:
            self.velocity[1] = self.speed[1] * elapsed_time
        if Mover.set_down:
            self.velocity[1] = -self.speed[1] * elapsed_time
        if Mover.set_left:
            self.velocity[0] = self.speed[0] * elapsed_time
        if Mover.set_right:
            self.velocity[0] = -self.speed[0] * elapsed_time

    def take_damage(self, weapon_damage):
        self.health -= weapon_damage

    def is_dead(self) -> bool:
        return self.health <= 0

    def draw_bars(self, screen):
        self.healthbar.draw_health_bar(screen, self.rect, self.health, self.max_health)
        self.energybar.draw_health_bar(screen, self.rect, self.energy, self.max_energy)
        self.experiencebar.draw_health_bar(screen, self.rect, self.experience, self.level_experience)

    def recover(self):
        if self.health < self.max_health:
            self.health += .1 + (.05 * self.ability_levels[S.ToughenUp])
        if self.energy < self.max_energy:
            self.energy += 1

    def level_up(self):
        if self.experience > self.level_experience:
            self.experience = 5 # Bars get very dark when using the left part... Probably need new images.
            self.level += 1
            self.level_experience += 200
            return True

    def increment_maxes(self):
        current_max_health = self.max_health
        health_change = 50
        self.max_health = 700 + (health_change * self.ability_levels[S.ToughenUp])
        if current_max_health != self.max_health:
            self.health += health_change