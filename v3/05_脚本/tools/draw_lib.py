from PIL import Image, ImageDraw, ImageFont
import math

FONT_PATH = '/System/Library/Fonts/Hiragino Sans GB.ttc'

def font(size, bold=False):
    return ImageFont.truetype(FONT_PATH, size, index=(1 if bold else 0))

class Sheet:
    """Technical drawing canvas. Coordinates in mm; origin given per view."""
    def __init__(self, wmm, hmm, ppm=4, ss=2, bg='#F6F8FA'):
        self.ppm = ppm * ss
        self.ss = ss
        self.W = int(wmm * self.ppm)
        self.H = int(hmm * self.ppm)
        self.im = Image.new('RGB', (self.W, self.H), bg)
        self.d = ImageDraw.Draw(self.im, 'RGBA')
        self.ox = self.oy = 0.0
        self.bg = bg

    # coordinate helpers
    def px(self, x): return (x + self.ox) * self.ppm
    def py(self, y): return (y + self.oy) * self.ppm
    def pts(self, ps): return [(self.px(x), self.py(y)) for x, y in ps]

    def origin(self, x, y):
        self.ox, self.oy = x, y

    def rrect(self, x, y, w, h, r, fill=None, outline=None, width=1.0):
        p = self.ppm
        self.d.rounded_rectangle([self.px(x), self.py(y), self.px(x+w), self.py(y+h)],
                                 radius=r*p, fill=fill, outline=outline, width=int(width*p))

    def rect(self, x, y, w, h, fill=None, outline=None, width=1.0):
        p = self.ppm
        self.d.rectangle([self.px(x), self.py(y), self.px(x+w), self.py(y+h)],
                         fill=fill, outline=outline, width=int(width*p))

    def line(self, ps, fill='#2A3342', width=1.0, dash=None):
        p = self.ppm
        pts = self.pts(ps)
        if not dash:
            self.d.line(pts, fill=fill, width=int(width*p), joint='curve')
            return
        # dash in mm
        on, off = dash
        for (x1,y1),(x2,y2) in zip(pts[:-1], pts[1:]):
            dx, dy = x2-x1, y2-y1
            L = math.hypot(dx,dy)
            if L == 0: continue
            ux, uy = dx/L, dy/L
            t = 0
            while t < L:
                e = min(t + on*p, L)
                self.d.line([(x1+ux*t, y1+uy*t), (x1+ux*e, y1+uy*e)], fill=fill, width=int(width*p))
                t = e + off*p

    def dashdot(self, ps, fill='#8A94A6', width=0.6):
        p = self.ppm
        pts = self.pts(ps)
        for (x1,y1),(x2,y2) in zip(pts[:-1], pts[1:]):
            dx, dy = x2-x1, y2-y1
            L = math.hypot(dx,dy); ux, uy = dx/L, dy/L
            t = 0; k = 0
            while t < L:
                on = (8 if k % 2 == 0 else 2) * p
                e = min(t+on, L)
                self.d.line([(x1+ux*t, y1+uy*t), (x1+ux*e, y1+uy*e)], fill=fill, width=int(width*p))
                t = e + 3*p; k += 1

    def circle(self, cx, cy, r, fill=None, outline=None, width=1.0):
        p = self.ppm
        self.d.ellipse([self.px(cx-r), self.py(cy-r), self.px(cx+r), self.py(cy+r)],
                       fill=fill, outline=outline, width=int(width*p))

    def text(self, x, y, s, size=9, fill='#1F2937', anchor='la', bold=False, rot=0):
        f = font(int(size*self.ppm), bold)
        if rot == 0:
            self.d.text((self.px(x), self.py(y)), s, font=f, fill=fill, anchor=anchor)
        else:
            # draw on separate layer and rotate
            tw = int(f.getlength(s))+8; th = int(size*self.ppm)+8
            layer = Image.new('RGBA', (tw, th), (0,0,0,0))
            ld = ImageDraw.Draw(layer)
            ld.text((4, th//2), s, font=f, fill=fill, anchor='lm')
            layer = layer.rotate(rot, expand=True)
            self.im.paste(layer, (int(self.px(x)-layer.width/2), int(self.py(y)-layer.height/2)), layer)

    def arrow(self, x1, y1, x2, y2, fill='#1D6FD6', width=0.7, head=2.2):
        p = self.ppm
        self.line([(x1,y1),(x2,y2)], fill=fill, width=width)
        ang = math.atan2(y2-y1, x2-x1)
        for s in (-1, 1):
            a = ang + s*math.radians(22)
            self.line([(x2,y2),(x2 - head*math.cos(a), y2 - head*math.sin(a))], fill=fill, width=width)

    def dim_h(self, x1, x2, y, label, off=0, color='#1D6FD6', size=8, above=True):
        # horizontal dimension line with extension lines
        self.line([(x1, y), (x2, y)], fill=color, width=0.5)
        self.arrow(x1, y, x2, y, fill=color, width=0.5)
        self.arrow(x2, y, x1, y, fill=color, width=0.5)
        self.line([(x1, y-2.5), (x1, y+2.5)], fill=color, width=0.4)
        self.line([(x2, y-2.5), (x2, y+2.5)], fill=color, width=0.4)
        ty = y - size*1.15 if above else y + size*0.45
        self.text((x1+x2)/2, ty, label, size=size, fill=color, anchor='ma')

    def dim_v(self, y1, y2, x, label, color='#1D6FD6', size=8, left=True):
        self.line([(x, y1), (x, y2)], fill=color, width=0.5)
        self.arrow(x, y1, x, y2, fill=color, width=0.5)
        self.arrow(x, y2, x, y1, fill=color, width=0.5)
        self.line([(x-2.5, y1), (x+2.5, y1)], fill=color, width=0.4)
        self.line([(x-2.5, y2), (x+2.5, y2)], fill=color, width=0.4)
        if left:
            self.text(x - 2.0, (y1+y2)/2, label, size=size, fill=color, anchor='rm')
        else:
            self.text(x + 2.0, (y1+y2)/2, label, size=size, fill=color, anchor='lm')

    def leader(self, x1, y1, x2, y2, label, size=7.5, fill='#2A3342', dot=0.8, anchor='la'):
        self.line([(x1,y1),(x2,y2)], fill=fill, width=0.45)
        self.circle(x1, y1, dot, fill=fill)
        self.text(x2, y2, label, size=size, fill=fill, anchor=anchor)

    def save(self, path, out_w=None):
        im = self.im
        if out_w:
            im = im.resize((out_w, int(self.H*out_w/self.W)), Image.LANCZOS)
        im.save(path)
