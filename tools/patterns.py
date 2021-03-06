#!/usr/bin/env python3
import logging

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from json import dumps as json_dumps, load as json_load
from random import seed as random_seed, random as random_random, uniform as random_uniform, choice as random_choice
from math import tau, pi, cos as mcos, sin as msin, pow as mpow, sqrt as msqrt, floor as mfloor
from os.path import join as path_join
from os import makedirs as os_makedirs

# Requires module "cairocffi"
# PYPI: https://pypi.python.org/pypi/cairocffi
# DOCS: http://cairocffi.readthedocs.io/en/latest/
# Install with: pip3 install cairocffi
import cairocffi as cairo

# INFO:
# * Arc is clockwise from horizonal

LOG = logging.getLogger(__name__)

REGISTERED_FUNCTIONS = {}
def register(func):
    REGISTERED_FUNCTIONS[func.__name__] = func
    return func

# TODO:
# * https://en.wikipedia.org/wiki/Ammann%E2%80%93Beenker_tiling
# * https://en.wikipedia.org/wiki/Anisohedral_tiling
# * https://en.wikipedia.org/wiki/Aperiodic_set_of_prototiles
# * https://en.wikipedia.org/wiki/Aperiodic_tiling
# * https://en.wikipedia.org/wiki/Conway_criterion
# * https://en.wikipedia.org/wiki/Girih_tiles
# * https://en.wikipedia.org/wiki/List_of_aperiodic_sets_of_tiles#List
# * https://en.wikipedia.org/wiki/List_of_isotoxal_polyhedra_and_tilings
# * https://en.wikipedia.org/wiki/Pentagonal_tiling
# * https://en.wikipedia.org/wiki/Rep-tile
# * https://en.wikipedia.org/wiki/Self-tiling_tile_set
# * https://en.wikipedia.org/wiki/Wang_tile

def frange(start, end, step):
    if start < end:
        while start < end:
            yield start
            start += step
    elif start > end:
        while start > end:
            yield start
            start += step

def polar_to_xy(radius, angle):
    return radius * mcos(angle), radius * msin(angle)

def _draw_centre_gradient(draw):
    radial_gradient = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    radial_gradient.add_color_stop_rgb(0, 1, 1, 1)
    radial_gradient.add_color_stop_rgb(1, 0, 0, 0)
    draw.set_source(radial_gradient)
    draw.rectangle(-1, -1, 2, 2)
    draw.fill()

def _draw_centre_discrete(draw, steps=10):
    for r in frange(1, 0, -1.0 / steps):
        draw.arc(0, 0, r, 0, tau)
        grey = 1 - r
        draw.set_source_rgb(grey, grey, grey)
        draw.fill()

#######################################################################################################################

@register
def archimedean_spiral(draw, anti_clockwise=False, radial=True, loops=5, line_width=0.05, iterations=10000):
    max_angle = loops * tau
    step_angle = max_angle / iterations

    # Adjust the amplitude so that a thick line doesn't clip
    a = (1.0 - (line_width / 2.0)) / max_angle
    if anti_clockwise:
        a = -a

    draw.move_to(0, 0)
    for angle in frange(0, max_angle, step_angle):
        r = a * angle
        x = r * mcos(angle)
        y = r * msin(angle)
        draw.line_to(x, y)

    if radial:
        radial_gradient = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
        radial_gradient.add_color_stop_rgb(0, 1, 1, 1)
        radial_gradient.add_color_stop_rgb(1, 0, 0, 0)
        draw.set_source(radial_gradient)
    else:
        draw.set_source_rgb(1, 1, 1)
    draw.set_line_width(line_width)
    draw.set_line_cap(cairo.LINE_CAP_ROUND)
    draw.stroke()

@register
def archimedean_double_spiral(draw, **kwargs):
    archimedean_spiral(draw, **kwargs)
    archimedean_spiral(draw, anti_clockwise=True, **kwargs)

@register
def theodorean_spiral(draw, resolution=0.1, number=111):
    # https://en.wikipedia.org/wiki/Spiral_of_Theodorus
    triangles = [(resolution, 0, resolution, resolution)]
    for _ in range(1, number):
        lx, ly = triangles[-1][2], triangles[-1][3]
        nx, ny = -ly, lx
        l = msqrt(nx * nx + ny * ny)
        triangles.append((lx, ly, lx + resolution * (nx / l), ly + resolution * (ny / l)))

    grey = 1.0 / number
    for ax, ay, bx, by in reversed(triangles):
        draw.move_to(0, 0)
        draw.line_to(ax, ay)
        draw.line_to(bx, by)
        draw.line_to(0, 0)
        draw.set_source_rgb(grey, grey, grey)
        draw.fill()
        grey += 1.0 / number

@register
def triple_spiral():
    # https://en.wikipedia.org/wiki/Triple_spiral
    pass

@register
def borjgalo():
    # https://en.wikipedia.org/wiki/Borjgali
    pass

@register
def radials(draw, spokes=16, line_width=0.05, truncate=0):
    _draw_centre_gradient(draw)
    radius = 1.0 - line_width
    for angle in frange(0, tau, tau / spokes):
        x_vec = mcos(angle)
        y_vec = msin(angle)
        draw.move_to(truncate * x_vec, truncate * y_vec)
        draw.line_to(radius * x_vec, radius * y_vec)

    draw.set_source_rgb(0, 0, 0)
    draw.set_line_width(line_width)
    draw.set_line_cap(cairo.LINE_CAP_SQUARE)
    draw.stroke()

@register
def random_spots(draw, iterations=1000, max_size=0.1, min_size=0.01, random=True):
    bubbles = []
    while len(bubbles) < iterations:
        x1, y1, r1 = random_uniform(-1, 1), random_uniform(-1, 1), random_uniform(min_size, max_size)
        for x2, y2, r2 in bubbles:
            if msqrt(mpow((x2 - x1), 2) + mpow((y2 - y1), 2)) < (r1 + r2):
                # Intersection
                break
        else:
            bubbles.append((x1, y1, r1))

    for x, y, r in bubbles:
        draw.arc(x, y, r, 0, tau)
        if random:
            grey = random_random()
        else:
            grey = 1.0 - (r / (max_size - min_size))
        draw.set_source_rgb(grey, grey, grey)
        draw.fill()

@register
def truchet_triangles(draw, resolution=0.1):
    # https://en.wikipedia.org/wiki/Truchet_tiles
    orientations = [1, 2, 3, 4]
    r = resolution
    for x in frange(-1, 1, r):
        for y in frange(-1, 1, r):
            selection = random_choice(orientations)
            if selection == 1:
                draw.move_to(x, y)
                draw.line_to(x, y + r)
                draw.line_to(x + r, y)
                draw.line_to(x, y)
            elif selection == 2:
                draw.move_to(x + r, y)
                draw.line_to(x + r, y + r)
                draw.line_to(x, y)
                draw.line_to(x + r, y)
            elif selection == 3:
                draw.move_to(x + r, y + r)
                draw.line_to(x, y + r)
                draw.line_to(x + r, y)
                draw.line_to(x + r, y + r)
            elif selection == 4:
                draw.move_to(x, y + r)
                draw.line_to(x, y)
                draw.line_to(x + r, y + r)
                draw.line_to(x, y + r)
    draw.set_source_rgb(1, 1, 1)
    draw.fill()

@register
def truchet_quarter_cirlces(draw, resolution=0.1, line_width=0.025):
    # https://en.wikipedia.org/wiki/Truchet_tiles
    orientations = [1, 2]
    r = resolution / 2.0
    for x in frange(-1, 1, resolution):
        for y in frange(-1, 1, resolution):
            selection = random_choice(orientations)
            if selection == 1:
                draw.new_sub_path()
                draw.arc(x, y, r, 0, pi / 2.0)
                draw.new_sub_path()
                draw.arc(x + resolution, y + resolution, r, pi, pi * 3.0 / 2.0)
            elif selection == 2:
                draw.new_sub_path()
                draw.arc(x + resolution, y, r, pi / 2.0, pi)
                draw.new_sub_path()
                draw.arc(x, y + resolution, r, pi * 3.0 / 2.0, tau)
    draw.set_source_rgb(1, 1, 1)
    draw.set_line_width(line_width)
    draw.stroke()

@register
def truchet_diagonals(draw, resolution=0.1, line_width=0.05):
    # https://en.wikipedia.org/wiki/Truchet_tiles
    orientations = [1, 2]
    r = resolution
    for x in frange(-1, 1, r):
        for y in frange(-1, 1, r):
            selection = random_choice(orientations)
            if selection == 1:
                draw.move_to(x, y)
                draw.line_to(x + r, y + r)
            elif selection == 2:
                draw.move_to(x + r, y)
                draw.line_to(x, y + r)
    draw.set_source_rgb(1, 1, 1)
    draw.set_line_width(line_width)
    draw.set_line_cap(cairo.LINE_CAP_ROUND)
    draw.stroke()

@register
def truchet_variation(draw, resolution=0.1, line_width=0.015):
    # https://en.wikipedia.org/wiki/Truchet_tiles
    orientations = [1, 2, 3, 4, 5, 6, 7]
    r = resolution / 2.0
    for x in frange(-1, 1, resolution):
        for y in frange(-1, 1, resolution):
            selection = random_choice(orientations)
            if selection == 1:
                draw.new_sub_path()
                draw.arc(x, y, r, 0, pi / 2.0)
                draw.new_sub_path()
                draw.arc(x + resolution, y + resolution, r, pi, pi * 3.0 / 2.0)
            elif selection == 2:
                draw.new_sub_path()
                draw.arc(x, y, r, 0, pi / 2.0)
                draw.move_to(x + r, y + resolution)
                draw.line_to(x + r, y + r)
                draw.line_to(x + resolution, y + r)
            elif selection == 3:
                draw.new_sub_path()
                draw.arc(x + resolution, y + resolution, r, pi, pi * 3.0 / 2.0)
                draw.move_to(x + r, y)
                draw.line_to(x + r, y + r)
                draw.line_to(x, y + r)
            elif selection == 4:
                draw.new_sub_path()
                draw.arc(x + resolution, y, r, pi / 2.0, pi)
                draw.new_sub_path()
                draw.arc(x, y + resolution, r, pi * 3.0 / 2.0, tau)
            elif selection == 5:
                draw.new_sub_path()
                draw.arc(x + resolution, y, r, pi / 2.0, pi)
                draw.move_to(x, y + r)
                draw.line_to(x + r, y + r)
                draw.line_to(x + r, y + resolution)
            elif selection == 6:
                draw.new_sub_path()
                draw.arc(x, y + resolution, r, pi * 3.0 / 2.0, tau)
                draw.move_to(x + r, y)
                draw.line_to(x + r, y + r)
                draw.line_to(x + resolution, y + r)
            elif selection == 7:
                draw.move_to(x + r, y)
                draw.line_to(x + r, y + resolution)
                draw.move_to(x, y + r)
                draw.line_to(x + resolution, y + r)
    draw.set_source_rgb(1, 1, 1)
    draw.set_line_width(line_width)
    draw.set_line_join(cairo.LINE_JOIN_BEVEL)
    draw.stroke()

@register
def truchet_12_variation(draw, resolution=0.1, line_width=0.025):
    # https://en.wikipedia.org/wiki/Truchet_tiles
    orientations = [1, 2]
    shapes = [1, 2, 3]
    r = resolution / 2.0
    for x in frange(-1, 1, resolution):
        for y in frange(-1, 1, resolution):
            selection = random_choice(orientations)
            if selection == 1:
                # Top left
                shape = random_choice(shapes)
                if shape == 1:
                    draw.new_sub_path()
                    draw.arc(x, y, r, 0, pi / 2.0)
                elif shape == 2:
                    draw.move_to(x + r, y)
                    draw.line_to(x, y + r)
                elif shape == 3:
                    draw.move_to(x + r, y)
                    draw.line_to(x + r, y + r)
                    draw.line_to(x, y + r)

                # Bottom right
                shape = random_choice(shapes)
                if shape == 1:
                    draw.new_sub_path()
                    draw.arc(x + resolution, y + resolution, r, pi, pi * 3.0 / 2.0)
                elif shape == 2:
                    draw.move_to(x + r, y + resolution)
                    draw.line_to(x + resolution, y + r)
                elif shape == 3:
                    draw.move_to(x + r, y + resolution)
                    draw.line_to(x + r, y + r)
                    draw.line_to(x + resolution, y + r)

            elif selection == 2:
                # Top right
                shape = random_choice(shapes)
                if shape == 1:
                    draw.new_sub_path()
                    draw.arc(x + resolution, y, r, pi / 2.0, pi)
                elif shape == 2:
                    draw.move_to(x + r, y)
                    draw.line_to(x + resolution, y + r)
                elif shape == 3:
                    draw.move_to(x + r, y)
                    draw.line_to(x + r, y + r)
                    draw.line_to(x + resolution, y + r)

                # Bottom left
                shape = random_choice(shapes)
                if shape == 1:
                    draw.new_sub_path()
                    draw.arc(x, y + resolution, r, pi * 3.0 / 2.0, tau)
                elif shape == 2:
                    draw.move_to(x, y + r)
                    draw.line_to(x + r, y + resolution)
                elif shape == 3:
                    draw.move_to(x, y + r)
                    draw.line_to(x + r, y + r)
                    draw.line_to(x + r, y + resolution)

    draw.set_source_rgb(1, 1, 1)
    draw.set_line_width(line_width)
    draw.set_line_join(cairo.LINE_JOIN_BEVEL)
    draw.set_line_cap(cairo.LINE_CAP_ROUND)
    draw.stroke()

@register
def truchet_diagonal_strips(draw, resolution=0.1, line_width=0.01):
    # https://en.wikipedia.org/wiki/Truchet_tiles
    orientations = [1, 2]
    r = resolution
    for x in frange(-1, 1, r):
        for y in frange(-1, 1, r):
            selection = random_choice(orientations)
            if selection == 1:
                for s in frange(line_width, resolution, 2.0 * line_width):
                    draw.move_to(x + s, y)
                    draw.line_to(x, y + s)
                    draw.move_to(x + resolution - s, y + resolution)
                    draw.line_to(x + resolution, y + resolution - s)
            elif selection == 2:
                for s in frange(line_width, resolution, 2.0 * line_width):
                    draw.move_to(x + s, y)
                    draw.line_to(x + resolution, y + resolution - s)
                    draw.move_to(x, y + s)
                    draw.line_to(x + resolution - s, y + resolution)
    draw.set_source_rgb(1, 1, 1)
    draw.set_line_width(line_width)
    draw.set_line_cap(cairo.LINE_CAP_ROUND)
    draw.stroke()

@register
def ring_blocks(draw, radial=False, rings=10, ring_depth_rate=0.85, inner_radius=0.4, block_max_width=0.05):
    ring_depth = (1.0 - inner_radius) / rings
    block_depth = ring_depth * ring_depth_rate

    for radius in frange(inner_radius, 1.0, ring_depth):
        circumference = tau * radius
        block_per_ring = mfloor(circumference / block_max_width)
        angle_per_block = (tau / block_per_ring) * 0.8

        for angle in frange(0, tau, tau / block_per_ring):
            draw.move_to(*polar_to_xy(radius, angle))
            draw.line_to(*polar_to_xy(radius + block_depth, angle))
            draw.line_to(*polar_to_xy(radius + block_depth, angle + angle_per_block))
            draw.line_to(*polar_to_xy(radius, angle + angle_per_block))
            draw.line_to(*polar_to_xy(radius, angle))

    if radial:
        radial_gradient = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
        radial_gradient.add_color_stop_rgb(0, 1, 1, 1)
        radial_gradient.add_color_stop_rgb(1, 0, 0, 0)
        draw.set_source(radial_gradient)
    else:
        draw.set_source_rgb(1, 1, 1)
    draw.fill()

@register
def archimedean_blocks(draw, radial=False, loops=12, ring_depth_rate=0.6, inner_radius=0.25,
                       block_max_width=0.03, block_min_width=0.005, blocks_per_run=30):

    ring_depth = (1.0 - inner_radius) / (loops + 1)
    amplitude = ring_depth / tau
    block_depth = ring_depth * ring_depth_rate

    angle = 0.0
    block_run_counter = 0
    while angle < loops * tau:
        # Take current radius to determine the additional block angle
        radius = inner_radius + amplitude * angle
        circumference = tau * radius
        # How many blocks fit into a ring at the current radius?
        max_angle_step = tau / (circumference / block_max_width)
        min_angle_step = tau / (circumference / block_min_width)
        angle_block = (max_angle_step - (max_angle_step - min_angle_step) * \
            (block_run_counter % blocks_per_run / blocks_per_run)) * 0.9

        draw.move_to(*polar_to_xy(radius, angle))
        draw.line_to(*polar_to_xy(radius + block_depth, angle))
        draw.line_to(*polar_to_xy(radius + block_depth, angle + angle_block))
        draw.line_to(*polar_to_xy(radius, angle + angle_block))
        draw.line_to(*polar_to_xy(radius, angle))

        angle += max_angle_step
        block_run_counter += 1

    if radial:
        radial_gradient = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
        radial_gradient.add_color_stop_rgb(0, 1, 1, 1)
        radial_gradient.add_color_stop_rgb(1, 0, 0, 0)
        draw.set_source(radial_gradient)
    else:
        draw.set_source_rgb(1, 1, 1)
    draw.fill()

@register
def ring_wedges(draw, radial=False, rings=10, ring_depth_rate=0.85, inner_radius=0.4, block_max_width=0.05,
                point_in=True, alternate=False):
    ring_depth = (1.0 - inner_radius) / rings
    block_depth = ring_depth * ring_depth_rate

    for radius in frange(inner_radius, 1.0, ring_depth):
        circumference = tau * radius
        block_per_ring = mfloor(circumference / block_max_width)
        angle_per_block = (tau / block_per_ring) * 0.8

        if alternate:
            for angle in frange(0, tau, tau / block_per_ring):
                width_angle = angle_per_block * 0.8
                draw.move_to(*polar_to_xy(radius, angle + (width_angle * 0.5)))
                draw.line_to(*polar_to_xy(radius + block_depth, angle))
                draw.line_to(*polar_to_xy(radius + block_depth, angle + width_angle))
                draw.line_to(*polar_to_xy(radius, angle + (width_angle * 0.5)))

                angle += (angle_per_block - width_angle) + (width_angle * 0.5)
                draw.move_to(*polar_to_xy(radius, angle))
                draw.line_to(*polar_to_xy(radius + block_depth, angle + (width_angle * 0.5)))
                draw.line_to(*polar_to_xy(radius, angle + width_angle))
                draw.line_to(*polar_to_xy(radius, angle))
        else:
            for angle in frange(0, tau, tau / block_per_ring):
                if point_in:
                    draw.move_to(*polar_to_xy(radius, angle + (angle_per_block * 0.5)))
                    draw.line_to(*polar_to_xy(radius + block_depth, angle))
                    draw.line_to(*polar_to_xy(radius + block_depth, angle + angle_per_block))
                    draw.line_to(*polar_to_xy(radius, angle + (angle_per_block * 0.5)))
                else:
                    draw.move_to(*polar_to_xy(radius, angle))
                    draw.line_to(*polar_to_xy(radius + block_depth, angle + (angle_per_block * 0.5)))
                    draw.line_to(*polar_to_xy(radius, angle + angle_per_block))
                    draw.line_to(*polar_to_xy(radius, angle))

    if radial:
        radial_gradient = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
        radial_gradient.add_color_stop_rgb(0, 1, 1, 1)
        radial_gradient.add_color_stop_rgb(1, 0, 0, 0)
        draw.set_source(radial_gradient)
    else:
        draw.set_source_rgb(1, 1, 1)
    draw.fill()

@register
def triangle(draw, iterations=50000, radius=0.002, proportion=0.5):
    points = [(0, -0.9), (0.9, 0.9), (-0.9, 0.9)]
    last = (random_random(), random_random())
    draw.set_source_rgb(1, 1, 1)
    for _ in range(iterations):
        direction = random_choice(points)
        last = ((direction[0] + last[0]) * proportion, (direction[1] + last[1]) * proportion)
        draw.arc(last[0], last[1], radius, 0, tau)
        draw.fill()

@register
def fern(draw, iterations=5000000, radius=0.002, proportion=0.5):
    last = (0.0, 0.0)
    draw.set_source_rgb(1, 1, 1)
    for _ in range(iterations):
        p = random_random()
        if p < 0.01:
            last = (0.0, 0.16 * last[1])
        elif p < 0.86:
            last = (0.85 * last[0] + 0.04 * last[1], -0.04 * last[0] + 0.85 * last[1] + 1.6)
        elif p < 0.93:
            last = (0.2 * last[0] - 0.26 * last[1], 0.23 * last[0] + 0.22 * last[1] + 1.6)
        else:
            last = (-0.15 * last[0] + 0.28 * last[1], 0.26 * last[0] + 0.24 * last[1] + 0.44)
        draw.arc(last[0], last[1], radius, 0, tau)
        draw.fill()

#######################################################################################################################

def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('config', help='Configuration JSON')
    parser.add_argument('--path', help='Output path')
    parser.add_argument('--seed', default='Boundless', help='Generation seed')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(format='%(message)s', level=level)
    LOG.debug('# %s', str(args))

    return args

def main():
    args = parse_args()

    with open(args.config) as f:
        configs = json_load(f)

    filenames = []
    for n, config in enumerate(configs):
        width, height = 1000, 1000
        image = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        draw = cairo.Context(image)

        # Black background by default
        draw.rectangle(0, 0, width, height)
        draw.set_source_rgb(0, 0, 0)
        draw.fill()

        # Translate the context into [-1,1]x[-1,1]
        draw.translate(width / 2.0, height / 2.0)
        draw.scale(min(width, height) / 2.0, min(width, height) / 2.0)

        random_seed(args.seed)
        fn_name = config.pop('_fn')
        REGISTERED_FUNCTIONS[fn_name](draw, **config)

        if args.debug:
            # Draw a red grid with resolution 0.1
            for offset in frange(-1, 1, 0.1):
                draw.move_to(-1, offset)
                draw.line_to(1, offset)
                draw.move_to(offset, -1)
                draw.line_to(offset, 1)
            draw.set_line_width(0.002)
            draw.set_source_rgb(1, 0, 0)
            draw.stroke()

            # Draw a blue radial grid
            for angle in frange(0, tau, tau / 32.0):
                draw.move_to(*polar_to_xy(0.1, angle))
                draw.line_to(*polar_to_xy(1.0, angle))
            draw.set_source_rgb(0, 0, 1)
            draw.stroke()

        filename = '{:03}.{}.png'.format(n, fn_name)
        if args.path:
            os_makedirs(args.path, exist_ok=True)
            filename = path_join(args.path, filename)

        image.flush()
        image.write_to_png(filename)
        filenames.append(filename)
        LOG.debug('# %s', filename)

    return {
        'dimensions': [width, height],
        'outputs': filenames
    }

if __name__ == '__main__':
    RESULT = main()
    print(json_dumps(RESULT, sort_keys=True, indent=2))
