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

import inkex
from random import shuffle


class BingoCardCreator(inkex.GenerateExtension):
    def add_arguments(self, pars):
        pars.add_argument("--rows", type=int, default=5, dest="rows")
        pars.add_argument("--columns", type=int, default=5, dest="columns")
        pars.add_argument("--row_range", type=int, default=15, dest="row_range")
        pars.add_argument("--card_header", type=str, default="BINGO", dest="card_header")

    def generate(self):
        self.card_header = self.options.card_header
        self.columns = self.options.columns
        self.row_range = self.options.row_range
        self.rows = self.options.rows
        # if row_range is smaller than the rows, reduce rows to row_range
        if self.row_range < self.rows:
            self.rows = self.row_range

        numbers = self._get_numbers()
        group = inkex.Group.new("Bingo Grid")

        x = 0
        y_start = 0

        # if the headline has a different length from "columns" do not try to put it in line
        if self.columns != len(self.card_header):
            group.insert(0, inkex.TextElement(self.card_header))
            y_start = 20

        # insert numbers as a grid
        for n in numbers:
            y = y_start
            for i in n:
                element = inkex.TextElement(str(i))
                element.set('x', x)
                element.set('y', y)
                group.insert(0, element)
                y += 20
            x += 20
        yield group

        # set a label to the automatically generated group
        group.getparent().set("inkscape:label", "Bingo")

    def _get_numbers(self):
        numbers = []
        for i in range(self.columns):
            num_start = (i * self.row_range) + 1
            num_end = ((i + 1) * self.row_range) + 1
            num_range = list(range(num_start, num_end))
            shuffle(num_range)
            num_range = num_range[:self.rows]
            if self.columns == len(self.card_header):
                num_range.insert(0, self.card_header[i])
            numbers.append(num_range)
        return numbers


if __name__ == '__main__':
    BingoCardCreator().run()
