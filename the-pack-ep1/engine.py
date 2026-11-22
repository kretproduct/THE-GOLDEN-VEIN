"""Flat 2D cartoon drawing engine (pycairo) for The Pack, Part 1."""
import math
import random
import cairo

W, H = 1920, 1080
FPS = 24

# ---------------------------------------------------------------- utilities

def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def lerp(a, b, t):
    return a + (b - a) * t


def seg(t, a, b):
    """0..1 progress of t through [a, b]."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def hexc(h, a=1.0):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def mix(c1, c2, t):
    c1 = hexc(c1) if isinstance(c1, str) else c1
    c2 = hexc(c2) if isinstance(c2, str) else c2
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def col(ctx, c, a=None):
    if isinstance(c, str):
        c = hexc(c)
    if a is not None:
        c = (c[0], c[1], c[2], a if len(c) < 4 else c[3] * a)
    if len(c) == 3:
        ctx.set_source_rgb(*c)
    else:
        ctx.set_source_rgba(*c)


def noise1(x, seed=0):
    """Smooth deterministic 1-D value noise in [-1, 1]."""
    i = math.floor(x)
    f = x - i

    def h(n):
        r = random.Random(n * 7919 + seed * 104729)
        return r.uniform(-1, 1)
    u = f * f * (3 - 2 * f)
    return lerp(h(i), h(i + 1), u)


_NOISE_CACHE = {}


def ridge_points(seed, x0, x1, base, amp, freq, step=24):
    key = (seed, x0, x1, base, amp, freq, step)
    if key in _NOISE_CACHE:
        return _NOISE_CACHE[key]
    pts = []
    x = x0
    while x <= x1 + step:
        n = (noise1(x * freq, seed) * 0.65 + noise1(x * freq * 2.7, seed + 9) * 0.25
             + noise1(x * freq * 7.1, seed + 3) * 0.10)
        pts.append((x, base - amp * (0.55 + 0.45 * n)))
        x += step
    _NOISE_CACHE[key] = pts
    return pts


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def ellipse(ctx, cx, cy, rx, ry):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def poly(ctx, pts, close=True):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()


def capsule(ctx, x1, y1, x2, y2, w, c):
    col(ctx, c)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()


# ---------------------------------------------------------------- palette
P = {
    'skin': '#F0C29E', 'skin_sh': '#DDA683', 'cheek': '#E98A7E',
    'hair': '#6E3B1E', 'hair_dk': '#4E2813', 'hair_hi': '#8E5129',
    'jacket': '#26221F', 'jacket_hi': '#3A3430', 'jacket_dk': '#171412',
    'pants': '#4F4A2E', 'pants_dk': '#3D3922', 'boot': '#2A211B',
    'pack': '#4A4434', 'pack_dk': '#37321F', 'strap': '#5E5741',
    'glove': '#2F2B28', 'glasses': '#1B1A1A',
    'snow': '#EEF3F7', 'snow_sh': '#C9D6E2', 'snow_dk': '#A9BACB',
    'yellow': '#F4C44E', 'red': '#E2533F', 'white': '#FFFFFF',
}


# ---------------------------------------------------------------- Range
DEFAULT_POSE = dict(
    arm_l=(0.12, 0.0), arm_r=(0.12, 0.0),    # (shoulder angle outward, elbow bend inward); 0 = hanging down, pi = straight up
    leg_l=(0.0, 0.0), leg_r=(0.0, 0.0),       # (hip angle, knee bend)
    look=0.0, look_y=0.0,                     # eye/face direction
    head_tilt=0.0, body_rot=0.0, bob=0.0,
    eyes='open', brows='neutral', mouth=0.0, mouth_shape='line',
    pack=True, blanket=False, hood=False, blink=0.0, item_r=None, item_l=None,
    gloves=True, frost=0.0, breath=None, lean=0.0,
)


def walk_pose(phase, amount=1.0, **kw):
    s = math.sin(phase)
    p = dict(DEFAULT_POSE)
    p.update(
        leg_l=(0.42 * s * amount, max(0, -s) * 0.5 * amount),
        leg_r=(-0.42 * s * amount, max(0, s) * 0.5 * amount),
        arm_l=(0.12 - 0.35 * s * amount, 0.25 * amount),
        arm_r=(0.12 + 0.35 * s * amount, 0.25 * amount),
        bob=abs(math.cos(phase)) * 6 * amount,
    )
    p.update(kw)
    return p


def pose(**kw):
    p = dict(DEFAULT_POSE)
    p.update(kw)
    return p


def _limb(ctx, sx, sy, a1, a2, l1, l2, w, c, end=None, end_r=0, end_c=None):
    ex = sx + math.sin(a1) * l1
    ey = sy + math.cos(a1) * l1
    a = a1 + a2
    hx = ex + math.sin(a) * l2
    hy = ey + math.cos(a) * l2
    col(ctx, c)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(sx, sy)
    ctx.line_to(ex, ey)
    ctx.line_to(hx, hy)
    ctx.stroke()
    if end == 'hand':
        col(ctx, end_c)
        ctx.arc(hx, hy, end_r, 0, 2 * math.pi)
        ctx.fill()
    elif end == 'boot':
        col(ctx, end_c)
        ctx.save()
        ctx.translate(hx, hy)
        ctx.rotate(-a * 0.6)
        rrect(ctx, -w * 0.62, -8, w * 1.55, 20, 9)
        ctx.fill()
        ctx.restore()
    return hx, hy


def draw_hair(ctx, hr, look):
    """Messy brown hair (after the reference portrait). Fringe stays above the glasses."""
    ox = look * hr * 0.14
    fy = -hr * 0.42  # fringe line
    # side hair / sideburns
    col(ctx, P['hair_dk'])
    for sd in (-1, 1):
        poly(ctx, [(sd * hr * 0.78 + ox * 0.3, -hr * 0.75), (sd * hr * 1.06, -hr * 0.45), (sd * hr * 1.02, -hr * 0.02),
                   (sd * hr * 0.9, -hr * 0.1), (sd * hr * 0.86, -hr * 0.4)])
        ctx.fill()
    # spikes around the crown
    spikes = [(-150, 0.55), (-128, 0.62), (-105, 0.66), (-85, 0.6), (-62, 0.66), (-40, 0.58), (-20, 0.5),
              (-170, 0.4), (-8, 0.4)]
    for i, (deg, ln) in enumerate(spikes):
        a = math.radians(deg)
        cx, cy = math.cos(a) * hr * 0.82 + ox * 0.4, math.sin(a) * hr * 0.82 - hr * 0.05
        tipx, tipy = cx + math.cos(a) * hr * ln, cy + math.sin(a) * hr * ln
        bx, by = math.cos(a + math.pi / 2) * hr * 0.26, math.sin(a + math.pi / 2) * hr * 0.26
        col(ctx, P['hair'] if i % 2 else P['hair_dk'])
        poly(ctx, [(cx + bx, cy + by), (tipx + math.sin(a) * 6, tipy), (cx - bx, cy - by)])
        ctx.fill()
    # main cap
    col(ctx, P['hair'])
    ctx.move_to(-hr * 1.02, fy + hr * 0.12)
    ctx.curve_to(-hr * 1.15, -hr * 1.25, hr * 1.15, -hr * 1.25, hr * 1.02, fy + hr * 0.12)
    # jagged fringe from right to left
    xs = [1.02, 0.78, 0.6, 0.36, 0.14, -0.1, -0.32, -0.56, -0.78, -1.02]
    for i, xx in enumerate(xs):
        yy = fy + (hr * 0.16 if i % 2 == 1 else -hr * 0.04) + (hr * 0.12 if i == 0 or i == len(xs) - 1 else 0)
        ctx.line_to(xx * hr + ox * (1 - abs(xx) * 0.5), yy)
    ctx.close_path()
    ctx.fill()
    # highlights
    col(ctx, P['hair_hi'], 0.7)
    ctx.set_line_width(hr * 0.07)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for a0 in (-0.55, -0.1, 0.4):
        ctx.move_to(hr * a0 + ox, -hr * 0.98)
        ctx.curve_to(hr * (a0 + 0.12) + ox, -hr * 0.85, hr * (a0 + 0.1) + ox, -hr * 0.7, hr * (a0 + 0.2) + ox, -hr * 0.6)
    ctx.stroke()


def draw_face(ctx, hr, p):
    look = p['look']
    ly = p['look_y']
    fx = look * hr * 0.32
    # ears
    col(ctx, P['skin_sh'])
    if look < 0.6:
        ellipse(ctx, hr * 0.98 + fx * 0.2, hr * 0.05, hr * 0.17, hr * 0.24)
        ctx.fill()
    if look > -0.6:
        ellipse(ctx, -hr * 0.98 + fx * 0.2, hr * 0.05, hr * 0.17, hr * 0.24)
        ctx.fill()
    # head
    col(ctx, P['skin'])
    ellipse(ctx, 0, 0, hr, hr * 1.02)
    ctx.fill()
    # cheeks
    col(ctx, P['cheek'], 0.45 + 0.3 * p['frost'])
    ellipse(ctx, fx - hr * 0.55, hr * 0.32, hr * 0.2, hr * 0.13)
    ctx.fill()
    ellipse(ctx, fx + hr * 0.55, hr * 0.32, hr * 0.2, hr * 0.13)
    ctx.fill()
    ey = -hr * 0.02 + ly * hr * 0.05
    ex = hr * 0.36
    er = hr * 0.22
    eyes = p['eyes']
    blink = p['blink']
    for side in (-1, 1):
        cx = fx + side * ex
        if eyes == 'closed' or blink > 0.5:
            col(ctx, '#2A1E18')
            ctx.set_line_width(hr * 0.06)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(cx - er * 0.8, ey + er * 0.1)
            ctx.curve_to(cx - er * 0.3, ey + er * 0.55, cx + er * 0.3, ey + er * 0.55, cx + er * 0.8, ey + er * 0.1)
            ctx.stroke()
        else:
            wide = 1.15 if eyes == 'wide' else 1.0
            sq = 0.55 if eyes == 'squint' else 1.0
            col(ctx, '#FFFFFF')
            ellipse(ctx, cx, ey, er * 0.95 * wide, er * 0.95 * wide * sq)
            ctx.fill()
            pr = er * (0.32 if eyes == 'wide' else 0.42)
            col(ctx, '#1A1412')
            ctx.arc(cx + look * er * 0.45, ey + ly * er * 0.4, pr, 0, 2 * math.pi)
            ctx.fill()
            if eyes == 'tired':
                col(ctx, P['skin'])
                ctx.rectangle(cx - er * 1.1, ey - er * 1.1, er * 2.2, er * 0.95)
                ctx.fill()
        # glasses rims
        col(ctx, P['glasses'])
        ctx.set_line_width(hr * 0.055)
        ctx.arc(cx, ey, er * 1.28, 0, 2 * math.pi)
        ctx.stroke()
        # frost glint
        col(ctx, '#FFFFFF', 0.35)
        ctx.set_line_width(hr * 0.04)
        ctx.arc(cx, ey, er * 1.05, math.pi * 1.1, math.pi * 1.4)
        ctx.stroke()
    col(ctx, P['glasses'])
    ctx.set_line_width(hr * 0.05)
    ctx.move_to(fx - ex + er * 1.25, ey - er * 0.2)
    ctx.curve_to(fx - er * 0.3, ey - er * 0.5, fx + er * 0.3, ey - er * 0.5, fx + ex - er * 1.25, ey - er * 0.2)
    ctx.stroke()
    # brows
    br = p['brows']
    col(ctx, P['hair_dk'])
    ctx.set_line_width(hr * 0.08)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    by = ey - er * 1.55
    for side in (-1, 1):
        cx = fx + side * ex
        if br == 'angry':      # inner end low (like the reference portrait)
            ctx.move_to(cx - side * er * 0.9, by + er * 0.35)
            ctx.line_to(cx + side * er * 0.8, by - er * 0.15)
        elif br == 'worried':  # inner end high
            ctx.move_to(cx - side * er * 0.9, by - er * 0.35)
            ctx.line_to(cx + side * er * 0.8, by + er * 0.12)
        elif br == 'raised':
            ctx.move_to(cx - er * 0.85, by - er * 0.2)
            ctx.curve_to(cx - er * 0.3, by - er * 0.6, cx + er * 0.3, by - er * 0.6, cx + er * 0.85, by - er * 0.2)
        else:
            ctx.move_to(cx - er * 0.85, by)
            ctx.line_to(cx + er * 0.85, by - er * 0.05)
        ctx.stroke()
    # nose
    col(ctx, P['skin_sh'])
    ellipse(ctx, fx + look * hr * 0.06, hr * 0.28, hr * 0.07, hr * 0.05)
    ctx.fill()
    # mouth
    mo = p['mouth']
    mx = fx + look * hr * 0.05
    my = hr * 0.55
    col(ctx, '#3B1E19')
    if mo > 0.08 or p['mouth_shape'] == 'o':
        o = max(mo, 0.35 if p['mouth_shape'] == 'o' else 0)
        ellipse(ctx, mx, my, hr * (0.1 + 0.06 * o if p['mouth_shape'] != 'o' else 0.1), hr * (0.04 + 0.14 * o))
        ctx.fill()
    else:
        ctx.set_line_width(hr * 0.055)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        if p['mouth_shape'] == 'frown':
            ctx.move_to(mx - hr * 0.12, my + hr * 0.04)
            ctx.curve_to(mx - hr * 0.04, my - hr * 0.03, mx + hr * 0.04, my - hr * 0.03, mx + hr * 0.12, my + hr * 0.04)
        elif p['mouth_shape'] == 'smile':
            ctx.move_to(mx - hr * 0.13, my - hr * 0.02)
            ctx.curve_to(mx - hr * 0.05, my + hr * 0.07, mx + hr * 0.05, my + hr * 0.07, mx + hr * 0.13, my - hr * 0.02)
        else:
            ctx.move_to(mx - hr * 0.09, my)
            ctx.line_to(mx + hr * 0.09, my)
        ctx.stroke()


def draw_range(ctx, x, y, s, p=None, t=0.0):
    """Draw Range with feet at (x, y), scale s (1.0 = ~420px tall)."""
    if p is None:
        p = DEFAULT_POSE
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.rotate(p['body_rot'])
    ctx.translate(0, -p['bob'])
    hip_y = -150
    sh_y = -262
    # shadow
    if p['body_rot'] == 0:
        col(ctx, '#000000', 0.18)
        ellipse(ctx, 0, p['bob'], 70, 12)
        ctx.fill()
    # legs
    _limb(ctx, -20, hip_y, p['leg_l'][0], -p['leg_l'][1], 76, 72, 36, P['pants_dk'], 'boot', 0, P['boot'])
    _limb(ctx, 20, hip_y, p['leg_r'][0], -p['leg_r'][1], 76, 72, 36, P['pants'], 'boot', 0, P['boot'])
    ctx.save()
    ctx.translate(0, hip_y)
    ctx.rotate(p['lean'])
    ctx.translate(0, -hip_y)
    # backpack behind torso
    if p['pack']:
        col(ctx, P['pack_dk'])
        rrect(ctx, -70, sh_y - 18, 140, 150, 26)
        ctx.fill()
        col(ctx, P['pack'])
        rrect(ctx, -64, sh_y - 52, 128, 60, 22)
        ctx.fill()
    # torso / jacket
    col(ctx, P['jacket'])
    rrect(ctx, -54, sh_y - 12, 108, 135, 30)
    ctx.fill()
    col(ctx, P['jacket_hi'])
    rrect(ctx, -54, sh_y - 12, 108, 22, 12)
    ctx.fill()
    col(ctx, P['jacket_dk'])
    ctx.set_line_width(4)
    ctx.move_to(0, sh_y + 5)
    ctx.line_to(0, sh_y + 118)
    ctx.stroke()
    # hood collar
    col(ctx, P['jacket_hi'])
    ellipse(ctx, 0, sh_y - 6, 48, 18)
    ctx.fill()
    if p['pack']:
        col(ctx, P['strap'])
        ctx.set_line_width(13)
        ctx.move_to(-36, sh_y - 8)
        ctx.line_to(-32, sh_y + 96)
        ctx.move_to(36, sh_y - 8)
        ctx.line_to(32, sh_y + 96)
        ctx.stroke()
        col(ctx, P['pack_dk'])
        ctx.rectangle(-36, sh_y + 52, 72, 8)
        ctx.fill()
    hand_c = P['glove'] if p['gloves'] else P['skin']
    # arms
    hands = []
    if p['blanket']:
        col(ctx, '#C9A54B')
        poly(ctx, [(-80, sh_y - 20), (80, sh_y - 20), (118, hip_y + 40), (-118, hip_y + 40)])
        ctx.fill()
        col(ctx, '#E9CF7A', 0.8)
        poly(ctx, [(-50, sh_y - 20), (-10, sh_y - 20), (-40, hip_y + 40), (-100, hip_y + 40)])
        ctx.fill()
        col(ctx, '#A88634')
        poly(ctx, [(30, sh_y - 20), (62, sh_y - 20), (104, hip_y + 40), (58, hip_y + 40)])
        ctx.fill()
    # head
    ctx.save()
    ctx.translate(0, sh_y - 70)
    ctx.rotate(p['head_tilt'])
    hr = 74
    if p['hood']:
        col(ctx, P['jacket_hi'])
        ellipse(ctx, 0, -8, hr * 1.22, hr * 1.2)
        ctx.fill()
    draw_face(ctx, hr, p)
    if not p['hood']:
        ctx.save()
        ctx.translate(0, -hr * 0.12)
        draw_hair(ctx, hr, p['look'])
        ctx.restore()
    else:
        col(ctx, P['hair'])
        poly(ctx, [(-hr * 0.8, -hr * 0.5), (-hr * 0.4, -hr * 0.8), (0, -hr * 0.45), (hr * 0.4, -hr * 0.8),
                   (hr * 0.8, -hr * 0.5), (hr * 0.6, -hr * 0.95), (-hr * 0.6, -hr * 0.95)])
        ctx.fill()
    if p['frost'] > 0:
        col(ctx, '#FFFFFF', 0.8 * p['frost'])
        for i in range(10):
            r = random.Random(i)
            ctx.arc(r.uniform(-hr, hr), r.uniform(-hr * 1.1, -hr * 0.6), r.uniform(2, 5), 0, 2 * math.pi)
            ctx.fill()
    ctx.restore()
    hands.append(_limb(ctx, -50, sh_y + 10, -p['arm_l'][0], p['arm_l'][1], 62, 60, 28,
                       P['jacket_dk'], 'hand', 15, hand_c))
    hands.append(_limb(ctx, 50, sh_y + 10, p['arm_r'][0], -p['arm_r'][1], 62, 60, 28, P['jacket'], 'hand', 15, hand_c))
    for item, (hx, hy) in ((p['item_l'], hands[0]), (p['item_r'], hands[1])):
        if item:
            draw_item(ctx, item, hx, hy, 1.0, t)
    ctx.restore()
    # breath cloud
    if p['breath'] is not None:
        bp = p['breath'] % 1.0
        col(ctx, '#FFFFFF', 0.5 * (1 - bp))
        bx = 40 + p['look'] * 50 + bp * 60 * (1 if p['look'] >= 0 else -1)
        ellipse(ctx, bx, sh_y - 40 - bp * 30, 18 + bp * 30, 12 + bp * 18)
        ctx.fill()
    ctx.restore()


# ---------------------------------------------------------------- items

def draw_item(ctx, name, x, y, s=1.0, t=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if name == 'map':
        flap = math.sin(t * 9) * 0.15
        col(ctx, '#E8DDBE')
        poly(ctx, [(-10, -50), (70, -60 + flap * 40), (75, 10 + flap * 30), (-8, 18)])
        ctx.fill()
        col(ctx, '#C9B98F')
        ctx.set_line_width(3)
        ctx.move_to(30, -55)
        ctx.line_to(33, 14)
        ctx.stroke()
        col(ctx, '#7FA06A')
        ellipse(ctx, 50, -20, 12, 9)
        ctx.fill()
        col(ctx, P['red'])
        ctx.set_line_width(3)
        ctx.move_to(0, -10)
        ctx.curve_to(20, -30, 40, 0, 62, -35)
        ctx.stroke()
    elif name == 'notebook':
        col(ctx, '#6B3F22')
        rrect(ctx, -26, -34, 52, 66, 6)
        ctx.fill()
        col(ctx, '#8A5631')
        ctx.rectangle(-26, -34, 9, 66)
        ctx.fill()
    elif name == 'pencil':
        col(ctx, P['yellow'])
        ctx.save()
        ctx.rotate(-0.6)
        ctx.rectangle(-4, -40, 8, 40)
        ctx.fill()
        col(ctx, '#3A2A1A')
        poly(ctx, [(-4, 0), (4, 0), (0, 10)])
        ctx.fill()
        ctx.restore()
    elif name == 'radio':
        col(ctx, '#3C4A3F')
        rrect(ctx, -26, -40, 52, 74, 8)
        ctx.fill()
        col(ctx, '#222')
        ctx.rectangle(-4, -70, 6, 32)
        ctx.fill()
        col(ctx, '#9FD39A')
        ctx.rectangle(-16, -30, 32, 16)
        ctx.fill()
        col(ctx, '#222')
        for i in range(3):
            ctx.arc(-10 + i * 10, 10, 4, 0, 2 * math.pi)
            ctx.fill()
    elif name == 'fuel':
        col(ctx, '#3E6FA8')
        rrect(ctx, -24, -44, 48, 78, 18)
        ctx.fill()
        col(ctx, '#C9CED4')
        ctx.rectangle(-9, -56, 18, 14)
        ctx.fill()
        col(ctx, '#FFFFFF', 0.8)
        ctx.rectangle(-16, -16, 32, 14)
        ctx.fill()
    elif name == 'food':
        col(ctx, '#B5703A')
        rrect(ctx, -30, -36, 60, 70, 8)
        ctx.fill()
        col(ctx, '#8E5226')
        ctx.rectangle(-30, -36, 60, 12)
        ctx.fill()
        col(ctx, '#F2E3C6')
        ellipse(ctx, 0, 4, 16, 12)
        ctx.fill()
    elif name == 'knife':
        col(ctx, '#5A3A22')
        rrect(ctx, -8, -4, 16, 40, 5)
        ctx.fill()
        col(ctx, '#D3D9DE')
        poly(ctx, [(-7, -4), (7, -4), (6, -56), (-2, -64), (-7, -50)])
        ctx.fill()
    elif name == 'firesteel':
        col(ctx, '#2D2D2D')
        rrect(ctx, -6, -46, 12, 60, 4)
        ctx.fill()
        col(ctx, P['red'])
        rrect(ctx, -9, 8, 18, 26, 6)
        ctx.fill()
    elif name == 'blanket':
        col(ctx, '#D4B054')
        poly(ctx, [(-36, -26), (30, -36), (38, 26), (-30, 34)])
        ctx.fill()
        col(ctx, '#F2DD95')
        poly(ctx, [(-20, -28), (0, -31), (-6, 31), (-24, 33)])
        ctx.fill()
    elif name == 'bars':
        for i, c in enumerate(('#C0392B', '#D35400')):
            col(ctx, c)
            rrect(ctx, -34 + i * 18, -30 + i * 10, 46, 22, 5)
            ctx.fill()
    elif name == 'bottle':
        col(ctx, '#7FB5D6', 0.6)
        rrect(ctx, -16, -44, 32, 80, 10)
        ctx.fill()
        col(ctx, '#3E8EC4')
        rrect(ctx, -16, -4, 32, 40, 10)
        ctx.fill()
        col(ctx, '#333')
        ctx.rectangle(-9, -56, 18, 14)
        ctx.fill()
    elif name == 'nest':
        col(ctx, '#7A5A36')
        ellipse(ctx, 0, 0, 34, 20)
        ctx.fill()
        col(ctx, '#5A3F24')
        ctx.set_line_width(3)
        for i in range(9):
            a = i * 0.7
            ctx.move_to(math.cos(a) * 34, math.sin(a) * 14)
            ctx.line_to(math.cos(a + 2.4) * 30, math.sin(a + 2.4) * 18)
        ctx.stroke()
        col(ctx, '#EDE6D6')
        ctx.save()
        ctx.rotate(0.6)
        ellipse(ctx, 22, -18, 12, 4)
        ctx.fill()
        ctx.restore()
    elif name == 'beacon':
        col(ctx, '#F28C28')
        rrect(ctx, -26, -40, 52, 76, 12)
        ctx.fill()
        col(ctx, '#222')
        ctx.rectangle(-16, -28, 32, 22)
        ctx.fill()
        col(ctx, '#7CFC9A')
        ctx.rectangle(-12, -24, 10, 14)
        ctx.fill()
    elif name == 'probe':
        col(ctx, '#B8C2CC')
        ctx.set_line_width(8)
        ctx.move_to(-40, 40)
        ctx.line_to(40, -40)
        ctx.stroke()
        col(ctx, P['red'])
        for i in range(4):
            ctx.arc(-30 + i * 20, 30 - i * 20, 6, 0, 2 * math.pi)
            ctx.fill()
    elif name == 'shovel':
        col(ctx, '#333')
        ctx.set_line_width(8)
        ctx.move_to(0, -50)
        ctx.line_to(0, 14)
        ctx.stroke()
        rrect(ctx, -14, -60, 28, 12, 5)
        ctx.fill()
        col(ctx, '#2F7BD8')
        poly(ctx, [(-24, 10), (24, 10), (20, 52), (0, 60), (-20, 52)])
        ctx.fill()
    elif name == 'partner':
        col(ctx, '#3F6EA8')
        rrect(ctx, -26, -10, 52, 60, 16)
        ctx.fill()
        col(ctx, P['skin'])
        ctx.arc(0, -32, 22, 0, 2 * math.pi)
        ctx.fill()
        col(ctx, '#C0392B')
        ellipse(ctx, 0, -46, 24, 12)
        ctx.fill()
    ctx.restore()


# ---------------------------------------------------------------- scenery

def sky(ctx, top, bottom, y0=0, y1=H):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgba(0, *hexc(top) if isinstance(top, str) else top)
    g.add_color_stop_rgba(1, *hexc(bottom) if isinstance(bottom, str) else bottom)
    ctx.set_source(g)
    ctx.rectangle(-W, -H, W * 3, H * 3)
    ctx.fill()


def sun(ctx, x, y, r, c='#FFE7A8', glow=0.35):
    g = cairo.RadialGradient(x, y, r * 0.5, x, y, r * 4)
    cc = hexc(c)
    g.add_color_stop_rgba(0, cc[0], cc[1], cc[2], glow)
    g.add_color_stop_rgba(1, cc[0], cc[1], cc[2], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r * 4, 0, 2 * math.pi)
    ctx.fill()
    col(ctx, c)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def mountains(ctx, seed, base, amp, c, cap=None, freq=0.004, x0=-400, x1=W + 400, offset=0.0, cap_frac=0.28,
              bottom=H * 2):
    pts = ridge_points(seed, x0, x1, base, amp, freq)
    ctx.save()
    ctx.translate(-offset, 0)
    col(ctx, c)
    ctx.move_to(x0, bottom)
    for px, py in pts:
        ctx.line_to(px, py)
    ctx.line_to(pts[-1][0], bottom)
    ctx.close_path()
    ctx.fill()
    if cap:
        # snow caps: band just under the ridge line
        col(ctx, cap)
        ctx.move_to(*pts[0])
        for px, py in pts:
            ctx.line_to(px, py)
        for px, py in reversed(pts):
            d = (base - py)
            ctx.line_to(px, py + d * cap_frac * (0.6 + 0.4 * noise1(px * 0.03, seed + 1)) + 6)
        ctx.close_path()
        ctx.fill()
    ctx.restore()


def pine(ctx, x, y, h, c='#1F3A33', c2=None, snow=0.0, sway=0.0):
    w = h * 0.42
    col(ctx, '#3A2A20')
    ctx.rectangle(x - h * 0.03, y - h * 0.1, h * 0.06, h * 0.12)
    ctx.fill()
    tiers = 4
    for i in range(tiers):
        tb = y - h * 0.08 - i * h * 0.21
        tw = w * (1 - i * 0.2)
        tt = tb - h * 0.38
        sx = sway * (i + 1) * 3
        col(ctx, c if (i % 2 == 0 or not c2) else c2)
        poly(ctx, [(x - tw + sx * 0.5, tb), (x + sx, tt), (x + tw + sx * 0.5, tb)])
        ctx.fill()
        if snow > 0:
            col(ctx, P['snow'], snow)
            poly(ctx, [(x - tw * 0.55 + sx * 0.6, tb - h * 0.12), (x + sx, tt), (x + tw * 0.55 + sx * 0.6, tb - h * 0.12),
                       (x + tw * 0.25, tb - h * 0.09), (x, tb - h * 0.14), (x - tw * 0.25, tb - h * 0.09)])
            ctx.fill()


def forest(ctx, seed, y, n, hmin, hmax, c, c2=None, snow=0.0, x0=-100, x1=W + 100, offset=0.0, sway=0.0):
    r = random.Random(seed)
    items = []
    for i in range(n):
        items.append((r.uniform(x0, x1), r.uniform(hmin, hmax), r.uniform(-8, 8)))
    items.sort(key=lambda a: a[1])
    for x, h, dy in items:
        pine(ctx, x - offset, y + dy, h, c, c2, snow, sway)


def snow_ground(ctx, y, c=None, seed=5, amp=18, offset=0.0):
    c = c or P['snow']
    pts = ridge_points(seed, -400, W + 400, y, amp, 0.003, step=30)
    ctx.save()
    ctx.translate(-offset, 0)
    col(ctx, c)
    ctx.move_to(-400, H * 2)
    for px, py in pts:
        ctx.line_to(px, py)
    ctx.line_to(W + 400, H * 2)
    ctx.close_path()
    ctx.fill()
    ctx.restore()


def snowfall(ctx, t, n=120, speed=60, size=(2, 5), alpha=0.8, seed=1, wind=20, area=(0, 0, W, H), c='#FFFFFF'):
    r = random.Random(seed)
    x0, y0, w, h = area
    col(ctx, c, alpha)
    for i in range(n):
        bx = r.uniform(0, w)
        by = r.uniform(0, h)
        sz = r.uniform(*size)
        sp = speed * (0.5 + sz / size[1])
        y = (by + t * sp) % h + y0
        x = (bx + t * wind * (sz / size[1]) + math.sin(t * 0.8 + i) * 12) % w + x0
        ctx.arc(x, y, sz, 0, 2 * math.pi)
        ctx.fill()


def light_beam(ctx, x, y, angle, length, w0, w1, alpha=0.12, c='#FFFFFF'):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    g = cairo.LinearGradient(0, 0, length, 0)
    cc = hexc(c)
    g.add_color_stop_rgba(0, cc[0], cc[1], cc[2], alpha)
    g.add_color_stop_rgba(1, cc[0], cc[1], cc[2], 0)
    ctx.set_source(g)
    poly(ctx, [(0, -w0 / 2), (length, -w1 / 2), (length, w1 / 2), (0, w0 / 2)])
    ctx.fill()
    ctx.restore()


def vignette(ctx, strength=0.55, c=(0, 0, 0)):
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.0)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], 0)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], strength)
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()


def overlay(ctx, c, a):
    col(ctx, c, a)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()


def glow(ctx, x, y, r, c, a):
    cc = hexc(c)
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, cc[0], cc[1], cc[2], a)
    g.add_color_stop_rgba(1, cc[0], cc[1], cc[2], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def arrow(ctx, x1, y1, x2, y2, c, w=10, prog=1.0, head=26):
    x2p = lerp(x1, x2, prog)
    y2p = lerp(y1, y2, prog)
    if prog <= 0.01:
        return
    col(ctx, c)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x1, y1)
    ctx.line_to(x2p, y2p)
    ctx.stroke()
    a = math.atan2(y2p - y1, x2p - x1)
    poly(ctx, [(x2p + math.cos(a) * head * 0.6, y2p + math.sin(a) * head * 0.6),
               (x2p + math.cos(a + 2.4) * head, y2p + math.sin(a + 2.4) * head),
               (x2p + math.cos(a - 2.4) * head, y2p + math.sin(a - 2.4) * head)])
    ctx.fill()


def cabin(ctx, x, y, s, sag=0.0, snow_drift=1.0, window_light=0.0, smoke=0.0, t=0.0, door_open=0.0, show_trap=True):
    """Log cabin, ground center at (x, y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    w, h = 420, 230
    # chimney
    col(ctx, '#5B5650')
    ctx.rectangle(110, -h - 150, 44, 120)
    ctx.fill()
    # logs
    for i in range(8):
        col(ctx, '#6B4A31' if i % 2 == 0 else '#5C3E28')
        rrect(ctx, -w / 2 - 12, -h + i * (h / 8), w + 24, h / 8 + 2, 14)
        ctx.fill()
    col(ctx, '#3E2A1C', 0.5)
    for i in range(8):
        ctx.arc(-w / 2 - 4, -h + i * (h / 8) + h / 16, 9, 0, 2 * math.pi)
        ctx.arc(w / 2 + 4, -h + i * (h / 8) + h / 16, 9, 0, 2 * math.pi)
        ctx.fill()
    # door
    col(ctx, '#2E1F15')
    ctx.rectangle(-150, -170, 90, 170)
    ctx.fill()
    if door_open > 0:
        col(ctx, '#0F0A07')
        ctx.rectangle(-150, -170, 90 * door_open, 170)
        ctx.fill()
    col(ctx, '#4A3322')
    ctx.rectangle(-150 + 90 * door_open, -170, 90 * (1 - door_open), 170)
    ctx.fill()
    # window
    wl = window_light
    col(ctx, mix('#1C2430', '#FFB65C', wl))
    ctx.rectangle(40, -170, 100, 80)
    ctx.fill()
    if wl > 0:
        glow(ctx, 90, -130, 260, '#FFB65C', 0.35 * wl)
    col(ctx, '#3E2A1C')
    ctx.set_line_width(8)
    ctx.rectangle(40, -170, 100, 80)
    ctx.move_to(90, -170)
    ctx.line_to(90, -90)
    ctx.move_to(40, -130)
    ctx.line_to(140, -130)
    ctx.stroke()
    # roof (with sagging right corner)
    sg = sag * 40
    col(ctx, '#3B2A1E')
    poly(ctx, [(-w / 2 - 50, -h + 10), (0, -h - 140), (w / 2 + 50, -h + 10 + sg)])
    ctx.fill()
    col(ctx, P['snow'])
    poly(ctx, [(-w / 2 - 62, -h + 4), (0, -h - 156), (w / 2 + 62, -h + 4 + sg), (w / 2 + 40, -h + 28 + sg),
               (w / 4, -h - 30 + sg * 0.6), (0, -h - 112), (-w / 4, -h - 34), (-w / 2 - 40, -h + 24)])
    ctx.fill()
    col(ctx, P['snow_sh'])
    poly(ctx, [(0, -h - 156), (w / 2 + 62, -h + 4 + sg), (w / 2 + 40, -h + 28 + sg), (w / 4, -h - 30 + sg * 0.6),
               (0, -h - 112)])
    ctx.fill()
    # antlers above door
    col(ctx, '#E8DCC2')
    ctx.set_line_width(7)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for sd in (-1, 1):
        ax = -105
        ctx.move_to(ax, -188)
        ctx.curve_to(ax + sd * 20, -205, ax + sd * 40, -215, ax + sd * 46, -240)
        ctx.move_to(ax + sd * 24, -206)
        ctx.line_to(ax + sd * 22, -228)
        ctx.move_to(ax + sd * 36, -214)
        ctx.line_to(ax + sd * 52, -222)
    ctx.stroke()
    # snow drifts
    if snow_drift > 0:
        col(ctx, P['snow'])
        ellipse(ctx, -w / 2 - 20, 0, 140 * snow_drift, 70 * snow_drift)
        ctx.fill()
        ellipse(ctx, w / 2 + 30, 0, 170 * snow_drift, 90 * snow_drift)
        ctx.fill()
        ellipse(ctx, 0, 6, 260, 26 * snow_drift)
        ctx.fill()
    # smoke
    if smoke > 0:
        for i in range(6):
            ph = (t * 0.25 + i / 6) % 1
            col(ctx, '#D8D8D8', smoke * 0.35 * (1 - ph))
            ctx.arc(132 + math.sin(ph * 6 + i) * 20 + ph * 60, -h - 160 - ph * 260, 18 + ph * 40, 0, 2 * math.pi)
            ctx.fill()
    ctx.restore()


def trap(ctx, x, y, s, open_=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    c = '#7A4A2A'
    col(ctx, c)
    ctx.set_line_width(6)
    ctx.arc(0, 0, 36, 0, 2 * math.pi)
    ctx.stroke()
    for sd in (-1, 1):
        ctx.save()
        ctx.rotate(sd * 0.9 * open_)
        ctx.move_to(-38, 0)
        for i in range(7):
            ctx.line_to(-38 + i * 12 + 6, sd * -14)
            ctx.line_to(-38 + i * 12 + 12, 0)
        ctx.stroke()
        ctx.restore()
    col(ctx, '#5A3A22')
    ctx.rectangle(-4, 30, 8, 30)
    ctx.fill()
    ctx.restore()


# ---------------------------------------------------------------- text

FONT = "Inter"


def set_font(ctx, size, weight=cairo.FONT_WEIGHT_BOLD, family=None):
    ctx.select_font_face(family or FONT, cairo.FONT_SLANT_NORMAL, weight)
    ctx.set_font_size(size)


def text_w(ctx, s):
    return ctx.text_extents(s).x_advance


def draw_text(ctx, s, x, y, size, c='#FFFFFF', align='center', shadow=True, alpha=1.0, family=None, outline=0):
    set_font(ctx, size, family=family)
    w = text_w(ctx, s)
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    if outline:
        ctx.move_to(x, y)
        ctx.text_path(s)
        col(ctx, '#000000', 0.85 * alpha)
        ctx.set_line_width(outline)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
    if shadow:
        col(ctx, '#000000', 0.55 * alpha)
        ctx.move_to(x + 3, y + 4)
        ctx.show_text(s)
    col(ctx, c, alpha)
    ctx.move_to(x, y)
    ctx.show_text(s)
    return w


def rich_line(ctx, parts, x, y, size, alpha=1.0, outline=7):
    """parts: list of (text, color). centered at x."""
    set_font(ctx, size)
    total = sum(text_w(ctx, s) for s, _ in parts)
    cx = x - total / 2
    for s, c in parts:
        ctx.move_to(cx, y)
        ctx.text_path(s)
        col(ctx, '#000000', 0.8 * alpha)
        ctx.set_line_width(outline)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
        cx += text_w(ctx, s)
    cx = x - total / 2
    for s, c in parts:
        col(ctx, c, alpha)
        ctx.move_to(cx, y)
        ctx.show_text(s)
        cx += text_w(ctx, s)


def lesson_card(ctx, text, prog, num=None, y=150):
    """Animated yellow lesson banner at top of frame. prog: 0..1 in, held at 1."""
    if prog <= 0:
        return
    a = ease_out(seg(prog, 0, 0.3))
    set_font(ctx, 50)
    tw = text_w(ctx, text)
    bw = tw + 120 + (70 if num else 0)
    x = W / 2 - bw / 2
    yy = y - 20 * (1 - a)
    col(ctx, '#000000', 0.35 * a)
    rrect(ctx, x + 6, yy - 62 + 8, bw, 96, 22)
    ctx.fill()
    col(ctx, '#1C1A17', 0.92 * a)
    rrect(ctx, x, yy - 62, bw, 96, 22)
    ctx.fill()
    col(ctx, P['yellow'], a)
    rrect(ctx, x, yy - 62, 14, 96, 7)
    ctx.fill()
    tx = x + 60
    if num:
        col(ctx, P['yellow'], a)
        ctx.arc(tx + 18, yy - 14, 30, 0, 2 * math.pi)
        ctx.fill()
        set_font(ctx, 38)
        col(ctx, '#1C1A17', a)
        nw = text_w(ctx, str(num))
        ctx.move_to(tx + 18 - nw / 2, yy - 1)
        ctx.show_text(str(num))
        tx += 70
    set_font(ctx, 50)
    col(ctx, P['yellow'], a)
    ctx.move_to(tx, yy + 4)
    ctx.show_text(text)


def top_title(ctx, text, prog, y=110, size=58, c=None):
    if prog <= 0:
        return
    a = ease_out(seg(prog, 0, 0.25))
    draw_text(ctx, text, W / 2, y - 16 * (1 - a), size, c or P['yellow'], alpha=a, outline=8)
