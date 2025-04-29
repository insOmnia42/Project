import pygame
import random
import sys
import time
import math

GAME_DURATION = 40
SPAWN_DISTANCE_MIN_RATIO = 0.1
FREEZE_TIME = 2


def run_game(screen, PLAYER_COUNT):

    pygame.mixer.init()
    pygame.mixer.music.load("bg_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    pygame.init()
    pygame.mixer.init()
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()

    screen_width, screen_height = screen.get_size()
    BIRD_SIZE = int(screen_width * 0.07)
    CROSSHAIR_SIZE = int(screen_width * 0.06)
    spawn_distance_min = screen_width * SPAWN_DISTANCE_MIN_RATIO

    shot_sound = pygame.mixer.Sound("laser_attack.mp3")
    spawn_sound = pygame.mixer.Sound("player_death.wav")
    hit_sound = pygame.mixer.Sound("bomb_attack.mp3")

    background = pygame.image.load("Back_game_3.jpg").convert()
    background = pygame.transform.scale(background, (screen_width, screen_height))
    bird_image = pygame.image.load("bird.png").convert_alpha()
    bird_image = pygame.transform.scale(bird_image, (BIRD_SIZE, BIRD_SIZE))
    bird_image1 = pygame.image.load("bird.png").convert_alpha()
    bird_image1 = pygame.transform.scale(bird_image1, (BIRD_SIZE, BIRD_SIZE))
    bird_image1 = pygame.transform.rotate(bird_image1, 90)
    crosshair_image = pygame.image.load("crosshair.png").convert_alpha()
    crosshair_image = pygame.transform.scale(crosshair_image, (CROSSHAIR_SIZE, CROSSHAIR_SIZE))
    key_icon = pygame.image.load("key.png").convert_alpha()
    key_icon = pygame.transform.scale(key_icon, (CROSSHAIR_SIZE, CROSSHAIR_SIZE))

    results = []

    for player_index in range(PLAYER_COUNT):
        icon = pygame.image.load(f"Player{player_index + 1}.png")
        icon = pygame.transform.scale(icon, (int(screen_width * 0.08), int(screen_width * 0.08)))
        score = 0
        start_time = time.time()
        birds = []
        dead_birds = []
        last_spawn_time = time.time()
        spawn_interval = 1.0
        freeze_until = 0

        while time.time() - start_time < GAME_DURATION:
            elapsed = time.time() - start_time
            current_time = time.time()
            dt = clock.tick(60) / 1000

            spawn_interval = max(0.3, 1.0 - elapsed * 0.025)
            max_birds = min(5, 2 + int(elapsed // 10))

            if current_time - last_spawn_time > spawn_interval and len(birds) < max_birds:
                for _ in range(10):
                    x = random.randint(BIRD_SIZE, screen_width - BIRD_SIZE)
                    y = random.randint(BIRD_SIZE, screen_height - BIRD_SIZE)
                    if all(math.hypot(x - b["pos"][0], y - b["pos"][1]) > spawn_distance_min for b in birds):
                        birds.append({"pos": (x, y), "spawn": current_time, "lifetime": random.uniform(1.2, 2.0)})
                        last_spawn_time = current_time
                        spawn_sound.play()
                        break

            birds = [b for b in birds if current_time - b["spawn"] < b["lifetime"]]

            screen.blit(background, (0, 0))
            screen.blit(icon, (20, 20))

            score_text = small_font.render(f"Очки: {score}", True, (255, 255, 255))
            screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, 20))

            time_left = GAME_DURATION - int(elapsed)
            timer = small_font.render(f"Осталось: {time_left} сек", True, (255, 255, 255))
            screen.blit(timer, (screen_width - 250, 20))

            for bird in birds:
                bx, by = bird["pos"]
                screen.blit(bird_image, (bx - BIRD_SIZE // 2, by - BIRD_SIZE // 2))

            new_dead_birds = []
            for db in dead_birds:
                if current_time - db["spawn"] < 1.5:
                    db["dy"] += 100 * dt
                    db["pos"][1] += db["dy"] * dt
                    screen.blit(bird_image, (db["pos"][0] - BIRD_SIZE // 2, db["pos"][1] - BIRD_SIZE // 2))
                    new_dead_birds.append(db)
            dead_birds = new_dead_birds

            mx, my = pygame.mouse.get_pos()
            screen.blit(crosshair_image, (mx - CROSSHAIR_SIZE // 2, my - CROSSHAIR_SIZE // 2))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return [0, 1, 2, 3][:PLAYER_COUNT]
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        return [0, 1, 2, 3][:PLAYER_COUNT]
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if current_time < freeze_until:
                        continue
                    shot_sound.play()
                    hit = False
                    for i, bird in enumerate(birds):
                        bx, by = bird["pos"]
                        if math.hypot(mx - bx, my - by) <= BIRD_SIZE // 2:
                            score += 1
                            hit = True
                            hit_sound.play()
                            dead_birds.append({"pos": [bx, by], "spawn": current_time, "dy": 0})
                            del birds[i]
                            break
                    if not hit:
                        freeze_until = current_time + FREEZE_TIME

        screen.blit(background, (0, 0))
        screen.blit(icon, (20, 20))
        result = font.render(f"Ваш результат: {score}", True, (255, 255, 255))
        screen.blit(result, (screen_width // 2 - result.get_width() // 2, screen_height // 2))
        pygame.display.flip()
        pygame.time.delay(2000)
        results.append((player_index, score))

    results.sort(key=lambda x: -x[1])
    new_order = [player_index for player_index, _ in results]

    key_rewards = [12, 8, 4, 2]

    screen.blit(background, (0, 0))
    title = font.render("Результаты:", True, (255, 255, 255))
    screen.blit(title, (100, 50))

    for i, (player_index, score) in enumerate(results):
        icon = pygame.image.load(f"Player{player_index + 1}.png")
        icon = pygame.transform.scale(icon, (int(screen_width * 0.06), int(screen_width * 0.06)))
        screen.blit(icon, (100, 120 + i * 70))

        if i != 0:
            if results[i][1] == results[i - 1][1]:
                text = font.render(f"{left_res} место — Очков: {score}", True, (255, 255, 255))
            else:
                text = font.render(f"{i + 1} место — Очков: {score}", True, (255, 255, 255))
                left_res = i + 1
        else:
            text = font.render(f"{i + 1} место — Очков: {score}", True, (255, 255, 255))
            left_res = i + 1
        screen.blit(text, (170, 120 + i * 70))

        screen.blit(key_icon, (480, 125 + i * 70))
        key_text = font.render(f"+{key_rewards[i]}", True, (255, 255, 0))
        screen.blit(key_text, (540, 125 + i * 70))

    pygame.display.flip()
    pygame.time.delay(4000)

    pygame.mixer.music.stop()
    return new_order