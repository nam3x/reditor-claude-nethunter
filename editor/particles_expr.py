#!/usr/bin/env python3
"""Cetak ekspresi geq ffmpeg untuk partikel melayang (deterministik, loop mulus per DETIK).
Pemakaian: python3 particles_expr.py JUMLAH R_MIN R_MAX DETIK SEED   (DETIK=0 -> medan statis 1 frame)"""
import random
import sys

n, rmin, rmax, sec, seed = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
rnd = random.Random(seed)
terms = []
for _ in range(n):
    x0, y0 = rnd.random(), rnd.random()
    amp = rnd.uniform(0.01, 0.05)
    loops = rnd.choice([1, 1, 2])  # naik 1–2 kali tinggi layar per loop -> loop mulus
    r = rnd.uniform(rmin, rmax)
    a = rnd.uniform(0.35, 1.0)
    ph = rnd.uniform(0, 6.28)
    if sec <= 0:  # mode statis: satu frame medan partikel (dianimasikan dengan crop bergulir)
        x, y = f"W*{x0:.4f}", f"H*{y0:.4f}"
    else:
        x = f"W*({x0:.4f}+{amp:.4f}*sin(2*PI*T/{sec}+{ph:.3f}))"
        y = f"H*(1-mod({y0:.4f}+{loops}*T/{sec},1))"
    terms.append(f"{a:.3f}*exp(-((X-{x})^2+(Y-{y})^2)/{2 * r * r:.2f})")
print("min(255,255*(" + "+".join(terms) + "))")
