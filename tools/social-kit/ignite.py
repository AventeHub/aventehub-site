"""Render the 2026 (lights off) and 2027 (lines draw themselves) clips for the Exterior film, from Max's two home renders.
Off-state = LED lines removed by inpainting (light.py); ignition = each line revealed along its own path, bottom to top."""
import cv2, numpy as np, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import light

W, H, FPS = 1080, 1920, 30
D = os.path.dirname(os.path.abspath(__file__))

def crop_frame(img, cx, zoom):
    h = img.shape[0]
    ch = h / zoom; cw = ch * 9 / 16
    x0 = cx - cw / 2; y0 = (h - ch) / 2 + (h - ch) * 0.25   # keep a little more ground than sky as we push in
    M = np.float32([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def writer(path):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS),
                             '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', path],
                            stdin=subprocess.PIPE)

def ease(t):
    t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)

def build(name, cx, off_len, ign_len, hold, z0=1.0, z1=1.12):
    on = cv2.imread(f'{D}/{name}.jpg')
    lines, _, _ = light.masks(on)
    off = light.off_state(on, lines)
    n, lab = cv2.connectedComponents(lines, connectivity=8)
    comps = [i for i in range(1, n) if (lab == i).sum() > 80]
    # order: lowest first (steps), roof last
    comps.sort(key=lambda i: -np.nonzero(lab == i)[0].mean())
    params = {i: light.path_param(lab, i) for i in comps}
    allm = cv2.GaussianBlur(lines.astype(np.float32), (0, 0), 16) + 1e-4
    onf, offf = on.astype(np.float32), off.astype(np.float32)
    # 2026 clip: lights off, dusk deepens a little
    w = writer(f'{D}/{name}-2026.mp4'); N = int(off_len * FPS)
    for f in range(N):
        t = f / max(1, N - 1)
        img = offf * (1.10 - 0.10 * t); img[..., 2] *= (1.04 - 0.04 * t)
        w.stdin.write(crop_frame(np.clip(img, 0, 255).astype(np.uint8), cx, z0 + (z1 - z0) * 0.5 * t).tobytes())
    w.stdin.close(); w.wait()
    # 2027 clip: lines draw themselves, staggered
    w = writer(f'{D}/{name}-2027.mp4'); N = int((ign_len + hold) * FPS)
    k = len(comps); seg = ign_len / (k * 0.55 + 0.45)          # each line takes `seg`, starts overlap
    for f in range(N):
        tt = f / FPS
        rev = np.zeros(lines.shape, np.float32)
        for j, i in enumerate(comps):
            p = ease((tt - j * seg * 0.55) / seg)
            if p <= 0: continue
            pm = params[i]
            rev[(pm >= 0) & (pm <= p)] = 1.0
        A = np.clip(cv2.GaussianBlur(rev, (0, 0), 16) / allm, 0, 1)
        A = np.maximum(A, rev)[..., None]
        img = offf + (onf - offf) * A
        z = z0 + (z1 - z0) * (0.5 + 0.5 * f / max(1, N - 1))
        w.stdin.write(crop_frame(np.clip(img, 0, 255).astype(np.uint8), cx, z).tobytes())
    w.stdin.close(); w.wait()

if __name__ == '__main__':
    build('home-A-arched-white', 848, 10.0, 9.0, 3.0)
    build('home-B-modern-stone', 768, 6.0, 9.0, 3.0)
