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
This extension generates bingo cards
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
        pars.add_argument("--row_range", type=int, default=15, dest="row_range")
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
        self.row_range = self.options.row_range
        self.rows = self.options.rows
        # if row_range is smaller than the rows, reduce rows to row_range
        if self.row_range < self.rows:
            self.rows = self.row_range

        self.font_size = self.options.font_size
        self.grid_size = self.options.grid_size
        self.header_color = self.options.header_color
        self.num_color = self.options.num_color
        self.render_grid = self.options.render_grid
        self.stroke_width = self.options.stroke_width

        numbers = self._get_numbers()
        number_group = self._render_numbers(numbers)
        grid_group = self._render_grid()

        yield number_group
        yield grid_group

        # set a label to the automatically generated group
        number_group.getparent().set("inkscape:label", "Bingo")

    def _get_numbers(self):
        numbers = []
        for i in range(self.columns):
            num_start = i * self.row_range + 1
            num_end = (i + 1) * self.row_range + 1
            num_range = list(range(num_start, num_end))
            shuffle(num_range)
            num_range = num_range[:self.rows]

            if self.free and i == ceil(self.rows / 2) - 1:
                num_range[ceil(self.rows / 2) - 1] = "★"

            if self.columns == len(self.card_header):
                num_range.insert(0, self.card_header[i])

            numbers.append(num_range)
        return numbers

    def _render_numbers(self, numbers):
        group = inkex.Group.new("Numbers")
        x = self.grid_size / 2
        y_start = (self.font_size / 2) - (self.grid_size / 2)
        header_style = "fill:%s;font-size:%s;text-anchor:middle;" % (self.header_color, self.font_size)

        # if the headline has a different length from "columns" use headline without grid spacings
        if self.columns != len(self.card_header) and self.card_header:
            header = inkex.TextElement(self.card_header, style=header_style, x=str((self.columns * self.grid_size) / 2), y=str(y_start))
            group.insert(0, header)
            y_start += self.grid_size

        # insert numbers as a grid
        for n in numbers:
            y = y_start
            for i, text in enumerate(n):
                # set color
                if self.columns == len(self.card_header) and i == 0:
                    color = self.header_color
                else:
                    color = self.num_color
                element_style = "fill:%s;font-size:%s;text-anchor:middle" % (color, self.font_size)

                element = inkex.TextElement(str(text), style=element_style, x=str(x), y=str(y))

                # insert into group
                group.insert(0, element)
                y += self.grid_size
            x += self.grid_size
            color = self.num_color
        return group

    def _render_grid(self):
        if not self.render_grid:
            return

        group = inkex.Group.new("Grid")
        x = 0
        y = 0
        rows = self.rows
        style = "stroke:#000000;fill:none;stroke-linecap:square;stroke-width:%s" % self.stroke_width

        if not self.card_header:
            y = -self.grid_size
            rows -= 1

        for i in range(self.columns + 1):
            element = inkex.Line().new((x, y), (x, rows * self.grid_size), style=style)
            group.insert(0, element)
            x += self.grid_size

        for i in range(self.rows + 1):
            element = inkex.Line().new((0, y), (self.columns * self.grid_size, y), style=style)
            group.insert(0, element)
            y += self.grid_size

        return group


if __name__ == '__main__':
    BingoCardCreator().run()
