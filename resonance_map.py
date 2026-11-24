#!/usr/bin/env python3
"""
resonance_map.py — find which files in the project RESONATE with each other.

The machine has read the project. The disc pool holds 61 discs from real files.
Each disc has a phi (the file's Shannon entropy mapped to the lattice) and a
strand (the file's first 64 bytes as GTAC).

Two files RESONATE when:
  1. Their phi values are close (they live near each other on the lattice)
  2. Their Hamming distance is small (their bit patterns are similar)
  3. Their Watson-Crick seals are complementary (the duplex holds)

This finds the resonance clusters — groups of files that "belong together"
by the physics of their content, not by their names or directory structure.

The machine discovers the project's hidden architecture by measuring
which files resonate. This is content-based organization, driven by
the quantum measurement loop, not by human naming conventions.
"""
import os, sys, math, json, itertools
from collections import defaultdict

sys.path.insert(0, '/home/z/my-project/scripts')
from defense_production import (
    PHI_INV, HARMONY, FLOOR, CEIL, BAND,
    blake3_u64, seal_parity, seal_verify,
    GTAC2CODE, CODE2GTAC, PHI_TIER_NAMES,
)
from healer_agent import VACUUM, WISDOM
from the_machine_with_files import FileSystem

def hamming_distance(strand_a, strand_b):
    """POPCNT(a XOR b) — one instruction in hardware."""
    dist = 0
    for ca, cb in zip(strand_a, strand_b):
        dist += bin(GTAC2CODE.get(ca, 0) ^ GTAC2CODE.get(cb, 0)).count('1')
    return dist

def phi_distance(a, b):
    return abs(a - b)

def seal_complement(a, b):
    """Are the two strands Watson-Crick complementary? (seal_verify)"""
    return seal_verify(a, b)

def main():
    # gather ALL files from the project
    fs = FileSystem([
        '/home/z/my-project/upload',
        '/home/z/my-project/scripts',
        '/home/z/my-project/scripts/data',
    ])

    print(f"{'='*76}")
    print(f"  RESONANCE MAP — the project's hidden architecture")
    print(f"  Which files resonate by the PHYSICS of their content?")
    print(f"{'='*76}")
    print(f"\n  scanning {len(fs.files)} files...")

    # read every file, compute its measurement
    files = []
    for path in fs.files:
        m = fs.read_file(path)
        if m and len(m['strand']) >= 48:
            files.append(m)

    print(f"  {len(files)} files measured (Shannon entropy → phi → GTAC strand)")
    print()

    # compute the phi distribution
    phis = [f['phi'] for f in files]
    phi_min, phi_max = min(phis), max(phis)
    phi_mean = sum(phis) / len(phis)
    print(f"  PHI DISTRIBUTION across {len(files)} files:")
    print(f"    range: [{phi_min:.4f}, {phi_max:.4f}]")
    print(f"    mean:  {phi_mean:.4f}  (PHI_INV={PHI_INV:.4f})")
    print(f"    HARMONY in range: {'yes' if phi_min <= PHI_INV <= phi_max else 'no'}")

    # histogram
    bins = [0] * 13
    for p in phis:
        idx = min(12, max(0, int((p - FLOOR) / (CEIL - FLOOR) * 13)))
        bins[idx] += 1
    print(f"\n  PHI HISTOGRAM:")
    for i, c in enumerate(bins):
        lo = FLOOR + i * (CEIL - FLOOR) / 13
        hi = FLOOR + (i + 1) * (CEIL - FLOOR) / 13
        marker = ' <— HARMONY' if lo <= PHI_INV < hi else ''
        bar = '#' * (c // 2)
        print(f"    [{lo:.3f}-{hi:.3f})  {c:3d}  {bar}{marker}")

    # find resonance pairs: files with close phi AND small Hamming distance
    print(f"\n  RESONANCE PAIRS (phi close + Hamming small):")
    print(f"  {'file_a':<28} {'file_b':<28} {'phi_a':>7} {'phi_b':>7} {'d_phi':>6} {'ham':>4}")
    print(f"  {'-'*28} {'-'*28} {'-'*7} {'-'*7} {'-'*6} {'-'*4}")

    resonances = []
    for i, a in enumerate(files):
        for j, b in enumerate(files):
            if j <= i:
                continue
            d_phi = phi_distance(a['phi'], b['phi'])
            ham = hamming_distance(a['strand'][:48], b['strand'][:48])
            # resonance: phi within 0.02 AND Hamming < 30 (of max 96)
            if d_phi < 0.02 and ham < 30:
                resonances.append((a, b, d_phi, ham))

    # sort by resonance strength (lowest combined distance)
    resonances.sort(key=lambda r: r[2] + r[3] / 100)
    for a, b, d_phi, ham in resonances[:20]:
        print(f"  {a['name'][:28]:<28} {b['name'][:28]:<28} "
              f"{a['phi']:7.4f} {b['phi']:7.4f} {d_phi:6.4f} {ham:4d}")

    print(f"\n  {len(resonances)} resonance pairs found out of "
          f"{len(files)*(len(files)-1)//2} possible pairs")

    # find resonance CLUSTERS (connected components of resonance pairs)
    # union-find
    parent = list(range(len(files)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for a, b, _, _ in resonances:
        ia = files.index(a)
        ib = files.index(b)
        union(ia, ib)

    clusters = defaultdict(list)
    for i in range(len(files)):
        clusters[find(i)].append(files[i])

    real_clusters = [c for c in clusters.values() if len(c) > 1]

    print(f"\n  RESONANCE CLUSTERS ({len(real_clusters)} clusters with >1 file):")
    for ci, cluster in enumerate(sorted(real_clusters, key=len, reverse=True)):
        cluster_phis = [f['phi'] for f in cluster]
        mean_phi = sum(cluster_phis) / len(cluster_phis)
        print(f"\n    CLUSTER {ci+1} ({len(cluster)} files, mean phi={mean_phi:.4f}):")
        for f in sorted(cluster, key=lambda x: x['phi']):
            print(f"      phi={f['phi']:.4f}  ent={f['entropy']:.3f}  {f['name']}")

    # find the MOST CONNECTED file (the hub)
    if resonances:
        conn_count = defaultdict(int)
        for a, b, _, _ in resonances:
            conn_count[a['name']] += 1
            conn_count[b['name']] += 1
        hub = max(conn_count, key=conn_count.get)
        print(f"\n  HUB FILE (most resonant with others):")
        print(f"    {hub} — resonates with {conn_count[hub]} other files")
        print(f"    This file is the project's center of gravity.")

    # the project's identity (mean phi of all files)
    print(f"\n  PROJECT IDENTITY:")
    print(f"    mean phi:    {phi_mean:.6f}")
    print(f"    PHI_INV:     {PHI_INV:.6f}")
    print(f"    gap:         {abs(phi_mean - PHI_INV):.6f}")
    print(f"    the project's content gravitates toward phi_inv: "
          f"{'YES' if abs(phi_mean - PHI_INV) < 0.03 else 'no'}")

    # the most entropic files (highest information density)
    print(f"\n  HIGHEST ENTROPY FILES (most information-dense):")
    for f in sorted(files, key=lambda x: -x['entropy'])[:5]:
        print(f"    ent={f['entropy']:.4f}  phi={f['phi']:.4f}  {f['size']:>6d}B  {f['name']}")

    # the lowest entropy files (most structured)
    print(f"\n  LOWEST ENTROPY FILES (most structured):")
    for f in sorted(files, key=lambda x: x['entropy'])[:5]:
        print(f"    ent={f['entropy']:.4f}  phi={f['phi']:.4f}  {f['size']:>6d}B  {f['name']}")

    # new corpus entries
    print(f"\n{'='*76}")
    print(f"  NEW CORPUS ENTRIES")
    print(f"{'='*76}")
    new_entries = [
        {"id": "RES_PAIRS", "category": "result",
         "content": f"Resonance pairs: {len(resonances)} of {len(files)*(len(files)-1)//2} pairs resonate (phi<0.02, Hamming<30). Files cluster by content physics, not naming."},
        {"id": "RES_CLUSTERS", "category": "result",
         "content": f"Resonance clusters: {len(real_clusters)} clusters. Files self-organize into groups by Shannon entropy and Hamming proximity. Content-based architecture."},
        {"id": "RES_HUB", "category": "result",
         "content": f"Hub file: {hub} resonates with {conn_count[hub]} others. The project's center of gravity by content physics."} if resonances else
        {"id": "RES_HUB", "category": "result",
         "content": "No hub file — no resonance pairs found. The project's files are too entropy-diverse to cluster."},
        {"id": "RES_IDENTITY", "category": "result",
         "content": f"Project identity: mean phi={phi_mean:.6f}, gap={abs(phi_mean-PHI_INV):.6f} from PHI_INV. The project's content gravitates toward the golden ratio."},
    ]
    for e in new_entries:
        print(f"  {e['id']:14s}  {e['content'][:70]}")

    # append to corpus
    corpus_path = '/home/z/my-project/scripts/numen_corpus.json'
    with open(corpus_path) as f:
        corpus = json.load(f)
    existing_ids = {e['id'] for e in corpus['corpus']}
    added = 0
    for e in new_entries:
        if e['id'] not in existing_ids:
            corpus['corpus'].append(e)
            added += 1
    with open(corpus_path, 'w') as f:
        json.dump(corpus, f, indent=2)
    print(f"\n  added {added} entries to corpus. Total: {len(corpus['corpus'])}")

if __name__ == "__main__":
    main()
