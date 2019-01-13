'''
Text PangoMongo: Draw text with Pango, Mongo style
'''

__all__ = ('LabelPangoMongo', )

from PIL import Image, ImageFont, ImageDraw

import cairo
import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango
from gi.repository import PangoCairo
from kivy.compat import text_type
from kivy.core.text import LabelBase
from kivy.core.image import ImageData


class LabelPangoMongo(LabelBase):
    _cache = {}

    def _select_font(self):
        fontsize = int(self.options['font_size'])
        fontname = self.options['font_name_r']
        try:
            id = '%s %s' % (text_type(fontname), text_type(fontsize))
        except UnicodeDecodeError:
            id = '%s %s' % (fontname, fontsize)

        if id not in self._cache:
            font = Pango.FontDescription(id)

            self._cache[id] = font

        return self._cache[id]

    def get_extents(self, text):
        font = self._select_font()

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0) # don't  need the surface, just the context
        c_context = cairo.Context(surface)
        c_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

        layout = PangoCairo.create_layout(c_context)
        layout.set_font_description(font)
        layout.set_text(text, -1)
        PangoCairo.update_layout(c_context, layout)

        extents = layout.get_pixel_extents()
        logical = extents[1]
        size = logical.width - logical.x, logical.height - logical.y
        return size

    def _render_begin(self):
        # create a surface, context, font...
        self.c_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self._size)
        self.c_context = cairo.Context(self.c_surface)
        self.c_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        self.layout = PangoCairo.create_layout(self.c_context)

    def _render_text(self, text, x, y):
        self.layout.set_font_description(self._select_font())
        self.c_context.set_source_rgba(*self.options['color'])
        self.c_context.translate(x, y)
        self.layout.set_text(text, -1)
        PangoCairo.update_layout(self.c_context, self.layout)
        PangoCairo.show_layout(self.c_context, self.layout)
        self.c_context.translate(-x, -y)


    def _render_end(self):
        c_data = cairo.ImageSurface.get_data(self.c_surface)
        data = ImageData(self._size[0], self._size[1],
                         'bgra', c_data)

        del self.layout
        del self.c_context
        del self.c_surface

        return data
