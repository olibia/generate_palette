#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inkscape extension to generate color palettes from selected objects' color properties
"""

import os
import sys
import inkex

def log(text):
  inkex.utils.debug(text)

def abort(text):
  inkex.errormsg(_(text))
  exit()

class GeneratePalette(inkex.Effect):

  def __init__(self):
    inkex.Effect.__init__(self)

    self.arg_parser.add_argument(
      '-n', '--name',
      type=str,
      dest='name',
      help='Palette name'
    )

    self.arg_parser.add_argument(
      '-p', '--property',
      type=str,
      dest='property',
      help='Color property'
    )

    self.arg_parser.add_argument(
      '-d', '--default',
      type=inkex.Boolean,
      dest='default',
      help='Default grays'
    )

    self.arg_parser.add_argument(
      '-s', '--sort',
      type=str,
      dest='sort',
      help='Sort type'
    )

    self.arg_parser.add_argument(
      '-r', '--replace',
      type=inkex.Boolean,
      dest='replace',
      help='Replace existing'
    )

  def get_palettes_path(self):
    if sys.platform.startswith('win'):
      path = os.path.join(os.environ['APPDATA'], 'inkscape', 'palettes')
    else:
      path = os.environ.get('XDG_CONFIG_HOME', '~/.config')
      path = os.path.join(path, 'inkscape', 'palettes')

    return os.path.expanduser(path)

  def get_file_path(self):
    name = str(self.options.name).replace(' ', '-')
    return "%s/%s.gpl" % (self.palettes_path, name)

  def get_default_colors(self):
    colors = [
      "  0   0   0  Black",
      " 26  26  26  90% Gray",
      " 51  51  51  80% Gray",
      " 77  77  77  70% Gray",
      "102 102 102  60% Gray",
      "128 128 128  50% Gray",
      "153 153 153  40% Gray",
      "179 179 179  30% Gray",
      "204 204 204  20% Gray",
      "230 230 230  10% Gray",
      "236 236 236  7.5% Gray",
      "242 242 242  5% Gray",
      "249 249 249  2.5% Gray",
      "255 255 255  White"
    ]

    return colors if self.options.default else []

  def get_node_prop(self, node, property):
    attr = node.attrib.get('style')
    style = dict(inkex.Style.parse_str(attr))

    return style.get(property, 'none')

  def get_node_index(self, args):
    node = args[1]
    id = node.attrib.get('id')

    return self.options.ids.index(id)

  def get_formatted_color(self, color):
    rgb = inkex.Color(color).to_rgb()
    
    if self.options.sort == 'hsl':
      key = inkex.Color(color).to_hsl()
      key = "{:03d}{:03d}{:03d}".format(*key)
    else:      
      key = "{:03d}{:03d}{:03d}".format(*rgb)
            
    rgb = "{:3d} {:3d} {:3d}".format(*rgb)

    return "%s  %s  %s" % (key, rgb, color)

  def get_selected_colors(self):
    colors   = []
    selected = list(self.svg.selected.items())

    selected.sort(key=self.get_node_index)

    for id, node in selected:
      if self.options.property in ['fill', 'both']:
        fill = self.get_node_prop(node, 'fill')

        if fill != 'none' and fill not in colors:
          colors.append(fill)

      if self.options.property in ['stroke', 'both']:
        stroke = self.get_node_prop(node, 'stroke')

        if stroke != 'none' and stroke not in colors:
          colors.append(stroke)

    colors = list(map(self.get_formatted_color, colors))

    if self.options.sort != 'unsorted':
      colors.sort()

    return list(map(lambda x : x[11:], colors))

  def write_palette(self):
    file = open(self.file_path, 'w')

    try:
      file.write("GIMP Palette\n")
      file.write("Name: %s\n" % self.options.name)
      file.write("#\n# Generated with Inkscape Generate Palette\n#\n")

      for color in self.default_colors:
        file.write("%s\n" % color)

      for color in self.selected_colors:
        if color[:11] not in list(map(lambda x : x[:11], self.default_colors)):
          file.write("%s\n" % color)
    finally:
      file.close()

  def effect(self):
    self.palettes_path   = self.get_palettes_path()
    self.file_path       = self.get_file_path()
    self.default_colors  = self.get_default_colors()
    self.selected_colors = self.get_selected_colors()

    if not self.options.replace and os.path.exists(self.file_path):
      abort('Palette already exists!')

    if not self.options.name:
      abort('Please enter a palette name.')

    if len(self.options.ids) < 2:
      abort('Please select at least 2 objects.')

    if not len(self.selected_colors):
      abort('No colors found in selected objects!')

    self.write_palette()

if __name__ == '__main__':
  palette = GeneratePalette()
  palette.run()
