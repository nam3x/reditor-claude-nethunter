#!/usr/bin/env python3
"""Buat LUT .cube (33^3) bergaya clean-modern tanpa dependensi. Lisensi: milik proyek (bebas pakai).
Pemakaian: python3 gen_luts.py <folder_output>
"""
import os, sys

N = 33

def clamp(x): return 0.0 if x < 0 else 1.0 if x > 1 else x

def smooth_contrast(x, k):
    # kurva S lembut di sekitar 0.5
    return clamp(0.5 + (x - 0.5) * k - (x - 0.5) ** 3 * (k - 1) * 1.2)

def luma(r, g, b): return 0.2126 * r + 0.7152 * g + 0.0722 * b

def sat(r, g, b, s):
    l = luma(r, g, b)
    return (clamp(l + (r - l) * s), clamp(l + (g - l) * s), clamp(l + (b - l) * s))

def clean_bright(r, g, b):
    r, g, b = (smooth_contrast(c * 1.03 + 0.015, 1.08) for c in (r, g, b))
    return sat(r, g, b, 1.08)

def teal_orange(r, g, b):
    l = luma(r, g, b)
    sh, hi = (1 - l) ** 2, l ** 2
    r = r - 0.04 * sh + 0.05 * hi
    g = g + 0.01 * sh + 0.015 * hi
    b = b + 0.06 * sh - 0.05 * hi
    r, g, b = (smooth_contrast(clamp(c), 1.12) for c in (r, g, b))
    return sat(r, g, b, 1.05)

def moody_film(r, g, b):
    # lift hitam, roll-off highlight, desaturasi halus, sedikit hijau di bayangan
    def curve(x): return clamp(0.045 + x * 0.9 - (x - 0.5) ** 3 * 0.25)
    l = luma(r, g, b); sh = (1 - l) ** 2
    r, g, b = curve(r) - 0.01 * sh, curve(g) + 0.012 * sh, curve(b) + 0.005 * sh
    return sat(clamp(r), clamp(g), clamp(b), 0.85)

def bw_contrast(r, g, b):
    l = smooth_contrast(luma(r, g, b), 1.25)
    return (l, l, l)

def warm_soft(r, g, b):
    r, g, b = r * 1.04 + 0.01, g * 1.01 + 0.005, b * 0.94
    r, g, b = (smooth_contrast(clamp(c), 0.96) for c in (r, g, b))
    return sat(r, g, b, 1.02)

LUTS = {
    "clean_bright": clean_bright,
    "teal_orange": teal_orange,
    "moody_film": moody_film,
    "bw_contrast": bw_contrast,
    "warm_soft": warm_soft,
}

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for name, fn in LUTS.items():
        p = os.path.join(out, f"{name}.cube")
        with open(p, "w") as f:
            f.write(f'TITLE "reditor {name}"\nLUT_3D_SIZE {N}\n')
            for bi in range(N):          # urutan .cube: R tercepat
                for gi in range(N):
                    for ri in range(N):
                        r, g, b = fn(ri / (N - 1), gi / (N - 1), bi / (N - 1))
                        f.write(f"{clamp(r):.6f} {clamp(g):.6f} {clamp(b):.6f}\n")
        print("LUT", p)

if __name__ == "__main__":
    main()
