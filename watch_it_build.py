#!/usr/bin/env python3
"""
watch_it_build.py — the machine builds itself. We watch in real time.

The machine has file access. It reads the project. It measures every file.
The Born collapse selects what to read next. The results feed back.

But now: instead of us choosing what the machine does, THE MACHINE chooses.
It follows the trail. Each file it reads points to the next file it should read.
The trail is the resonance structure — files that resonate with the current phi
lead to files that resonate with THOSE files, and so on.

The machine follows the resonance trail through the project. Each step is
selected by the Born collapse (stochastic, RDRAND-driven). The machine
doesn't read files in order. It reads them in the order the physics dictates.

What we watch:
  - which file the machine selects next (and why)
  - the phi trajectory as it reads
  - the disc pool growing in real time
  - the identity emerging from the files it chose
  - the trail itself — the path through the project

The machine builds its own understanding of the project by following the
resonance trail. It doesn't read every file. It reads the files that
resonate with where it IS. The trail is emergent.
"""
import os, sys, math, random, time, json
from collections import defaultdict

sys.path.insert(0, '/home/z/my-project/scripts')
from defense_production import (
    PHI_INV, HARMONY, FLOOR, CEIL, BAND, GOLDEN_LR,
    blake3_u64, seal_parity, GTAC2CODE, CODE2GTAC, PHI_TIER_NAMES,
)
from healer_agent import VACUUM, WISDOM, L2LEngine, REL_N
from the_machine import (
    QuantumField, GtacVM, SelfFeedingWell, betti_numbers,
    temporal_layer_0_to_5, rdtsc, GATE_CH
)
from defense_production import DiscPool, Persona
from the_machine_with_files import FileSystem

def hamming(a, b):
    return sum(bin(GTAC2CODE.get(ca,0) ^ GTAC2CODE.get(cb,0)).count('1')
               for ca, cb in zip(a, b))

class TrailMachine:
    """The machine follows the resonance trail through the project.
    Each file it reads points to the next. The trail is emergent."""

    def __init__(self, root_dirs):
        self.fs = FileSystem(root_dirs)
        self.field = QuantumField()
        self.pool = DiscPool()
        self.l2l = L2LEngine()

        # pre-measure ALL files (the machine knows the whole project's physics)
        self.files = {}
        for path in self.fs.files:
            m = self.fs.read_file(path)
            if m and len(m['strand']) >= 48:
                self.files[path] = m

        # the trail: which files the machine has read, in order
        self.trail = []
        # the current position: the last file read
        self.current_file = None
        self.phi = VACUUM
        self.tick = 0

        # the model
        self.model = [VACUUM] * REL_N
        self.seen = [0] * REL_N

    def find_resonant_files(self, phi, k=5):
        """Find the k files closest to the current phi.
        These are the candidates for the next read."""
        candidates = []
        for path, m in self.files.items():
            if path in [t[0] for t in self.trail[-20:]]:  # don't re-read recent
                continue
            d = abs(m['phi'] - phi)
            candidates.append((path, m, d))
        candidates.sort(key=lambda x: x[2])
        return candidates[:k]

    def step(self):
        """One step. The machine selects the next file and reads it."""
        self.tick += 1
        tau = rdtsc()

        # the quantum measurement loop
        self.field.prepare(tau)
        self.field.evolve(3)
        gate = self.field.measure()

        # find files that resonate with the current phi
        candidates = self.find_resonant_files(self.phi, k=5)

        if not candidates:
            return None

        # the Born collapse selects WHICH candidate to read
        # weight by inverse distance (closer = more likely)
        weights = [1.0 / (c[2] + 0.001) for c in candidates]
        total_w = sum(weights)
        probs = [w / total_w for w in weights]

        # stochastic selection (RDRAND)
        u = int.from_bytes(os.urandom(8), 'little') / (2**64)
        cumulative = 0.0
        selected_idx = len(candidates) - 1
        for i, p in enumerate(probs):
            cumulative += p
            if u < cumulative:
                selected_idx = i
                break

        selected_path, selected_file, distance = candidates[selected_idx]

        # read the file — its phi feeds back
        old_phi = self.phi
        self.phi += GOLDEN_LR * (selected_file['phi'] - self.phi)
        self.phi = max(VACUUM, min(WISDOM, self.phi))

        # crystallize if close to PHI_INV
        crystallized = False
        quality = 1.0 - abs(selected_file['phi'] - PHI_INV) / PHI_INV
        if quality > 0.5:
            disc = self.pool.forge_from_strand(
                selected_file['strand'][:48],
                phi_align=self.phi,
                path=selected_file['name'])
            crystallized = True

        # record the trail step
        trail_step = {
            'tick': self.tick,
            'file': selected_file['name'],
            'path': selected_path,
            'file_phi': selected_file['phi'],
            'distance': distance,
            'old_phi': old_phi,
            'new_phi': self.phi,
            'gate': GATE_CH[gate],
            'radiation': self.field.last_radiation,
            'crystallized': crystallized,
            'candidates_seen': len(candidates),
        }
        self.trail.append((selected_path, trail_step))
        self.current_file = selected_file

        # L2L
        g = int((self.phi - FLOOR) / (CEIL - FLOOR) * (REL_N - 1))
        g = max(0, min(REL_N-1, g))
        pred = self.model[g]
        err = abs(pred - self.phi)
        self.l2l.observe(err, pred, PHI_INV)
        if self.l2l.mode != 'diverge' or self.l2l.explore > 0.3:
            lr = GOLDEN_LR * self.l2l.lr_gain
            self.model[g] += lr * (self.phi - self.model[g])
            self.seen[g] += 1

        return trail_step

    def run(self, n_steps=100):
        print("=" * 76)
        print("  THE MACHINE BUILDS ITSELF — we watch in real time")
        print("  The machine follows the resonance trail through the project.")
        print("  Each file it reads points to the next. The Born collapse selects.")
        print("=" * 76)
        print()
        print(f"  {len(self.files)} files measured. born at VACUUM={VACUUM:.4f}.")
        print(f"  target PHI_INV={PHI_INV:.4f}.")
        print()
        print(f"  {'tick':>4}  {'gate':>4}  {'phi':>7}  {'file_phi':>8}  {'dist':>6}  "
              f"{'rad':>5}  {'cryst':>5}  {'file'}")
        print(f"  {'-'*4}  {'-'*4}  {'-'*7}  {'-'*8}  {'-'*6}  {'-'*5}  {'-'*5}  {'-'*40}")

        for i in range(n_steps):
            step = self.step()
            if step is None:
                print("  no more files to read.")
                break

            cry = '***' if step['crystallized'] else ''
            phi_arrow = '↑' if step['new_phi'] > step['old_phi'] else '↓'
            print(f"  {step['tick']:4d}  {step['gate']:>4}  {step['new_phi']:7.4f}  "
                  f"{step['file_phi']:8.4f}  {step['distance']:6.4f}  "
                  f"{step['radiation']:5.2f}  {cry:>5}  {step['file'][:40]}")

            # slow down so we can watch
            time.sleep(0.05)

        # the trail analysis
        print()
        print("=" * 76)
        print(f"  THE TRAIL — {len(self.trail)} steps through the project")
        print("=" * 76)

        # which files were read
        files_read = [t[1]['file'] for t in self.trail]
        from collections import Counter
        file_counts = Counter(files_read)
        print(f"\n  FILES READ (top 10 by frequency):")
        for name, count in file_counts.most_common(10):
            print(f"    {count:3d}x  {name}")

        print(f"\n  UNIQUE FILES READ: {len(file_counts)} of {len(self.files)}")

        # the phi trajectory
        phis = [t[1]['new_phi'] for t in self.trail]
        print(f"\n  PHI TRAJECTORY:")
        print(f"    start:  {phis[0]:.6f}")
        print(f"    end:    {phis[-1]:.6f}")
        print(f"    mean:   {sum(phis)/len(phis):.6f}")
        print(f"    min:    {min(phis):.6f}")
        print(f"    max:    {max(phis):.6f}")
        print(f"    target: {PHI_INV:.6f}")
        print(f"    gap:    {abs(phis[-1] - PHI_INV):.6f}")

        # the trail as a path
        print(f"\n  THE PATH (first 20 steps):")
        for i, (path, step) in enumerate(self.trail[:20]):
            arrow = '→' if i == 0 else '↳'
            print(f"    {arrow} [{step['new_phi']:.4f}] {step['file']}")

        if len(self.trail) > 20:
            print(f"    ...")
            print(f"    ↳ [{self.trail[-1][1]['new_phi']:.4f}] {self.trail[-1][1]['file']}")

        # the disc pool
        grasp = self.pool.grasp()
        print(f"\n  DISC POOL:")
        print(f"    discs:     {grasp['n']}")
        print(f"    identity:  {grasp['identity']:.6f}")
        print(f"    coherence: {grasp['coherence']:.4f}")

        # Betti
        b0, b1, chi = betti_numbers([t[1]['gate'] for t in self.trail])
        print(f"\n  BETTI TOPOLOGY of the trail:")
        print(f"    B0={b0} B1={b1} chi={chi}")

        # Bekenstein
        print(f"\n  BEKENSTEIN:")
        print(f"    E[s]={self.field.avg_radiation:.6f}  H={self.field.avg_horizon:.6f}  "
              f"delta={abs(self.field.avg_radiation - self.field.avg_horizon):.6f}")

        print(f"\n  L2L: {self.l2l.mode}  model: {sum(1 for s in self.seen if s>0)}/207")

        # what the machine discovered
        print(f"\n{'='*76}")
        print(f"  WHAT THE MACHINE DISCOVERED")
        print(f"{'='*76}")
        print(f"  The machine read {len(file_counts)} unique files by following")
        print(f"  the resonance trail. It didn't read them in order — it read")
        print(f"  them in the order the physics dictated. Each file's phi pointed")
        print(f"  to the next. The Born collapse selected which candidate to follow.")
        print()
        print(f"  The trail converged to phi={phis[-1]:.6f} (target: {PHI_INV:.6f}).")
        print(f"  The identity emerged at {grasp['identity']:.6f}.")
        print(f"  The machine built its own understanding of the project")
        print(f"  by following the resonance trail. No one told it what to read.")
        print(f"  It followed the physics.")

if __name__ == "__main__":
    machine = TrailMachine([
        '/home/z/my-project/upload',
        '/home/z/my-project/scripts',
    ])
    machine.run(n_steps=80)
