"""Render frames -> video segments (multiprocess), then concat."""
import os
import sys
import math
import subprocess
import random
import multiprocessing as mp
import numpy as np
import cairo
from engine import W, H, FPS, rich_line, P, col, overlay
import scenes_a as A
import scenes_b as B
from timeline import EDL, SCENE_START, TOTAL, subtitle_at

SCENES = {1: A.s01, 2: A.s02, 3: A.s03, 4: A.s04, 5: A.s05, 6: A.s06, 7: A.s07, 8: A.s08, 9: A.s09, 10: A.s10,
          11: A.s11, 12: B.s12, 13: B.s13, 14: B.s14, 15: B.s15, 16: B.s16, 17: B.s17, 18: B.s18, 19: B.s19,
          20: B.s20, 21: B.s21, 22: B.s22}
HERE = os.path.dirname(os.path.abspath(__file__))

_grain = None


def grain():
    global _grain
    if _grain is None:
        rng = np.random.default_rng(1)
        a = (rng.random((H, W)) * 255).astype(np.uint8)
        buf = np.zeros((H, W, 4), dtype=np.uint8)
        buf[..., 0] = a
        buf[..., 1] = a
        buf[..., 2] = a
        buf[..., 3] = 255
        surf = cairo.ImageSurface.create_for_data(memoryview(buf), cairo.FORMAT_ARGB32, W, H, W * 4)
        pat = cairo.SurfacePattern(surf)
        pat.set_extend(cairo.EXTEND_REPEAT)
        _grain = (pat, surf, buf)
    return _grain[0]


def scene_at(T):
    for s in sorted(EDL):
        if T < SCENE_START[s] + EDL[s][0] or s == 22:
            return s, T - SCENE_START[s]


def draw_subtitle(ctx, T):
    sub = subtitle_at(T)
    if not sub:
        return
    words, sp, age = sub
    a = min(1.0, age / 0.08)
    parts = []
    for i, (w, hi) in enumerate(words):
        parts.append((w + (' ' if i < len(words) - 1 else ''), P['yellow'] if hi else P['white']))
    rich_line(ctx, parts, W / 2, 1012, 56, alpha=a, outline=9)


def render_frame(T, surf=None):
    if surf is None:
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    s, lt = scene_at(T)
    ctx.save()
    SCENES[s](ctx, lt, T, EDL[s][0])
    ctx.restore()
    ctx.set_dash([])
    draw_subtitle(ctx, T)
    # film grain
    ctx.save()
    pat = grain()
    r = random.Random(int(T * FPS))
    m = cairo.Matrix()
    m.translate(r.randint(0, W), r.randint(0, H))
    pat.set_matrix(m)
    ctx.set_source(pat)
    ctx.paint_with_alpha(0.035)
    ctx.restore()
    return surf


def render_segment(args):
    idx, f0, f1, out = args
    proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}',
                             '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
                             '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    for f in range(f0, f1):
        render_frame(f / FPS, surf)
        surf.flush()
        proc.stdin.write(surf.get_data())
    proc.stdin.close()
    proc.wait()
    return idx


def main():
    outdir = os.path.join(HERE, 'build', 'seg')
    os.makedirs(outdir, exist_ok=True)
    nframes = int(round(TOTAL * FPS))
    seglen = FPS * 20
    jobs = []
    for i, f0 in enumerate(range(0, nframes, seglen)):
        out = os.path.join(outdir, f'seg{i:04d}.mp4')
        jobs.append((i, f0, min(nframes, f0 + seglen), out))
    only = sys.argv[1:] and [int(x) for x in sys.argv[1:]]
    if only:
        jobs = [j for j in jobs if j[0] in only]
    with mp.Pool(int(os.environ.get('NPROC', mp.cpu_count()))) as pool:
        for i in pool.imap_unordered(render_segment, jobs):
            print('done', i, flush=True)
    with open(os.path.join(outdir, 'list.txt'), 'w') as f:
        for i in range(len(range(0, nframes, seglen))):
            f.write(f"file 'seg{i:04d}.mp4'\n")


if __name__ == '__main__':
    main()
