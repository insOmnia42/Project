import pygame
import sys
import random
import math
import time

PLAYER_SPEED = math.radians(90)
LASER_WIDTH_RATIO = 0.005
BOMB_SIZE_RATIO = 0.1
PROJECTILE_RADIUS_RATIO = 0.015
PROJECTILE_DAMAGE_RADIUS_RATIO = 0.04
PLAYER_KEYS = [pygame.K_a, pygame.K_s, pygame.K_k, pygame.K_l]


def run_game(screen, PLAYER_COUNT):
    pygame.mixer.init()
    pygame.mixer.music.load("bg_music.mp3")
    pygame.mixer.music.play(-1)

    laser_sound = pygame.mixer.Sound("laser_attack.mp3")
    bomb_sound = pygame.mixer.Sound("bomb_attack.mp3")
    wave_sound = pygame.mixer.Sound("projectile_wave.mp3")
    death_sound = pygame.mixer.Sound("player_death.wav")

    pygame.init()
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()

    screen_width, screen_height = screen.get_size()
    CENTER = (screen_width // 2, screen_height // 2)
    RADIUS = int(min(screen_width, screen_height) * 0.35)

    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 0))

    # Загрузка изображений
    bomb_image_orig = pygame.image.load("bomb.png").convert_alpha()
    bomb_size = int(screen_width * BOMB_SIZE_RATIO)
    bomb_image_orig = pygame.transform.scale(bomb_image_orig, (bomb_size, bomb_size))

    monster_image_orig = pygame.image.load("monster.png").convert_alpha()
    monster_size = int(screen_width * 0.15)
    monster_image_orig = pygame.transform.scale(monster_image_orig, (monster_size, monster_size))

    player_icons = [
        pygame.transform.scale(pygame.image.load(f"Player{i+1}.png"), (int(screen_width * 0.05), int(screen_width * 0.05)))
        for i in range(PLAYER_COUNT)
    ]

    angles = [i * (2 * math.pi / PLAYER_COUNT) for i in range(PLAYER_COUNT)]
    directions = [1 for _ in range(PLAYER_COUNT)]
    alive = [True] * PLAYER_COUNT

    is_attacking = False
    attack_type = None
    attack_type_prev = None
    attack_start_time = 0
    attack_duration = 0
    last_attack_end_time = time.time()
    attack_interval = 5.0
    attack_speedup = 0.5
    wave_count = 0

    bombs = []
    projectiles = []
    projectile_waves_remaining = 0
    last_projectile_wave_time = 0
    projectile_wave_interval = 1.5
    monster_angle = 0

    def spawn_projectile_wave():
        num_projectiles = random.randint(4, 5)
        for _ in range(num_projectiles):
            angle = random.uniform(0, 2 * math.pi)
            dir_x = math.cos(angle)
            dir_y = math.sin(angle)
            projectiles.append({
                "pos": [CENTER[0], CENTER[1]],
                "dir": [dir_x, dir_y]
            })

    running = True
    while running:
        dt = clock.tick(60) / 1000
        now = time.time()
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return [0, 1, 2, 3][:PLAYER_COUNT]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return [0, 1, 2, 3][:PLAYER_COUNT]  # Выход по ESC
                for i in range(PLAYER_COUNT):
                    if event.key == PLAYER_KEYS[i] and alive[i]:
                        directions[i] *= -1

        for i in range(PLAYER_COUNT):
            if alive[i]:
                angles[i] += directions[i] * PLAYER_SPEED * dt

        if not is_attacking and now - last_attack_end_time > attack_interval:

            is_attacking = True
            attack_choices = ['laser', 'bombs', 'bomb_wave']
            if attack_type_prev in attack_choices:
                attack_choices.remove(attack_type_prev)
            attack_type = random.choice(attack_choices)
            attack_type_prev = attack_type
            attack_start_time = now
            attack_duration = random.uniform(5, 7)
            wave_count += 1
            attack_interval = max(2.0, attack_interval - attack_speedup)

            if attack_type == "bomb_wave":
                projectile_waves_remaining = 3
                last_projectile_wave_time = now - projectile_wave_interval

        pygame.draw.circle(screen, (120, 120, 120), CENTER, RADIUS, 2)

        monster_angle += 90 * dt
        rotated_monster = pygame.transform.rotate(monster_image_orig, monster_angle)
        monster_rect = rotated_monster.get_rect(center=CENTER)
        screen.blit(rotated_monster, monster_rect)

        player_positions = []
        for i in range(PLAYER_COUNT):
            if not alive[i]:
                continue
            x = CENTER[0] + RADIUS * math.cos(angles[i])
            y = CENTER[1] + RADIUS * math.sin(angles[i])
            screen.blit(player_icons[i], player_icons[i].get_rect(center=(x, y)))
            player_positions.append((i, (x, y)))

        if attack_type == "laser":
            laser_sound.play()
        elif attack_type == "bombs":
            bomb_sound.play()
        elif attack_type == "bomb_wave":
            wave_sound.play()

        if is_attacking and attack_type == 'laser':
            laser_width = int(screen_width * LASER_WIDTH_RATIO)
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                end_x = CENTER[0] + dx * screen_width
                end_y = CENTER[1] + dy * screen_height
                pygame.draw.line(screen, (255, 0, 0), CENTER, (end_x, end_y), laser_width)

            for i, (px, py) in player_positions:
                if (
                    abs(px - CENTER[0]) <= laser_width // 2 or
                    abs(py - CENTER[1]) <= laser_width // 2
                ):
                    alive[i] = False
                    death_sound.play()

        if is_attacking and attack_type == "bombs":
            bombs_to_spawn = 2 + wave_count // 10
            spacing = screen_width * 0.25
            bomb_speed = 200 + wave_count * 15

            if not bombs:
                for i in range(bombs_to_spawn):
                    offset = (i - (bombs_to_spawn - 1) / 2) * spacing
                    bombs.append({
                        "x": CENTER[0] + offset,
                        "y": -bomb_size,
                        "angle": random.uniform(0, 360),
                        "speed": bomb_speed
                    })

            new_bombs = []
            for bomb in bombs:
                bomb["y"] += bomb["speed"] * dt
                bomb["angle"] += 150 * dt
                rotated = pygame.transform.rotate(bomb_image_orig, bomb["angle"])
                rect = rotated.get_rect(center=(bomb["x"], bomb["y"]))
                screen.blit(rotated, rect)

                for i, (px, py) in player_positions:
                    if math.hypot(px - bomb["x"], py - bomb["y"]) < bomb_size // 2:
                        alive[i] = False
                        death_sound.play()

                if bomb["y"] < screen_height + bomb_size:
                    new_bombs.append(bomb)
            bombs = new_bombs

        if is_attacking and attack_type == "bomb_wave":
            if projectile_waves_remaining > 0 and now - last_projectile_wave_time >= projectile_wave_interval:
                spawn_projectile_wave()
                last_projectile_wave_time = now
                projectile_waves_remaining -= 1

            for proj in projectiles:
                proj["pos"][0] += proj["dir"][0] * screen_width * PROJECTILE_RADIUS_RATIO * dt * 5
                proj["pos"][1] += proj["dir"][1] * screen_width * PROJECTILE_RADIUS_RATIO * dt * 5
                pygame.draw.circle(screen, (255, 100, 0), (int(proj["pos"][0]), int(proj["pos"][1])), int(screen_width * PROJECTILE_RADIUS_RATIO))

            for proj in projectiles:
                px, py = proj["pos"]
                for i, (px_i, py_i) in player_positions:
                    if math.hypot(px - px_i, py - py_i) <= screen_width * PROJECTILE_DAMAGE_RADIUS_RATIO:
                        alive[i] = False
                        death_sound.play()

            projectiles = [p for p in projectiles if 0 <= p["pos"][0] <= screen_width and 0 <= p["pos"][1] <= screen_height]

        if is_attacking and now - attack_start_time >= attack_duration:
            is_attacking = False
            bombs = []
            projectiles = []
            last_attack_end_time = now

        wave_text = small_font.render(f"Волна: {wave_count}", True, (255, 255, 255))
        screen.blit(wave_text, (20, 20))

        alive_indices = [i for i, alive_flag in enumerate(alive) if alive_flag]

        if PLAYER_COUNT > 1 and len(alive_indices) == 1:
            final_order = [alive_indices[0]] + [i for i in range(PLAYER_COUNT) if i != alive_indices[0]]

            key_icon = pygame.image.load("key.png").convert_alpha()
            key_icon = pygame.transform.scale(key_icon, (int(screen_width * 0.035), int(screen_width * 0.035)))

            screen.fill((0, 0, 0))
            title = font.render("Результаты:", True, (255, 255, 255))
            title_rect = title.get_rect(center=(screen_width // 2, int(screen_height * 0.1)))
            screen.blit(title, title_rect)

            keys_per_place = [12, 8, 4, 2]

            start_y = int(screen_height * 0.25)
            line_spacing = int(screen_height * 0.12)

            for place, player_index in enumerate(final_order):
                place_text = font.render(f"{place + 1}", True, (255, 215, 0))
                place_rect = place_text.get_rect()
                place_rect.left = int(screen_width * 0.2)
                place_rect.centery = start_y + place * line_spacing
                screen.blit(place_text, place_rect)

                icon = pygame.image.load(f"Player{player_index + 1}.png").convert_alpha()
                icon = pygame.transform.scale(icon, (int(screen_width * 0.05), int(screen_width * 0.05)))
                icon_rect = icon.get_rect()
                icon_rect.left = place_rect.right + int(screen_width * 0.02)
                icon_rect.centery = place_rect.centery
                screen.blit(icon, icon_rect)

                keys = keys_per_place[place] if place < len(keys_per_place) else 2
                key_icon_rect = key_icon.get_rect()
                key_icon_rect.left = icon_rect.right + int(screen_width * 0.03)
                key_icon_rect.centery = icon_rect.centery
                screen.blit(key_icon, key_icon_rect)

                keys_text = small_font.render(f"+{keys}", True, (255, 255, 0))
                keys_text_rect = keys_text.get_rect()
                keys_text_rect.left = key_icon_rect.right + int(screen_width * 0.01)
                keys_text_rect.centery = key_icon_rect.centery
                screen.blit(keys_text, keys_text_rect)

            pygame.display.update()
            pygame.time.delay(4000)
            pygame.mixer.music.stop()
            return final_order

        elif PLAYER_COUNT == 1 and len(alive_indices) == 0:
            key_icon = pygame.image.load("key.png").convert_alpha()
            key_icon = pygame.transform.scale(key_icon, (int(screen_width * 0.035), int(screen_width * 0.035)))

            screen.fill((0, 0, 0))

            title = font.render("Результаты:", True, (255, 255, 255))
            title_rect = title.get_rect(center=(screen_width // 2, 80))
            screen.blit(title, title_rect)

            icon = pygame.image.load(f"Player1.png")
            icon = pygame.transform.scale(icon, (int(screen_width * 0.05), int(screen_width * 0.05)))
            icon_x = screen_width // 2 - 100
            icon_y = 150
            screen.blit(icon, (icon_x, icon_y))

            key_x = screen_width // 2 + 20
            screen.blit(key_icon, (key_x, icon_y))

            keys_text = small_font.render(f"x {12}", True, (255, 255, 255))
            screen.blit(keys_text, (key_x + 50, icon_y + 10))

            pygame.display.flip()
            pygame.time.wait(4000)
            pygame.mixer.music.stop()

            return [0]

        pygame.display.flip()
