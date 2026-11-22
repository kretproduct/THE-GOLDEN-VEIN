"""Scenes 1-11."""
import math
import random
from engine import *
from timeline import find_word, word_at, mouth_at, EDL


def cam(ctx, z=1.0, cx=W / 2, cy=H / 2, rot=0.0):
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.rotate(rot)
    ctx.translate(-cx, -cy)


def shake(ctx, t, amp):
    if amp <= 0:
        return
    ctx.translate(math.sin(t * 61.3) * amp + math.sin(t * 23.1) * amp * 0.5,
                  math.cos(t * 53.7) * amp + math.sin(t * 31.9) * amp * 0.5)


def blink(T, period=4.3, off=0.0):
    return 1.0 if ((T + off) % period) < 0.13 else 0.0


def talk(T):
    return mouth_at(T)


def label(ctx, text, x, y, a=1.0, size=34, c='#FFFFFF'):
    draw_text(ctx, text, x, y, size, c, alpha=a, outline=6)


def snow_texture(ctx, seed, n, area, c1, c2, rmin=10, rmax=40, t=0.0, jitter=0.0):
    r = random.Random(seed)
    x0, y0, w, h = area
    for i in range(n):
        x = x0 + r.uniform(0, w) + math.sin(t * 3 + i) * jitter
        y = y0 + r.uniform(0, h) + math.cos(t * 2.6 + i) * jitter
        rad = r.uniform(rmin, rmax)
        col(ctx, mix(c1, c2, r.random()))
        ctx.arc(x, y, rad, 0, 2 * math.pi)
        ctx.fill()


# =============================================================== 01 Fifteen Minutes
def s01(ctx, t, T, d):
    col(ctx, '#02040A')
    ctx.paint()
    ctx.save()
    z = lerp(1.0, 0.82, ease(t / d))
    cam(ctx, z, W / 2, H / 2)
    # face, extreme close-up on one eye
    hr = 760
    ctx.save()
    ctx.translate(W / 2 + hr * 0.36, H / 2 + hr * 0.02 + 40)
    lk = 0.0
    if 13 < t < 19:
        lk = math.sin((t - 13) * 2.2) * 0.8
    p = pose(eyes='open', brows='worried', look=lk, blink=1.0 if 9.0 < t < 9.25 or 20.0 < t < 20.2 else 0.0)
    draw_face(ctx, hr, p)
    ctx.restore()
    # snow pressed around the face (even-odd hole)
    ctx.save()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.rectangle(-W, -H, W * 3, H * 3)
    ellipse(ctx, W / 2 - 40, H / 2 + 60, 760, 470)
    col(ctx, '#BFD3E6')
    ctx.fill()
    ctx.restore()
    snow_texture(ctx, 4, 70, (-300, -200, W + 600, 330), '#A9C2D9', '#E3EEF7', 40, 120)
    snow_texture(ctx, 5, 70, (-300, H - 100, W + 600, 330), '#A9C2D9', '#E3EEF7', 40, 120)
    snow_texture(ctx, 6, 30, (-300, 0, 330, H), '#A9C2D9', '#E3EEF7', 40, 120)
    snow_texture(ctx, 7, 30, (W - 30, 0, 330, H), '#A9C2D9', '#E3EEF7', 40, 120)
    # ice crystals on lashes
    r = random.Random(3)
    for i in range(26):
        x = W / 2 + r.uniform(-260, 260)
        y = H / 2 + r.uniform(-230, -150) + 40
        tw = 0.5 + 0.5 * math.sin(t * 3 + i * 1.7)
        col(ctx, '#FFFFFF', 0.5 + 0.5 * tw)
        s = r.uniform(4, 10)
        ctx.move_to(x - s, y)
        ctx.line_to(x + s, y)
        ctx.move_to(x, y - s)
        ctx.line_to(x, y + s)
        ctx.set_line_width(2.5)
        ctx.stroke()
    ctx.restore()
    # blue grade + heartbeat-pulsed glow
    hb = (t % 1.05)
    pulse = math.exp(-hb * 9) + 0.6 * math.exp(-max(0, hb - 0.22) * 9) * (hb > 0.22)
    overlay(ctx, '#071A3A', 0.55 - 0.08 * pulse)
    glow(ctx, W / 2, 80, 900, '#6FA6E8', 0.25 + 0.1 * pulse)
    vignette(ctx, 0.85)
    overlay(ctx, '#000000', 1 - ease(seg(t, 0.5, 7.0)))


# =============================================================== 02 Title
def s02(ctx, t, T, d):
    sky(ctx, '#3D5A8A', '#F2A65A')
    sun(ctx, 1380, 560, 70, '#FFD38A', 0.5)
    mountains(ctx, 11, 560, 260, '#7C6F95', '#E8C9C3', offset=t * 8)
    mountains(ctx, 12, 690, 260, '#5B5478', '#D9B7B8', offset=t * 18)
    # foreground ridge line
    mountains(ctx, 13, 900, 300, '#2E2C44', '#F0E0DC', freq=0.0016, offset=t * 40 - 200, cap_frac=0.12)
    # tiny figure on the ridge
    pts = ridge_points(13, -400, W + 400, 900, 300, 0.0016)
    fx = 980
    gx = fx + t * 40 - 200
    fy = min(pts, key=lambda p: abs(p[0] - gx))[1]
    draw_range(ctx, fx, fy + 4, 0.11, walk_pose(t * 5), t)
    snowfall(ctx, t, 60, 30, (1.5, 3), 0.6, wind=60)
    vignette(ctx, 0.4)
    a = ease(seg(t, 4.0, 5.2)) * (1 - ease(seg(t, 10.6, 11.6)))
    if a > 0:
        draw_text(ctx, 'THE PACK', W / 2, 470, 190, '#FFFFFF', alpha=a, outline=12)
        draw_text(ctx, 'PART 1: THE AVALANCHE', W / 2, 560, 64, P['yellow'], alpha=a, outline=8)
    overlay(ctx, '#FFFFFF', 1 - ease_out(seg(t, 0, 0.9)))


# =============================================================== 03 The Ridge
def s03(ctx, t, T, d):
    if t < 12:
        sky(ctx, '#7DA2C9', '#E6E1D6')
        sun(ctx, 1600, 260, 50, '#FFF1C9', 0.3)
        mountains(ctx, 21, 620, 330, '#8C9DB9', '#EEF3F8', offset=t * 6)
        mountains(ctx, 22, 760, 260, '#6E819F', '#DCE6EF', offset=t * 16)
        forest(ctx, 23, 860, 30, 70, 120, '#2D4B45', '#26403B', snow=0.6, offset=t * 60, x0=-100, x1=W + 900)
        snow_ground(ctx, 870, offset=t * 120, x1=W + 2000)
        # footprints trail: left behind Range, scrolling away with the ground
        col(ctx, P['snow_sh'])
        step = 0.6
        k0 = int(t / step)
        for k in range(k0, max(-1, k0 - 14), -1):
            x = 790 - (t - k * step) * 120 * 2
            if x < 730:
                ellipse(ctx, x, 1010 + (k % 2) * 16, 22, 8)
                ctx.fill()
        p = walk_pose(t * 5.2, look=0.55, frost=0.6, breath=t * 0.7, brows='angry')
        p['blink'] = blink(T)
        draw_range(ctx, 800, 1010, 1.25, p, t)
        snowfall(ctx, t, 140, 40, (1.5, 4), 0.8, wind=-240, seed=3)
    elif t < 21:
        lt = t - 12
        sky(ctx, '#86A8CC', '#EDE6DA')
        mountains(ctx, 31, 520, 380, '#9AA9C2', '#F2F6FA', offset=lt * 5)
        mountains(ctx, 32, 640, 300, '#7D8FAC', '#E2EAF2', offset=lt * 10)
        mountains(ctx, 33, 780, 260, '#62748F', '#D3DEE8', offset=lt * 18)
        snow_ground(ctx, 840, seed=9, amp=30, offset=lt * 25)
        # long trail of footprints to the tiny figure
        col(ctx, P['snow_sh'])
        for k in range(40):
            ctx.arc(980 - k * 18 - lt * 4, 905 + math.sin(k * 0.5) * 4, 2.5, 0, 2 * math.pi)
            ctx.fill()
        draw_range(ctx, 1000 + lt * 4, 910, 0.13, walk_pose(lt * 5), t)
        snowfall(ctx, t, 90, 30, (1, 2.5), 0.6, wind=-160, seed=4)
    else:
        lt = t - 21
        sky(ctx, '#7DA2C9', '#E6E1D6')
        mountains(ctx, 21, 620, 330, '#8C9DB9', '#EEF3F8')
        mountains(ctx, 22, 760, 260, '#6E819F', '#DCE6EF')
        forest(ctx, 23, 860, 18, 70, 120, '#2D4B45', '#26403B', snow=0.6)
        snow_ground(ctx, 870)
        ctx.save()
        cam(ctx, lerp(1.0, 1.12, ease(lt / 13)), 900, 640)
        p = pose(look=0.35, look_y=0.6, frost=0.6, breath=lt * 0.6, item_r='map', item_l=None,
                 arm_r=(0.9, 1.6), arm_l=(0.5, 1.9), brows='neutral', mouth=talk(T), blink=blink(T))
        draw_range(ctx, 900, 1010, 1.3, p, t)
        ctx.restore()
        snowfall(ctx, t, 140, 40, (1.5, 4), 0.8, wind=-240, seed=3)
        top_title(ctx, 'DAY 4', seg(t, 22.0, 23.0), y=150, size=90, c='#FFFFFF')
    vignette(ctx, 0.45)


# =============================================================== 04 The Count
def s04(ctx, t, T, d):
    sky(ctx, '#7FA1C4', '#E7E1D4')
    mountains(ctx, 41, 640, 300, '#8C9DB9', '#EEF3F8')
    forest(ctx, 42, 820, 16, 80, 130, '#2D4B45', '#26403B', snow=0.6)
    snow_ground(ctx, 830)
    ctx.save()
    cam(ctx, lerp(1.05, 1.15, ease(t / d)), 900, 600)
    # Range kneeling behind the open pack (pack covers his legs)
    reach = 0.0
    tf, tu, tr_, tm = (find_word(4, 'Food'), find_word(4, 'Fuel'), find_word(4, 'Radio'), find_word(4, 'Map'))
    for tt in (tf, tu, tr_, tm):
        reach = max(reach, 1 - abs(t - tt + 0.4) / 0.6)
    reach = clamp(reach)
    p = pose(pack=False, look=0.5, look_y=0.8, arm_r=(lerp(0.2, 1.1, reach), lerp(0.3, 1.2, reach)), arm_l=(0.3, 0.6),
             mouth=talk(T), blink=blink(T), frost=0.5, breath=t * 0.6)
    if t > 24:
        k = ease(seg(t, 24, 25.5)) * (1 - ease(seg(t, 26.5, 28)))
        p['arm_r'] = (lerp(0.2, 1.4, k), lerp(0.3, 2.6, k))
        p['item_r'] = 'notebook' if 24 < t < 27.3 else None
    draw_range(ctx, 780, 1130, 1.25, p, t)
    # the open pack in the foreground
    col(ctx, P['pack_dk'])
    rrect(ctx, 820, 840, 330, 260, 40)
    ctx.fill()
    col(ctx, P['pack'])
    rrect(ctx, 840, 860, 290, 230, 34)
    ctx.fill()
    col(ctx, '#2A2618')
    ellipse(ctx, 985, 868, 140, 30)
    ctx.fill()
    col(ctx, P['strap'])
    ctx.set_line_width(16)
    ctx.move_to(880, 900)
    ctx.line_to(880, 1080)
    ctx.move_to(1090, 900)
    ctx.line_to(1090, 1080)
    ctx.stroke()
    ctx.restore()
    # items fly out of the pack to a shelf row
    items = [('food', 'FOOD 3 DAYS', tf), ('fuel', 'FUEL 4 DAYS', tu), ('radio', 'RADIO', tr_), ('map', 'MAP', tm)]
    for k, (it, name, tt) in enumerate(items):
        pr = ease_out(seg(t, tt - 0.2, tt + 0.6))
        if pr <= 0:
            continue
        tx, ty = 1340 + (k % 2) * 260, 430 + (k // 2) * 250
        x = lerp(990, tx, pr)
        y = lerp(860, ty, pr) - math.sin(pr * math.pi) * 160
        col(ctx, '#000000', 0.25 * pr)
        rrect(ctx, tx - 105, ty - 95, 210, 200, 26)
        ctx.fill()
        draw_item(ctx, it, x, y, 1.5, t)
        label(ctx, name, tx, ty + 135, pr, 30)
    if t > tf - 0.2:
        txt = ' · '.join(n for _, n, tt in items if t > tt)
        top_title(ctx, txt, seg(t, tf, tf + 0.5), y=120, size=52)
    vignette(ctx, 0.45)


# =============================================================== 05 Whumpf
def slope_bg(ctx, t, dark=0.0):
    sky(ctx, '#6E93BD', '#DCE3EA')
    mountains(ctx, 51, 520, 300, '#8796B1', '#EDF2F7')
    # the steep smooth slope: big diagonal plane
    col(ctx, '#E9F0F6')
    poly(ctx, [(-200, 260), (W + 200, 640), (W + 200, H + 200), (-200, H + 200)])
    ctx.fill()
    col(ctx, '#D6E1EB')
    poly(ctx, [(-200, 260), (W + 200, 640), (W + 200, 700), (-200, 330)])
    ctx.fill()
    for k in range(5):
        col(ctx, '#FFFFFF', 0.35)
        ctx.set_line_width(3)
        y0 = 420 + k * 120
        ctx.move_to(-200, y0)
        ctx.line_to(W + 200, y0 + 380)
        ctx.stroke()
    # rocks at the far edge
    col(ctx, '#545A66')
    for x, y, r in ((1750, 760, 60), (1830, 820, 80), (120, 1000, 70)):
        poly(ctx, [(x - r, y + r * 0.4), (x - r * 0.4, y - r * 0.6), (x + r * 0.5, y - r * 0.5), (x + r, y + r * 0.4)])
        ctx.fill()
    if dark:
        overlay(ctx, '#000000', dark)


def slope_y(x):
    return 260 + (x + 200) / (W + 400) * 380 + 330


def crack_path(seed, x0, y0, length, prog):
    r = random.Random(seed)
    pts = [(x0, y0)]
    n = 18
    for i in range(1, int(n * prog) + 1):
        x = x0 + length * i / n
        y = y0 + (x - x0) * 0.19 + r.uniform(-14, 14)
        pts.append((x, y))
    return pts


def s05(ctx, t, T, d):
    ctx.save()
    sh = 18 * math.exp(-max(0, t - 6.5) * 5) if t > 6.5 else 0
    shake(ctx, t, sh)
    # camera: wide, push in to the crack, back out
    zc = ease(seg(t, 6.8, 8.0)) * (1 - ease(seg(t, 11.0, 13.0)))
    cam(ctx, 1 + 0.9 * zc, lerp(W / 2, 1000, zc), lerp(H / 2, 880, zc))
    slope_bg(ctx, t)
    if t < 6:
        x = lerp(380, 860, t / 6)
        p = walk_pose(t * 5, look=0.6, frost=0.4, breath=t * 0.6)
    elif t < 33:
        x = 860
        st = 'wide' if t > 6.5 else 'open'
        p = pose(look=0.3 if t < 6.5 else -0.2, look_y=0.8 if 6.8 < t < 12 else 0.2, eyes=st,
                 brows='worried' if t > 6.5 else 'neutral', mouth=talk(T), frost=0.4, breath=t * 0.8)
    else:
        k = seg(t, 33.5, 42)
        x = lerp(860, 520, ease(k))
        p = walk_pose((t - 33.5) * 3.0, 0.6, look=-0.6, eyes='open', brows='worried', frost=0.4)
    p['blink'] = blink(T) if t < 6.5 or t > 14 else 0
    # cracks
    if t > 6.7:
        for seed, dy, ln in ((5, 0, 900), (8, 40, 640), (2, -30, 520)):
            pr = ease_out(seg(t, 6.7 + (seed % 3) * 0.15, 8.2))
            pts = crack_path(seed, 900, slope_y(900) + dy, ln, pr)
            col(ctx, '#7D8DA0')
            ctx.set_line_width(5)
            poly(ctx, pts, close=False)
            ctx.stroke()
            col(ctx, '#FFFFFF', 0.8)
            ctx.set_line_width(2)
            poly(ctx, [(a + 2, b + 3) for a, b in pts], close=False)
            ctx.stroke()
    draw_range(ctx, x, slope_y(x), 0.95, p, t)
    # whumpf dust puff
    if 6.5 < t < 9:
        k = seg(t, 6.5, 9)
        for i in range(10):
            a = i / 10 * math.pi
            col(ctx, '#FFFFFF', 0.6 * (1 - k))
            ctx.arc(860 + math.cos(a) * 200 * k * 1.5, slope_y(860) - math.sin(a) * 50 * k, 30 + 40 * k, 0, 2 * math.pi)
            ctx.fill()
    ctx.restore()
    if 6.5 < t < 8.2:
        k = seg(t, 6.5, 8.2)
        draw_text(ctx, 'WHUMPF!', W / 2, 360 - 30 * k, 150, '#FFFFFF', alpha=1 - k, outline=12)
    # cross-section inset
    ta = find_word(7, 'weak')
    tb = find_word(7, 'collapsed')
    tc = find_word(7, 'rubber')
    te = find_word(7, 'Most')
    a = ease(seg(t, ta - 0.5, ta + 0.3)) * (1 - ease(seg(t, te + 3.0, te + 3.8)))
    if a > 0:
        bx, by, bw, bh = 1180, 210, 640, 470
        col(ctx, '#11161D', 0.88 * a)
        rrect(ctx, bx, by, bw, bh, 26)
        ctx.fill()
        label(ctx, 'INSIDE THE SNOW', bx + bw / 2, by + 56, a, 34, P['yellow'])
        drop = 28 * ease(seg(t, tb, tb + 0.4))
        # layers
        col(ctx, mix('#7E8A99', '#5E6875', 0.5), a)
        ctx.rectangle(bx + 30, by + 360, bw - 60, 80)
        ctx.fill()
        label(ctx, 'OLD SNOW', bx + bw / 2, by + 412, a * 0.9, 26)
        wl_h = 60 - drop
        col(ctx, '#B79B76', a)
        ctx.rectangle(bx + 30, by + 360 - wl_h, bw - 60, wl_h)
        ctx.fill()
        col(ctx, '#8C7357', a)
        r = random.Random(1)
        for i in range(40):
            ctx.arc(bx + 40 + r.uniform(0, bw - 80), by + 360 - r.uniform(4, max(6, wl_h - 4)), 3, 0, 2 * math.pi)
            ctx.fill()
        label(ctx, 'WEAK LAYER', bx + bw / 2, by + 360 - wl_h / 2 + 10, a, 26, '#FFFFFF')
        col(ctx, mix('#EEF3F8', '#DCE6EF', 0.3), a)
        ctx.rectangle(bx + 30, by + 110 + drop, bw - 60, 190)
        ctx.fill()
        label(ctx, 'SLAB', bx + bw / 2, by + 220 + drop, a, 30, '#3A4656')
        if t > tc:
            # stretched rubber band
            k = ease(seg(t, tc, tc + 0.6))
            col(ctx, P['red'], a)
            ctx.set_line_width(7)
            ctx.move_to(bx + 60, by + 140 + drop)
            ctx.curve_to(bx + 200, by + 140 + drop + 30 * k, bx + bw - 200, by + 140 + drop + 30 * k, bx + bw - 60, by + 140 + drop)
            ctx.stroke()
            label(ctx, 'TENSE', bx + bw / 2, by + 190 + drop + 20 * k, a * k, 28, P['red'])
        if t > tb:
            k = seg(t, tb, tb + 0.5)
            col(ctx, '#FFFFFF', a)
            ctx.set_line_width(4)
            for i in range(5):
                xx = bx + 90 + i * 115
                ctx.move_to(xx, by + 110 + drop)
                ctx.line_to(xx + 12, by + 110 + drop + 80 * k)
                ctx.line_to(xx - 6, by + 110 + drop + 140 * k)
            ctx.stroke()
    tm = find_word(7, 'Back')
    if t > tm - 0.3:
        top_title(ctx, 'BACK OFF THE WAY YOU CAME. GENTLY.', seg(t, tm, tm + 0.5) * (1 - seg(t, 39.6, 40.0)), y=130, size=50,
                  c='#FFFFFF')
    lesson_card(ctx, 'WHUMPF OR CRACKS = GET OFF THE SLOPE', seg(t, 40.5, 42.0), num=1)
    vignette(ctx, 0.45)


# =============================================================== 06 Release
def wave_blobs(ctx, t, front_y, seed=3, n=60, alpha=1.0, spread=500):
    r = random.Random(seed)
    for i in range(n):
        x = r.uniform(-200, W + 200)
        yo = r.uniform(-spread, 60)
        rad = r.uniform(60, 180)
        wob = math.sin(t * 6 + i) * 14
        col(ctx, mix('#FFFFFF', '#C9D8E6', r.random() * 0.6), alpha)
        ctx.arc(x + wob, front_y + yo + wob * 0.5, rad, 0, 2 * math.pi)
        ctx.fill()


def s06(ctx, t, T, d):
    ctx.save()
    shake(ctx, t, 0 if t < 2.2 else lerp(4, 22, seg(t, 2.2, 5.0)))
    slope_bg(ctx, t)
    # fracture line and sliding slab
    if t > 2.0:
        k = ease_in(seg(t, 2.5, 4.8))
        off = k * 900
        col(ctx, '#C7D5E2')
        poly(ctx, [(-200, 300 + off), (W + 200, 680 + off), (W + 200, 760 + off), (-200, 380 + off)])
        ctx.fill()
        col(ctx, '#56657A')
        ctx.set_line_width(6)
        pts = crack_path(11, -200, 300, W + 400, ease_out(seg(t, 2.0, 2.6)))
        poly(ctx, pts, close=False)
        ctx.stroke()
        # broken blocks
        if t > 3.2:
            r = random.Random(9)
            for i in range(26):
                bx = r.uniform(-100, W + 100)
                by = 300 + (bx + 200) * 0.19 + off * r.uniform(0.8, 1.3) - 60
                s = r.uniform(30, 80)
                ctx.save()
                ctx.translate(bx, by)
                ctx.rotate(t * r.uniform(-3, 3))
                col(ctx, '#E3ECF4')
                rrect(ctx, -s, -s * 0.6, s * 2, s * 1.2, 10)
                ctx.fill()
                col(ctx, '#B9C9D9')
                ctx.rectangle(-s, s * 0.2, s * 2, s * 0.4)
                ctx.fill()
                ctx.restore()
    # Range
    hit = 4.8
    if t < hit:
        p = pose(look=-0.8 if t > 0.6 else 0.2, look_y=-0.8 if t > 2.2 else 0.0, eyes='wide' if t > 2.2 else 'open',
                 brows='worried', mouth=talk(T), frost=0.4)
        if t > 2.2:
            p['mouth_shape'] = 'o'
        draw_range(ctx, 860, slope_y(860), 0.95, p, t)
    else:
        k = t - hit
        p = pose(eyes='wide', brows='worried', mouth=max(0.6, talk(T)), mouth_shape='o', arm_r=(2.4, 0.4),
                 arm_l=(2.0 + math.sin(k * 7), 0.6), leg_l=(0.6, 1.0), leg_r=(-0.4, 0.5), body_rot=k * 4.5)
        draw_range(ctx, 860 + k * 160, slope_y(860) - 160 + k * 60, 0.95, p, t)
    if t > 3.2:
        front = lerp(-300, 1500, seg(t, 3.2, 6.6))
        wave_blobs(ctx, t, front, n=70, spread=900)
        col(ctx, '#F1F5F9')
        ctx.rectangle(-200, -400, W + 400, front - 450)
        ctx.fill()
    ctx.restore()
    # speed lines once we're inside the wave
    if t > 6.6:
        col(ctx, '#EEF3F8')
        ctx.paint()
        wave_blobs(ctx, t * 1.5, 500, seed=19, n=50, alpha=1, spread=900)
        r = random.Random(4)
        col(ctx, '#FFFFFF', 0.8)
        ctx.set_line_width(4)
        for i in range(30):
            y = (r.uniform(0, H) + t * 1600) % H
            x = r.uniform(0, W)
            ctx.move_to(x, y)
            ctx.line_to(x - 30, y - 260)
        ctx.stroke()
        p = pose(eyes='wide', brows='worried', mouth_shape='o', mouth=0.5, arm_r=(2.2 + math.sin(t * 9) * 0.6, 0.5),
                 arm_l=(1.6 + math.cos(t * 8) * 0.6, 0.8), leg_l=(0.8, 1.0), leg_r=(-0.5, 0.6), body_rot=t * 3.1)
        draw_range(ctx, W / 2 + math.sin(t * 2) * 120, 760, 0.85, p, t)
        wave_blobs(ctx, t * 2, 1250, seed=8, n=26, alpha=0.9, spread=200)
        ts = find_word(9, 'speed')
        if t > ts:
            top_title(ctx, 'AS FAST AS A CAR ON A HIGHWAY', seg(t, ts, ts + 0.5), y=150, size=56, c='#1F2C3A')
    vignette(ctx, 0.35)


# =============================================================== 07 Freeze frame
def s07(ctx, t, T, d):
    unfreeze = 38.0
    tf = find_word(10, 'fight')
    tside = find_word(10, 'side')
    ttree = find_word(10, 'tree')
    tswim = find_word(10, 'Kick')
    tarm = find_word(10, 'push')
    tface = find_word(10, 'other')
    tpocket = find_word(10, 'pocket')
    ctx.save()
    orbit = math.sin(t * 0.18) * 0.08
    z = lerp(1.0, 1.12, ease(seg(t, 0, 30)))
    cam(ctx, z, W / 2, H / 2 + 20, orbit)
    col(ctx, '#EEF3F8')
    ctx.paint()
    frozen_t = 9.3
    wave_blobs(ctx, frozen_t, 300, seed=5, n=40, alpha=1, spread=700)
    # hanging snow chunks
    r = random.Random(12)
    for i in range(50):
        x, y = r.uniform(0, W), r.uniform(0, H)
        dx = math.sin(t * 0.3 + i) * 3
        col(ctx, '#B9CADB')
        ctx.arc(x + dx, y, r.uniform(4, 14), 0, 2 * math.pi)
        ctx.fill()
    # Range mid-tumble -> learns the moves
    armup = ease(seg(t, tarm, tarm + 0.8))
    face = ease(seg(t, tface, tface + 0.8))
    rot = lerp(0.55, 0.0, ease(seg(t, tarm - 1.0, tarm + 0.5)))
    fl = 1 - armup
    p = pose(eyes='wide', brows='worried', mouth_shape='o' if face < 0.5 else 'line', mouth=0.4 * fl,
             arm_r=(lerp(2.3, math.pi - 0.45, armup), lerp(0.5, -0.25, armup)),
             arm_l=(lerp(1.6, 2.0, face), lerp(0.9, 3.75, face)),
             leg_l=(0.7 * fl + 0.15, 0.9 * fl), leg_r=(-0.4 * fl - 0.1, 0.6 * fl), body_rot=rot)
    sink = 0.0
    if t > unfreeze:
        sink = ease(seg(t, unfreeze, unfreeze + 4.0))
    draw_range(ctx, W / 2 - 60, 860 + sink * 120, 1.15, p, t)
    if t > unfreeze:
        # snow swallows him
        lvl = lerp(H + 200, 260, ease(seg(t, unfreeze, unfreeze + 4.5)))
        wave_blobs(ctx, t, lvl, seed=31, n=50, alpha=1, spread=120)
        col(ctx, '#E4ECF3')
        ctx.rectangle(-300, lvl + 60, W + 600, H + 600)
        ctx.fill()
    ctx.restore()
    if t < unfreeze:
        # frozen-frame UI: blue tint + corner brackets
        overlay(ctx, '#5B86B8', 0.12)
        col(ctx, '#FFFFFF', 0.9)
        ctx.set_line_width(8)
        m, L = 50, 110
        for sx, sy in ((m, m), (W - m, m), (m, H - m), (W - m, H - m)):
            dx = 1 if sx < W / 2 else -1
            dy = 1 if sy < H / 2 else -1
            ctx.move_to(sx, sy + dy * L)
            ctx.line_to(sx, sy)
            ctx.line_to(sx + dx * L, sy)
        ctx.stroke()
        a = ease(seg(t, 0.3, 1.0))
        col(ctx, P['red'], a * (0.6 + 0.4 * math.sin(t * 4)))
        ctx.arc(110, 120, 14, 0, 2 * math.pi)
        ctx.fill()
        draw_text(ctx, 'PAUSED', 140, 133, 36, '#FFFFFF', align='left', alpha=a, outline=6)
        # coaching arrows
        cx, cy = W / 2 - 60, 600
        if t > tf:
            label(ctx, 'FIGHT!', 520, 330, ease(seg(t, tf, tf + 0.4)) * (1 - seg(t, tside - 0.2, tside)), 80, P['yellow'])
        if tside < t < tarm:
            k = ease(seg(t, tside, tside + 0.8))
            arrow(ctx, cx + 180, cy, 1650, cy, P['yellow'], 14, k, 40)
            label(ctx, 'GET TO THE SIDE', 1450, cy - 40, k * (1 - seg(t, tarm - 0.5, tarm)), 40, P['yellow'])
        if t > ttree:
            k = ease(seg(t, ttree, ttree + 0.6)) * (1 - seg(t, tarm - 0.5, tarm))
            ctx.save()
            ctx.translate(0, 0)
            pine(ctx, 1740, 900, 360 * k + 1, '#2D4B45', '#26403B', snow=0.8)
            ctx.restore()
            label(ctx, 'GRAB A TREE', 1740, 980, k, 34)
        if t > tswim:
            k = ease(seg(t, tswim, tswim + 0.6)) * (1 - seg(t, tarm - 0.5, tarm))
            for dx in (-80, 80):
                arrow(ctx, cx + dx, cy - 330, cx + dx, cy - 470, '#FFFFFF', 12, k, 34)
            label(ctx, 'SWIM — STAY ON TOP', cx, cy - 500, k, 40)
        if t > tarm:
            k = ease(seg(t, tarm + 0.4, tarm + 1.0))
            arrow(ctx, cx + 200, 330, cx + 200, 170, P['yellow'], 14, k, 40)
            label(ctx, 'ONE HAND UP', cx + 420, 260, k, 44, P['yellow'])
        if t > tface:
            k = ease(seg(t, tface + 0.5, tface + 1.0))
            col(ctx, P['yellow'], k)
            ctx.set_line_width(8)
            ctx.new_path()
            ctx.arc(cx - 45, 440, 120, 0, 2 * math.pi)
            ctx.stroke()
            label(ctx, 'HAND OVER FACE', cx - 420, 470, k, 44, P['yellow'])
        if t > tpocket:
            k = ease(seg(t, tpocket - 0.3, tpocket + 0.4))
            label(ctx, '= AIR POCKET', cx - 420, 530, k, 44, '#FFFFFF')
    else:
        overlay(ctx, '#0B1830', 0.6 * ease(seg(t, unfreeze + 2.5, d)))
    lesson_card(ctx, 'AS IT SLOWS: ONE HAND UP, ONE HAND OVER YOUR FACE', seg(t, unfreeze + 1.0, unfreeze + 2.5), num=2)
    vignette(ctx, 0.4)


# =============================================================== 08 Silence
def s08(ctx, t, T, d):
    ctx.save()
    cam(ctx, lerp(1.0, 1.06, t / d), W / 2, H / 2)
    sky(ctx, '#6C93C0', '#E3E8EE')
    sun(ctx, 1500, 200, 60, '#FFF6DA', 0.45)
    mountains(ctx, 51, 520, 300, '#8796B1', '#EDF2F7')
    col(ctx, '#E5EDF4')
    poly(ctx, [(-200, 300), (W + 200, 680), (W + 200, H + 200), (-200, H + 200)])
    ctx.fill()
    # rubble field
    r = random.Random(81)
    for i in range(70):
        x = r.uniform(-100, W + 100)
        y = 380 + (x + 200) * 0.19 + r.uniform(60, 650)
        s = r.uniform(20, 60)
        col(ctx, '#C3D2E0')
        ellipse(ctx, x, y + s * 0.3, s * 1.2, s * 0.5)
        ctx.fill()
        col(ctx, '#F3F7FA')
        ellipse(ctx, x, y, s * 1.1, s * 0.55)
        ctx.fill()
    ctx.restore()
    # glittering dust drifting down
    r = random.Random(7)
    for i in range(160):
        x = (r.uniform(0, W) + t * 10) % W
        y = (r.uniform(0, H) + t * r.uniform(8, 25)) % H
        tw = 0.5 + 0.5 * math.sin(t * r.uniform(2, 5) + i)
        col(ctx, '#FFFFFF', 0.25 + 0.6 * tw)
        ctx.arc(x, y, r.uniform(1.5, 3.5), 0, 2 * math.pi)
        ctx.fill()
    # a crow far away
    cx = lerp(200, 1300, seg(t, 1.5, 11))
    cy = 180 + math.sin(t * 1.2) * 20
    flap = math.sin(t * 9) * 12
    col(ctx, '#1A1A1E')
    ctx.set_line_width(4)
    ctx.move_to(cx - 18, cy - flap)
    ctx.line_to(cx, cy)
    ctx.line_to(cx + 18, cy - flap)
    ctx.stroke()
    vignette(ctx, 0.4)


# =============================================================== 09 Like Concrete
def pocket_frame(ctx, t, hr, fx, fy, light=0.0, jitter=0.0, seed=91, rot=0.0):
    col(ctx, '#050A16')
    ctx.paint()
    ctx.save()
    ctx.translate(fx, fy)
    ctx.rotate(rot)
    ctx.translate(-fx, -fy)
    glow(ctx, fx, fy - hr * 0.2, hr * 2.4, '#3A6FB0', 0.35 + light)
    return


def s09(ctx, t, T, d):
    hr = 250
    fx, fy = W / 2 - 40, H / 2 + 40
    pocket_frame(ctx, t, hr, fx, fy)
    strain = 2.6 < t < 6.5
    calm = ease(seg(t, find_word(14, 'Slow'), find_word(14, 'Slow') + 2.5))
    jit = (math.sin(t * 40) * 6) if strain else 0
    p = pose(eyes='squint' if strain else ('closed' if calm > 0.6 else 'open'), brows='worried', mouth=talk(T),
             look=math.sin(t * 0.7) * 0.3 * (1 - calm), blink=blink(T) * (1 - calm))
    ctx.save()
    ctx.translate(fx + jit, fy)
    draw_face(ctx, hr, p)
    ctx.translate(0, -hr * 0.12)
    draw_hair(ctx, hr, p['look'])
    ctx.restore()
    # gloved hand cupped in front of the mouth
    col(ctx, P['glove'])
    ellipse(ctx, fx + jit + 90, fy + hr * 0.95, 150, 80)
    ctx.fill()
    for k in range(4):
        rrect(ctx, fx + jit + 10 + k * 46, fy + hr * 0.62, 40, 100, 20)
        ctx.fill()
    # breath fog in the pocket
    rate = lerp(1.6, 0.45, calm)
    ph = (t * rate) % 1
    col(ctx, '#CFE3F7', 0.28 * (1 - ph))
    ellipse(ctx, fx + jit, fy + hr * 0.75 - ph * 40, 60 + ph * 120, 30 + ph * 50)
    ctx.fill()
    # snow mass around the pocket (even-odd hole), packed grains
    ts = find_word(13, 'stops')
    locked = t > ts
    ctx.save()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.rectangle(-50, -50, W + 100, H + 100)
    ellipse(ctx, fx, fy + 30, hr * 1.55, hr * 1.5)
    col(ctx, '#132743')
    ctx.fill()
    ctx.restore()
    r = random.Random(5)
    for i in range(260):
        a = r.uniform(0, 2 * math.pi)
        dist = r.uniform(1.0, 3.2)
        x = fx + math.cos(a) * hr * 1.55 * dist
        y = fy + 30 + math.sin(a) * hr * 1.5 * dist
        if not locked:
            x += math.sin(t * 5 + i) * 10
            y += math.cos(t * 4 + i) * 10
        rad = r.uniform(14, 34)
        col(ctx, mix('#1E3A60', '#3D6798', r.random()))
        ctx.arc(x, y, rad, 0, 2 * math.pi)
        ctx.fill()
    if locked:
        k = ease(seg(t, ts, ts + 0.5)) * (1 - ease(seg(t, ts + 6, ts + 7)))
        label(ctx, 'SETS LIKE CONCRETE', W / 2, 160, k, 64, P['yellow'])
    # air meter
    ta = find_word(13, 'running')
    if t > ta - 0.5:
        k = ease(seg(t, ta - 0.5, ta))
        air = clamp(1 - (t - ta) / 60)
        col(ctx, '#000000', 0.5 * k)
        rrect(ctx, 80, 900, 420, 70, 18)
        ctx.fill()
        label(ctx, 'AIR', 140, 950, k, 34, '#FFFFFF')
        col(ctx, '#2A3442', k)
        rrect(ctx, 200, 920, 270, 30, 12)
        ctx.fill()
        col(ctx, mix('#E2533F', '#6FD38A', air), k)
        rrect(ctx, 200, 920, 270 * air, 30, 12)
        ctx.fill()
    if t > find_word(14, 'Panic'):
        label(ctx, 'PANIC BURNS AIR', W / 2, 160, ease(seg(t, find_word(14, 'Panic'), find_word(14, 'Panic') + 0.4)), 64,
              P['yellow'])
    vignette(ctx, 0.7)


# =============================================================== 10 Which Way Is Up?
def s10(ctx, t, T, d):
    hr = 330
    fx, fy = W / 2, H / 2 + 30
    pocket_frame(ctx, t, hr, fx, fy, light=0.05)
    tspit = 27.0
    dart = math.sin(t * 3.3) * 0.9 if t < 12 else math.sin(t * 1.1) * 0.4
    p = pose(eyes='wide' if t < 12 else 'open', brows='worried', look=dart if t < tspit else 0.8, look_y=0.0,
             mouth=talk(T), blink=blink(T))
    ctx.save()
    ctx.translate(fx, fy)
    draw_face(ctx, hr, p)
    ctx.translate(0, -hr * 0.12)
    draw_hair(ctx, hr, p['look'])
    ctx.restore()
    # spit drop sliding sideways toward his ear
    if t > tspit:
        k = ease(seg(t, tspit, tspit + 3.5))
        x = lerp(fx + 40, fx + hr * 0.95, k)
        y = fy + hr * 0.58 + math.sin(k * math.pi) * -10
        col(ctx, '#DDF1FF', 0.9)
        ellipse(ctx, x, y, 22, 15)
        ctx.fill()
        col(ctx, '#FFFFFF')
        ctx.arc(x - 6, y - 4, 5, 0, 2 * math.pi)
        ctx.fill()
        col(ctx, '#BFE3FF', 0.6)
        ctx.set_line_width(6)
        ctx.move_to(fx + 40, fy + hr * 0.58)
        ctx.line_to(x, y)
        ctx.stroke()
    ctx.save()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.rectangle(-50, -50, W + 100, H + 100)
    ellipse(ctx, fx, fy, hr * 1.5, hr * 1.4)
    col(ctx, '#162C4C')
    ctx.fill()
    ctx.restore()
    snow_texture(ctx, 17, 120, (-100, -100, W + 200, 260), '#1F3B62', '#3F6A9C', 20, 40)
    snow_texture(ctx, 18, 120, (-100, H - 160, W + 200, 260), '#1F3B62', '#3F6A9C', 20, 40)
    snow_texture(ctx, 19, 60, (-100, 0, 360, H), '#1F3B62', '#3F6A9C', 20, 40)
    snow_texture(ctx, 20, 60, (W - 260, 0, 360, H), '#1F3B62', '#3F6A9C', 20, 40)
    # question marks while lost
    if 3 < t < 13:
        for i, (qx, qy) in enumerate(((300, 300), (1600, 280), (260, 760), (1650, 760))):
            k = 0.5 + 0.5 * math.sin(t * 3 + i * 1.6)
            label(ctx, '?', qx, qy, k, 120, '#FFFFFF')
    tg = find_word(15, 'Gravity')
    if tg - 0.3 < t < tspit:
        k = ease(seg(t, tg - 0.3, tg + 0.3))
        label(ctx, 'GRAVITY ALWAYS WINS', W / 2, 170, k, 64, P['yellow'])
    if t > tspit + 2.5:
        k = ease(seg(t, tspit + 2.5, tspit + 3.2))
        arrow(ctx, fx + hr * 1.1, fy + hr * 0.6, fx + hr * 1.1 + 260, fy + hr * 0.6, P['yellow'], 14, k, 40)
        label(ctx, 'DOWN', fx + hr * 1.1 + 150, fy + hr * 0.6 - 30, k, 44, P['yellow'])
        arrow(ctx, fx - hr * 1.1, fy, fx - hr * 1.1 - 260, fy, '#FFFFFF', 14, k, 40)
        label(ctx, 'DIG THIS WAY', fx - hr * 1.1 - 160, fy - 40, k, 44, '#FFFFFF')
    lesson_card(ctx, 'LOST WHICH WAY IS UP? LET GRAVITY TELL YOU', seg(t, 30.0, 31.5), num=3)
    vignette(ctx, 0.7)


# =============================================================== 11 Digging Out
def s11(ctx, t, T, d):
    sky(ctx, '#6E95C2', '#E4E9EE')
    mountains(ctx, 111, 520, 280, '#8796B1', '#EDF2F7')
    surf = 700
    col(ctx, '#E9F0F6')
    ctx.rectangle(0, surf, W, H)
    ctx.fill()
    # rubble blocks
    r = random.Random(112)
    for i in range(40):
        x = r.uniform(-50, W + 50)
        y = surf + r.uniform(-10, 380)
        s = r.uniform(25, 70)
        col(ctx, '#C3D2E0')
        ellipse(ctx, x, y + s * 0.3, s * 1.2, s * 0.5)
        ctx.fill()
        col(ctx, '#F4F8FB')
        ellipse(ctx, x, y, s * 1.1, s * 0.55)
        ctx.fill()
    hx = 960
    # hole widening
    hole = ease(seg(t, 3.5, 28))
    col(ctx, '#7F94AC')
    ellipse(ctx, hx, surf + 80, 40 + 220 * hole, 18 + 70 * hole)
    ctx.fill()
    # Range rising out of the hole
    rise = ease(seg(t, 6.0, 28))
    if rise > 0:
        ctx.save()
        ctx.rectangle(0, 0, W, surf + 80 + 18 + 60 * hole)
        ctx.clip()
        p = pose(eyes='squint' if rise < 0.7 else 'open', brows='worried', mouth=0.3 + 0.3 * abs(math.sin(t * 5)),
                 arm_r=(math.pi - 0.3 + math.sin(t * 4) * 0.2, 0.3),
                 arm_l=(1.2 + math.sin(t * 5) * 0.5, 1.0), frost=0.8, blink=blink(T))
        draw_range(ctx, hx, surf + 80 + 470 - rise * 420, 1.0, p, t)
        ctx.restore()
    else:
        # just the gloved hand clawing through
        k = ease_out(seg(t, 0.4, 2.5))
        y = surf + 70 - k * 130
        ang = math.sin(t * 6) * 0.2
        ctx.save()
        ctx.translate(hx + 60, y)
        ctx.rotate(ang)
        col(ctx, P['jacket_dk'])
        ctx.rectangle(-16, 10, 32, 140)
        ctx.fill()
        col(ctx, P['glove'])
        ellipse(ctx, 0, 0, 30, 34)
        ctx.fill()
        for f in range(4):
            fa = -0.6 + f * 0.4 + math.sin(t * 9 + f) * 0.25
            ctx.save()
            ctx.rotate(fa)
            rrect(ctx, -8, -70, 16, 46, 8)
            ctx.fill()
            ctx.restore()
        ctx.restore()
        # chunks flying
        for i in range(8):
            kk = seg(t, 0.4 + i * 0.1, 2.0 + i * 0.1)
            if 0 < kk < 1:
                col(ctx, '#F4F8FB')
                ctx.arc(hx + 60 + math.cos(i) * 140 * kk, surf + 40 - math.sin(kk * math.pi) * 120, 12, 0, 2 * math.pi)
                ctx.fill()
    # gear cards
    tb = find_word(17, 'beacon')
    tal = find_word(17, 'alone', 1) if True else None
    if t > tb - 0.3:
        gear = [('beacon', 'BEACON'), ('probe', 'PROBE'), ('shovel', 'SHOVEL'), ('partner', 'PARTNER')]
        for k, (it, name) in enumerate(gear):
            tk = tb + k * 0.75 if k < 3 else find_word(17, 'partner')
            pr = ease_out(seg(t, tk - 0.3, tk + 0.3))
            if pr <= 0:
                continue
            x = 300 + k * 440
            y = 230 - 30 * (1 - pr)
            col(ctx, '#11161D', 0.85 * pr)
            rrect(ctx, x - 150, y - 130, 300, 250, 26)
            ctx.fill()
            draw_item(ctx, it, x, y - 20, 1.3, t)
            label(ctx, name, x, y + 95, pr, 36, P['yellow'])
        if t > tal:
            k = ease(seg(t, tal, tal + 0.4))
            x, y = 300 + 3 * 440, 230
            col(ctx, P['red'], k)
            ctx.set_line_width(14)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(x - 100, y - 90)
            ctx.line_to(x + 100, y + 90)
            ctx.move_to(x + 100, y - 90)
            ctx.line_to(x - 100, y + 90)
            ctx.stroke()
    snowfall(ctx, t, 40, 20, (1, 2.5), 0.5, wind=30)
    vignette(ctx, 0.4)
