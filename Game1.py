import pygame
import random
import time
import sys

MEMORIZE_TIME = 5000


def run_game(screen, PLAYER_COUNT):
    pygame.init()
    pygame.mixer.init()

    screen_width, screen_height = screen.get_size()

    font = pygame.font.SysFont(None, int(screen_width * 0.06))
    small_font = pygame.font.SysFont(None, int(screen_width * 0.04))

    click_sound = pygame.mixer.Sound("click.wav")
    pygame.mixer.music.load("bg_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    key_icon = pygame.image.load("key.png")
    key_icon = pygame.transform.scale(key_icon, (int(screen_width * 0.03), int(screen_width * 0.03)))

    results = []

    for player_index in range(PLAYER_COUNT):
        icon = pygame.image.load(f"Player{player_index + 1}.png")
        icon = pygame.transform.scale(icon, (int(screen_width * 0.06), int(screen_width * 0.06)))

        score = 0
        number_length = 1
        playing = True

        while playing:
            number = ''.join(str(random.randint(0, 9)) for _ in range(number_length))

            start_time = pygame.time.get_ticks()
            while pygame.time.get_ticks() - start_time < MEMORIZE_TIME:
                elapsed = pygame.time.get_ticks() - start_time
                progress = elapsed / MEMORIZE_TIME
                bar_width = int(screen_width * 0.4 * (1 - progress))

                screen.fill((135, 206, 250))
                screen.blit(icon, (int(screen_width * 0.03), int(screen_height * 0.03)))

                number_text = font.render(number, True, (255, 255, 255))
                screen.blit(number_text, (screen_width // 2 - number_text.get_width() // 2, int(screen_height * 0.35)))

                pygame.draw.rect(screen, (255, 255, 255), (int(screen_width * 0.1), int(screen_height * 0.2), int(screen_width * 0.4), int(screen_height * 0.03)), 2)
                pygame.draw.rect(screen, (255, 255, 255), (int(screen_width * 0.1), int(screen_height * 0.2), bar_width, int(screen_height * 0.03)))
                pygame.display.flip()

            input_text = ""
            asking = True
            pygame.event.clear()
            while asking:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.mixer.music.stop()
                        return [0, 1, 2, 3][:PLAYER_COUNT]
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.mixer.music.stop()
                            return [0, 1, 2, 3][:PLAYER_COUNT]
                        elif event.key == pygame.K_RETURN:
                            click_sound.play()
                            asking = False
                        elif event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        elif event.unicode.isdigit():
                            click_sound.play()
                            input_text += event.unicode

                screen.fill((135, 206, 250))
                screen.blit(icon, (int(screen_width * 0.03), int(screen_height * 0.03)))
                prompt = font.render("Какое число было?", True, (255, 255, 255))
                screen.blit(prompt, (screen_width // 2 - prompt.get_width() // 2, int(screen_height * 0.25)))

                pygame.draw.rect(screen, (255, 255, 255), (int(screen_width * 0.1), int(screen_height * 0.4), int(screen_width * 0.6), int(screen_height * 0.1)), 2)
                answer = font.render(input_text, True, (255, 255, 255))
                screen.blit(answer, (int(screen_width * 0.12), int(screen_height * 0.42)))
                pygame.display.flip()

            if input_text == number:
                score += 1
                number_length += 1
            else:
                screen.fill((135, 206, 250))
                screen.blit(icon, (int(screen_width * 0.03), int(screen_height * 0.03)))
                result = font.render(f"Неправильно! Очков: {score}", True, (255, 255, 255))
                screen.blit(result, (screen_width // 2 - result.get_width() // 2, int(screen_height * 0.4)))
                pygame.display.flip()
                pygame.time.delay(2000)
                playing = False

        results.append((player_index, score))

    results.sort(key=lambda x: -x[1])
    new_order = [player_index for player_index, _ in results]
    key_rewards = {}
    for i, (player_index, _) in enumerate(results):
        key_rewards[player_index] = [12, 8, 4, 2][i] if i < 4 else 2

    screen.fill((135, 206, 250))
    title = font.render("Результаты:", True, (255, 255, 255))
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, 50))

    left_res = 0
    for i, (player_index, score) in enumerate(results):
        icon = pygame.image.load(f"Player{player_index + 1}.png")
        icon = pygame.transform.scale(icon, (int(screen_width * 0.05), int(screen_width * 0.05)))
        y_pos = 120 + i * int(screen_height * 0.12)
        screen.blit(icon, (100, y_pos))
        if i != 0:
            if results[i][1] == results[i - 1][1]:
                text = font.render(f"{left_res} место — Очков: {score}", True, (255, 255, 255))
            else:
                text = font.render(f"{i + 1} место — Очков: {score}", True, (255, 255, 255))
                left_res = i + 1
        else:
            text = font.render(f"{i + 1} место — Очков: {score}", True, (255, 255, 255))
            left_res = i + 1
        screen.blit(text, (180, y_pos))
        screen.blit(key_icon, (screen_width - 180, y_pos + 5))
        key_text = small_font.render(f"x {key_rewards[player_index]}", True, (255, 255, 255))
        screen.blit(key_text, (screen_width - 130, y_pos + 10))

    pygame.display.flip()
    pygame.time.delay(4000)
    pygame.mixer.music.stop()

    return new_order
