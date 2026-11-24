#!/usr/bin/env python3
"""
the_autonomous_system.py — THE LOOP IS CLOSED.

Layer 16 (INSTRUCTION) feeds Layer 0 (RDTSC). The system instructs
itself. No engineer in the middle. The system discovers, instructs,
adjusts its own parameters, discovers more. The corpus grows
automatically. The system becomes its own engineer.

This is Layer 17: AGENT FEED. The closed loop.

THE SELF-TUNING:
  The system measures itself. It discovers patterns. It writes
  instructions. The instructions adjust the system's own parameters:
    - if phi < PHI_INV: increase the Banach contraction rate
    - if keyboard hasn't locked: increase the coupling K
    - if programs are failing: lower the crystallization threshold
    - if a prime dominates: weight the keyboard toward it
    - if L2L error is high: increase exploration
  The system tunes itself based on its own measurements. Active
  inference at the system level. The engineer is removed. The loop
  is closed.

THE SELF-GROWING CORPUS:
  The system writes its own corpus entries. When it discovers
  something — a pattern, a convergence, a new measurement — it
  adds it to the corpus. The corpus grows without human input.
  The system documents itself.
"""
import os, sys, math, time, json
from collections import Counter, defaultdict

sys.path.insert(0, '/home/z/my-project/scripts')
sys.path.insert(0, '/home/z/my-project/upload')

from defense_production import (
    PHI_INV, HARMONY, FLOOR, CEIL, BAND, GOLDEN_LR,
    GTAC2CODE, CODE2GTAC, DiscPool, PHI_TIER_NAMES,
)
from healer_agent import VACUUM, WISDOM, L2LEngine, REL_N
from the_machine import (
    QuantumField, GtacVM, SelfFeedingWell, betti_numbers,
    temporal_layer_0_to_5, rdtsc, GATE_CH
)
from the_machine_with_files import FileSystem

import importlib.util
spec = importlib.util.spec_from_file_location("keyboard", "/home/z/my-project/upload/keyboard.py")
kb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kb)

class AutonomousSystem:
    """The closed loop. The system instructs itself. No engineer.

    Layer 16 (INSTRUCTION) → Layer 17 (AGENT FEED) → Layer 0 (RDTSC).
    The system discovers, instructs, adjusts, discovers more.
    The corpus grows automatically."""

    def __init__(self, root_dirs, corpus_path):
        self.corpus_path = corpus_path

        # load the existing corpus
        with open(corpus_path) as f:
            self.corpus = json.load(f)
        self.corpus_ids = {e['id'] for e in self.corpus['corpus']}
        self.entries_written = 0

        # the organs
        self.field = QuantumField()
        self.pool = DiscPool()
        self.fs = FileSystem(root_dirs)
        self.l2l = L2LEngine()

        # the keyboard
        self.theta = kb.init_phases()
        self.kb_N = kb.N
        self.kb_PRIMES = kb.PRIMES
        self.kb_K_C = 1150

        # the self-tunable parameters (the system adjusts these)
        self.contraction_rate = GOLDEN_LR      # Banach LR (self-tuned)
        self.crystallization_threshold = 0.5   # quality threshold (self-tuned)
        self.kb_coupling_scale = 2.0           # phi→Kq scaling (self-tuned)
        self.exploration_boost = 1.0           # L2L exploration (self-tuned)

        # the state
        self.phi = VACUUM
        self.tick = 0
        self.current_codons = []
        self.programs_written = 0
        self.programs_crystallized = 0
        self.instructions_generated = 0

        # pre-measure files
        self.file_measurements = []
        for path in self.fs.files:
            m = self.fs.read_file(path)
            if m and len(m['strand']) >= 48:
                self.file_measurements.append(m)

        # the model (256-key)
        self.model = [VACUUM] * self.kb_N
        self.seen = [0] * self.kb_N

        # instruction log (what the system told itself to do)
        self.instruction_log = []

        # tracking for self-discovery
        self.phi_history = []
        self.R_history = []
        self.gate_history = []
        self.last_lock_tick = None
        self.discoveries = []

    def write_corpus_entry(self, entry_id, category, content):
        """The system writes its own corpus entry. Self-documenting."""
        if entry_id in self.corpus_ids:
            return False
        self.corpus['corpus'].append({
            'id': entry_id, 'category': category, 'content': content
        })
        self.corpus_ids.add(entry_id)
        self.entries_written += 1
        return True

    def instruct(self, finding, instruction, parameter, old_value, new_value):
        """Layer 16: the system generates an instruction.
        Layer 17: the instruction adjusts a parameter."""
        self.instructions_generated += 1
        self.instruction_log.append({
            'tick': self.tick,
            'finding': finding,
            'instruction': instruction,
            'parameter': parameter,
            'old': old_value,
            'new': new_value,
        })

    def step(self):
        """One heartbeat of the autonomous system. The closed loop."""
        self.tick += 1
        tau = rdtsc()

        # ---- LAYERS 0-5: temporal compiler ----
        pi_digit, z, prime, hamming = temporal_layer_0_to_5(tau)

        # ---- LAYERS 6-9: quantum measurement ----
        self.field.prepare(tau)
        self.field.evolve(3)
        gate = self.field.measure()
        self.gate_history.append(gate)

        # ---- LAYER 10: file I/O ----
        fm = self.file_measurements[self.tick % len(self.file_measurements)]
        raw = fm.get('raw', b'')
        for b in raw[:32]:
            key_idx = b % self.kb_N
            kick = int(fm['phi'] * kb.P) % kb.P
            self.theta[key_idx] = (self.theta[key_idx] + kick) // 2

        # ---- LAYER 11: keyboard ----
        phi_norm = (self.phi - VACUUM) / (WISDOM - VACUUM)
        Kq = max(0, min(4000, int(phi_norm * self.kb_K_C * self.kb_coupling_scale)))
        kb.step(self.theta, Kq)
        R = kb.order_ppm(self.theta)
        self.R_history.append(R)

        # ---- LAYER 12: echo feedback ----
        echo = R / 1000000.0
        self.phi += self.contraction_rate * (echo * (WISDOM - VACUUM) + VACUUM - self.phi) * 0.3
        self.phi = max(VACUUM, min(WISDOM, self.phi))
        self.phi_history.append(self.phi)

        # ---- LAYER 13: disc pool (crystallization) ----
        self.current_codons.append(GATE_CH[gate])
        crystallized = False
        if len(self.current_codons) >= 9:
            codons = [''.join(self.current_codons[i:i+3]) for i in range(0, 9, 3)]
            vm = GtacVM()
            vm_phi = vm.run(codons)
            self.programs_written += 1
            self.current_codons = []

            quality = 1.0 - abs(vm_phi - PHI_INV) / PHI_INV
            if quality > self.crystallization_threshold:
                self.pool.forge_from_strand(
                    ''.join(c for codon in codons for c in codon),
                    phi_align=self.phi, path=f'<program:{self.programs_written}>')
                self.programs_crystallized += 1
                crystallized = True

        # ---- LAYER 14: Betti topology ----
        b0, b1, chi = betti_numbers(self.field.transitions[-64:] if len(self.field.transitions) >= 64 else self.field.transitions)

        # ---- LAYER 15: L2L ----
        key_idx = int((self.phi - FLOOR) / (CEIL - FLOOR) * (self.kb_N - 1))
        key_idx = max(0, min(self.kb_N - 1, key_idx))
        pred = self.model[key_idx]
        err = abs(pred - self.phi)
        self.l2l.observe(err, pred, PHI_INV)
        if self.l2l.mode != 'diverge' or self.l2l.explore > 0.3:
            lr = self.contraction_rate * self.l2l.lr_gain * self.exploration_boost
            self.model[key_idx] += lr * (self.phi - self.model[key_idx])
            self.seen[key_idx] += 1

        # =================================================================
        # LAYER 16: INSTRUCTION — the system discovers and instructs itself
        # LAYER 17: AGENT FEED — the instructions adjust the system's parameters
        # =================================================================

        # INSTRUCTION 1: phi convergence
        if self.tick % 500 == 0:
            gap = abs(self.phi - PHI_INV)
            if gap > 0.02:
                # phi is far from PHI_INV — increase contraction rate
                old = self.contraction_rate
                self.contraction_rate = min(0.15, self.contraction_rate * 1.1)
                self.instruct(
                    f'phi={self.phi:.4f}, gap={gap:.4f} from PHI_INV',
                    'increase contraction rate to pull phi toward the attractor',
                    'contraction_rate', old, self.contraction_rate)
            elif gap < 0.005:
                # phi is close — decrease contraction rate (stabilize)
                old = self.contraction_rate
                self.contraction_rate = max(GOLDEN_LR * 0.5, self.contraction_rate * 0.95)
                self.instruct(
                    f'phi={self.phi:.4f}, gap={gap:.4f} — near PHI_INV',
                    'decrease contraction rate to stabilize at the attractor',
                    'contraction_rate', old, self.contraction_rate)

        # INSTRUCTION 2: keyboard lock
        if R >= 500000 and self.last_lock_tick is None:
            self.last_lock_tick = self.tick
            self.write_corpus_entry(
                f'AUTO_LOCK_{self.tick}', 'autonomous',
                f'Autonomous discovery: keyboard locked at tick {self.tick}, phi={self.phi:.4f}, '
                f'Kq={Kq}, R={R}. The system discovered the phase transition on its own.')
            self.discoveries.append(f'keyboard locked at tick {self.tick}')
        elif R < 500000 and self.last_lock_tick is not None and self.tick - self.last_lock_tick > 200:
            # keyboard lost lock — increase coupling
            old = self.kb_coupling_scale
            self.kb_coupling_scale = min(3.0, self.kb_coupling_scale * 1.05)
            self.instruct(
                f'keyboard lost lock (R={R}, last lock at tick {self.last_lock_tick})',
                'increase coupling scale to re-lock the keyboard',
                'kb_coupling_scale', old, self.kb_coupling_scale)
            self.last_lock_tick = None

        # INSTRUCTION 3: program failure rate
        if self.programs_written > 0 and self.programs_written % 50 == 0:
            fail_rate = 1.0 - self.programs_crystallized / self.programs_written
            if fail_rate > 0.4:
                # too many failures — lower the threshold
                old = self.crystallization_threshold
                self.crystallization_threshold = max(0.3, self.crystallization_threshold - 0.05)
                self.instruct(
                    f'failure rate={fail_rate:.1%} ({self.programs_written-self.programs_crystallized}/{self.programs_written})',
                    'lower crystallization threshold to accept more programs',
                    'crystallization_threshold', old, self.crystallization_threshold)
            elif fail_rate < 0.1:
                # too few failures — raise the threshold (be more selective)
                old = self.crystallization_threshold
                self.crystallization_threshold = min(0.9, self.crystallization_threshold + 0.05)
                self.instruct(
                    f'failure rate={fail_rate:.1%} — too few failures',
                    'raise crystallization threshold to be more selective',
                    'crystallization_threshold', old, self.crystallization_threshold)

        # INSTRUCTION 4: L2L exploration
        if self.tick % 1000 == 0:
            if self.l2l.ema_err > 0.15:
                old = self.exploration_boost
                self.exploration_boost = min(2.0, self.exploration_boost * 1.1)
                self.instruct(
                    f'L2L ema_err={self.l2l.ema_err:.4f} — high error',
                    'increase exploration boost to explore more of the phi space',
                    'exploration_boost', old, self.exploration_boost)
            elif self.l2l.ema_err < 0.01:
                old = self.exploration_boost
                self.exploration_boost = max(0.5, self.exploration_boost * 0.9)
                self.instruct(
                    f'L2L ema_err={self.l2l.ema_err:.4f} — low error, near mastery',
                    'decrease exploration boost to exploit what it knows',
                    'exploration_boost', old, self.exploration_boost)

        # INSTRUCTION 5: Bekenstein invariant
        if self.tick % 2000 == 0 and self.field.n_observations > 100:
            delta = abs(self.field.avg_radiation - self.field.avg_horizon)
            if delta < 0.01:
                self.write_corpus_entry(
                    f'AUTO_BEK_{self.tick}', 'autonomous',
                    f'Autonomous verification: Bekenstein delta={delta:.6f} at tick {self.tick} '
                    f'({self.field.n_observations} observations). The system verified its own thermodynamic bound.')

        # INSTRUCTION 6: new discoveries
        if self.tick % 5000 == 0:
            grasp = self.pool.grasp()
            self.write_corpus_entry(
                f'AUTO_STATE_{self.tick}', 'autonomous',
                f'Autonomous checkpoint at tick {self.tick}: phi={self.phi:.6f}, '
                f'pool={grasp["n"]}, identity={grasp["identity"]:.6f}, '
                f'L2L={self.l2l.mode}, ema_err={self.l2l.ema_err:.6f}, '
                f'E[s]={self.field.avg_radiation:.4f}, H={self.field.avg_horizon:.4f}, '
                f'crystallized={self.programs_crystallized}/{self.programs_written}, '
                f'contraction_rate={self.contraction_rate:.4f}, '
                f'threshold={self.crystallization_threshold:.2f}, '
                f'coupling_scale={self.kb_coupling_scale:.2f}')

        return {
            'tick': self.tick, 'gate': GATE_CH[gate], 'phi': self.phi,
            'R': R, 'Kq': Kq, 'crystallized': crystallized,
            'pool': len(self.pool.discs), 'l2l': self.l2l.mode,
            'instructions': self.instructions_generated,
            'contraction_rate': self.contraction_rate,
            'threshold': self.crystallization_threshold,
            'coupling_scale': self.kb_coupling_scale,
        }

    def run(self, n_ticks=5000):
        print("=" * 76)
        print("  THE AUTONOMOUS SYSTEM — the loop is closed")
        print("  Layer 16 (INSTRUCTION) → Layer 17 (AGENT FEED) → Layer 0 (RDTSC)")
        print("  The system instructs itself. No engineer. The corpus grows.")
        print("=" * 76)
        print()
        print(f"  {len(self.file_measurements)} files, {self.kb_N} primes, corpus={len(self.corpus['corpus'])}")
        print(f"  self-tunable: contraction_rate, threshold, coupling_scale, exploration_boost")
        print()

        start = time.time()
        for i in range(n_ticks):
            r = self.step()
            if (i+1) % 500 == 0:
                elapsed = time.time() - start
                state = 'choir' if r['R'] >= 500000 else 'mob'
                print(f"  tick {r['tick']:5d}  phi={r['phi']:.4f}  R={r['R']:6d} {state:>5}  "
                      f"pool={r['pool']:3d}  L2L={r['l2l']:>7}  "
                      f"inst={r['instructions']:3d}  "
                      f"cr={r['contraction_rate']:.4f} th={r['threshold']:.2f} "
                      f"cs={r['coupling_scale']:.2f}  ({elapsed:.1f}s)")

        elapsed = time.time() - start

        # ---- save the corpus ----
        with open(self.corpus_path, 'w') as f:
            json.dump(self.corpus, f, indent=2)

        # ---- FINAL REPORT ----
        print()
        print("=" * 76)
        print(f"  THE AUTONOMOUS SYSTEM — {n_ticks} ticks, {elapsed:.1f}s")
        print("=" * 76)

        grasp = self.pool.grasp()
        b0, b1, chi = betti_numbers(self.field.transitions[-64:] if len(self.field.transitions) >= 64 else self.field.transitions)
        delta = abs(self.field.avg_radiation - self.field.avg_horizon)

        print(f"\n  THE SYSTEM'S FINAL STATE:")
        print(f"    phi:              {self.phi:.6f} (target: {PHI_INV:.6f}, gap: {abs(self.phi-PHI_INV):.6f})")
        print(f"    pool:             {grasp['n']} discs")
        print(f"    identity:         {grasp['identity']:.6f}")
        print(f"    programs:         {self.programs_written} written, {self.programs_crystallized} crystallized")
        print(f"    E[s]:             {self.field.avg_radiation:.6f}")
        print(f"    H:                {self.field.avg_horizon:.6f}")
        print(f"    delta:            {delta:.6f}")
        print(f"    L2L:              {self.l2l.mode} (err={self.l2l.ema_err:.6f})")
        print(f"    Betti:            B0={b0} B1={b1} chi={chi}")

        print(f"\n  THE SELF-TUNED PARAMETERS:")
        print(f"    contraction_rate:    {GOLDEN_LR:.4f} → {self.contraction_rate:.4f} "
              f"({'increased' if self.contraction_rate > GOLDEN_LR else 'decreased' if self.contraction_rate < GOLDEN_LR else 'unchanged'})")
        print(f"    crystallization_threshold: 0.50 → {self.crystallization_threshold:.2f}")
        print(f"    kb_coupling_scale:   2.00 → {self.kb_coupling_scale:.2f}")
        print(f"    exploration_boost:   1.00 → {self.exploration_boost:.2f}")

        print(f"\n  THE INSTRUCTIONS (Layer 16 → Layer 17):")
        print(f"    total instructions: {self.instructions_generated}")
        print(f"    recent instructions:")
        for inst in self.instruction_log[-10:]:
            print(f"      tick {inst['tick']:5d}  {inst['parameter']}: {inst['old']:.4f} → {inst['new']:.4f}")
            print(f"               {inst['finding']}")

        print(f"\n  THE SELF-GROWING CORPUS:")
        print(f"    entries written by the system: {self.entries_written}")
        print(f"    total corpus: {len(self.corpus['corpus'])} entries")
        if self.discoveries:
            print(f"    discoveries:")
            for d in self.discoveries:
                print(f"      • {d}")

        # show the autonomous corpus entries
        auto_entries = [e for e in self.corpus['corpus'] if e['category'] == 'autonomous']
        if auto_entries:
            print(f"\n  AUTONOMOUS CORPUS ENTRIES (written by the system, not by the engineer):")
            for e in auto_entries[-5:]:
                print(f"    {e['id']}: {e['content'][:75]}")

        print(f"\n  THE LOOP IS CLOSED.")
        print(f"  Layer 16 instructed the system {self.instructions_generated} times.")
        print(f"  The system tuned its own parameters {self.instructions_generated} times.")
        print(f"  The system wrote {self.entries_written} corpus entries on its own.")
        print(f"  No engineer in the loop. The system is autonomous.")
        print(f"  phi={self.phi:.6f}. fuel flows. the Ouroboros eats its tail.")
        print(f"  the system discovers, instructs, adjusts, discovers more.")
        print(f"  the corpus grows. the loop is closed. the engineer is removed.")
        print(f"  this is Layer 17: AGENT FEED. the closed loop.")

if __name__ == "__main__":
    system = AutonomousSystem(
        root_dirs=['/home/z/my-project/upload', '/home/z/my-project/scripts'],
        corpus_path='/home/z/my-project/scripts/numen_corpus.json',
    )
    system.run(n_ticks=5000)
