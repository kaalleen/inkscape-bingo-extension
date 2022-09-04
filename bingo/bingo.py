#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2022 Kaalleen
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

"""
This extension generates bingo cards.
If used with a template open it will insert itself into the correct positions.
The template can force parameters through a rectangle with a special id starting with 'bingo-area'
"""

from math import ceil
from random import shuffle

import inkex


class BingoCardCreator(inkex.GenerateExtension):
    def add_arguments(self, pars):
        self.arg_parser.add_argument("--tabs", type=str, default=None, dest="tabs")
        self.arg_parser.add_argument("--content", type=str, default=None, dest="content")
        self.arg_parser.add_argument("--layout", type=str, default=None, dest="layout")

        pars.add_argument("--rows", type=int, default=5, dest="rows")
        pars.add_argument("--columns", type=int, default=5, dest="columns")
        pars.add_argument("--num_range", type=int, default=15, dest="num_range")
        pars.add_argument("--card_header", type=str, default="", dest="card_header")
        pars.add_argument("--free", type=inkex.Boolean, default=True, dest="free")

        pars.add_argument("--grid_size", type=int, default=20, dest="grid_size")
        pars.add_argument("--font_size", type=float, default=10, dest="font_size")
        pars.add_argument("--header_color", type=inkex.Color, default=inkex.Color('#e01b24'), dest="header_color")
        pars.add_argument("--num_color", type=inkex.Color, default=inkex.Color('#000000'), dest="num_color")
        pars.add_argument("--render_grid", type=inkex.Boolean, default=True, dest="render_grid")
        pars.add_argument("--stroke_width", type=float, default=1, dest="stroke_width")

    def generate(self):
        self.card_header = self.options.card_header
        self.free = self.options.free
        self.columns = self.options.columns
        self.num_range = self.options.num_range
        self.rows = self.options.rows
        self.font_size = self.options.font_size
        self.grid_height = self.options.grid_size
        self.grid_width = self.options.grid_size
        self.header_color = self.options.header_color
        self.num_color = self.options.num_color
        self.render_grid = self.options.render_grid
        self.stroke_width = self.options.stroke_width
        self.free_spaces = None
        # if num_range is smaller than the rows, reduce rows to num_range
        if self.num_range < self.rows:
            self.rows = self.num_range

        # check if a bingo template is used
        template_bingo_fields = self.svg.xpath(".//svg:rect[starts-with(@id,'bingo-area')]", namespaces=inkex.NSS)
        if not template_bingo_fields:
            numbers = self._get_numbers()
            number_group = self._render_numbers(numbers)
            grid_group = self._render_grid()

            yield number_group
            yield grid_group
        else:
            for bingo_field in template_bingo_fields:
                # get template params
                # params of first bingo field will also be used for the others - if not defined specifically
                self.font_size = float(bingo_field.get('bingo-font-size', self.font_size))
                self.columns = int(bingo_field.get('bingo-columns', self.columns))
                self.rows = int(bingo_field.get('bingo-rows', self.rows))
                self.free_spaces = bingo_field.get('bingo-free', None)
                self.free = inkex.Boolean(bingo_field.get('bingo-star', str(self.free)))
                self.render_grid = inkex.Boolean(bingo_field.get('bingo-render-grid', str(self.render_grid)))
                self.card_header = bingo_field.get('bingo-headline', self.card_header)
                self.header_color = inkex.Color(bingo_field.get('bingo-headline-color', self.header_color))
                self.num_color = inkex.Color(bingo_field.get('bingo-color', self.num_color))
                self.num_range = int(bingo_field.get('bingo-column-range', self.num_range))
                if self.card_header == "none":
                    self.card_header = ""

                self.grid_height = float(bingo_field.get('height')) / self.rows
                self.grid_width = float(bingo_field.get('width')) / self.columns

                numbers = self._get_numbers()
                number_group = self._render_numbers(numbers)
                grid_group = self._render_grid()

                # get correct positioning
                transform = bingo_field.composed_transform()
                transform_x = bingo_field.get('x', 0)
                transform_y = bingo_field.get('y', 0)
                transform = transform @ inkex.Transform(translate=(transform_x, transform_y))
                number_group.set('transform', transform)
                if grid_group is not None:
                    grid_group.set('transform', transform)

                yield number_group
                yield grid_group

        # set a label to the automatically generated group
        number_group.getparent().set("inkscape:label", "Bingo")

    def container_transform(self):
        return inkex.Transform(translate=(0, 0))

    def _get_numbers(self):
        numbers = []
        for i in range(self.columns):
            num_start = i * self.num_range + 1
            num_end = (i + 1) * self.num_range + 1
            num_range = list(range(num_start, num_end))
            shuffle(num_range)
            num_range = num_range[:self.rows]

            # apply free spaces
            if self.free and i == ceil(self.rows / 2) - 1:
                num_range[ceil(self.rows / 2) - 1] = "★"

            numbers.append(num_range)

        # apply free spaces from template
        if self.free_spaces:
            spaces = self.free_spaces.split(';')
            for space in spaces:
                position = space.split('.')
                try:
                    numbers[int(position[0]) - 1][int(position[1]) - 1] = ""
                except (IndexError, ValueError):
                    pass

        # insert card header
        if self.columns == len(self.card_header):
            for i in range(self.columns):
                numbers[i].insert(0, self.card_header[i])

        return numbers

    def _render_numbers(self, numbers):
        x = self.grid_width / 2
        y_start = (self.font_size / 2) - (self.grid_height / 2)
        if not self.card_header:
            y_start += self.grid_height

        header_style = "fill:%s;font-size:%s;text-anchor:middle;" % (self.header_color, self.font_size)
        element_style = "fill:%s;font-size:%s;text-anchor:middle;" % (self.num_color, self.font_size)
        text_element = inkex.TextElement(style=element_style)

        # if the headline has a different length from "columns" use headline without grid spacings
        if self.columns != len(self.card_header) and self.card_header:
            header = inkex.Tspan(self.card_header, style=header_style, x=str((self.columns * self.grid_width) / 2), y=str(y_start))
            text_element.insert(0, header)
            y_start += self.grid_height

        # insert numbers as a grid
        for n in numbers:
            y = y_start
            for i, text in enumerate(n):
                element = inkex.Tspan(str(text), style=element_style, x=str(x), y=str(y))
                # set style for header elements
                if self.columns == len(self.card_header) and i == 0:
                    element.style = header_style
                # insert into group
                text_element.insert(0, element)
                y += self.grid_height
            x += self.grid_width
        return text_element

    def _render_grid(self):
        if not self.render_grid:
            return

        group = inkex.Group.new("Grid")
        x = 0
        y = 0
        rows = self.rows
        style = "stroke:#000000;fill:none;stroke-linecap:square;stroke-width:%s" % self.stroke_width

        for i in range(self.columns + 1):
            element = inkex.Line().new((x, y), (x, rows * self.grid_height), style=style)
            group.insert(0, element)
            x += self.grid_width

        for i in range(self.rows + 1):
            element = inkex.Line().new((0, y), (self.columns * self.grid_width, y), style=style)
            group.insert(0, element)
            y += self.grid_height

        return group


if __name__ == '__main__':
    BingoCardCreator().run()
