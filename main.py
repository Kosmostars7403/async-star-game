import asyncio
import time
import curses
import random

from curses_tools import draw_frame, read_controls
from utils import get_random_animation_time, get_random_star_char, get_max_coordinates, get_spaceship_frames, \
    get_canvas_center, get_max_available_coords_for_moving
from itertools import cycle

TIC_TIMEOUT = 0.1
STARS_AMOUNT = 100


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(get_random_animation_time(20)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(get_random_animation_time(3)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(get_random_animation_time(5)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(get_random_animation_time(3)):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def draw_spaceship(canvas, row, column, spaceship_frames):
    tic = 0
    frame_iterator = cycle(spaceship_frames)

    y_coord = row
    x_coord = column
    current_frame = spaceship_frames[0]

    max_rows, max_cols, space_from_border = get_max_available_coords_for_moving(canvas, current_frame)

    while True:
        tic += 1
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        if rows_direction != 0 or columns_direction != 0:
            draw_frame(canvas, y_coord, x_coord, current_frame, negative=True)
            y_coord += rows_direction
            x_coord += columns_direction

            if y_coord < space_from_border:
                y_coord = space_from_border
            if y_coord > max_rows:
                y_coord = max_rows
            if x_coord < space_from_border:
                x_coord = space_from_border
            if x_coord > max_cols:
                x_coord = max_cols

            draw_frame(canvas, y_coord, x_coord, current_frame)

        if tic % 2 == 0:
            draw_frame(canvas, y_coord, x_coord, current_frame, negative=True)
            current_frame = next(frame_iterator)
            draw_frame(canvas, y_coord, x_coord, current_frame)
            canvas.refresh()

        await asyncio.sleep(0)


def get_random_stars(canvas):
    max_coordinates = get_max_coordinates(canvas)

    coroutines = []

    for star in range(STARS_AMOUNT):
        couroutine = blink(
            canvas,
            random.randint(1, max_coordinates[0]),
            random.randint(1, max_coordinates[1]),
            get_random_star_char()
        )
        coroutines.append(couroutine)

    return coroutines


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    canvas_center = get_canvas_center(canvas)

    coroutines = get_random_stars(canvas)

    gun_shot = fire(canvas, canvas_center[0], canvas_center[1])
    coroutines.append(gun_shot)

    spaceship_y_coord = canvas_center[0]
    spaceship_x_coord = canvas_center[1]

    spaceship = draw_spaceship(canvas, spaceship_y_coord, spaceship_x_coord, spaceship_frames)
    coroutines.append(spaceship)

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break

        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    spaceship_frames = get_spaceship_frames()
    curses.update_lines_cols()
    curses.wrapper(draw)
