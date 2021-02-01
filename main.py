import time
import curses

from curses_tools import read_controls
from explosion import explode
from obstacles import Obstacle
from physics import update_speed
from utils import *
from itertools import cycle


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(get_random_animation_time(20))

        canvas.addstr(row, column, symbol)
        await sleep(get_random_animation_time(3))

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(get_random_animation_time(5))

        canvas.addstr(row, column, symbol)
        await sleep(get_random_animation_time(3))


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
        row += columns_speed

        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    garbage_row_size, garbage_column_size = get_frame_size(garbage_frame)

    row = 0

    obstacle = Obstacle(row, column, garbage_row_size, garbage_column_size)
    obstacles.append(obstacle)

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        obstacle.row += speed
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        if obstacle in obstacles_in_last_collisions:
            obstacles_in_last_collisions.remove(obstacle)
            obstacles.remove(obstacle)
            center_row, center_column = obstacle.get_frame_center()
            await explode(canvas, center_row, center_column)
            return

    obstacles.remove(obstacle)


async def draw_spaceship(canvas, row, column, spaceship_frames):
    tic = 0
    frame_iterator = cycle(spaceship_frames)

    y_coord = row
    x_coord = column
    row_speed = column_speed = 0

    current_frame = spaceship_frames[0]

    max_rows, max_cols, space_from_border, spaceship_width = get_max_available_coords_for_moving(canvas, current_frame)

    while True:
        tic += 1
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        for obstacle in obstacles:
            if obstacle.has_collision(y_coord, x_coord):
                obstacles_in_last_collisions.append(obstacle)
                draw_frame(canvas, y_coord, x_coord, current_frame, negative=True)
                game_over = show_game_over(canvas)
                coroutines.append(game_over)
                return

        if rows_direction != 0 or columns_direction != 0:
            draw_frame(canvas, y_coord, x_coord, current_frame, negative=True)

            row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)

            y_coord += row_speed
            x_coord += column_speed

            if y_coord < space_from_border:
                y_coord = space_from_border
            if y_coord > max_rows:
                y_coord = max_rows
            if x_coord < space_from_border:
                x_coord = space_from_border
            if x_coord > max_cols:
                x_coord = max_cols

            draw_frame(canvas, y_coord, x_coord, current_frame)
        else:
            row_speed = column_speed = 0

        if space_pressed and year >= 2020:
            spaceship_center = x_coord + round(spaceship_width / 2)
            gun_shot = fire(canvas, y_coord, spaceship_center)
            coroutines.append(gun_shot)

        if tic % 2 == 0:
            draw_frame(canvas, y_coord, x_coord, current_frame, negative=True)
            current_frame = next(frame_iterator)
            draw_frame(canvas, y_coord, x_coord, current_frame)
            canvas.refresh()

        await sleep(1)


async def fill_orbit_with_garbage(canvas):
    while True:
        appear_column = get_random_appear_column(canvas)
        garbage_frame = get_random_garbage_frame()
        garbage = fly_garbage(canvas, appear_column, garbage_frame, speed=0.5)
        coroutines.append(garbage)
        frequency = get_garbage_delay_tics(year)

        await sleep(frequency)


def get_random_stars(canvas):
    max_coordinates = get_max_coordinates(canvas)

    stars_coroutines = []

    for star in range(STARS_AMOUNT):
        couroutine = blink(
            canvas,
            random.randint(1, max_coordinates[0]),
            random.randint(1, max_coordinates[1]),
            get_random_star_char()
        )
        stars_coroutines.append(couroutine)

    return stars_coroutines


async def show_year(canvas):
    global year
    year = START_YEAR
    while True:
        canvas.addstr(0, 0, f'Year {year}')
        canvas.refresh()
        await sleep(TICS_FOR_YEAR)
        year += 1


async def show_history_message(canvas):
    frame = PHRASES[START_YEAR]
    while True:
        if year in PHRASES:
            frame = PHRASES[year]
        draw_frame(canvas, 0, 0, frame)
        canvas.refresh()
        await sleep()
        draw_frame(canvas, 0, 0, frame, negative=True)


async def release_garbage(canvas):
    while year < 1961:
        await sleep(15)
    await fill_orbit_with_garbage(canvas)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    coroutines = get_random_stars(canvas)

    canvas_center = get_canvas_center(canvas)

    max_row, max_column = get_max_coordinates(canvas)
    year_counting_canvas = canvas.derwin(max_row, max_column - 30)
    year_counting = show_year(year_counting_canvas)
    coroutines.append(year_counting)

    history_messages_canvas = canvas.derwin(max_row, 2)
    history_messages = show_history_message(history_messages_canvas)
    coroutines.append(history_messages)

    spaceship_y_coord = canvas_center[0]
    spaceship_x_coord = canvas_center[1]

    garbage = release_garbage(canvas)
    coroutines.append(garbage)

    spaceship = draw_spaceship(canvas, spaceship_y_coord, spaceship_x_coord, spaceship_frames)
    coroutines.append(spaceship)

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                canvas.refresh()
                canvas.border()
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break

        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    coroutines = []
    obstacles = []
    obstacles_in_last_collisions = []
    spaceship_frames = get_spaceship_frames()
    curses.update_lines_cols()
    curses.wrapper(draw)
