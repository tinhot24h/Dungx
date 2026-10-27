import json
import math
import struct
import unittest
import zlib
from design import artwork, layout, settings


def pixels(png):
    offset, data = 8, b''
    while offset < len(png):
        size = struct.unpack('!I', png[offset:offset+4])[0]
        kind = png[offset+4:offset+8]
        if kind == b'IDAT':
            data += png[offset+8:offset+8+size]
        offset += size+12
    raw = zlib.decompress(data)
    return lambda x, y: tuple(raw[y*(720*4+1)+1+x*4:y*(720*4+1)+5+x*4])


class DesignTests(unittest.TestCase):
    def options(self, **changes):
        return settings(dict(template='blue', color='#20375d', title='Tiêu đề',
                             body='Nội dung', cta='', **changes))

    def test_transparent_to_opaque_without_hard_edge(self):
        sample = pixels(artwork(self.options()))
        self.assertEqual(sample(360, 500)[3], 0)
        self.assertTrue(70 < sample(360, 680)[3] < 210)
        self.assertEqual(sample(360, 850)[3], 255)
        alphas = [sample(360, y)[3] for y in range(550, 800)]
        self.assertEqual(alphas, sorted(alphas))
        self.assertLessEqual(max(b-a for a, b in zip(alphas, alphas[1:])), 3)

    def test_card_motion_does_not_move_gradient(self):
        first = self.options(card_y=58)
        second = self.options(card_y=70)
        first['template'] = second['template'] = 'pink'
        p, q = pixels(artwork(first)), pixels(artwork(second))
        for y in range(550, 740, 20):
            self.assertEqual(p(360,y), q(360,y))
        self.assertNotEqual(p(360,800), q(360,800))

    def test_text_stays_on_canvas_at_extremes(self):
        for template in ('pink', 'blue'):
            for y in (58, 70):
                opts = self.options(card_y=y)
                opts['template'] = template
                for item in layout(opts):
                    self.assertLess(item['y'] + len(item['text'].splitlines())*(item['size']+3),1280)

    def test_untrusted_numeric_options_rejected(self):
        for value in (-1,101,True,'50',math.inf,math.nan):
            with self.assertRaises(ValueError):
                self.options(opacity=value)


if __name__ == '__main__':
    unittest.main()
