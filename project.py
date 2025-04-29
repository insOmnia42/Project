import pygame
import sys
import level_1

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Главное меню")

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
LIGHT_BLUE = (173, 216, 230)
HOVER_COLOR = (220, 220, 220)

font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 35)

MENU = "menu"
PLAYER_SELECT = "player_select"
GAME_LENGTH_SELECT = "game_length_select"
FIELD_SELECT = "field_select"
running = True
game_state = MENU
selected_game_length = 10
selected_num_players = 4

player_icons = [
    pygame.transform.scale(pygame.image.load("Player1.png"), (80, 80)),
    pygame.transform.scale(pygame.image.load("Player2.png"), (80, 80)),
    pygame.transform.scale(pygame.image.load("Player3.png"), (80, 80)),
    pygame.transform.scale(pygame.image.load("Player4.png"), (80, 80))
]

buttons = {
    "play": (WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 60, "Играть"),
    "1player": (WIDTH // 2 - 270, 250, 100, 60, "1"),
    "2players": (WIDTH // 2 - 120, 250, 100, 60, "2"),
    "3players": (WIDTH // 2 + 30, 250, 100, 60, "3"),
    "4players": (WIDTH // 2 + 180, 250, 100, 60, "4"),
    "short_game": (WIDTH // 2 - 250, 200, 500, 60, "Короткая игра (10 раундов)"),
    "long_game": (WIDTH // 2 - 250, 300, 500, 60, "Длинная игра (20 раундов)"),
    "back": (WIDTH // 2 - 100, 500, 200, 60, "Назад"),
    "random_field": (WIDTH // 2 - 350, 200, 720, 60, "Случайное поле(выглядит сомнительно)"),
    "field_1": (WIDTH // 2 - 350, 300, 720, 60, "Заранее созданое поле")
}


def draw_gradient_background():
    for y in range(HEIGHT):
        color = (
            int(BLUE[0] + (LIGHT_BLUE[0] - BLUE[0]) * (y / HEIGHT)),
            int(BLUE[1] + (LIGHT_BLUE[1] - BLUE[1]) * (y / HEIGHT)),
            int(BLUE[2] + (LIGHT_BLUE[2] - BLUE[2]) * (y / HEIGHT))
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))


def draw_button(x, y, width, height, text, mouse_hover=False):
    color = HOVER_COLOR if mouse_hover else WHITE
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=10)
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 2, border_radius=10)
    label = font.render(text, True, BLACK)
    label_rect = label.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(label, label_rect)


def main_menu():
    draw_gradient_background()

    start_x = WIDTH // 2 - (len(player_icons) * 90) // 2
    y_icons = 100
    for idx, icon in enumerate(player_icons):
        screen.blit(icon, (start_x + idx * 90, y_icons))

    x, y, w, h, text = buttons["play"]
    mouse_x, mouse_y = pygame.mouse.get_pos()
    hover = x <= mouse_x <= x + w and y <= mouse_y <= y + h
    draw_button(x, y, w, h, text, hover)


def player_select_menu():
    draw_gradient_background()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    start_x = WIDTH // 2 - (len(player_icons) * 90) // 2
    y_icons = 100
    for idx, icon in enumerate(player_icons):
        screen.blit(icon, (start_x + idx * 90, y_icons))

    for key in ["1player", "2players", "3players", "4players"]:
        x, y, w, h, text = buttons[key]
        hover = x <= mouse_x <= x + w and y <= mouse_y <= y + h
        draw_button(x, y, w, h, text, hover)

    x, y, w, h, text = buttons["back"]
    hover = x <= mouse_x <= x + w and y <= mouse_y <= y + h
    draw_button(x, y, w, h, text, hover)


def game_length_menu():
    draw_gradient_background()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    start_x = WIDTH // 2 - (len(player_icons) * 90) // 2
    y_icons = 100
    for idx, icon in enumerate(player_icons):
        screen.blit(icon, (start_x + idx * 90, y_icons))

    for key in ["short_game", "long_game"]:
        x, y, w, h, text = buttons[key]
        hover = x <= mouse_x <= x + w and y <= mouse_y <= y + h
        draw_button(x, y, w, h, text, hover)

    x, y, w, h, text = buttons["back"]
    hover = x <= mouse_x <= x + w and y <= mouse_y <= y + h
    draw_button(x, y, w, h, text, hover)


def field_select_menu():
    draw_gradient_background()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    start_x = WIDTH // 2 - (len(player_icons) * 90) // 2
    y_icons = 100
    for idx, icon in enumerate(player_icons):
        screen.blit(icon, (start_x + idx * 90, y_icons))

    for key in ["random_field", "field_1"]:
        x, y, w, h, text = buttons[key]
        hover = x <= mouse_x <= x + w and y <= mouse_y <= y + h
        draw_button(x, y, w, h, text, hover)

    x, y, w, h, text = buttons["back"]
    hover = x <= mouse_x <= x + w and y <= mouse_y <= y + h
    draw_button(x, y, w, h, text, hover)


def start():
    global running, game_state, selected_num_players

    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == MENU:
                    x, y, w, h, _ = buttons["play"]
                    if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                        game_state = PLAYER_SELECT

                elif game_state == PLAYER_SELECT:
                    for key, (x, y, w, h, text) in buttons.items():
                        if key in ["1player", "2players", "3players", "4players"]:
                            if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                                selected_num_players = int(text)
                                game_state = GAME_LENGTH_SELECT
                        elif key == "back":
                            if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                                game_state = MENU

                elif game_state == GAME_LENGTH_SELECT:
                    x, y, w, h, _ = buttons["short_game"]
                    if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                        selected_game_length = 3
                        game_state = FIELD_SELECT

                    x, y, w, h, _ = buttons["long_game"]
                    if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                        selected_game_length = 20
                        game_state = FIELD_SELECT

                    x, y, w, h, _ = buttons["back"]
                    if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                        game_state = PLAYER_SELECT


                elif game_state == FIELD_SELECT:
                    x, y, w, h, _ = buttons["random_field"]
                    if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                        level_1.level_1(selected_num_players, selected_game_length, 1)
                        running = False

                    x, y, w, h, _ = buttons["field_1"]
                    if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                        level_1.level_1(selected_num_players, selected_game_length, 2)
                        running = False

                    x, y, w, h, _ = buttons["back"]
                    if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                        game_state = GAME_LENGTH_SELECT

        if game_state == MENU:
            main_menu()
        elif game_state == PLAYER_SELECT:
            player_select_menu()
        elif game_state == GAME_LENGTH_SELECT:
            game_length_menu()
        elif game_state == FIELD_SELECT:
            field_select_menu()

        pygame.display.flip()
        pygame.time.delay(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    start()
