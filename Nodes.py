import math
import Gen_graph
import random
import time


class Node:
    def __init__(self, x, y, special_type=None):
        self.pos = [x, y]
        self.neighbors = []
        self.special_type = special_type
        self.size = 60
        self.flash_timer = 0

    def connect(self, other):
        if other not in self.neighbors:
            self.neighbors.append(other)


def create_nodes(screen_width, screen_height, gen_or_create):
    node_defs = []
    edges = []
    points = []
    if gen_or_create == 1:
        points, edges = Gen_graph.start()

    elif gen_or_create == 2:
        points = [
            (1.8, 1.8), (1.65, 1.8), (1.5, 1.8), (1.35, 1.8),
            (1.35, 1.65), (1.2, 1.65), (1.05, 1.65), (0.9, 1.65),
            (0.75, 1.75), (0.6, 1.75), (0.45, 1.75), (0.45, 1.5),
            (0.45, 1.25), (0.45, 1.0), (0.45, 0.75), (0.3, 0.75),
            (0.15, 0.75), (0.15, 0.5), (0.15, 0.25), (0.15, 0),
            (0.15, -0.25), (0.3, -0.25), (0.45, -0.25), (0.45, -0.5),
            (0.45, -0.75), (0.65, -0.75), (0.85, -0.75), (1.05, -0.75),
            (1.25, -0.75), (1.25, -0.5), (1.25, -0.25), (1.4, -0.35),
            (1.55, -0.45), (1.7, -0.55), (1.85, -0.55), (2, -0.55),
            (2, -0.3), (2, -0.05), (2, 0.2), (2.1, 0.4),
            (2.2, 0.6), (2.2, 0.85), (2.2, 1.1), (2.2, 1.35),
            (2.2, 1.6), (2.065, 1.7), (1.94, 1.8), (1.4, -0.1),
            (1.55, 0.05), (1.7, 0.2), (1.85, 0.2), (1.35, 1.50),
            (1.35, 1.25), (1.35, 1.00), (1.50, 0.8), (1.65, 0.6),
            (1.7, 0.4), (1.2, 0.8), (1.05, 0.6), (0.6, 0.6),
            (0.75, 0.6), (0.9, 0.6), (1.05, 0.4), (1.05, 0.2),
            (1.15, -0.05), (0.85, -0.5), (0.85, -0.25), (0.65, -0.25)
        ]
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10),
            (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17), (17, 18),
            (18, 19), (19, 20), (20, 21), (21, 22), (22, 23), (23, 24), (24, 25), (25, 26),
            (26, 27), (27, 28), (28, 29), (29, 30), (30, 31), (31, 32), (32, 33), (33, 34),
            (34, 35), (35, 36), (36, 37), (37, 38), (38, 39), (39, 40), (40, 41), (41, 42),
            (42, 43), (43, 44), (44, 45), (45, 46), (46, 0), (30, 47), (47, 48), (48, 49),
            (49, 50), (50, 38), (4, 51), (51, 52), (52, 53), (53, 54), (54, 55), (55, 56),
            (56, 49), (53, 57), (59, 60), (60, 61), (61, 58), (57, 58), (14, 59), (58, 62),
            (62, 63), (63, 64), (64, 30), (22, 67), (67, 66), (66, 65), (65, 26)
        ]

    types = ["hp-", "hp+", "key-", "key+", "kill", "chest"]
    giving_types = []
    for el in types:
        if el == "chest":
            for _ in range(3):
                giving_types.append("chest")
        else:
            for _ in range(len(points) // 7):
                giving_types.append(el)
    while len(giving_types) < len(points) - 1:
        giving_types.append(None)

    random.seed(time.time())
    random.shuffle(giving_types)
    giving_types.append(None)
    giving_types.reverse()
    for i in range(len(points)):
        node_defs.append((points[i][0], points[i][1], giving_types[i]))

    nodes = [Node(int(x * screen_width), int(y * screen_height), t) for x, y, t in node_defs]

    for src_idx, dst_idx in edges:
        nodes[src_idx].connect(nodes[dst_idx])

    return nodes
