import random
import math

STARS_CHARS = ['+', '*', '.', ':']
SPACE_FROM_SCREEN_EDGES = 2


def get_random_star_char():
    return random.choice(STARS_CHARS)


def get_max_coordinates(canvas):
    max_coordinates = []

    for size in canvas.getmaxyx():
        max_coordinates.append(size - SPACE_FROM_SCREEN_EDGES)

    return max_coordinates


def get_canvas_center(canvas):
    max_coordinates = get_max_coordinates(canvas)
    center_coordinates = []
    for coord in max_coordinates:
        center_coordinates.append(round(coord/2))
    return center_coordinates


def get_random_animation_time(reference_time):
    adder = math.ceil(reference_time * 0.5)
    return random.randint(reference_time - adder, reference_time + adder)


def get_spaceship_frames():
    with open('frames/rocket_frame_1.txt', 'r') as file1, open('frames/rocket_frame_2.txt', 'r') as file2:
        spaceship_frame1 = file1.read()
        spaceship_frame2 = file2.read()
    return spaceship_frame1, spaceship_frame2


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def get_max_available_coords_for_moving(canvas, frame):
    frame_rows, frame_cols = get_frame_size(frame)
    max_y, max_x = canvas.getmaxyx()
    space_from_border = 1

    max_available_rows = max_y - frame_rows - space_from_border
    max_available_cols = max_x - frame_cols - space_from_border

    return max_available_rows, max_available_cols, space_from_border
