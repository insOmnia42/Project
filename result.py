import pygame
import sys


def show_result(screen, players_stats, player_sprite_sets):
    pygame.display.set_caption("Итоги игры")

    font_big = pygame.font.SysFont(None, 70)
    font_small = pygame.font.SysFont(None, 40)
    font_button = pygame.font.SysFont(None, 50)

    first_medal = pygame.image.load("first.png").convert_alpha()
    second_medal = pygame.image.load("second.png").convert_alpha()
    third_medal = pygame.image.load("third.png").convert_alpha()
    fourth_medal = pygame.image.load("fourth.png").convert_alpha()

    player_1 = pygame.image.load("Player 1_big.png").convert_alpha()

    cup_icon = pygame.image.load("cup.png").convert_alpha()
    key_icon = pygame.image.load("key.png").convert_alpha()

    sorted_indices = sorted(
        range(len(players_stats)),
        key=lambda i: (-players_stats[i]['chests'], -players_stats[i]['keys'])
    )

    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

    exit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 60)

    running = True

    while running:
        screen.fill((255, 255, 255))

        title = font_big.render("Итоги игры!", True, (0, 0, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        positions = [
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100),
            (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH // 2 + 250, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 250)
        ]

        medal_images = [first_medal, second_medal, third_medal, fourth_medal]

        for rank, idx in enumerate(sorted_indices):
            if rank >= 4:
                break

            x, y = positions[rank]

            if rank == 0:
                sprite_size = (180, 180)
            elif rank == 3:
                sprite_size = (100, 100)
            else:
                sprite_size = (140, 140)

            sprite = pygame.transform.scale(player_sprite_sets[idx][0], sprite_size)
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)

            sprite = pygame.transform.scale(player_sprite_sets[idx][0], sprite_size)
            sprite_rect = sprite.get_rect(center=(x, y))
            screen.blit(sprite, sprite_rect)

            medal = pygame.transform.scale(medal_images[rank], (60, 60))
            medal_rect = medal.get_rect(center=(x, y - sprite_rect.height // 2 - 40))
            screen.blit(medal, medal_rect)

            chests = players_stats[idx]["chests"]
            keys = players_stats[idx]["keys"]

            cup_icon_scaled = pygame.transform.scale(cup_icon, (40, 40))
            key_icon_scaled = pygame.transform.scale(key_icon, (40, 40))

            screen.blit(cup_icon_scaled, (x - 50, y + sprite_rect.height // 2 + 10))
            screen.blit(key_icon_scaled, (x + 10, y + sprite_rect.height // 2 + 10))

            chest_text = font_small.render(str(chests), True, (0, 0, 0))
            key_text = font_small.render(str(keys), True, (0, 0, 0))

            screen.blit(chest_text, (x - 5, y + sprite_rect.height // 2 + 15))
            screen.blit(key_text, (x + 55, y + sprite_rect.height // 2 + 15))

        pygame.draw.rect(screen, (200, 200, 200), exit_button_rect, border_radius=10)
        exit_text = font_button.render("Выход", True, (0, 0, 0))
        exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
        screen.blit(exit_text, exit_text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button_rect.collidepoint(event.pos):
                    running = False
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
