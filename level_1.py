import pygame
import sys
import random
import math
import time
from Nodes import create_nodes
from collections import defaultdict
import Game1
import Game2
import Game3
import Game4
import Game5
import result

MINI_GAMES = [Game1, Game2, Game3, Game4, Game5]

PLAYER_COUNT = 4
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
NODE_RADIUS = 60
PLAYER_RADIUS = 30
ROLL_KEY = pygame.K_SPACE
CAMERA_SPEED = 100

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
BLUE = (0, 120, 255)
GREEN = (0, 255, 100)
RED = (255, 50, 50)
LIGHT_BLUE = (173, 216, 230)
PLAYER_COLORS = [(0, 120, 255), (255, 100, 0), (100, 255, 100), (255, 0, 150)]
PLAYER_INDICATOR_RADIUS = 10

pygame.init()
font = pygame.font.SysFont(None, 32)

vert_image_original = pygame.image.load("Vert1.png").convert_alpha()
vert_image_original.set_colorkey((255, 255, 255))



vert_image = pygame.image.load("Vert1.png")
vert_image = pygame.transform.scale(vert_image, (NODE_RADIUS * 2, NODE_RADIUS * 2))
vert_image.set_colorkey((255, 255, 255))
transparent_image = pygame.Surface(vert_image.get_size(), pygame.SRCALPHA)
transparent_image.blit(vert_image, (0, 0))

hp_icon = pygame.image.load("heart.png")
key_icon = pygame.image.load("key.png")
chest_icon = pygame.image.load("cup.png")
plus_icon = pygame.image.load("Plus.png")
minus_icon = pygame.image.load("Minus.png")
skull_icon = pygame.image.load("Scull.png")

cup_sound = pygame.mixer.Sound("cup.mp3")
death_sound = pygame.mixer.Sound("death.mp3")
heartbeat_sound = pygame.mixer.Sound("heartbeat.mp3")
key_sound = pygame.mixer.Sound("key_sound.mp3")


player_icons = [
        pygame.image.load("Player1.png"),
        pygame.image.load("Player2.png"),
        pygame.image.load("Player3.png"),
        pygame.image.load("Player4.png")
    ]


class Node:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.neighbors = []

    def connect(self, other):
        if other not in self.neighbors:
            self.neighbors.append(other)
            other.neighbors.append(self)


class Player:
    def __init__(self, node, sprite_images=None):
        self.current_node = node
        self.steps_remaining = 0
        self.target_node = None
        self.target_pos = None
        self.move_time = 1.5
        self.move_progress = 0
        self.is_moving = False
        self.sprite_images = sprite_images or []
        self.sprite_index = 0
        self.current_sprite = self.sprite_images[0] if self.sprite_images else None
        self.actual_pos = node.pos[:]
        self.flip_sprite = False
        self.just_stopped = False
        self.waiting_node_effect = False
        self.is_dead = False
        self.dead_timer = 0

    def set_target(self, target_node):
        self.target_node = target_node
        self.target_pos = target_node.pos
        self.move_progress = 0
        self.is_moving = True
        dx = self.target_node.pos[0] - self.current_node.pos[0]
        self.flip_sprite = dx < 0

    def update_position(self, dt):
        if self.is_moving:
            self.move_progress += dt / self.move_time
            if self.move_progress >= 1:
                self.move_progress = 1
                self.is_moving = False
                self.current_node = self.target_node
                self.actual_pos = self.target_node.pos[:]
                self.just_stopped = True

                if self.steps_remaining == 0:
                    self.waiting_node_effect = True

                if self.sprite_images:
                    sprite = self.sprite_images[0]
                    self.current_sprite = sprite
            else:
                x = self.current_node.pos[0] + (self.target_pos[0] - self.current_node.pos[0]) * self.move_progress
                y = self.current_node.pos[1] + (self.target_pos[1] - self.current_node.pos[1]) * self.move_progress
                self.actual_pos = [x, y]

                if self.sprite_images:
                    self.sprite_index += dt * 10
                    if self.sprite_index >= len(self.sprite_images):
                        self.sprite_index = 0
                    sprite = self.sprite_images[int(self.sprite_index)]
                    if self.flip_sprite:
                        sprite = pygame.transform.flip(sprite, True, False)
                    self.current_sprite = sprite


def apply_camera(pos, camera_offset, camera_zoom):
    return ((pos[0] - camera_offset[0]) * camera_zoom, (pos[1] - camera_offset[1]) * camera_zoom)


def shorten_line(start, end, radius):
    dx, dy = end[0] - start[0], end[1] - start[1]
    dist = math.hypot(dx, dy)
    if dist == 0:
        return start, end
    scale = radius / dist
    new_start = (start[0] + dx * scale, start[1] + dy * scale)
    new_end = (end[0] - dx * scale, end[1] - dy * scale)
    return new_start, new_end


def draw_background(screen, background, camera_offset):
    bg_width, bg_height = background.get_size()

    start_x = int(-camera_offset[0] % bg_width - bg_width)
    start_y = int(-camera_offset[1] % bg_height - bg_height)

    for x in range(start_x, SCREEN_WIDTH + bg_width, bg_width):
        for y in range(start_y, SCREEN_HEIGHT + bg_height, bg_height):
            screen.blit(background, (x, y))


def draw_vert(screen, node, camera_offset, camera_zoom):
    node_screen_pos = apply_camera(node.pos, camera_offset, camera_zoom)
    x = node_screen_pos[0]
    y = node_screen_pos[1]

    # Масштабируем оригинальную картинку прямо перед рисованием
    size = int(NODE_RADIUS * 2 * camera_zoom)
    scaled_image = pygame.transform.scale(vert_image_original, (size, size))

    rect = scaled_image.get_rect(center=(int(x), int(y)))
    screen.blit(scaled_image, rect)

    icon_size = NODE_RADIUS * camera_zoom
    center = (x, y)
    if node.special_type == "key+":
        screen.blit(pygame.transform.scale(key_icon, (icon_size, icon_size)), (x - icon_size//2, y - icon_size//2))
        screen.blit(pygame.transform.scale(plus_icon, (icon_size//2, icon_size//2)), (x, y - icon_size//2))
    elif node.special_type == "key-":
        screen.blit(pygame.transform.scale(key_icon, (icon_size, icon_size)), (x - icon_size//2, y - icon_size//2))
        screen.blit(pygame.transform.scale(minus_icon, (icon_size//2, icon_size//2)), (x, y - icon_size//2))
    elif node.special_type == "hp+":
        screen.blit(pygame.transform.scale(hp_icon, (icon_size, icon_size)), (x - icon_size//2, y - icon_size//2))
        screen.blit(pygame.transform.scale(plus_icon, (icon_size//2, icon_size//2)), (x, y - icon_size//2))
    elif node.special_type == "hp-":
        screen.blit(pygame.transform.scale(hp_icon, (icon_size, icon_size)), (x - icon_size//2, y - icon_size//2))
        screen.blit(pygame.transform.scale(minus_icon, (icon_size//2, icon_size//2)), (x, y - icon_size//2))
    elif node.special_type == "kill":
        screen.blit(pygame.transform.scale(skull_icon, (icon_size, icon_size)), (x - icon_size//2, y - icon_size//2))
    elif node.special_type == "chest":
        screen.blit(pygame.transform.scale(chest_icon, (icon_size, icon_size)), (x - icon_size//2, y - icon_size//2))

    if node.flash_timer > 0:
        pygame.draw.circle(screen, (255, 255, 0), (x, y), NODE_RADIUS // 2 * camera_zoom, 5)


def handle_node_effect(player_index, node, players_stats):
    node_type = getattr(node, "special_type", None)
    stats = players_stats[player_index]

    if node_type == "key+":
        stats["keys"] += 5
        key_sound.play()

    elif node_type == "key-":
        stats["keys"] = max(0, stats["keys"] - 5)
        key_sound.play()

    elif node_type == "hp+":
        stats["hp"] = min(30, stats["hp"] + 10)
        heartbeat_sound.play()

    elif node_type == "hp-":
        stats["hp"] = max(0, stats["hp"] - 10)
        heartbeat_sound.play()

    elif node_type == "kill":
        available_targets = [
            i for i in range(len(players_stats))
            if i != player_index and players_stats[i]["hp"] > 0
        ]
        return True, available_targets, player_index

    return False, [], None


def handle_chest_on_step(player_index, node, players_stats):
    if getattr(node, "special_type", None) == "chest":
        stats = players_stats[player_index]
        if stats["keys"] >= 30:
            stats["keys"] -= 30
            stats["chests"] += 1
            cup_sound.play()


import pygame
import math

# Функция для вычисления угла между точками
def angle_between_points(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    return math.atan2(dy, dx)

# Функция для интерполяции цвета
def interpolate_color(color1, color2, factor):
    r = int(color1[0] + (color2[0] - color1[0]) * factor)
    g = int(color1[1] + (color2[1] - color1[1]) * factor)
    b = int(color1[2] + (color2[2] - color1[2]) * factor)
    return (r, g, b)

# Функция для рисования стрелки с градиентом
def draw_arrow(surface, start, end, color_start, color_end, width, camera_zoom):
    # Вычисление угла между начальной и конечной точкой
    angle = angle_between_points(start, end)

    # Длина стрелки
    arrow_length = surface.get_width() // 50 * camera_zoom

    # Ширина стрелки
    arrow_width = surface.get_width() // 100 * camera_zoom

    # Количество шагов для градиента (чем больше шагов, тем плавнее переход)
    steps = int(math.hypot(end[0] - start[0], end[1] - start[1]) / 5)

    # Рисуем линии с градиентом от начала до конца
    for i in range(steps):
        factor = i / steps  # Интерполяционный коэффициент
        intermediate_color = interpolate_color(color_start, color_end, factor)
        intermediate_end = (start[0] + (end[0] - start[0]) * factor, start[1] + (end[1] - start[1]) * factor)
        intermediate_start = (start[0] + (end[0] - start[0]) * (factor - 1 / steps), start[1] + (end[1] - start[1]) * (factor - 1 / steps))
        pygame.draw.line(surface, intermediate_color, intermediate_start, intermediate_end, width)

    # Рассчитываем координаты концов стрелки для наконечника
    p1 = (end[0] - arrow_length * math.cos(angle - math.pi / 10), end[1] - arrow_length * math.sin(angle - math.pi / 10))
    p2 = (end[0] - arrow_length * math.cos(angle + math.pi / 10), end[1] - arrow_length * math.sin(angle + math.pi / 10))

    # Рисуем наконечник стрелки
    pygame.draw.polygon(surface, color_end, [end, p1, p2])


def draw_nodes(screen, nodes, camera_offset, camera_zoom):
    for node in nodes:
        for neighbor in node.neighbors:
            start, end = shorten_line(node.pos, neighbor.pos, NODE_RADIUS * camera_zoom)
            start = apply_camera(start, camera_offset, camera_zoom)
            end = apply_camera(end, camera_offset, camera_zoom)
            draw_arrow(screen, start, end, RED, GREEN, 3, camera_zoom)

    for node in nodes:
        draw_vert(screen, node, camera_offset, camera_zoom)


def load_player_sprites(prefix, count):
    return [
        pygame.transform.scale(
            pygame.image.load(f"{prefix}{i}.png").convert_alpha(),
            (PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
        )
        for i in range(1, count + 1)
    ]


def draw_players(screen, players, camera_offset, camera_zoom):
    position_map = defaultdict(list)
    for idx, player in enumerate(players):
        key = tuple(player.current_node.pos) if not player.is_moving else tuple(player.actual_pos)
        position_map[key].append((idx, player))

    for (pos_x, pos_y), grouped_players in position_map.items():
        count = len(grouped_players)
        angle_step = 2 * math.pi / count if count > 1 else 0
        radius = 28 * camera_zoom if count > 1 else 0  # радиус тоже масштабируем

        for i, (idx, player) in enumerate(grouped_players):
            angle = i * angle_step
            offset_x = radius * math.cos(angle)
            offset_y = radius * math.sin(angle)

            x, y = apply_camera(player.actual_pos, camera_offset, camera_zoom)  # <- исправлено
            x += offset_x
            y += offset_y

            img = player.current_sprite
            if img is None:
                img = pygame.Surface((PLAYER_RADIUS * 2, PLAYER_RADIUS * 2), pygame.SRCALPHA)
                pygame.draw.circle(img, (255, 0, 0), (PLAYER_RADIUS, PLAYER_RADIUS), PLAYER_RADIUS)

            # Масштабировать спрайт под zoom
            size = int(img.get_width() * camera_zoom), int(img.get_height() * camera_zoom)
            scaled_img = pygame.transform.scale(img, size)

            img_rect = scaled_img.get_rect(center=(x, y))
            screen.blit(scaled_img, img_rect)


def draw_turn_order_ui(screen, players, turn_order, current_turn_index, screen_width, screen_height):
    cell_size = int(screen_height * 0.07)
    spacing = int(screen_width * 0.005)
    x_offset = screen_width - (len(turn_order) * (cell_size + spacing)) - int(screen_width * 0.02)
    y_offset = int(screen_height * 0.02)

    text_color = (0, 0, 0)
    border_color = (150, 150, 150)
    highlight_color = (255, 0, 0)
    font = pygame.font.SysFont(None, int(screen_height * 0.035))

    # Первая строка — иконки
    for i, player_idx in enumerate(turn_order):
        player = players[player_idx]
        icon = pygame.transform.scale(player.sprite_images[0], (cell_size, cell_size))
        cell_x = x_offset + i * (cell_size + spacing)
        cell_y = y_offset

        # Рамка
        pygame.draw.rect(screen, highlight_color if i == current_turn_index else border_color,
                         (cell_x - 2, cell_y - 2, cell_size + 4, cell_size + 4), 2)
        screen.blit(icon, (cell_x, cell_y))

    # Вторая строка — оставшиеся ходы
    for i, player_idx in enumerate(turn_order):
        player = players[player_idx]
        cell_x = x_offset + i * (cell_size + spacing)
        cell_y = y_offset + cell_size + int(screen_height * 0.005)

        steps_text = str(player.steps_remaining)
        text_surf = font.render(steps_text, True, text_color)
        text_rect = text_surf.get_rect(center=(cell_x + cell_size // 2, cell_y + cell_size // 2))
        screen.blit(text_surf, text_rect)


def draw_gradient_background(screen, screen_width, screen_height):
    for y in range(SCREEN_HEIGHT):
        color = (
            int(BLUE[0] + (LIGHT_BLUE[0] - BLUE[0]) * (y / screen_height)),
            int(BLUE[1] + (LIGHT_BLUE[1] - BLUE[1]) * (y / screen_height)),
            int(BLUE[2] + (LIGHT_BLUE[2] - BLUE[2]) * (y / screen_height))
        )
        pygame.draw.line(screen, color, (0, y), (screen_width, y))


def draw_rounds_progress(screen, rounds_passed, max_rounds, screen_width, screen_height):
    font = pygame.font.SysFont(None, int(screen_height * 0.04))
    text = font.render(f"Раунд: {rounds_passed} / {max_rounds}", True, (0, 0, 0))
    screen.blit(text, (screen_width - text.get_width() - 20, int(screen_height * 0.2)))


def draw_player_stats(screen, players_stats, screen_width, screen_height):
    icon_size = int(screen_height * 0.045)
    padding = int(screen_width * 0.008)
    font = pygame.font.SysFont(None, int(screen_height * 0.03))
    line_height = icon_size + padding * 2

    # Медали
    medal_images = [
        pygame.image.load("first.png").convert_alpha(),
        pygame.image.load("second.png").convert_alpha(),
        pygame.image.load("third.png").convert_alpha(),
        pygame.image.load("fourth.png").convert_alpha()
    ]
    medal_images = [pygame.transform.scale(img, (icon_size, icon_size)) for img in medal_images]

    sorted_indices = sorted(
        range(len(players_stats)),
        key=lambda i: (-players_stats[i]['chests'], -players_stats[i]['keys'])
    )

    base_x = int(screen_width * 0.02)
    base_y = int(screen_height * 0.02)
    cell_width = int(screen_width * 0.3)
    cell_height = line_height

    for i, idx in enumerate(sorted_indices):
        stats = players_stats[idx]
        y = base_y + i * (cell_height + padding)

        # Фон прямоугольника
        pygame.draw.rect(screen, (230, 230, 230), (base_x, y, cell_width, cell_height), border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), (base_x, y, cell_width, cell_height), 2, border_radius=8)

        x = base_x + padding

        # Медаль
        screen.blit(medal_images[i], (x, y + padding))
        x += icon_size + padding

        # Иконка игрока
        icon = pygame.transform.scale(player_icons[idx], (icon_size, icon_size))
        screen.blit(icon, (x, y + padding))
        x += icon_size + padding

        # HP
        hp = pygame.transform.scale(hp_icon, (icon_size, icon_size))
        screen.blit(hp, (x, y + padding))
        text = font.render(str(stats['hp']), True, (0, 0, 0))
        screen.blit(text, (x + icon_size + padding // 2, y + padding))
        x += icon_size * 2 + padding * 2

        # Ключи
        key = pygame.transform.scale(key_icon, (icon_size, icon_size))
        screen.blit(key, (x, y + padding))
        text = font.render(str(stats['keys']), True, (0, 0, 0))
        screen.blit(text, (x + icon_size + padding // 2, y + padding))
        x += icon_size * 2 + padding * 2

        # Сундуки
        chest = pygame.transform.scale(chest_icon, (icon_size, icon_size))
        screen.blit(chest, (x, y + padding))
        text = font.render(str(stats['chests']), True, (0, 0, 0))
        screen.blit(text, (x + icon_size + padding // 2, y + padding))


def level_1(PLAYERS_CNT, MAX_ROUNDS, GER_OR_CREATED):
    PLAYER_COUNT = PLAYERS_CNT
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    pygame.display.set_caption("Level 1 — Camera and Large Map")

    player_sprite_sets = [
        load_player_sprites("Player1_", 10),
        load_player_sprites("Player2_", 5),
        load_player_sprites("Player3_", 9),
        load_player_sprites("Player4_", 12)
    ]
    player_sprite_sets = player_sprite_sets[:PLAYER_COUNT]

    hp_icon.convert_alpha()
    key_icon.convert_alpha()
    chest_icon.convert_alpha()

    players_stats = [
        {'hp': 20, 'keys': 10, 'chests': 0},
        {'hp': 20, 'keys': 10, 'chests': 0},
        {'hp': 20, 'keys': 10, 'chests': 0},
        {'hp': 20, 'keys': 10, 'chests': 0}
    ]

    players_stats = players_stats[:PLAYER_COUNT]

    #background = pygame.image.load("BAcK.png").convert()
    #background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    #background_rect = background.get_rect()

    clock = pygame.time.Clock()

    all_nodes = create_nodes(screen.get_width(), screen.get_height(), GER_OR_CREATED)
    players = [Player(all_nodes[0], sprite_images=sprites) for sprites in player_sprite_sets]

    current_player_index = 0
    rolled_number = None
    last_moved_player_index = None

    camera_offset = [0, 0]
    camera_follow_player = True
    camera_zoom = 1.0

    pending_mini_game = False
    pending_mini_game_timer = 0

    round_passed = 1

    choosing_target = False
    available_targets = []

    is_fullscreen = True

    turn_order = list(range(PLAYER_COUNT))
    random.shuffle(turn_order)
    current_turn_index = 0


    running = True
    while running:
        dt = clock.tick(60) / 1000
        #screen.blit(background, (-camera_offset[0], -camera_offset[1]))
        screen.fill(WHITE)
        CAMERA_SPEED = int(20 / camera_zoom)

        # --- Управление ---
        keys = pygame.key.get_pressed()
        if not camera_follow_player:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                camera_offset[0] -= CAMERA_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                camera_offset[0] += CAMERA_SPEED
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                camera_offset[1] -= CAMERA_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                camera_offset[1] += CAMERA_SPEED

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and choosing_target:
                mx, my = event.pos
                for idx in available_targets:
                    x = 100 + idx * 150
                    y = SCREEN_HEIGHT // 2
                    if x <= mx <= x + 100 and y <= my <= y + 100:
                        stolen_keys = players_stats[idx]["keys"] // 2
                        players_stats[idx]["keys"] -= stolen_keys
                        players_stats[killer_index]["keys"] += stolen_keys
                        players_stats[idx]["hp"] = 0

                        choosing_target = False
                        available_targets = []
                        killer_index = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    camera_zoom *= 0.95
                    camera_zoom = max(0.1, camera_zoom)  # Минимальный зум
                elif event.key == pygame.K_w:
                    camera_zoom *= 1.05
                    camera_zoom = min(5.0, camera_zoom)
                elif event.key == pygame.K_e:
                    camera_zoom = 1
                elif event.key == pygame.K_ESCAPE:
                    if is_fullscreen:
                        is_fullscreen = False
                        pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
                    else:
                        is_fullscreen = True
                        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

                current_player = players[turn_order[current_turn_index]]

                if event.key == pygame.K_TAB:
                    camera_follow_player = not camera_follow_player

                elif event.key == ROLL_KEY and current_player.steps_remaining == 0:
                    random.seed(time.time())
                    rolled_number = random.randint(1, 6)
                    current_player.steps_remaining = rolled_number

                elif current_player.steps_remaining > 0 and not current_player.is_moving:
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        index = event.key - pygame.K_1
                        neighbors = current_player.current_node.neighbors
                        if index < len(neighbors):
                            current_player.set_target(neighbors[index])
                            current_player.steps_remaining -= 1
                            if current_player.steps_remaining == 0:
                                last_moved_player_index = turn_order[current_turn_index]
                                current_turn_index += 1
                                if current_turn_index >= len(players):
                                    round_passed += 1
                                    if round_passed > MAX_ROUNDS:
                                        result.show_result(screen, players_stats, player_sprite_sets)
                                        running = False
                                        break
                                    pending_mini_game = True
                                    pending_mini_game_timer = 1.5
                                    current_turn_index = 0
                                rolled_number = None

        if not running:
            break

        if camera_follow_player and current_turn_index < len(turn_order):
            current = players[turn_order[current_turn_index]]
            target_x = current.current_node.pos[0] - SCREEN_WIDTH // 2
            target_y = current.current_node.pos[1] - SCREEN_HEIGHT // 2
            camera_offset[0] += (target_x - camera_offset[0]) * 0.1
            camera_offset[1] += (target_y - camera_offset[1]) * 0.1

        for player in players:
            player.update_position(dt)

        for i, player in enumerate(players):
            player.update_position(dt)
            if not player.is_moving:
                node = player.current_node
                if getattr(node, "special_type", None) == "chest":
                    stats = players_stats[i]
                    if stats["keys"] >= 30:
                        stats["keys"] -= 30
                        stats["chests"] += 1
                        cup_sound.play()
                        node.flash_timer = 0.5
                        node.special_type = None

                        empty_nodes = [n for n in all_nodes if getattr(n, "special_type", None) is None]
                        if empty_nodes:
                            random.seed(time.time())
                            new_chest_node = random.choice(empty_nodes)
                            new_chest_node.special_type = "chest"

            if players_stats[i]['hp'] <= 0 and not player.is_dead:
                player.is_dead = True
                player.dead_timer = 0
                death_sound.play()

            if player.is_dead:
                player.dead_timer += dt
                if player.dead_timer >= 1.5:
                    player.is_dead = False
                    player.dead_timer = 0
                    player.current_node = all_nodes[0]
                    player.actual_pos = player.current_node.pos[:]
                    players_stats[i]['hp'] = 30

        if last_moved_player_index is not None:
            player = players[last_moved_player_index]
            if player.waiting_node_effect and player.just_stopped:
                player.waiting_node_effect = False
                player.just_stopped = False
                choosing_target_now, targets, killer = handle_node_effect(last_moved_player_index, player.current_node,
                                                                          players_stats)
                if choosing_target_now:
                    choosing_target = True
                    available_targets = targets
                    killer_index = killer
                last_moved_player_index = None

        if choosing_target:
            for idx in available_targets:
                x = 100 + idx * 150
                y = SCREEN_HEIGHT // 2

                icon = pygame.transform.scale(player_icons[idx], (100, 100))
                screen.blit(icon, (x, y))

            choose_text = font.render("Выберите игрока для убийства", True, RED)
            screen.blit(choose_text, (SCREEN_WIDTH // 2 - choose_text.get_width() // 2, SCREEN_HEIGHT // 2 - 150))


        # --- Отрисовка ---
        draw_nodes(screen, all_nodes, camera_offset, camera_zoom)
        draw_players(screen, players, camera_offset, camera_zoom)
        draw_turn_order_ui(screen, players, turn_order, current_turn_index, screen.get_width(), screen.get_height())
        draw_player_stats(screen, players_stats, screen.get_width(), screen.get_height())
        draw_rounds_progress(screen, round_passed, MAX_ROUNDS, screen.get_width(), screen.get_height())

        for node in all_nodes:
            if node.flash_timer > 0:
                node.flash_timer -= dt
                if node.flash_timer < 0:
                    node.flash_timer = 0

        if pending_mini_game:
            pending_mini_game_timer -= dt
            if pending_mini_game_timer <= 0:
                pending_mini_game = False
                if "last_game_index" not in locals():
                    last_game_index = -1

                available_indices = [i for i in range(len(MINI_GAMES)) if i != last_game_index]
                random.seed(time.time())
                new_game_index = random.choice(available_indices)
                GAME = MINI_GAMES[new_game_index]
                last_game_index = new_game_index

                turn_order = GAME.run_game(screen, PLAYER_COUNT)

                for i, el in enumerate(turn_order):
                    if i == 0:
                        players_stats[el]["keys"] += 12
                    elif i == 1:
                        players_stats[el]["keys"] += 8
                    elif i == 2:
                        players_stats[el]["keys"] += 4
                    else:
                        players_stats[el]["keys"] += 2

        # Подсветка
        if players[turn_order[current_turn_index]].steps_remaining > 0:
            for i, neighbor in enumerate(players[turn_order[current_turn_index]].current_node.neighbors):
                x, y = apply_camera(neighbor.pos, camera_offset, camera_zoom)
                pygame.draw.circle(screen, GREEN, (x, y), NODE_RADIUS * camera_zoom, 3)
                number = font.render(str(i + 1), True, RED)
                screen.blit(number, (x - 5, y - 25))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    level_1()