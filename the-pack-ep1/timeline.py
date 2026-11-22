"""Edit decision list: scene durations, voice cue placement, subtitle + lip-sync timing."""
import os
import re
import subprocess
import functools
import numpy as np
from lines import LINES

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 16000  # analysis rate

# scene: (duration_s, [(line_idx, offset_s), ...])
EDL = {
    1: (26, [(0, 4.0)]),
    2: (12, [(1, 2.5)]),
    3: (34, [(2, 1.5), (3, 22.0)]),
    4: (30, [(4, 3.0), (5, 11.0)]),
    5: (48, [(6, 9.0), (7, 12.0)]),
    6: (17, [(8, 4.8), (9, 9.0)]),
    7: (46, [(10, 2.0)]),
    8: (12, [(11, 4.0)]),
    9: (40, [(12, 3.0), (13, 6.5), (14, 31.0)]),
    10: (36, [(15, 2.0), (16, 31.5)]),
    11: (36, [(17, 4.0)]),
    12: (25, [(18, 7.0), (19, 13.0)]),
    13: (34, [(20, 7.0), (21, 18.5)]),
    14: (40, [(22, 2.5), (23, 6.5)]),
    15: (20, [(24, 1.5), (25, 16.0)]),
    16: (20, [(26, 3.0), (27, 14.0)]),
    17: (34, [(28, 2.0), (29, 28.5)]),
    18: (46, [(30, 2.0), (31, 16.5), (32, 39.0)]),
    19: (20, [(33, 7.0)]),
    20: (21, [(34, 2.0), (35, 11.0)]),
    21: (50, [(36, 3.0)]),
    22: (26, [(37, 14.0), (38, 17.0)]),
}

SCENE_START = {}
_t = 0.0
for _s in sorted(EDL):
    SCENE_START[_s] = _t
    _t += EDL[_s][0]
TOTAL = _t


def vo_path(i):
    return os.path.join(HERE, 'audio', 'vo', f'L{i:02d}.mp3')


@functools.lru_cache(maxsize=None)
def load_pcm(i, sr=SR):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', vo_path(i), '-ac', '1', '-ar', str(sr),
                                   '-f', 'f32le', '-'])
    return np.frombuffer(raw, dtype=np.float32).copy()


@functools.lru_cache(maxsize=None)
def envelope(i):
    """RMS envelope at 100 Hz, normalised to 0..1."""
    x = load_pcm(i)
    hop = SR // 100
    n = len(x) // hop
    e = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    return e / (e.max() + 1e-9)


@functools.lru_cache(maxsize=None)
def voiced_frames(i):
    e = envelope(i)
    v = e > 0.07
    # close gaps shorter than 80 ms, drop islands shorter than 40 ms
    idx = np.where(v)[0]
    if len(idx) == 0:
        return np.arange(len(e))
    out = v.copy()
    gap_start = None
    for k in range(len(out)):
        if not out[k]:
            if gap_start is None:
                gap_start = k
        else:
            if gap_start is not None and k - gap_start < 8 and gap_start > 0:
                out[gap_start:k] = True
            gap_start = None
    return np.where(out)[0]


def tokenize(text):
    return text.split()


@functools.lru_cache(maxsize=None)
def word_times(i):
    """[(word, start_s, end_s)] for line i, relative to line start."""
    words = tokenize(LINES[i][2])
    vf = voiced_frames(i)
    weights = [len(re.sub(r'[^A-Za-z0-9]', '', w)) + 1.5 for w in words]
    tot = sum(weights)
    out = []
    acc = 0.0
    nv = len(vf)
    for w, wt in zip(words, weights):
        a = vf[min(nv - 1, int(acc / tot * nv))] / 100.0
        acc += wt
        b = vf[min(nv - 1, int(acc / tot * nv) - 1)] / 100.0 + 0.01
        out.append((w, a, max(b, a + 0.05)))
    return out


def line_abs_start(i):
    for s, (d, cues) in EDL.items():
        for li, off in cues:
            if li == i:
                return SCENE_START[s] + off
    raise KeyError(i)


def line_scene(i):
    for s, (d, cues) in EDL.items():
        for li, off in cues:
            if li == i:
                return s, off


def word_at(i, k):
    """Scene-local time when word k of line i starts."""
    s, off = line_scene(i)
    return off + word_times(i)[k][1]


def find_word(i, needle, nth=0):
    """Scene-local start time of the nth word in line i that starts with needle."""
    c = 0
    for k, (w, a, b) in enumerate(word_times(i)):
        if re.sub(r'[^A-Za-z]', '', w).lower().startswith(needle.lower()):
            if c == nth:
                s, off = line_scene(i)
                return off + a
            c += 1
    raise KeyError((i, needle))


STOP = set('a an the and or of to in on at is it its it\'s that this be you your he his him for with as by '
           'from up out can if so are was were has have had not no do don\'t won\'t but then just one what '
           'there here who which way when all about into before after over only them they their'.split())


@functools.lru_cache(maxsize=None)
def subtitle_chunks():
    """[(abs_start, abs_end, [(word, highlighted)], speaker)]"""
    chunks = []
    for i, (sc, sp, text) in enumerate(LINES):
        if (sc, sp) == (20, 'R') and i == 34:
            pass
        base = line_abs_start(i)
        wt = word_times(i)
        cur = []
        for k, (w, a, b) in enumerate(wt):
            cur.append((w, a, b))
            end_punct = w[-1] in '.,:;!?' or w.endswith('...')
            if len(cur) >= 4 or (end_punct and len(cur) >= 2) or k == len(wt) - 1 or (w[-1] in '.!?' and cur):
                words = [c[0] for c in cur]
                # highlight the most "important" word
                cands = [(len(re.sub(r'[^A-Za-z0-9]', '', x)), j) for j, x in enumerate(words)
                         if re.sub(r'[^A-Za-z\']', '', x).lower() not in STOP]
                hi = max(cands)[1] if cands and max(cands)[0] >= 4 else -1
                chunks.append((base + cur[0][1], base + cur[-1][2],
                               [(x.upper(), j == hi) for j, x in enumerate(words)], sp))
                cur = []
    # extend each chunk to the next one (no flicker), cap at +0.6 s
    out = []
    for n, (a, b, ws, sp) in enumerate(chunks):
        nxt = chunks[n + 1][0] if n + 1 < len(chunks) else b + 0.6
        out.append((a, min(max(b + 0.25, b), nxt if nxt - b < 0.6 else b + 0.6), ws, sp))
    return out


def subtitle_at(t):
    for a, b, ws, sp in subtitle_chunks():
        if a <= t < b:
            return ws, sp, t - a
    return None


@functools.lru_cache(maxsize=None)
def range_mouth_track():
    """Per-100Hz-frame mouth openness for Range's on-camera dialogue across the whole film."""
    n = int(TOTAL * 100) + 10
    m = np.zeros(n, dtype=np.float32)
    for i, (sc, sp, text) in enumerate(LINES):
        if sp != 'R' or i == 34:   # line 34 is a voice-over (writing in notebook)
            continue
        st = int(line_abs_start(i) * 100)
        e = envelope(i)
        e = np.clip(e * 1.6, 0, 1)
        m[st:st + len(e)] = np.maximum(m[st:st + len(e)], e[:max(0, min(len(e), n - st))])
    return m


def mouth_at(t):
    m = range_mouth_track()
    k = int(t * 100)
    if 0 <= k < len(m):
        return float(m[k])
    return 0.0


if __name__ == '__main__':
    print('total', TOTAL, 'chunks', len(subtitle_chunks()))
    for s in sorted(EDL):
        d, cues = EDL[s]
        for li, off in cues:
            from timeline import word_times as _w
            end = off + _w(li)[-1][2]
            flag = '  <-- OVER' if end > d else ''
            print(f'S{s:02d} d={d} L{li:02d} {off:5.1f}-{end:5.1f}{flag}')
