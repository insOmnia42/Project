import pygame
import random
import sys
import time

ATTEMPTS_PER_PLAYER = 3
MAX_REACTION_TIME = 3000
CAR_SPEED_RATIO = 0.7


def run_game(screen, PLAYER_COUNT):
    pygame.init()
    pygame.mixer.init()
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()

    screen_width, screen_height = screen.get_size()

    background = pygame.image.load("Back_game4.jpg").convert()
    background = pygame.transform.scale(background, (screen_width, screen_height))

    car_image = pygame.image.load("car.png").convert_alpha()
    car_width = int(screen_width * 0.15)
    car_height = int(car_width * 0.6)
    car_image = pygame.transform.scale(car_image, (car_width, car_height))
    car_image = pygame.transform.flip(car_image, True, False)

    key_icon = pygame.image.load("key.png").convert_alpha()
    key_icon = pygame.transform.scale(key_icon, (int(screen_width * 0.035), int(screen_width * 0.035)))

    wait_sound = pygame.mixer.Sound("wait_start.mp3")
    drive_sound = pygame.mixer.Sound("car_drive.mp3")

    wait_sound.set_volume(0.5)
    drive_sound.set_volume(0.5)

    results = []

    for player_index in range(PLAYER_COUNT):
        icon = pygame.image.load(f"Player{player_index + 1}.png")
        icon = pygame.transform.scale(icon, (int(screen_width * 0.08), int(screen_width * 0.08)))

        total_time = 0
        attempts = 0

        while attempts < ATTEMPTS_PER_PLAYER:
            car_x = 0
            car_y = int(screen_height * 0.6)
            car_started = False
            reacted = False
            reaction_time = MAX_REACTION_TIME
            input_locked = False

            wait_time = random.uniform(1.5, 3.5)
            start_time = time.time() + wait_time
            wait_channel = wait_sound.play()

            drive_channel = None
            drive_started = False

            while True:
                dt = clock.tick(60) / 1000
                screen.blit(background, (0, 0))
                screen.blit(icon, (int(screen_width * 0.03), int(screen_height * 0.03)))

                now = time.time()

                if now >= start_time:
                    if not car_started:
                        car_started = True
                        if wait_channel:
                            wait_channel.stop()
                        drive_channel = drive_sound.play()
                        drive_started = True

                    car_x += CAR_SPEED_RATIO * screen_width * dt

                screen.blit(car_image, (car_x, car_y))

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:

                        return [0, 1, 2, 3][:PLAYER_COUNT]
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if not drive_channel is None:
                                drive_channel.stop()
                            wait_channel.stop()
                            return [0, 1, 2, 3][:PLAYER_COUNT]
                        elif event.key == pygame.K_SPACE and not input_locked:
                            input_locked = True
                            if car_started:
                                reacted = True
                                reaction_time = int((now - start_time) * 1000)
                            else:
                                reaction_time = MAX_REACTION_TIME

                if car_x > screen_width:
                    if drive_started and drive_channel:
                        drive_channel.stop()
                    break

                round_text = small_font.render(f"Попытка {attempts + 1}/3", True, (0, 0, 0))
                screen.blit(round_text, (screen_width - 250, int(screen_height * 0.02)))

                if car_started and not reacted:
                    info = small_font.render("ЖМИ ПРОБЕЛ!", True, (0, 0, 0))
                    screen.blit(info, (screen_width // 2 - 100, int(screen_height * 0.05)))

                pygame.display.flip()

            total_time += reaction_time
            result_text = font.render(f"{reaction_time} мс", True, (0, 0, 0))
            screen.blit(background, (0, 0))
            screen.blit(icon, (int(screen_width * 0.03), int(screen_height * 0.03)))
            screen.blit(result_text, result_text.get_rect(center=(screen_width // 2, screen_height // 2)))
            pygame.display.flip()
            pygame.time.delay(2000)

            attempts += 1

        results.append((player_index, total_time))

    results.sort(key=lambda x: x[1])
    new_order = [player_index for player_index, _ in results]
    keys_awarded = [12, 8, 4, 2]

    screen.blit(background, (0, 0))
    title = font.render("Результаты:", True, (0, 0, 0))
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, 50))

    for i, (player_index, score) in enumerate(results):
        icon = pygame.image.load(f"Player{player_index + 1}.png")
        icon = pygame.transform.scale(icon, (int(screen_width * 0.06), int(screen_width * 0.06)))
        icon_x = 100
        icon_y = 150 + i * 100
        screen.blit(icon, (icon_x, icon_y))

        if i != 0:
            if results[i][1] == results[i - 1][1]:
                text = font.render(f"{left_res} место — Очков: {score}", True, (255, 255, 255))
            else:
                text = font.render(f"{i + 1} место — Очков: {score}", True, (255, 255, 255))
                left_res = i + 1
        else:
            text = font.render(f"{i + 1} место — Очков: {score}", True, (255, 255, 255))
            left_res = i + 1
        screen.blit(text, (icon_x + 80, icon_y + 10))

        screen.blit(key_icon, (screen_width - 180, icon_y + 10))
        key_text = font.render(f"{keys_awarded[i]}", True, (255, 215, 0))
        screen.blit(key_text, (screen_width - 120, icon_y + 10))

    pygame.display.flip()
    pygame.time.delay(4000)

    return new_order
