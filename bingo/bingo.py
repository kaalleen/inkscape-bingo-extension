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

from random import shuffle

from inkex import (NSS, Boolean, GenerateExtension, Group, Line, TextElement,
                   Transform, Tspan, addNS, colors, errormsg)
from inkex.localization import inkex_gettext as _

INKSCAPE_LABEL = addNS('label', 'inkscape')
XLINK_HREF = addNS('href', 'xlink')


class BingoCardCreator(GenerateExtension):
    """Outputs bingo cards as a svg fragment"""

    container_layer = True

    def __init__(self, *args, **kwargs):
        GenerateExtension.__init__(self, *args, **kwargs)

        self.card_header = 'BINGO'
        self.free_center = True
        self.free_rows = 0
        self.columns = 5
        self.rows = 5
        self.num_range = 15
        self.font_size = 10.0
        self.grid_height = 20
        self.grid_width = 20
        self.header_color = colors.Color('#e01b24')
        self.num_color = colors.Color('#000000')
        self.render_grid = False
        self.stroke_width = 1
        self.free_spaces = ''

    def container_transform(self):
        return Transform(translate=(0, 0))

    def add_arguments(self, pars):
        self.arg_parser.add_argument("--tabs", type=str, default=None, dest="tabs")
        self.arg_parser.add_argument("--content", type=str, default=None, dest="content")
        self.arg_parser.add_argument("--layout", type=str, default=None, dest="layout")

        pars.add_argument("--rows", type=int, default=5, dest="rows")
        pars.add_argument("--columns", type=int, default=5, dest="columns")
        pars.add_argument("--num_range", type=int, default=15, dest="num_range")
        pars.add_argument("--card_header", type=str, default="", dest="card_header")
        pars.add_argument("--free_center", type=Boolean, default=True, dest="free_center")
        pars.add_argument("--free_rows", type=int, default=0, dest="free_rows")

        pars.add_argument("--grid_size", type=int, default=20, dest="grid_size")
        pars.add_argument("--font_size", type=float, default=10, dest="font_size")
        pars.add_argument("--header_color", type=colors.Color, default=colors.Color('#e01b24'),
                          dest="header_color")
        pars.add_argument("--num_color", type=colors.Color, default=colors.Color('#000000'),
                          dest="num_color")
        pars.add_argument("--render_grid", type=Boolean, default=True, dest="render_grid")
        pars.add_argument("--stroke_width", type=float, default=1, dest="stroke_width")

    def generate(self):
        self.card_header = self.options.card_header
        self.free_center = self.options.free_center
        self.free_rows = self.options.free_rows
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

        if self.rows < 1 or self.columns < 1:
            return
        # check if a bingo template is used
        xpath = ".//svg:rect[starts-with(@id,'bingo-area')]|\
                 .//svg:use[starts-with(@id,'bingo-area')]"
        template_bingo_fields = self.svg.xpath(xpath)
        if not template_bingo_fields:
            numbers = self._get_numbers()
            number_group = self._render_numbers(numbers)
            grid_group = self._render_grid()

            yield number_group
            yield grid_group
        else:
            for bingo_field in template_bingo_fields:
                # reset clone and bingo_group_transform
                bingo_clone = None
                bingo_group_transform = None

                if bingo_field.tag_name == "use":
                    bingo_clone = bingo_field
                    bingo_field, bingo_group_transform = self._get_clone_origin(bingo_field)
                    if bingo_field is None:
                        continue

                # template params
                # if not overwritten parameters are carried over to subsequent areas
                self._load_area_params(bingo_field)

                # set grid size
                self.grid_height = float(bingo_field.get('height')) / self.rows
                self.grid_width = float(bingo_field.get('width')) / self.columns

                # generate numbers and grid
                numbers = self._get_numbers()
                number_group = self._render_numbers(numbers)
                grid_group = self._render_grid()

                transform = self._get_transform(bingo_field, bingo_clone, bingo_group_transform)

                number_group.set('transform', transform)
                if grid_group is not None:
                    grid_group.set('transform', transform)

                yield number_group
                yield grid_group

        # set a label to the automatically generated layer
        self._set_layer_label(number_group.getparent())

    def _load_area_params(self, bingo_field):
        try:
            self.font_size = float(bingo_field.get('bingo-font-size', self.font_size))
            self.columns = int(bingo_field.get('bingo-columns', self.columns))
            self.rows = int(bingo_field.get('bingo-rows', self.rows))
            self.free_spaces = bingo_field.get('bingo-free', None)
            self.free_center = Boolean(bingo_field.get('bingo-star', str(self.free_center)))
            self.free_rows = int(bingo_field.get('bingo-free-rows', self.free_rows))
            self.render_grid = Boolean(bingo_field.get('bingo-render-grid', str(self.render_grid)))
            self.header_color = colors.Color(bingo_field.get('bingo-headline-color',
                                             self.header_color))
            self.num_color = colors.Color(bingo_field.get('bingo-color', self.num_color))
            self.num_range = int(bingo_field.get('bingo-column-range', self.num_range))
            self.card_header = bingo_field.get('bingo-headline', self.card_header)
            if self.card_header == "none":
                self.card_header = ""
        except (TypeError, ValueError, colors.ColorError):
            label = bingo_field.get(INKSCAPE_LABEL, '')
            el_id = bingo_field.get('id')
            errormsg(_(f'Please verify bingo attributes for {label}: {el_id}'))

    def _get_transform(self, bingo_field, bingo_clone, bingo_group_transform):
        # get correct positioning
        transform_x = bingo_field.get('x', 0)
        transform_y = bingo_field.get('y', 0)
        transform = Transform('')

        if bingo_group_transform is not None:
            transform = bingo_group_transform

        bingo_field_transform = transform @ Transform(translate=(transform_x, transform_y))
        transform = bingo_field.composed_transform() @ bingo_field_transform

        # clone positioning
        if bingo_clone is not None:
            transform_x = int(bingo_clone.get('x', 0))
            transform_y = int(bingo_clone.get('y', 0))

            transform = Transform(bingo_field.get('transform', '')) @ bingo_field_transform
            transform = Transform(translate=(transform_x, transform_y)) @ transform
            transform = bingo_clone.composed_transform() @ transform

        return transform

    def _set_layer_label(self, layer):
        bingo_layers = self.document.xpath(".//svg:g[starts-with(@inkscape:label, 'Bingo #')]\
                                           /@inkscape:label", namespaces=NSS)
        if bingo_layers:
            bingo_layers = [int(layer[7:]) for layer in bingo_layers]
            bingo_layers.sort(reverse=True)
            num_layer = bingo_layers[0] + 1
        else:
            num_layer = 1
        label = f'Bingo #{num_layer}'
        layer.set("inkscape:label", label)

    def _get_clone_origin(self, clone):
        # returns the origin of the clone and transform information for grouped clones
        bingo_group_transform = None
        source_id = clone.get(XLINK_HREF)[1:]
        xpath = f'.//*[@id="{source_id}"]'
        bingo_field = self.document.xpath(xpath)[0]
        if bingo_field.tag_name == "g":
            xpath = ".//svg:rect[starts-with(@id,'bingo-area')]"
            bingo_field = bingo_field.xpath(xpath)
            if not bingo_field:
                return None, None
            bingo_field = bingo_field[0]
            group_transforms = Transform('')
            for ancestor in bingo_field.iterancestors():
                group_transforms = Transform(ancestor.get('transform', '')) @ group_transforms
                if ancestor.get('id', str()) == source_id:
                    break
            bingo_group_transform = group_transforms
        if bingo_field.tag_name != "rect":
            return None, None
        return bingo_field, bingo_group_transform

    def _get_numbers(self):
        numbers = []
        for i in range(self.columns):
            num_start = i * self.num_range + 1
            num_end = (i + 1) * self.num_range + 1
            num_range = list(range(num_start, num_end))
            shuffle(num_range)
            num_range = num_range[:self.rows]

            numbers.append(num_range)

        numbers = self._apply_free_spaces(numbers)

        # insert card header
        if self.columns == len(self.card_header):
            for i in range(self.columns):
                numbers[i].insert(0, self.card_header[i])

        return numbers

    def _apply_free_spaces(self, numbers):
        # apply free spaces from template
        if self.free_spaces:
            spaces = self.free_spaces.split(';')
            for space in spaces:
                position = space.split('.')
                try:
                    numbers[int(position[0]) - 1][int(position[1]) - 1] = ""
                except (IndexError, ValueError):
                    pass

        # apply free spaces per rows
        if self.free_rows > 0:
            for i in range(self.rows):
                free = list(range(1, self.columns + 1))
                shuffle(free)
                free = free[:self.free_rows]
                for free_space in free:
                    numbers[free_space - 1][i] = ""

        # apply star at center
        if self.free_center:
            numbers[int(self.columns / 2)][int(self.rows / 2)] = "★"

        return numbers

    def _render_numbers(self, numbers):
        header_style = f'fill:{self.header_color};font-size:{self.font_size};text-anchor:middle;'
        element_style = f'fill:{self.num_color};font-size:{self.font_size};text-anchor:middle;'
        text_element = TextElement(style=element_style)

        x_start = self.grid_width / 2
        y_coord = (self.font_size / 2) - (self.grid_height / 2)
        if not self.card_header:
            y_coord += self.grid_height

        # if the headline has a different length from "columns" use headline without grid spacings
        if self.columns != len(self.card_header) and self.card_header:
            header = Tspan(self.card_header,
                           style=header_style,
                           x=str((self.columns * self.grid_width) / 2),
                           y=str(y_coord))
            text_element.insert(0, header)
            y_coord += self.grid_height

        # insert number grid
        for i in range(len(numbers[0])):
            x_coord = x_start
            for k in range(self.columns):
                text = str(numbers[k][i])
                element = Tspan(str(text), style=element_style, x=str(x_coord), y=str(y_coord))
                if not text.isdigit() and text != "★":
                    element.style = header_style
                text_element.insert(len(text_element), element)
                x_coord += self.grid_width
            y_coord += self.grid_height

        return text_element

    def _render_grid(self):
        if not self.render_grid:
            return None

        group = Group.new("Grid")
        x_coord = 0
        y_coord = 0
        rows = self.rows
        style = f'stroke:#000000;fill:none;stroke-linecap:square;stroke-width:{self.stroke_width}'

        for _i in range(self.columns + 1):
            element = Line().new((x_coord, y_coord),
                                 (x_coord, rows * self.grid_height),
                                 style=style)
            group.insert(0, element)
            x_coord += self.grid_width

        for _i in range(self.rows + 1):
            element = Line().new((0, y_coord),
                                 (self.columns * self.grid_width, y_coord),
                                 style=style)
            group.insert(0, element)
            y_coord += self.grid_height

        return group


if __name__ == '__main__':
    BingoCardCreator().run()
