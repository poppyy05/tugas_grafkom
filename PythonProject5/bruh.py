import pygame
import sys
import math

pygame.init()

# Setup screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aplikasi Grafis 2D")

# Warna dasar
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 0, 0)
CLIP_COLOR = (0, 255, 0)

# Global state
objects = []
selected_tool = "line"
color = BLACK
thickness = 2
transform_mode = None
window_rect = pygame.Rect(200, 150, 400, 300)
is_clipping = False


# Fungsi menggambar objek
def draw_objects():
    screen.fill(WHITE)
    pygame.draw.rect(screen, (200, 200, 200), window_rect, 2)  # Windowing area

    for obj in objects:
        obj_type, points, c, thick = obj["type"], obj["points"], obj["color"], obj["thickness"]
        if obj_type == "point":
            pygame.draw.circle(screen, c, points[0], thick)
        elif obj_type == "line":
            pygame.draw.line(screen, c, points[0], points[1], thick)
        elif obj_type == "rect":
            x, y = points[0]
            w, h = points[1][0] - x, points[1][1] - y
            pygame.draw.rect(screen, c, (x, y, w, h), thick)
        elif obj_type == "ellipse":
            x, y = points[0]
            w, h = points[1][0] - x, points[1][1] - y
            pygame.draw.ellipse(screen, c, (x, y, w, h), thick)


# Fungsi transformasi
def translate(obj, dx, dy):
    obj["points"] = [(x + dx, y + dy) for x, y in obj["points"]]


def rotate(obj, angle_deg, center=None):
    angle = math.radians(angle_deg)
    cx, cy = center if center else obj["points"][0]
    new_points = []
    for x, y in obj["points"]:
        dx, dy = x - cx, y - cy
        nx = cx + dx * math.cos(angle) - dy * math.sin(angle)
        ny = cy + dx * math.sin(angle) + dy * math.cos(angle)
        new_points.append((nx, ny))
    obj["points"] = new_points


def scale(obj, sx, sy, center=None):
    cx, cy = center if center else obj["points"][0]
    obj["points"] = [((x - cx) * sx + cx, (y - cy) * sy + cy) for x, y in obj["points"]]


# Fungsi windowing
def apply_windowing():
    for obj in objects:
        in_window = all(window_rect.collidepoint(p) for p in obj["points"])
        if in_window:
            obj["color"] = HIGHLIGHT_COLOR


# Fungsi clipping garis dengan Cohen-Sutherland
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8


def compute_out_code(x, y, rect):
    code = INSIDE
    if x < rect.left:
        code |= LEFT
    elif x > rect.right:
        code |= RIGHT
    if y < rect.top:
        code |= TOP
    elif y > rect.bottom:
        code |= BOTTOM
    return code


def cohen_sutherland_clip(p1, p2, rect):
    x0, y0 = p1
    x1, y1 = p2
    out_code0 = compute_out_code(x0, y0, rect)
    out_code1 = compute_out_code(x1, y1, rect)
    accept = False

    while True:
        if not (out_code0 | out_code1):
            accept = True
            break
        elif out_code0 & out_code1:
            break
        else:
            out_code_out = out_code0 if out_code0 else out_code1
            if out_code_out & TOP:
                x = x0 + (x1 - x0) * (rect.top - y0) / (y1 - y0)
                y = rect.top
            elif out_code_out & BOTTOM:
                x = x0 + (x1 - x0) * (rect.bottom - y0) / (y1 - y0)
                y = rect.bottom
            elif out_code_out & RIGHT:
                y = y0 + (y1 - y0) * (rect.right - x0) / (x1 - x0)
                x = rect.right
            elif out_code_out & LEFT:
                y = y0 + (y1 - y0) * (rect.left - x0) / (x1 - x0)
                x = rect.left

            if out_code_out == out_code0:
                x0, y0 = x, y
                out_code0 = compute_out_code(x0, y0, rect)
            else:
                x1, y1 = x, y
                out_code1 = compute_out_code(x1, y1, rect)

    if accept:
        return [(int(x0), int(y0)), (int(x1), int(y1))]
    else:
        return None


# Main loop
drawing = False
start_pos = None

while True:
    draw_objects()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Tombol keyboard
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                selected_tool = "point"
            elif event.key == pygame.K_2:
                selected_tool = "line"
            elif event.key == pygame.K_3:
                selected_tool = "rect"
            elif event.key == pygame.K_4:
                selected_tool = "ellipse"
            elif event.key == pygame.K_w:
                apply_windowing()
            elif event.key == pygame.K_c:
                is_clipping = True
                clipped_objects = []
                for obj in objects:
                    if obj["type"] == "line":
                        clipped = cohen_sutherland_clip(obj["points"][0], obj["points"][1], window_rect)
                        if clipped:
                            clipped_objects.append({
                                "type": "line",
                                "points": clipped,
                                "color": CLIP_COLOR,
                                "thickness": obj["thickness"]
                            })
                objects = clipped_objects

        # Mouse control
        if event.type == pygame.MOUSEBUTTONDOWN:
            start_pos = pygame.mouse.get_pos()
            drawing = True

        elif event.type == pygame.MOUSEBUTTONUP:
            end_pos = pygame.mouse.get_pos()
            if selected_tool == "point":
                objects.append({"type": "point", "points": [end_pos], "color": color, "thickness": thickness})
            elif selected_tool == "line":
                objects.append({"type": "line", "points": [start_pos, end_pos], "color": color, "thickness": thickness})
            elif selected_tool == "rect":
                objects.append({"type": "rect", "points": [start_pos, end_pos], "color": color, "thickness": thickness})
            elif selected_tool == "ellipse":
                objects.append(
                    {"type": "ellipse", "points": [start_pos, end_pos], "color": color, "thickness": thickness})
            drawing = False
