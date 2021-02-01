import asyncio
import os
import random
import math

from curses_tools import draw_frame
from settings import *


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
    with open('frames/spaceship/rocket_frame_1.txt', 'r') as file1, open('frames/spaceship/rocket_frame_2.txt', 'r') as file2:
        spaceship_frame1 = file1.read()
        spaceship_frame2 = file2.read()
    return spaceship_frame1, spaceship_frame2


def get_random_garbage_frame():
    garbage_frame_file_path = os.path.join(GARBAGE_FRAMES_DIR, random.choice(os.listdir(GARBAGE_FRAMES_DIR)))
    with open(garbage_frame_file_path, 'r') as file:
        garbage_frame = file.read()
    return garbage_frame


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

    return max_available_rows, max_available_cols, space_from_border, frame_cols


def get_random_appear_column(canvas):
    columns_amount = canvas.getmaxyx()[1]
    return random.randint(1, columns_amount-1)


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def show_game_over(canvas):
    rows_center, columns_center = get_canvas_center(canvas)

    with open('frames/gameover.txt', 'r') as file:
        game_over_frame = file.read()

    row_size, column_size = get_frame_size(game_over_frame)

    row = rows_center - round(row_size/2)
    column = columns_center - round(column_size/2)

    while True:
        draw_frame(canvas, row, column, game_over_frame)
        await sleep(1)


def get_garbage_delay_tics(year):
    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2