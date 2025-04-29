import pygame
import random
import sys

GRID_SIZE = 3
MEMORIZE_DELAY = 800
SHOW_TIME = 500
BG_COLOR = (135, 206, 250)
GRID_COLOR = (169, 169, 169)
CELL_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0)


def run_game(screen, PLAYER_COUNT):
    pygame.init()
    pygame.mixer.init()

    highlight_sound = pygame.mixer.Sound("highlight.wav")
    click_sound = pygame.mixer.Sound("click.wav")
    pygame.mixer.music.load("bg_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    screen_width, screen_height = screen.get_size()
    cell_size = int(screen_width * 0.08)
    gap = int(cell_size * 0.1)
    font = pygame.font.SysFont(None, int(screen_width * 0.04))
    small_font = pygame.font.SysFont(None, int(screen_width * 0.03))

    grid_origin_x = screen_width // 2 - ((cell_size + gap) * GRID_SIZE - gap) // 2
    grid_origin_y = screen_height // 2 - ((cell_size + gap) * GRID_SIZE - gap) // 2

    key_icon = pygame.image.load("key.png")
    key_icon = pygame.transform.scale(key_icon, (int(screen_width * 0.03), int(screen_width * 0.03)))

    def draw_grid(highlight_index=None):
        for i in range(GRID_SIZE * GRID_SIZE):
            row = i // GRID_SIZE
            col = i % GRID_SIZE
            x = grid_origin_x + col * (cell_size + gap)
            y = grid_origin_y + row * (cell_size + gap)
            color = HIGHLIGHT_COLOR if i == highlight_index else CELL_COLOR
            pygame.draw.rect(screen, GRID_COLOR, (x - 2, y - 2, cell_size + 4, cell_size + 4))
            pygame.draw.rect(screen, color, (x, y, cell_size, cell_size))

    def get_clicked_cell(pos):
        for i in range(GRID_SIZE * GRID_SIZE):
            row = i // GRID_SIZE
            col = i % GRID_SIZE
            x = grid_origin_x + col * (cell_size + gap)
            y = grid_origin_y + row * (cell_size + gap)
            rect = pygame.Rect(x, y, cell_size, cell_size)
            if rect.collidepoint(pos):
                return i
        return None

    players = list(range(PLAYER_COUNT))
    random.shuffle(players)
    results = []

    for player_index in players:
        icon = pygame.image.load(f"Player{player_index + 1}.png")
        icon = pygame.transform.scale(icon, (int(screen_width * 0.05), int(screen_width * 0.05)))
        score = 0
        sequence = []
        playing = True

        while playing:
            next_cell = random.randint(0, GRID_SIZE * GRID_SIZE - 1)
            while sequence and next_cell == sequence[-1]:
                next_cell = random.randint(0, GRID_SIZE * GRID_SIZE - 1)
            sequence.append(next_cell)

            can_click = False
            for index in sequence:
                highlight_sound.play()
                screen.fill(BG_COLOR)
                screen.blit(icon, (20, 20))
                score_text = small_font.render(f"Очки: {score}", True, (0, 0, 0))
                screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, 50))
                draw_grid(index)
                pygame.display.flip()
                pygame.time.delay(SHOW_TIME)

                screen.fill(BG_COLOR)
                screen.blit(icon, (20, 20))
                screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, 50))
                draw_grid()
                pygame.display.flip()
                pygame.time.delay(MEMORIZE_DELAY)

            input_index = 0
            can_click = True
            pygame.event.clear()
            pygame.time.delay(1000)
            answering = True
            while answering:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return [0, 1, 2, 3][:PLAYER_COUNT]
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.mixer.music.stop()
                            return [0, 1, 2, 3][:PLAYER_COUNT]
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if not can_click:
                            continue

                        clicked = get_clicked_cell(event.pos)
                        if clicked is not None:

                            click_sound.play()

                            screen.fill(BG_COLOR)
                            screen.blit(icon, (20, 20))
                            draw_grid(clicked)
                            pygame.display.flip()
                            pygame.time.delay(300)

                            if clicked == sequence[input_index]:
                                input_index += 1
                                if input_index == len(sequence):
                                    score += 1
                                    answering = False
                            else:
                                screen.fill(BG_COLOR)
                                screen.blit(icon, (20, 20))
                                draw_grid()
                                lose_text = font.render("Ошибка!", True, (255, 0, 0))
                                score_text = small_font.render(f"Ваш результат: {score}", True, (0, 0, 0))
                                screen.blit(lose_text, (screen_width // 2 - lose_text.get_width() // 2, screen_height // 2 - 40))
                                screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 2 + 10))
                                pygame.display.flip()
                                pygame.time.delay(2000)
                                answering = False
                                playing = False
                                break

                screen.fill(BG_COLOR)
                screen.blit(icon, (20, 20))
                draw_grid()
                pygame.display.flip()

        results.append((player_index, score))

    score_groups = {}
    for idx, score in results:
        score_groups.setdefault(score, []).append(idx)

    sorted_scores = sorted(score_groups.keys(), reverse=True)
    new_order = []
    key_rewards = {}
    current_place = 1

    for score in sorted_scores:
        group = score_groups[score]
        random.shuffle(group)
        new_order.extend(group)

        reward = 12 if current_place == 1 else 8 if current_place == 2 else 4 if current_place == 3 else 2
        for player in group:
            key_rewards[player] = reward
        current_place += len(group)

    screen.fill(BG_COLOR)
    title = font.render("Результаты:", True, (0, 0, 0))
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, 40))
    player_scores = dict(results)

    for i, player_index in enumerate(new_order):
        icon = pygame.image.load(f"Player{player_index + 1}.png")
        icon = pygame.transform.scale(icon, (int(screen_width * 0.05), int(screen_width * 0.05)))
        y_pos = 120 + i * int(screen_height * 0.12)
        screen.blit(icon, (100, y_pos))
        if i != 0:
            if results[i][1] == results[i - 1][1]:
                text = font.render(f"{left_res} место — Очков: {player_scores[player_index]}", True, (255, 255, 255))
            else:
                text = font.render(f"{i + 1} место — Очков: {player_scores[player_index]}", True, (255, 255, 255))
                left_res = i + 1
        else:
            text = font.render(f"{i + 1} место — Очков: {player_scores[player_index]}", True, (255, 255, 255))
            left_res = i + 1
        screen.blit(text, (180, y_pos))
        screen.blit(key_icon, (screen_width - 180, y_pos + 5))
        key_text = small_font.render(f"x {key_rewards[player_index]}", True, (0, 0, 0))
        screen.blit(key_text, (screen_width - 130, y_pos + 10))

    pygame.display.flip()
    pygame.time.delay(4000)
    pygame.mixer.music.stop()

    return new_order
