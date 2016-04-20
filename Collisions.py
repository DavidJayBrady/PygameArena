import pygame

class Collider:

    @staticmethod
    def check_collision_group(most_sprites, screen):
        single = pygame.sprite.GroupSingle()
        for sprite in most_sprites:
            most_sprites.remove(sprite)
            single.add(sprite)

            collided_sprites_dict = pygame.sprite.groupcollide(single, most_sprites, False, False)

            if len(collided_sprites_dict) > 0:
                sprite.handle_collision(collided_sprites_dict[sprite])

            most_sprites.add(sprite)


'''
    @staticmethod
    def check_collision_group(most_sprites: pygame.sprite.Group, screen):
        for sprite in most_sprites:
            most_sprites.remove(sprite)

            removed_friendlies = []
            if isinstance(sprite, Arrow): # To prevent friendly projectiles from colliding with each other.
                for sprite2 in most_sprites:
                    if isinstance(sprite2, Arrow) and sprite.from_player == sprite.from_player:
                        most_sprites.remove(sprite2); removed_friendlies.append(sprite2)

            # Prevent projectiles from colliding with friendlies. (Monster arrow doesn't hit other monster.)
            if isinstance(sprite, Arrow) and sprite.from_player is False:
                for sprite2 in most_sprites:
                    if isinstance(sprite2, Monster):
                        most_sprites.remove(sprite2)
                        removed_friendlies.append(sprite2)

            collided_sprite = pygame.sprite.spritecollideany(sprite, most_sprites)
            most_sprites.add(removed_friendlies)
            if collided_sprite is not None:
                sprite.handle_collision(collided_sprite)
            most_sprites.add(sprite)

'''