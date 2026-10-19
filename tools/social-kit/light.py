import cv2, numpy as np
from collections import deque

def masks(img):
    im = img.astype(np.float32)
    b, g, r = im[..., 0], im[..., 1], im[..., 2]
    lum = 0.3*r + 0.59*g + 0.11*b
    core = ((lum > 215) & ((r - b) > 25)).astype(np.uint8)
    core = cv2.dilate(core, np.ones((3, 3), np.uint8), iterations=2)
    n, lab, st, _ = cv2.connectedComponentsWithStats(core, 8)
    lines = np.zeros_like(core)
    keep = []
    for i in range(1, n):
        x, y, w, h, a = st[i]
        span = max(w, h)
        fill = a / float(w*h)
        aspect = span / max(1, min(w, h))
        if span > 60 and (fill < 0.35 or aspect > 4.5):   # long and thin = an LED line
            lines[lab == i] = 1; keep.append(i)
    # grow into the line's own bloom (hysteresis on a weaker warm-bright threshold)
    weak = ((lum > 140) & ((r - b) > 18)).astype(np.uint8)
    other = cv2.dilate(((core > 0) & (lines == 0)).astype(np.uint8), np.ones((3, 3), np.uint8), iterations=6)
    grow = cv2.dilate(lines, np.ones((3, 3), np.uint8), iterations=5) & weak & (1 - other)
    lines = np.maximum(lines, grow)
    return lines, lab, keep

def off_state(img, lines):
    m = cv2.dilate(lines, np.ones((3, 3), np.uint8), iterations=3) * 255
    base = cv2.inpaint(img, m, 7, cv2.INPAINT_TELEA)
    halo = cv2.GaussianBlur(lines.astype(np.float32), (0, 0), 22)
    halo = np.clip(halo / (halo.max() + 1e-6) * 2.2, 0, 1)
    f = base.astype(np.float32)
    k = 0.30 * halo[..., None]
    f = f * (1 - k)                                   # remove the light spill
    f[..., 2] -= 10 * halo; f[..., 0] += 6 * halo      # less warm where the spill was
    return np.clip(f, 0, 255).astype(np.uint8)

def path_param(lab, comp):
    """0..1 along each line component, by geodesic distance from its lowest-left pixel."""
    ys, xs = np.nonzero(lab == comp)
    start = np.argmax(ys * 4 - xs)       # lowest, then left
    pts = set(zip(ys.tolist(), xs.tolist()))
    dist = {(ys[start], xs[start]): 0}
    q = deque([(ys[start], xs[start])])
    while q:
        p = q.popleft(); d = dist[p] + 1
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nb = (p[0]+dy, p[1]+dx)
                if nb in pts and nb not in dist:
                    dist[nb] = d; q.append(nb)
    out = np.full(lab.shape, -1.0, np.float32)
    mx = max(dist.values()) or 1
    for (y, x), d in dist.items():
        out[y, x] = d / mx
    return out
