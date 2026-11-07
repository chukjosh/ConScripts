"""Spinning ASCII donut for the terminal. Press Ctrl+C to stop.

Pure Python with no extra packages. It only prints text to the terminal.
"""

import math
import os
import sys
import time

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 24

TUBE_RADIUS = 1.0         # thickness of the donut's ring
RING_RADIUS = 2.0         # distance from the donut center to the middle of the tube
CAMERA_DISTANCE = 5.0     # how far the donut is from the viewer
PROJECTION_SCALE = 30.0   # zoom level

# Smaller steps look smoother but run slower
TUBE_ANGLE_STEP = 0.07
SPIN_ANGLE_STEP = 0.03

SHADE_CHARACTERS = ".,-~:;=!*#$@"  # dark to bright
TWO_PI = 2 * math.pi

HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
CLEAR_SCREEN = "\x1b[2J"
MOVE_CURSOR_TO_TOP_LEFT = "\x1b[H"


def frange(start, stop, step):
    """Yield floating point values from start up to (not including) stop."""
    value = start
    while value < stop:
        yield value
        value += step


def render_frame(rotation_around_x, rotation_around_z):
    """Return one frame of the donut as a multi-line string."""
    character_buffer = [" "] * (SCREEN_WIDTH * SCREEN_HEIGHT)
    depth_buffer = [0.0] * (SCREEN_WIDTH * SCREEN_HEIGHT)

    sin_x, cos_x = math.sin(rotation_around_x), math.cos(rotation_around_x)
    sin_z, cos_z = math.sin(rotation_around_z), math.cos(rotation_around_z)

    for tube_angle in frange(0.0, TWO_PI, TUBE_ANGLE_STEP):
        sin_tube, cos_tube = math.sin(tube_angle), math.cos(tube_angle)

        # Position of this point on the tube's cross-section circle
        circle_x = RING_RADIUS + TUBE_RADIUS * cos_tube
        circle_y = TUBE_RADIUS * sin_tube

        for spin_angle in frange(0.0, TWO_PI, SPIN_ANGLE_STEP):
            sin_spin, cos_spin = math.sin(spin_angle), math.cos(spin_angle)

            # 3D position after spinning around the donut's axis and rotating the whole donut
            point_x = circle_x * (cos_z * cos_spin + sin_x * sin_z * sin_spin) - circle_y * cos_x * sin_z
            point_y = circle_x * (sin_z * cos_spin - sin_x * cos_z * sin_spin) + circle_y * cos_x * cos_z
            point_z = CAMERA_DISTANCE + cos_x * circle_x * sin_spin + circle_y * sin_x
            inverse_depth = 1 / point_z

            # Project onto the 2D screen (characters are about twice as tall as wide)
            screen_column = int(SCREEN_WIDTH / 2 + PROJECTION_SCALE * inverse_depth * point_x)
            screen_row = int(SCREEN_HEIGHT / 2 - (PROJECTION_SCALE / 2) * inverse_depth * point_y)

            # Brightness from a light shining from above and behind the viewer
            brightness = (
                cos_spin * cos_tube * sin_z
                - cos_x * cos_tube * sin_spin
                - sin_x * sin_tube
                + cos_z * (cos_x * sin_tube - cos_tube * sin_x * sin_spin)
            )

            is_on_screen = 0 <= screen_column < SCREEN_WIDTH and 0 <= screen_row < SCREEN_HEIGHT
            if brightness > 0 and is_on_screen:
                buffer_index = screen_row * SCREEN_WIDTH + screen_column

                # Only draw if this point is closer to the viewer than what is already there
                if inverse_depth > depth_buffer[buffer_index]:
                    depth_buffer[buffer_index] = inverse_depth
                    shade_index = min(int(brightness * 8), len(SHADE_CHARACTERS) - 1)
                    character_buffer[buffer_index] = SHADE_CHARACTERS[shade_index]

    rows_of_text = [
        "".join(character_buffer[row * SCREEN_WIDTH:(row + 1) * SCREEN_WIDTH])
        for row in range(SCREEN_HEIGHT)
    ]
    return "\n".join(rows_of_text)


def main():
    # Running an empty command turns on ANSI escape code support in older Windows consoles
    if os.name == "nt":
        os.system("")

    rotation_around_x = 0.0
    rotation_around_z = 0.0

    try:
        sys.stdout.write(HIDE_CURSOR + CLEAR_SCREEN)
        while True:
            frame_text = render_frame(rotation_around_x, rotation_around_z)
            sys.stdout.write(MOVE_CURSOR_TO_TOP_LEFT + frame_text)
            sys.stdout.flush()

            rotation_around_x += 0.07
            rotation_around_z += 0.03
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        # Always bring the cursor back, even after Ctrl+C
        sys.stdout.write(SHOW_CURSOR + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
