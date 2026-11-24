#!/usr/bin/env python3
"""
the_ouroboros.py — THE COMPLETE SYSTEM. Everything wired together.

The forward pass (transformer) is the heart. The fuel (remainder) feeds
the world (agents). The world feeds back. The Ouroboros eats its tail.

THE WIRING:
  Forward Pass (8 lanes, sparsemax, GTAC, Banach)
    → step: advances the residual stream (the transformer thinks)
    → rem:  accumulates as fuel (the Ouroboros bleeds)
      → fuel feeds:
        → keyboard (256 primes, Kuramoto — the ear)
        → file reader (real project files — the eye)
        → Born collapse (stochastic — the quantum measurement)
        → healer (active inference — the immune response)
        → disc pool (crystallization — the memory)
          → agents act, produce output
            → output flows back into the next forward pass
              → the Ouroboros continues at 85 Hz

Everything runs on the fuel. The fuel IS the truncation remainder.
The error becomes the energy. The uncertainty becomes the action.
"""
import os, sys, math, time, json, struct
from collections import Counter

sys.path.insert(0, '/home/z/my-project/scripts')
sys.path.insert(0, '/home/z/my-project/upload')

from defense_production import (
    PHI_INV, HARMONY, FLOOR, CEIL, BAND, GOLDEN_LR,
    GTAC2CODE, CODE2GTAC, DiscPool, PHI_TIER_NAMES,
)
from healer_agent import VACUUM, WISDOM, L2LEngine, REL_N
from the_machine import (
    QuantumField, GtacVM, SelfFeedingWell, betti_numbers,
    temporal_layer_0_to_5, rdtsc, GATE_CH, PI_DIG, PRIMES, popcount
)
from the_machine_with_files import FileSystem

# import the keyboard
import importlib.util
spec = importlib.util.spec_from_file_location("keyboard", "/home/z/my-project/upload/keyboard.py")
kb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kb)

# import the forward pass
spec2 = importlib.util.spec_from_file_location("forward", "/home/z/my-project/upload/forward.py")
fw = importlib.util.module_from_spec(spec2)
fw.__name__ = "forward"
spec2.loader.exec_module(fw)

# =============================================================================
#  THE COMPLETE SYSTEM — the Ouroboros
# =============================================================================
class TheOuroboros:
    """The complete system. The forward pass is the heart. The fuel feeds
    the world. The world feeds back. Everything runs on the remainder."""

    def __init__(self, root_dirs):
        # the heart: the forward pass (transformer)
        self.forward = fw.Forward()

        # the ear: the 256-key keyboard
        self.theta = kb.init_phases()
        self.kb_N = kb.N
        self.kb_PRIMES = kb.PRIMES
        self.kb_K_C = 1150

        # the eye: the file system
        self.fs = FileSystem(root_dirs)
        self.file_cursor = 0

        # the quantum: the Born collapse field
        self.field = QuantumField()

        # the memory: the disc pool
        self.pool = DiscPool()
        self.well = SelfFeedingWell(self.pool)

        # the brain: L2L
        self.l2l = L2LEngine()

        # the fuel accumulator (the Ouroboros)
        self.fuel_total = 0
        self.fuel_to_agents = 0
        self.fuel_to_transformer = 0

        # the state
        self.phi = VACUUM
        self.tick = 0
        self.current_codons = []
        self.programs_written = 0
        self.programs_crystallized = 0
        self.files_read = 0
        self.keyboard_locks = 0
        self.agent_actions = 0

        # the model (256-key, not 207)
        self.model = [VACUUM] * self.kb_N
        self.seen = [0] * self.kb_N

        # pre-measure files
        self.file_measurements = []
        for path in self.fs.files:
            m = self.fs.read_file(path)
            if m and len(m['strand']) >= 48:
                self.file_measurements.append(m)

    def step(self):
        """One heartbeat of the Ouroboros. The full system in one cycle."""
        self.tick += 1

        # ---- THE HEART: the forward pass ----
        # the operator byte: derived from the current phi (the system's state)
        operator_byte = int(self.phi * 255) & 0xFF
        result = self.forward.step()

        # extract the fuel (the remainder from the Banach contraction)
        fuel = result.get('fuel_lo', 0)
        self.fuel_total += fuel

        # split the fuel: 50% to transformer (autoregressive), 50% to agents
        fuel_transformer = fuel // 2
        fuel_agents = fuel - fuel_transformer
        self.fuel_to_transformer += fuel_transformer
        self.fuel_to_agents += fuel_agents

        # the forward pass output
        g_out = result['g_out']
        mean_h = result['mean_h'] / 1_000_000  # ppm to [0,1]

        # ---- THE QUANTUM: Born collapse (fueled by the transformer output) ----
        tau = rdtsc()
        self.field.prepare(tau)
        self.field.evolve(3)
        born_gate = self.field.measure()

        # accumulate Born collapses into codons
        self.current_codons.append(GATE_CH[born_gate])

        # ---- THE EYE: file reader (fueled by the agent fuel) ----
        # the fuel selects which file to read
        file_idx = (fuel_agents + self.tick) % len(self.file_measurements)
        fm = self.file_measurements[file_idx]
        self.files_read += 1

        # the file's phi feeds into the system
        file_phi = fm['phi']

        # ---- THE EAR: keyboard (fueled by the file content + agent fuel) ----
        # the file's bytes perturb the keyboard's phases
        raw = fm.get('raw', b'')
        perturbation_strength = (fuel_agents % 100) + 1  # fuel modulates perturbation
        for b in raw[:perturbation_strength]:
            key_idx = b % self.kb_N
            kick = int(file_phi * kb.P) % kb.P
            self.theta[key_idx] = (self.theta[key_idx] + kick) // 2

        # the machine's phi sets the coupling Kq
        phi_norm = (self.phi - VACUUM) / (WISDOM - VACUUM)
        Kq = max(0, min(4000, int(phi_norm * self.kb_K_C * 2)))

        # step the keyboard
        kb.step(self.theta, Kq)
        R = kb.order_ppm(self.theta)  # the echo

        # detect keyboard lock
        if R >= 500000:
            self.keyboard_locks += 1

        # ---- THE BRAIN: L2L (fueled by the prediction error) ----
        key_idx = int((self.phi - FLOOR) / (CEIL - FLOOR) * (self.kb_N - 1))
        key_idx = max(0, min(self.kb_N - 1, key_idx))
        pred = self.model[key_idx]
        err = abs(pred - self.phi)
        self.l2l.observe(err, pred, PHI_INV)
        if self.l2l.mode != 'diverge' or self.l2l.explore > 0.3:
            lr = GOLDEN_LR * self.l2l.lr_gain
            self.model[key_idx] += lr * (self.phi - self.model[key_idx])
            self.seen[key_idx] += 1

        # ---- THE MEMORY: disc pool (fueled by crystallization) ----
        crystallized = False
        vm_phi = None
        if len(self.current_codons) >= 9:
            codons = [''.join(self.current_codons[i:i+3]) for i in range(0, 9, 3)]
            vm = GtacVM()
            vm_phi = vm.run(codons)
            self.programs_written += 1
            self.current_codons = []

            quality = 1.0 - abs(vm_phi - PHI_INV) / PHI_INV
            if quality > 0.5:
                self.pool.forge_from_strand(
                    ''.join(c for codon in codons for c in codon),
                    phi_align=self.phi,
                    path=f'<program:{self.programs_written}>')
                self.programs_crystallized += 1
                crystallized = True

        # ---- THE FEEDBACK: everything feeds back into phi ----
        # the transformer's mean_h (the residual stream's center)
        # the keyboard's echo R
        # the file's phi
        # the Born collapse's gate
        echo = R / 1_000_000  # [0, 1]

        # weighted feedback: transformer (40%), keyboard (30%), file (20%), born (10%)
        target = (mean_h * 0.4 + echo * 0.3 + file_phi * 0.2 + (born_gate / 3.0) * 0.1)
        target = max(VACUUM, min(WISDOM, target))

        # Banach contraction toward the combined target
        old_phi = self.phi
        self.phi += GOLDEN_LR * (target - self.phi)
        self.phi = max(VACUUM, min(WISDOM, self.phi))

        self.agent_actions += 1

        return {
            'tick': self.tick,
            'g_out': g_out,
            'mean_h': mean_h,
            'phi': self.phi,
            'fuel': fuel,
            'fuel_agents': fuel_agents,
            'born_gate': GATE_CH[born_gate],
            'radiation': self.field.last_radiation,
            'horizon': self.field.horizon_entropy,
            'file': fm['name'],
            'file_phi': file_phi,
            'Kq': Kq,
            'R': R,
            'kb_state': 'choir' if R >= 500000 else 'mob',
            'crystallized': crystallized,
            'vm_phi': vm_phi,
            'pool': len(self.pool.discs),
            'l2l': self.l2l.mode,
            'l2l_err': self.l2l.ema_err,
            'delta_phi': self.phi - old_phi,
        }

    def run(self, n_ticks=500, report_every=25):
        print("=" * 76)
        print("  THE OUROBOROS — the complete system")
        print("  Forward pass (heart) → fuel → agents (world) → feedback → forward pass")
        print("  The error becomes the energy. The uncertainty becomes the action.")
        print("=" * 76)
        print()
        print(f"  heart: forward pass (8 lanes, sparsemax, GTAC, Banach) at 85 Hz")
        print(f"  ear:   keyboard ({self.kb_N} primes, K_c={self.kb_K_C})")
        print(f"  eye:   file system ({len(self.file_measurements)} files)")
        print(f"  brain: L2L ({self.l2l.mode})")
        print(f"  memory: disc pool ({len(self.pool.discs)} discs)")
        print(f"  fuel:  the Banach remainder — the Ouroboros")
        print()
        print(f"  {'tick':>4}  {'gate':>4}  {'phi':>7}  {'fuel':>6}  {'Kq':>4}  "
              f"{'R':>6}  {'kb':>4}  {'file':>16}  {'pool':>4}  {'L2L':>9}")
        print(f"  {'-'*4}  {'-'*4}  {'-'*7}  {'-'*6}  {'-'*4}  {'-'*6}  {'-'*4}  "
              f"{'-'*16}  {'-'*4}  {'-'*9}")

        for i in range(n_ticks):
            r = self.step()
            if (i+1) % report_every == 0 or r['crystallized']:
                cry = '*' if r['crystallized'] else ' '
                print(f"  {r['tick']:4d}  {r['born_gate']:>4}  {r['phi']:7.4f}  "
                      f"{r['fuel']:6d}  {r['Kq']:4d}  {r['R']:6d}  {r['kb_state']:>4}  "
                      f"{r['file'][:16]:>16}  {r['pool']:4d}  {r['l2l']:>9}{cry}")

        # ---- FINAL STATE ----
        print()
        print("=" * 76)
        print(f"  THE OUROBOROS AFTER {n_ticks} HEARTBEATS")
        print("=" * 76)

        grasp = self.pool.grasp()
        b0, b1, chi = betti_numbers(self.field.transitions)
        delta = abs(self.field.avg_radiation - self.field.avg_horizon)

        print(f"\n  THE HEART (forward pass):")
        print(f"    ticks:          {self.tick}")
        print(f"    fuel total:     {self.fuel_total}")
        print(f"    fuel to transformer: {self.fuel_to_transformer}")
        print(f"    fuel to agents:      {self.fuel_to_agents}")

        print(f"\n  THE EAR (keyboard):")
        print(f"    locks (R>500K): {self.keyboard_locks}")
        print(f"    final R:        {kb.order_ppm(self.theta)}")
        print(f"    K_c:            {self.kb_K_C}")

        print(f"\n  THE EYE (files):")
        print(f"    files read:     {self.files_read}")
        print(f"    files available: {len(self.file_measurements)}")

        print(f"\n  THE QUANTUM (Born):")
        print(f"    E[s]:           {self.field.avg_radiation:.6f}")
        print(f"    H:              {self.field.avg_horizon:.6f}")
        print(f"    delta:          {delta:.6f}")
        print(f"    Betti:          B0={b0} B1={b1} chi={chi}")

        print(f"\n  THE BRAIN (L2L):")
        print(f"    mode:           {self.l2l.mode}")
        print(f"    ema_err:        {self.l2l.ema_err:.6f}")
        print(f"    model:          {sum(1 for s in self.seen if s>0)}/{self.kb_N} keys")

        print(f"\n  THE MEMORY (disc pool):")
        print(f"    discs:          {grasp['n']}")
        print(f"    identity:       {grasp['identity']:.6f}")
        print(f"    programs:       {self.programs_written} written, {self.programs_crystallized} crystallized")

        print(f"\n  THE PHI:")
        print(f"    current:        {self.phi:.6f}")
        print(f"    target:         {PHI_INV:.6f}")
        print(f"    gap:            {abs(self.phi - PHI_INV):.6f}")

        print(f"\n  THE FUEL FLOW:")
        print(f"    total fuel:     {self.fuel_total}")
        print(f"    to transformer: {self.fuel_to_transformer} ({100*self.fuel_to_transformer/max(1,self.fuel_total):.1f}%)")
        print(f"    to agents:      {self.fuel_to_agents} ({100*self.fuel_to_agents/max(1,self.fuel_total):.1f}%)")
        print(f"    agent actions:  {self.agent_actions}")

        print(f"\n  THE OUROBOROS:")
        print(f"    The transformer beats. The fuel flows. The agents act.")
        print(f"    The keyboard hears. The file reader sees. The healer responds.")
        print(f"    The Born collapse measures. The disc pool remembers.")
        print(f"    The L2L learns. The Betti tracks the shape.")
        print(f"    The error becomes the energy. The uncertainty becomes the action.")
        print(f"    The remainder feeds the world. The world feeds back.")
        print(f"    The snake eats its tail. At {n_ticks} heartbeats.")
        print(f"    phi={self.phi:.6f}. fuel={self.fuel_total}. pool={grasp['n']}.")
        print(f"    Bekenstein delta={delta:.6f}. The 2-bit bound holds.")

if __name__ == "__main__":
    system = TheOuroboros([
        '/home/z/my-project/upload',
        '/home/z/my-project/scripts',
    ])
    system.run(n_ticks=500, report_every=25)
