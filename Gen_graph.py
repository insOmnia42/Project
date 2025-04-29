import pygame
import random
import math

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()


def dist(a, b):
    return (a[0] - b[0])**2 + (a[1] - b[1])**2


def segments_intersect(a, b, c, d):
    def ccw(p1, p2, p3):
        return (p3[1]-p1[1])*(p2[0]-p1[0]) > (p2[1]-p1[1])*(p3[0]-p1[0])
    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)


def generate_near_point(points, min_dist=200, max_dist=350):
    base_point = random.choice(points)
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(min_dist, max_dist)
    new_x = base_point[0] + distance * math.cos(angle)
    new_y = base_point[1] + distance * math.sin(angle)
    return (new_x, new_y)


def convex_hull(points):
    points = sorted(points)
    if len(points) <= 1:
        return points

    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def is_inside(point, hull):
    if len(hull) < 3:
        return False
    for i in range(len(hull)):
        a = hull[i]
        b = hull[(i+1)%len(hull)]
        cross = (b[0]-a[0])*(point[1]-a[1]) - (b[1]-a[1])*(point[0]-a[0])
        if cross < 0:
            return False
    return True


def find_edges(new_point, points, edges):
    candidates_from_new = []
    candidates_to_new = []

    new_index = len(points)

    for i, p in enumerate(points):
        ok = True
        for (u, v) in edges:
            if segments_intersect(new_point, p, points[u], points[v]):
                ok = False
                break
        if ok:
            candidates_from_new.append((dist(new_point, p), (new_index, i)))

        ok = True
        for (u, v) in edges:
            if segments_intersect(p, new_point, points[u], points[v]):
                ok = False
                break
        if ok:
            candidates_to_new.append((dist(new_point, p), (i, new_index)))

    candidates_from_new.sort()
    candidates_to_new.sort()

    selected_edges = []
    if candidates_from_new:
        selected_edges.append(candidates_from_new[0][1])
    if candidates_to_new:
        selected_edges.append(candidates_to_new[0][1])

    return selected_edges


def start():
    points = []
    edges = []

    for _ in range(3):
        while True:
            point = (random.randint(200, 600), random.randint(150, 450))
            if all(dist(point, p) > 1000 for p in points):
                points.append(point)
                break

    edges.append((0, 1))
    edges.append((1, 2))
    edges.append((2, 0))

    running = True
    step = 0

    while step < 50:
        hull = convex_hull(points)

        for _ in range(100):
            new_point = generate_near_point(points)
            if all(dist(new_point, p) >= 10000 for p in points) and not is_inside(new_point, hull):
                break
        else:
            print("Не смогли найти подходящую точку")
            break

        new_index = len(points)
        points.append(new_point)

        new_edges = find_edges(new_point, points[:-1], edges)
        edges.extend(new_edges)

        step += 1

    points = [(x[0] / 400, x[1] / 300) for x in points]
    return points, edges
