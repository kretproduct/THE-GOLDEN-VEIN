"""Scenes 12-22."""
import math
import random
from engine import *
from timeline import find_word, word_at, word_times, line_scene, mouth_at
from scenes_a import cam, shake, blink, talk, label, snow_texture


def check_mark(ctx, x, y, s, c, a=1.0):
    col(ctx, c, a)
    ctx.set_line_width(s * 0.22)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(x - s * 0.5, y)
    ctx.line_to(x - s * 0.1, y + s * 0.4)
    ctx.line_to(x + s * 0.6, y - s * 0.45)
    ctx.stroke()


def cross_mark(ctx, x, y, s, c, a=1.0):
    col(ctx, c, a)
    ctx.set_line_width(s * 0.22)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x - s * 0.5, y - s * 0.5)
    ctx.line_to(x + s * 0.5, y + s * 0.5)
    ctx.move_to(x + s * 0.5, y - s * 0.5)
    ctx.line_to(x - s * 0.5, y + s * 0.5)
    ctx.stroke()


def panel(ctx, x, y, w, h, a=1.0, c='#11161D'):
    col(ctx, '#000000', 0.3 * a)
    rrect(ctx, x + 6, y + 8, w, h, 24)
    ctx.fill()
    col(ctx, c, 0.88 * a)
    rrect(ctx, x, y, w, h, 24)
    ctx.fill()


def debris_field(ctx, seed, y0, n, spread=400, c1='#F4F8FB', c2='#C3D2E0'):
    r = random.Random(seed)
    items = [(r.uniform(-60, W + 60), y0 + r.uniform(-20, spread), r.uniform(25, 80)) for _ in range(n)]
    items.sort(key=lambda a: a[1])
    for x, y, s in items:
        col(ctx, c2)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(r.uniform(-0.3, 0.3))
        rrect(ctx, -s, -s * 0.35, s * 2, s * 0.9, s * 0.3)
        ctx.fill()
        col(ctx, c1)
        rrect(ctx, -s, -s * 0.55, s * 2, s * 0.75, s * 0.3)
        ctx.fill()
        ctx.restore()


# =============================================================== 12 Head to Toe
def s12(ctx, t, T, d):
    sky(ctx, '#7097C3', '#E6EAEE')
    mountains(ctx, 121, 560, 260, '#8796B1', '#EDF2F7')
    col(ctx, '#E9F0F6')
    ctx.rectangle(0, 760, W, H)
    ctx.fill()
    debris_field(ctx, 122, 780, 22, 300)
    sit = ease(seg(t, 5.0, 7.0))
    # checks while he speaks
    th = find_word(18, 'Head')
    ta = find_word(18, 'Arms')
    tr_ = find_word(18, 'ribs')
    tl = find_word(18, 'Legs')
    tgt = 'none'
    for nm, tt in (('head', th), ('arms', ta), ('ribs', tr_), ('legs', tl)):
        if t > tt - 0.3:
            tgt = nm
    if t > tl + 2.5:
        tgt = 'none'
    arm_r = (0.15, 0.2)
    arm_l = (0.15, 0.2)
    eyes, brows = 'open', 'neutral'
    if tgt == 'head':
        arm_r, arm_l = (2.4, 1.6), (2.4, 1.6)
    elif tgt == 'arms':
        arm_r, arm_l = (0.5, 2.4), (0.2, 0.3)
    elif tgt == 'ribs':
        arm_r, arm_l = (0.5, 1.9), (0.2, 0.3)
        eyes, brows = 'squint', 'worried'
    elif tgt == 'legs':
        arm_r, arm_l = (0.1, 0.1), (0.1, 0.1)
    gasp = 1 - sit
    p = pose(eyes='closed' if t < 2.5 else eyes, brows='worried' if t < 7 else brows, mouth=max(talk(T), 0.5 * gasp * abs(math.sin(t * 4))),
             arm_r=arm_r if sit > 0.9 else (2.6, 0.2), arm_l=arm_l if sit > 0.9 else (2.3, 0.4),
             body_rot=lerp(-math.pi / 2, 0, sit), bob=gasp * abs(math.sin(t * 4)) * 6, look_y=-1.0 * gasp,
             blink=blink(T), frost=0.8, pack=False)
    x = lerp(980, 900, sit)
    y = lerp(860, 1010, sit)
    if sit < 0.5:
        p['look'] = 0
    draw_range(ctx, x, y, 0.95, p, t)
    # snow drift covering his legs once sitting
    col(ctx, '#F2F6FA')
    ellipse(ctx, 900, 1050, 320, 150 * sit + 10)
    ctx.fill()
    if t < 6:
        ph = (t * 1.3) % 1
        col(ctx, '#FFFFFF', 0.5 * (1 - ph))
        ellipse(ctx, 740 - ph * 40, 780 - ph * 70, 30 + ph * 40, 20 + ph * 26)
        ctx.fill()
    # body checklist
    if t > th - 0.5:
        a = ease(seg(t, th - 0.5, th))
        panel(ctx, 1340, 250, 460, 520, a)
        rows = [('HEAD', th, 'ok'), ('ARMS', ta, 'ok'), ('RIBS', tr_, 'bruised'), ('LEGS', tl, 'ok')]
        for k, (nm, tt, st) in enumerate(rows):
            yy = 340 + k * 115
            draw_text(ctx, nm, 1400, yy + 18, 52, '#FFFFFF', align='left', alpha=a, outline=0)
            if t > tt + 0.3:
                kk = ease(seg(t, tt + 0.3, tt + 0.6))
                if st == 'ok':
                    check_mark(ctx, 1720, yy, 50, '#6FD38A', kk)
                else:
                    draw_text(ctx, 'BRUISED', 1740, yy + 16, 34, '#F29B3A', align='right', alpha=kk, outline=0)
        tb = find_word(19, 'adrenaline')
        if t > tb:
            kk = ease(seg(t, tb, tb + 0.4))
            label(ctx, 'ADRENALINE HIDES PAIN', 1570, 730, kk, 30, P['yellow'])
    vignette(ctx, 0.4)


# =============================================================== 13 What's Left
def s13(ctx, t, T, d):
    sky(ctx, '#7B97BD', '#E2DFDC')
    mountains(ctx, 131, 540, 250, '#8B95AE', '#EBEFF4')
    col(ctx, '#E7EEF4')
    ctx.rectangle(0, 700, W, H)
    ctx.fill()
    debris_field(ctx, 132, 720, 36, 360)
    # torn strap sticking out of the snow
    sx, sy = 1180, 900
    col(ctx, P['strap'])
    ctx.save()
    ctx.translate(sx, sy)
    ctx.rotate(0.25 + (math.sin(t * 8) * 0.1 if 3.5 < t < 6.5 else 0))
    ctx.rectangle(-9, -120 - (40 if t > 5.5 else 0), 18, 120 + (40 if t > 5.5 else 0))
    ctx.fill()
    col(ctx, '#3C3727')
    poly(ctx, [(-9, -120 - (40 if t > 5.5 else 0)), (9, -128 - (40 if t > 5.5 else 0)), (4, -112 - (40 if t > 5.5 else 0)),
               (-3, -134 - (40 if t > 5.5 else 0))])
    ctx.fill()
    ctx.restore()
    col(ctx, '#C3D2E0')
    ellipse(ctx, sx, sy + 6, 70, 18)
    ctx.fill()
    dig = 3.0 < t < 6.5
    p = pose(pack=False, look=0.7 if t < 7 else 0.1, look_y=0.8 if dig else 0.0, mouth=talk(T), blink=blink(T), frost=0.7,
             eyes='open', brows='worried' if t > 5.5 else 'neutral')
    if dig:
        p['arm_r'] = (0.7 + math.sin(t * 9) * 0.4, 0.6)
        p['arm_l'] = (0.3 + math.cos(t * 9) * 0.3, 1.2)
        p['lean'] = 0.25
    if t < 3:
        p['look'] = math.sin(t * 1.5) * 0.8
    # items pulled from pockets
    names = [('knife', 'KNIFE', 'Knife'), ('firesteel', 'FIRE STEEL', 'Fire'), ('blanket', 'EMERGENCY BLANKET', 'Emergency'),
             ('notebook', 'NOTEBOOK', 'Notebook'), ('bars', '2 ENERGY BARS', 'energy'), ('bottle', '½ BOTTLE OF WATER', 'Water')]
    times = [find_word(20, w) for _, _, w in names]
    hold = None
    for (it, nm, w), tt in zip(names, times):
        if tt - 0.4 < t < tt + 0.5:
            hold = it
    if hold and t < 17:
        p['arm_r'] = (0.9, 1.6)
        p['item_r'] = hold
    draw_range(ctx, 1000, 1020, 1.0, p, t)
    # pocket highlight
    tp = find_word(21, 'Pockets')
    if t > tp - 0.2:
        k = 0.5 + 0.5 * math.sin((t - tp) * 6)
        col(ctx, P['yellow'], 0.6 * k * (1 - seg(t, tp + 2.5, tp + 3)))
        ctx.set_line_width(6)
        for dx in (-30, 30):
            rrect(ctx, 1000 + dx - 22, 1020 - 230, 44, 40, 8)
        ctx.stroke()
    # old inventory: crossed out
    olds = [('FOOD', 'food'), ('FUEL', 'pack'), ('RADIO', 'radio'), ('MAP', 'map')]
    a0 = ease(seg(t, 6.5, 7.0))
    if a0 > 0:
        panel(ctx, 1180, 120, 690, 110, a0)
        set_font(ctx, 46)
        x = 1225
        for nm, w in olds:
            draw_text(ctx, nm, x, 192, 46, '#FFFFFF', align='left', alpha=a0, shadow=False)
            tw = text_w(ctx, nm)
            tt = find_word(20, w)
            k = ease(seg(t, tt, tt + 0.35))
            if k > 0:
                col(ctx, P['red'], a0)
                ctx.set_line_width(8)
                ctx.move_to(x - 6, 176)
                ctx.line_to(x - 6 + (tw + 12) * k, 176)
                ctx.stroke()
            set_font(ctx, 46)
            x += tw + 34
    # new list (pocket items) as icon row along the bottom-top area
    for k, ((it, nm, w), tt) in enumerate(zip(names, times)):
        pr = ease_out(seg(t, tt + 0.3, tt + 0.8))
        if pr <= 0:
            continue
        x = 150 + (k % 3) * 270
        y = 300 + (k // 3) * 250
        panel(ctx, x - 125, y - 105, 250, 210, pr)
        draw_item(ctx, it, x, y - 15, 1.15, t)
        label(ctx, nm, x, y + 80, pr, 22 if len(nm) > 12 else 28, P['yellow'])
    vignette(ctx, 0.4)


# =============================================================== 14 Shelter First
def s14(ctx, t, T, d):
    tilt = 0.0
    if 2.0 < t < 6.0:
        tilt = -ease(seg(t, 2.2, 3.2)) * (1 - ease(seg(t, 3.8, 4.6))) + ease(seg(t, 4.0, 5.2)) * 0.8 * (1 - ease(seg(t, 6.0, 7.0)))
    ctx.save()
    cam(ctx, 1.0, W / 2, H / 2 + tilt * 120)
    sky(ctx, '#3F5D8A', '#F0A766', -200, H)
    sun(ctx, 1420, 520, 62, '#FFC872', 0.45)
    mountains(ctx, 141, 560, 300, '#6E6789', '#E7C3B3')
    mountains(ctx, 142, 700, 220, '#4F4C6B', '#D7B3A8')
    # dark forest line far below
    forest(ctx, 143, 830, 60, 30, 50, '#1C2D2C', '#16241F', snow=0.3)
    col(ctx, '#E8E2E4')
    poly(ctx, [(-200, 860), (W + 200, 780), (W + 200, H + 300), (-200, H + 300)])
    ctx.fill()
    ctx.restore()
    # wind streamers off the ridge
    for i in range(7):
        ph = (t * 0.35 + i / 7) % 1
        y = 250 + i * 60
        col(ctx, '#FFFFFF', 0.18 * math.sin(ph * math.pi))
        ctx.set_line_width(14)
        ctx.move_to(-200 + ph * W * 1.4, y)
        ctx.curve_to(ph * W * 1.4 + 100, y - 30, ph * W * 1.4 + 300, y + 20, ph * W * 1.4 + 520, y - 10)
        ctx.stroke()
    shiver = math.sin(t * 40) * 3 if t > find_word(23, 'damp') else 0
    lk_y = -1.0 if 2.2 < t < 4.0 else (0.9 if 4.0 < t < 6.5 else 0.0)
    p = pose(pack=False, look=-0.4 if t < 4 else 0.5, look_y=lk_y, mouth=talk(T), blink=blink(T), frost=0.9,
             breath=t * 0.7, brows='worried', hood=t > 30, arm_l=(0.5, 2.2) if t > find_word(23, 'damp') else (0.12, 0),
             arm_r=(0.5, 2.2) if t > find_word(23, 'damp') else (0.12, 0))
    draw_range(ctx, 420 + shiver, 1010, 1.05, p, t)
    snowfall(ctx, t, 160, 30, (1.5, 3.5), 0.8, wind=-420, seed=14)
    # rule of threes cards
    keys = [('minutes', '3 MINUTES', 'AIR'), ('hours', '3 HOURS', 'SHELTER'), ('days', '3 DAYS', 'WATER'),
            ('weeks', '3 WEEKS', 'FOOD')]
    tr = find_word(23, 'rule')
    tgone = find_word(23, 'damp')
    tair = find_word(23, 'air', 1)
    tcold = find_word(23, 'cold', 1)
    a_all = ease(seg(t, tr, tr + 0.5)) * (1 - ease(seg(t, tgone, tgone + 0.6)))
    if a_all > 0:
        draw_text(ctx, 'RULE OF THREES', 1260, 150, 60, P['yellow'], alpha=a_all, outline=8)
        for k, (w, big, small) in enumerate(keys):
            tt = find_word(23, w)
            pr = ease_out(seg(t, tt - 0.3, tt + 0.3)) * a_all
            if pr <= 0:
                continue
            x = 880 + k * 250
            y = 380
            hl = 0.0
            if k == 1 and t > tcold:
                hl = 0.5 + 0.5 * math.sin((t - tcold) * 7)
            panel(ctx, x - 110, y - 130, 220, 300, pr, c=mix('#11161D', '#5A1C16', hl))
            # icon
            ctx.save()
            ctx.translate(x, y - 40)
            col(ctx, '#FFFFFF', pr)
            if small == 'AIR':
                ctx.set_line_width(8)
                for j in range(3):
                    ctx.move_to(-50, -25 + j * 25)
                    ctx.curve_to(-10, -45 + j * 25, 10, -5 + j * 25, 50, -25 + j * 25)
                ctx.stroke()
            elif small == 'SHELTER':
                poly(ctx, [(-55, 10), (0, -45), (55, 10)])
                ctx.fill()
                ctx.rectangle(-40, 10, 80, 45)
                ctx.fill()
            elif small == 'WATER':
                ctx.move_to(0, -55)
                ctx.curve_to(40, -5, 40, 45, 0, 45)
                ctx.curve_to(-40, 45, -40, -5, 0, -55)
                ctx.fill()
            else:
                ellipse(ctx, 0, 5, 45, 40)
                ctx.fill()
                col(ctx, '#11161D', pr)
                ctx.rectangle(-3, -45, 6, 16)
                ctx.fill()
            ctx.restore()
            draw_text(ctx, big, x, y + 70, 34, P['yellow'], alpha=pr, outline=0)
            draw_text(ctx, small, x, y + 120, 32, '#FFFFFF', alpha=pr, outline=0)
            if k == 0 and t > tair:
                check_mark(ctx, x + 70, y - 100, 40, '#6FD38A', ease(seg(t, tair, tair + 0.4)) * a_all)
    lesson_card(ctx, 'SHELTER FIRST. COLD KILLS FASTER THAN HUNGER', seg(t, 33.0, 34.5), num=4)
    vignette(ctx, 0.5)


# =============================================================== 15 A Roof in the Trees
def s15(ctx, t, T, d):
    stop = 12.0
    pan = ease(seg(t, stop, stop + 3.5))
    ctx.save()
    cam(ctx, 1.0, W / 2 + pan * 380, H / 2)
    sky(ctx, '#4A4F7A', '#F39A55', -100, H)
    sun(ctx, 1500, 430, 55, '#FFB862', 0.5)
    mountains(ctx, 151, 520, 260, '#6A5B7E', '#E9B59A', x1=W + 900)
    # valley forest with the cabin roof among trees
    forest(ctx, 152, 760, 40, 110, 190, '#253B37', '#1F332F', snow=0.4, x0=200, x1=W + 800)
    # cabin roof line (a straight line among trees)
    rx, ry = 1960, 770
    col(ctx, '#3B2A1E')
    poly(ctx, [(rx - 200, ry), (rx, ry - 110), (rx + 200, ry)])
    ctx.fill()
    col(ctx, P['snow'])
    poly(ctx, [(rx - 214, ry - 4), (rx, ry - 124), (rx + 214, ry - 4), (rx + 190, ry + 10), (rx, ry - 90), (rx - 190, ry + 10)])
    ctx.fill()
    if t > stop + 2.5:
        k = ease(seg(t, stop + 2.5, stop + 3.3))
        col(ctx, P['yellow'], k)
        ctx.set_line_width(7)
        ctx.move_to(rx - 214, ry - 4)
        ctx.line_to(rx, ry - 124)
        ctx.line_to(rx + 214, ry - 4)
        ctx.stroke()
    forest(ctx, 153, 900, 10, 160, 260, '#1E302D', '#192926', snow=0.5, x0=1500, x1=2400)
    # slope with rocks, path along slide edge
    col(ctx, '#EDE3E0')
    poly(ctx, [(-300, 760), (1300, 980), (1300, H + 300), (-300, H + 300)])
    ctx.fill()
    col(ctx, '#5A5560')
    for x, y, rr in ((150, 820, 60), (520, 880, 50), (980, 950, 70), (-100, 800, 70)):
        poly(ctx, [(x - rr, y + rr * 0.4), (x - rr * 0.4, y - rr * 0.6), (x + rr * 0.5, y - rr * 0.5), (x + rr, y + rr * 0.4)])
        ctx.fill()
    walk = seg(t, 0, stop)
    x = lerp(150, 900, ease(walk) * 0.2 + walk * 0.8)
    y = 760 + (x + 300) / 1600 * 220 + 60
    if t < stop:
        p = walk_pose(t * 4.5, look=0.6, frost=0.7, breath=t * 0.6, brows='neutral')
    else:
        p = pose(look=0.9, look_y=0.2, eyes='wide' if t > stop + 2.5 else 'open', brows='raised' if t > stop + 2.5 else 'neutral',
                 mouth=talk(T), frost=0.7, breath=t * 0.6, mouth_shape='smile' if t > 16.6 else 'line')
    p['blink'] = blink(T)
    draw_range(ctx, x, y, 0.85, p, t)
    # foreground trees passing
    forest(ctx, 154, 1150, 5, 500, 700, '#132320', '#0F1C1A', snow=0.3, x0=-200, x1=1600, offset=t * 40)
    ctx.restore()
    overlay(ctx, '#FF8A3D', 0.08)
    vignette(ctx, 0.5)


# =============================================================== 16 The Hunter's Cabin
def s16(ctx, t, T, d):
    close = t > 11.5
    if not close:
        ctx.save()
        cam(ctx, 1.0, W / 2 + t * 25, H / 2)
        sky(ctx, '#2F3557', '#C9825A')
        mountains(ctx, 161, 520, 240, '#4C4A68', '#B99A95', x1=W + 600)
        forest(ctx, 162, 700, 40, 220, 360, '#1B2B29', '#162422', snow=0.4, x0=-200, x1=W + 700)
        col(ctx, '#E4DEE2')
        ctx.rectangle(-300, 820, W + 1200, 600)
        ctx.fill()
        cabin(ctx, 1420, 860, 1.0, sag=1.0, snow_drift=1.3)
        # tree with trap beside the cabin
        col(ctx, '#3A2A20')
        ctx.rectangle(1820, 380, 50, 500)
        ctx.fill()
        trap(ctx, 1845, 620, 0.9)
        pine(ctx, 1845, 520, 420, '#1B2B29', '#162422', snow=0.5)
        x = lerp(300, 900, seg(t, 0, 11))
        p = walk_pose(t * 3.4, 0.7, look=0.7, frost=0.7, breath=t * 0.6, brows='neutral', blink=blink(T))
        draw_range(ctx, x, 1010, 0.9, p, t)
        # deep snow over his legs
        col(ctx, '#EEE9EC')
        ellipse(ctx, x, 1010, 160, 70)
        ctx.fill()
        col(ctx, '#D6CFD6')
        for k in range(6):
            ellipse(ctx, x - 140 - k * 120, 1000 + (k % 2) * 6, 60, 22)
            ctx.fill()
        ctx.restore()
    else:
        lt = t - 11.5
        sky(ctx, '#2F3557', '#B9785A')
        forest(ctx, 163, 760, 20, 300, 500, '#1B2B29', '#162422', snow=0.4)
        col(ctx, '#E4DEE2')
        ctx.rectangle(0, 900, W, 200)
        ctx.fill()
        col(ctx, '#3A2A20')
        ctx.rectangle(1180, -50, 120, 1000)
        ctx.fill()
        col(ctx, '#2C1F17')
        for k in range(8):
            ctx.rectangle(1195 + (k % 3) * 30, k * 120, 6, 80)
        ctx.fill()
        trap(ctx, 1240, 430, 2.4)
        reach = ease(seg(lt, 0.5, 1.6))
        p = pose(look=0.8, look_y=-0.1, arm_r=(lerp(0.12, 1.5, reach), lerp(0, 0.2, reach)), mouth=talk(T), frost=0.7,
                 blink=blink(T), brows='raised' if lt > 2 else 'neutral')
        draw_range(ctx, 860, 1180, 1.6, p, t)
    overlay(ctx, '#3B2A5A', 0.12)
    vignette(ctx, 0.55)


# =============================================================== 17 Check Before You Trust
def s17(ctx, t, T, d):
    troof = find_word(28, 'roof')
    tcar = find_word(28, 'car')
    tlook = find_word(28, 'Look', 1)
    ctx.save()
    zr = ease(seg(t, troof - 0.5, troof + 1.0)) * (1 - ease(seg(t, 23.0, 24.5)))
    cam(ctx, 1 + 0.35 * zr, lerp(W / 2, 1150, zr), lerp(H / 2, 470, zr))
    sky(ctx, '#252B4A', '#8E6A6A')
    forest(ctx, 171, 700, 34, 260, 420, '#18262A', '#131F22', snow=0.4)
    col(ctx, '#DCD8E0')
    ctx.rectangle(-300, 820, W + 600, 600)
    ctx.fill()
    cabin(ctx, 960, 860, 1.25, sag=1.0, snow_drift=1.1)
    # sagging corner highlight
    if t > troof:
        k = ease(seg(t, troof, troof + 0.5))
        col(ctx, P['red'], k * (0.6 + 0.4 * math.sin(t * 6)))
        ctx.set_line_width(8)
        ctx.set_dash([22, 14])
        ctx.move_to(960 + 1.25 * 105, 860 - 1.25 * 260)
        ctx.line_to(960 + 1.25 * 272, 860 - 1.25 * 180)
        ctx.stroke()
        ctx.set_dash([])
    # car weight icon
    if tcar - 0.2 < t < tlook + 3:
        k = ease(seg(t, tcar - 0.2, tcar + 0.4)) * (1 - ease(seg(t, tlook + 2.2, tlook + 3)))
        cx, cy = 1250, 400 - 60 * (1 - k)
        col(ctx, '#C0392B', k)
        rrect(ctx, cx - 90, cy - 30, 180, 50, 14)
        ctx.fill()
        rrect(ctx, cx - 55, cy - 70, 110, 50, 16)
        ctx.fill()
        col(ctx, '#9FD3F0', k)
        ctx.rectangle(cx - 40, cy - 60, 35, 30)
        ctx.rectangle(cx + 5, cy - 60, 35, 30)
        ctx.fill()
        col(ctx, '#111', k)
        ctx.arc(cx - 50, cy + 22, 20, 0, 2 * math.pi)
        ctx.arc(cx + 50, cy + 22, 20, 0, 2 * math.pi)
        ctx.fill()
        arrow(ctx, cx, cy + 50, cx, cy + 120, '#FFFFFF', 10, k, 30)
        label(ctx, 'WET SNOW = WEIGHT OF A CAR', cx, cy - 100, k, 34, P['yellow'])
    # Range circles the cabin: walks left -> right in front, stops, knocks, draws line
    if t < 12:
        x = lerp(380, 1500, seg(t, 0.5, 12))
        p = walk_pose(t * 4, 0.8, look=0.5, look_y=-0.6, frost=0.6, breath=t * 0.6, blink=blink(T))
    else:
        x = 1500 if t < 22 else lerp(1500, 1350, seg(t, 24, 28))
        p = pose(look=-0.6, look_y=-1.0 if t < 22 else 0.6, frost=0.6, breath=t * 0.6, blink=blink(T), mouth=talk(T),
                 brows='angry' if t > 28 else 'neutral')
        if tlook < t < tlook + 3.5:
            k = math.sin((t - tlook) * 12)
            p['arm_l'] = (1.3, 0.3 + 0.2 * k)
            p['item_l'] = 'knife'
        if 24 < t < 28:
            p['leg_l'] = (-0.5, 0.2)
            p['look_y'] = 1.0
        if t > 28.5:
            p['arm_l'] = (1.9, 0.1)
    draw_range(ctx, x, 1010, 0.95, p, t)
    if t > 24:
        k = seg(t, 24, 28)
        col(ctx, '#6E6A78')
        ctx.set_line_width(7)
        ctx.move_to(1600, 1040)
        ctx.line_to(1600 - 480 * k, 1040 - 20 * k)
        ctx.stroke()
    ctx.restore()
    top_title(ctx, 'CHECK #1: ROOF', seg(t, troof, troof + 0.5), y=130, size=64)
    overlay(ctx, '#2A2050', 0.12)
    vignette(ctx, 0.55)


# =============================================================== 18 Floor and Chimney
def interior(ctx, light=0.0, fire=0.0, t=0.0, dark=0.0):
    # back wall logs
    for i in range(12):
        col(ctx, mix('#4A3424' if i % 2 == 0 else '#3F2C1F', '#2B1E15', dark))
        ctx.rectangle(-200, -60 + i * 80, W + 400, 82)
        ctx.fill()
    # floor boards
    col(ctx, mix('#5B4130', '#2B1E15', dark))
    ctx.rectangle(-200, 860, W + 400, 400)
    ctx.fill()
    col(ctx, '#2E2016')
    ctx.set_line_width(4)
    for k in range(-6, 16):
        ctx.move_to(k * 160, 860)
        ctx.line_to(k * 160 - 220, 1100)
    ctx.stroke()
    # traps on the wall
    for x in (380, 560):
        trap(ctx, x, 360, 1.0)
    # bunk frame
    col(ctx, '#3A2618')
    ctx.rectangle(60, 640, 520, 30)
    ctx.rectangle(60, 640, 26, 240)
    ctx.rectangle(554, 640, 26, 240)
    ctx.fill()
    # stove + pipe
    col(ctx, '#2A2A2C')
    rrect(ctx, 1380, 640, 260, 240, 20)
    ctx.fill()
    ctx.rectangle(1480, -100, 60, 750)
    ctx.fill()
    col(ctx, '#1B1B1D')
    rrect(ctx, 1420, 700, 180, 120, 14)
    ctx.fill()
    if fire > 0:
        col(ctx, '#FF8A2A', fire)
        rrect(ctx, 1430, 712, 160, 100, 12)
        ctx.fill()
        for i in range(5):
            fl = 0.6 + 0.4 * math.sin(t * 13 + i * 2)
            col(ctx, '#FFD34D', fire)
            ellipse(ctx, 1460 + i * 26, 790 - 20 * fl, 14, 30 * fl)
            ctx.fill()
    col(ctx, '#3A3A3D')
    ctx.rectangle(1360, 870, 300, 16)
    ctx.fill()


def s18(ctx, t, T, d):
    tfloor = find_word(30, 'Second')
    tdrop = find_word(30, 'droppings')
    tchew = find_word(30, 'chewed')
    tnest = find_word(30, 'nest')
    tchim = find_word(31, 'chimney')
    tco = find_word(31, 'carbon')
    tsee = find_word(31, 'see')
    tsmell = find_word(31, 'smell')
    thead = find_word(31, 'headache')
    tsleepy = find_word(31, 'sleepy')
    tclear = find_word(31, 'clear')
    col(ctx, '#1A120C')
    ctx.paint()
    door = ease(seg(t, 0.0, 1.5))
    interior(ctx)
    # light beam from the open door
    light_beam(ctx, 0, 300, 0.35, 1500, 300, 700, 0.18 * door, '#CFE0F5')
    # dust motes
    r = random.Random(4)
    for i in range(60):
        x = (r.uniform(0, 1200) + math.sin(t * 0.3 + i) * 30)
        y = (r.uniform(300, 900) + math.cos(t * 0.2 + i) * 20)
        col(ctx, '#FFFFFF', 0.25 + 0.2 * math.sin(t + i))
        ctx.arc(x, y, 2, 0, 2 * math.pi)
        ctx.fill()
    # Range path: steps across the floor, testing each board
    if t < 14.5:
        steps = seg(t, 1.5, 14.0)
        x = lerp(200, 1180, steps)
        ph = (t - 1.5) * 2.2
        p = walk_pose(ph, 0.55, look=0.4, look_y=0.9, frost=0.3, blink=blink(T), brows='neutral')
        # highlight the board under the front foot
        bx = x + 60
        k = 0.5 + 0.5 * math.sin(ph * 2)
        if t > tfloor - 0.5:
            col(ctx, P['yellow'], 0.25 * k)
            poly(ctx, [(bx - 70, 1000), (bx + 70, 1000), (bx + 40, 1060), (bx - 100, 1060)])
            ctx.fill()
    elif t < 38:
        x = 1180
        pull = ease(seg(t, 15.0, 16.5))
        p = pose(look=0.9, look_y=-0.4 if t < 17 else 0.2, frost=0.3, blink=blink(T), arm_r=(lerp(0.2, 1.4, pull), lerp(0, 0.8, pull)),
                 brows='raised' if 16.5 < t < 19 else 'neutral', mouth=talk(T))
        if t > 16.2:
            p['item_r'] = 'nest' if t < 19 else None
            if t > 19:
                p['arm_r'] = (0.2, 0.2)
    else:
        x = 1180
        p = pose(look=0.8, look_y=-1.0, mouth=talk(T), blink=blink(T), frost=0.3, mouth_shape='smile', brows='raised')
    draw_range(ctx, x, 1020, 0.95, p, t)
    # tossed nest
    if 19 < t < 21:
        k = seg(t, 19, 21)
        draw_item(ctx, 'nest', lerp(1300, 900, k), 820 - math.sin(k * math.pi) * 200 + k * 200, 1.0, t)
    elif t > 21:
        draw_item(ctx, 'nest', 900, 1020, 1.0, t)
    # animal-sign callouts
    for tt, nm, xx in ((tdrop, 'DROPPINGS', 300), (tchew, 'CHEWED WOOD', 700), (tnest, 'NESTS', 1100)):
        if tt - 0.2 < t < 15.5:
            k = ease(seg(t, tt - 0.2, tt + 0.3))
            panel(ctx, xx - 150, 150, 300, 90, k)
            label(ctx, nm, xx, 210, k, 34, P['yellow'])
    # CO diagram
    if tco - 0.5 < t < tclear + 1.0:
        k = ease(seg(t, tco - 0.5, tco + 0.3)) * (1 - ease(seg(t, tclear, tclear + 1.0)))
        r = random.Random(8)
        for i in range(40):
            cx = 900 + r.uniform(-700, 700) + math.sin(t * 0.8 + i) * 40
            cy = 500 + r.uniform(-300, 200) + math.cos(t * 0.6 + i) * 30
            col(ctx, '#9AA0A8', 0.12 * k)
            ctx.arc(cx, cy, r.uniform(60, 140), 0, 2 * math.pi)
            ctx.fill()
        for i in range(8):
            cx = 900 + r.uniform(-600, 600) + math.sin(t + i) * 30
            cy = 450 + r.uniform(-250, 200) - (t * 20 % 60)
            col(ctx, '#D7DCE2', 0.7 * k)
            ctx.arc(cx, cy, 34, 0, 2 * math.pi)
            ctx.fill()
            draw_text(ctx, 'CO', cx, cy + 12, 30, '#30363E', alpha=k, shadow=False)
        icons = [(tsee, "CAN'T SEE IT"), (tsmell, "CAN'T SMELL IT"), (thead, 'HEADACHE'), (tsleepy, 'SLEEPY → DANGER')]
        for j, (tt, nm) in enumerate(icons):
            kk = ease(seg(t, tt - 0.2, tt + 0.3)) * k
            if kk > 0:
                panel(ctx, 60, 140 + j * 110, 460, 90, kk)
                label(ctx, nm, 290, 200 + j * 110, kk, 34, '#FFFFFF' if j < 2 else P['yellow'])
    # view up the clear pipe
    if t > 38.0:
        k = ease(seg(t, 38.0, 38.8))
        panel(ctx, 1580, 160, 300, 300, k, c='#0B0B0C')
        col(ctx, '#9AA6B4', k)
        ctx.arc(1730, 310, 90, 0, 2 * math.pi)
        ctx.fill()
        col(ctx, '#C2CCD6', k)
        ellipse(ctx, 1700, 290, 50, 20)
        ctx.fill()
    top_title(ctx, 'CHECK #2: FLOOR', seg(t, tfloor, tfloor + 0.5) * (1 - seg(t, tchim - 0.6, tchim - 0.2)), y=120, size=60)
    top_title(ctx, 'CHECK #3: CHIMNEY', seg(t, tchim, tchim + 0.5) * (1 - seg(t, tco - 0.8, tco - 0.4)), y=120, size=60)
    if t > tclear:
        k = ease(seg(t, tclear, tclear + 0.6))
        for j in range(3):
            arrow(ctx, 1510, 600 - j * 10, 1510, 120 - j * 10, '#DADDE2', 10, seg(t, tclear + j * 0.2, tclear + 1 + j * 0.2), 28)
    lesson_card(ctx, 'BEFORE YOU MOVE IN: ROOF · FLOOR · CHIMNEY', seg(t, 41.0, 42.5), num=5)
    vignette(ctx, 0.6)


# =============================================================== 19 First Fire
def s19(ctx, t, T, d):
    flame = ease(seg(t, 4.3, 12.0))
    col(ctx, '#140D08')
    ctx.paint()
    ctx.save()
    cam(ctx, 1.35, 1220, 640)
    interior(ctx, fire=flame, t=t, dark=0.35 * (1 - flame))
    strikes = (1.8, 2.7, 3.6, 4.2)
    strike = any(s - 0.05 < t < s + 0.2 for s in strikes)
    p = pose(pack=False, look=0.9, look_y=0.6, frost=0.2, blink=blink(T),
             arm_r=(1.2, 1.4 + (0.4 if strike else 0)), arm_l=(0.9, 1.6), item_r='firesteel' if t < 6 else None,
             item_l='knife' if t < 6 else None, mouth_shape='smile' if t > 8 else 'line', eyes='open')
    if t < 1.6:
        p['item_r'] = None
        p['item_l'] = None
        p['arm_r'] = (0.9 + math.sin(t * 10) * 0.2, 1.4)
    draw_range(ctx, 1150, 1130, 1.0, p, t)
    # sparks
    for s in strikes:
        k = seg(t, s, s + 0.6)
        if 0 < k < 1:
            r = random.Random(int(s * 10))
            for i in range(18):
                a = r.uniform(-2.6, -0.4)
                v = r.uniform(80, 220)
                col(ctx, '#FFD25A', 1 - k)
                ctx.arc(1420 + math.cos(a) * v * k, 780 + math.sin(a) * v * k + 120 * k * k, 3, 0, 2 * math.pi)
                ctx.fill()
    ctx.restore()
    # warm light filling the cabin
    glow(ctx, 1450, 760, 1400, '#FF9A3C', 0.35 * flame * (0.9 + 0.1 * math.sin(t * 11)))
    overlay(ctx, '#000000', 0.45 * (1 - flame))
    vignette(ctx, 0.65)


# =============================================================== 20 Day Four (notebook)
def s20(ctx, t, T, d):
    col(ctx, '#140D08')
    ctx.paint()
    ctx.save()
    z = lerp(1.15, 1.45, ease(seg(t, 10.5, d)))
    cam(ctx, z, 1050, 620)
    interior(ctx, fire=0.9, t=t)
    p = pose(pack=False, blanket=True, look=-0.2, look_y=0.9 if t < 10.5 else 0.3, item_r='notebook', item_l='pencil',
             arm_r=(0.7, 1.5), arm_l=(0.6, 1.7 + math.sin(t * 6) * 0.08 * (2 < t < 9)), blink=blink(T),
             eyes='open', mouth_shape='line' if t < 12 else 'smile', frost=0.0)
    draw_range(ctx, 1000, 1110, 1.0, p, t)
    ctx.restore()
    glow(ctx, 1450, 760, 1300, '#FF9A3C', 0.32 * (0.9 + 0.1 * math.sin(t * 11)))
    # notebook page inset with handwriting synced to his voice
    s, off = line_scene(34)
    wt = word_times(34)
    a = ease(seg(t, 1.5, 2.2)) * (1 - ease(seg(t, 10.0, 10.8)))
    if a > 0:
        panel(ctx, 1180, 160, 640, 520, a, c='#E9DFC7')
        col(ctx, '#B9C9DA', a)
        ctx.set_line_width(2)
        for k in range(8):
            ctx.move_to(1210, 250 + k * 52)
            ctx.line_to(1790, 250 + k * 52)
        ctx.stroke()
        written = [w for w, a0, b0 in wt if t > off + a0]
        lines_out, cur = [], ''
        set_font(ctx, 40, cairo.FONT_WEIGHT_NORMAL, 'DejaVu Serif')
        for w in written:
            cand = (cur + ' ' + w).strip()
            if text_w(ctx, cand) > 560:
                lines_out.append(cur)
                cur = w
            else:
                cur = cand
        if cur:
            lines_out.append(cur)
        for k, ln in enumerate(lines_out):
            ctx.select_font_face('DejaVu Serif', cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(38)
            col(ctx, '#2B2A4A', a)
            ctx.move_to(1215, 240 + k * 52)
            ctx.show_text(ln)
    vignette(ctx, 0.6)


# =============================================================== 21 Survival Notes
def s21(ctx, t, T, d):
    ctx.save()
    cam(ctx, lerp(1.0, 1.25, ease(t / d)), 1250, 640)
    sky(ctx, '#0B1226', '#25304F')
    col(ctx, '#E9EEF5')
    ctx.arc(320, 180, 50, 0, 2 * math.pi)
    ctx.fill()
    r = random.Random(3)
    for i in range(80):
        col(ctx, '#FFFFFF', 0.3 + 0.4 * math.sin(t + i))
        ctx.arc(r.uniform(0, W), r.uniform(0, 500), 1.5, 0, 2 * math.pi)
        ctx.fill()
    forest(ctx, 211, 760, 40, 260, 420, '#0E1A1C', '#0B1517', snow=0.3)
    col(ctx, '#BFC8D8')
    ctx.rectangle(-300, 840, W + 600, 500)
    ctx.fill()
    cabin(ctx, 1250, 880, 1.15, sag=1.0, snow_drift=1.0, window_light=1.0, smoke=1.0, t=t)
    ctx.restore()
    overlay(ctx, '#0A1530', 0.25)
    snowfall(ctx, t, 140, 50, (1.5, 3.5), 0.8, wind=20, seed=21)
    rows = [('One', 'WHUMPF OR CRACKS = GET OFF THE SLOPE', 'crack'),
            ('Two', 'ONE HAND UP, ONE OVER YOUR FACE', 'hand'),
            ('Three', 'LET GRAVITY TELL YOU WHICH WAY IS UP', 'drop'),
            ('Four', 'SHELTER FIRST', 'house'),
            ('Five', 'ROOF · FLOOR · CHIMNEY', 'roof'),
            ('bonus', 'NEVER TRAVEL IN AVALANCHE COUNTRY ALONE', 'partner')]
    for k, (w, txt, ic) in enumerate(rows):
        tt = find_word(36, w)
        pr = ease_out(seg(t, tt - 0.2, tt + 0.4))
        if pr <= 0:
            continue
        y = 150 + k * 128
        x = 70 - 40 * (1 - pr)
        set_font(ctx, 36)
        wbox = text_w(ctx, txt) + 190
        bonus = k == 5
        panel(ctx, x, y, wbox, 100, pr, c='#3A1A14' if bonus else '#11161D')
        col(ctx, P['yellow'], pr)
        ctx.arc(x + 55, y + 50, 32, 0, 2 * math.pi)
        ctx.fill()
        n = '★' if bonus else str(k + 1)
        draw_text(ctx, n, x + 55, y + 63, 36, '#11161D', alpha=pr, shadow=False, family='DejaVu Sans' if bonus else None)
        draw_text(ctx, txt, x + 110, y + 63, 36, P['yellow'] if not bonus else '#FFB4A6', align='left', alpha=pr, shadow=False)
    vignette(ctx, 0.55)


# =============================================================== 22 The Howl
def wolf_eyes(ctx, x, y, s, a):
    for dx in (-1, 1):
        glow(ctx, x + dx * 14 * s, y, 30 * s, '#FFD36A', 0.5 * a)
        col(ctx, '#FFE7A0', a)
        ellipse(ctx, x + dx * 14 * s, y, 7 * s, 4 * s)
        ctx.fill()


def s22(ctx, t, T, d):
    outside = 6.0 < t < 10.5
    if t < 19.5 and not outside:
        col(ctx, '#0A0705')
        ctx.paint()
        ctx.save()
        cam(ctx, 1.25, 1080, 640)
        interior(ctx, fire=0.45, t=t, dark=0.55)
        awake = t > 3.0
        turn = ease(seg(t, 11.5, 13.5))
        p = pose(pack=False, blanket=True, eyes='wide' if awake else 'closed', brows='worried' if awake else 'neutral',
                 head_tilt=0.0 if awake else 0.25, look=lerp(0.2, -1.0, turn) if awake else 0.0, mouth=talk(T),
                 blink=0.0, frost=0.0, arm_r=(0.4, 1.4), arm_l=(0.4, 1.4))
        if not awake:
            p['mouth_shape'] = 'line'
        draw_range(ctx, 1000, 1110, 1.0, p, t)
        ctx.restore()
        glow(ctx, 1450, 760, 900, '#FF8A2A', 0.2 * (0.9 + 0.1 * math.sin(t * 9)))
        if not awake:
            for i in range(3):
                ph = (t * 0.6 + i / 3) % 1
                draw_text(ctx, 'z', 1120 + ph * 80, 380 - ph * 120, 40 + ph * 30, '#FFFFFF', alpha=1 - ph, shadow=False)
        overlay(ctx, '#0A1530', 0.25)
        # door on the left, the howls come from there
        if t > 11.0:
            k = 0.5 + 0.5 * math.sin(t * 2)
            col(ctx, '#4B6B9A', 0.08 * k)
            ctx.rectangle(0, 0, 220, H)
            ctx.fill()
        vignette(ctx, 0.8)
    elif outside:
        lt = t - 6.0
        sky(ctx, '#060A16', '#141D33')
        col(ctx, '#DDE4EE')
        ctx.arc(1500, 200, 70, 0, 2 * math.pi)
        ctx.fill()
        glow(ctx, 1500, 200, 400, '#9FB4D8', 0.2)
        forest(ctx, 221, 760, 40, 300, 460, '#060B0D', '#04080A')
        col(ctx, '#1E2638')
        ctx.rectangle(0, 820, W, 300)
        ctx.fill()
        forest(ctx, 222, 1000, 12, 500, 700, '#020405', '#020405')
        # howl rings
        for i in range(3):
            ph = (lt * 0.5 + i / 3) % 1
            col(ctx, '#9FB4D8', 0.25 * (1 - ph))
            ctx.set_line_width(4)
            ctx.arc(700, 700, 60 + ph * 500, math.pi * 1.1, math.pi * 1.9)
            ctx.stroke()
        for k, (x, y, tt) in enumerate(((620, 820, 0.4), (980, 860, 1.4), (1300, 840, 3.0))):
            a = ease(seg(lt, tt, tt + 0.6)) * (0.7 + 0.3 * math.sin(lt * 3 + k))
            if a > 0:
                wolf_eyes(ctx, x + math.sin(lt + k) * 6, y + (k * 8), 1.0 + k * 0.15, a)
        vignette(ctx, 0.8)
    else:
        # end card
        lt = t - 19.5
        col(ctx, '#07090D')
        ctx.paint()
        a = ease(seg(lt, 0.2, 1.2))
        draw_text(ctx, 'THE PACK', W / 2, 400, 160, '#FFFFFF', alpha=a, outline=10)
        draw_text(ctx, 'PART 2: COLD COUNT', W / 2, 500, 70, P['yellow'], alpha=a, outline=8)
        b = ease(seg(lt, 1.2, 2.0))
        col(ctx, '#E62117', b)
        rrect(ctx, W / 2 - 230, 600, 460, 100, 20)
        ctx.fill()
        draw_text(ctx, 'SUBSCRIBE', W / 2, 668, 52, '#FFFFFF', alpha=b, shadow=False)
        draw_text(ctx, "so you don't miss it", W / 2, 770, 40, '#C9D1DC', alpha=b, shadow=False)
        for i in range(3):
            ph = (lt * 0.4 + i / 3) % 1
            wolf_eyes(ctx, 300 + i * 650, 950, 0.8, 0.4 * math.sin(ph * math.pi) * a)
        overlay(ctx, '#000000', ease(seg(lt, 5.5, 6.5)))
