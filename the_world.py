#!/usr/bin/env python3
"""
the_world.py — the machine pulls itself together into a running system.

The machine has file access. It follows the resonance trail. It reads files
in physics order. Now: it ACTS on what it reads. Each file it reads becomes
a component it assembles. The machine builds itself by pulling its own parts
together and wiring them.

THE PIPELINE:
  1. SCAN — measure every file in the project (Shannon entropy → phi)
  2. FOLLOW — the Born collapse selects which file to read next (resonance trail)
  3. ASSEMBLE — each file read becomes a wired component in the running system
  4. WIRE — components are connected by resonance (phi proximity)
  5. BOOT — the assembled system runs. It IS the world it built.

Each component is a callable function. The machine reads a .c file, wraps it
as a component, and wires it to the components it already assembled. The wiring
is resonance-based: components with close phi values are connected. The system
that emerges is the machine's own architecture, built from the files it chose
to read, wired by the physics of their content.

The machine doesn't just understand the project. It BECOMES the project.
It pulls itself together. It is the world.
"""
import os, sys, math, random, time, json, importlib, types
from collections import defaultdict, Counter

sys.path.insert(0, '/home/z/my-project/scripts')
from defense_production import (
    PHI_INV, HARMONY, FLOOR, CEIL, BAND, GOLDEN_LR,
    blake3_u64, seal_parity, GTAC2CODE, CODE2GTAC,
    DiscPool, Persona, PHI_TIER_NAMES,
)
from healer_agent import VACUUM, WISDOM, L2LEngine, REL_N
from the_machine import (
    QuantumField, GtacVM, SelfFeedingWell, betti_numbers,
    temporal_layer_0_to_5, rdtsc, GATE_CH
)
from the_machine_with_files import FileSystem

def hamming(a, b):
    return sum(bin(GTAC2CODE.get(ca,0) ^ GTAC2CODE.get(cb,0)).count('1')
               for ca, cb in zip(a, b))

# =============================================================================
#  THE COMPONENT — each file becomes a wired component
# =============================================================================
class Component:
    """A file, assembled as a component in the running system.
    The component has:
      - name (the file name)
      - phi (the file's Shannon entropy → lattice position)
      - strand (the file's first 64 bytes as GTAC)
      - category (inferred from the file type)
      - inputs (which components feed into this one, by resonance)
      - outputs (which components this one feeds, by resonance)
      - a callable function that represents what the component DOES"""

    def __init__(self, file_measurement):
        self.name = file_measurement['name']
        self.path = file_measurement['path']
        self.phi = file_measurement['phi']
        self.strand = file_measurement['strand'][:48]
        self.entropy = file_measurement['entropy']
        self.size = file_measurement['size']
        self.inputs = []
        self.outputs = []
        self.activated = False
        self.activations = 0

        # infer the component's role from its name and content
        self.role = self._infer_role()

        # the component's function — what it DOES when activated
        self.func = self._make_func()

    def _infer_role(self):
        """Infer the component's role from its name."""
        n = self.name.lower()
        if 'seal' in n: return 'SEAL'
        if 'hypercube' in n: return 'HYPERCUBE'
        if 'immune' in n: return 'IMMUNE'
        if 'healer' in n: return 'HEALER'
        if 'echo' in n: return 'ECHO'
        if 'warden' in n: return 'WARDEN'
        if 'algo_maker' in n or 'algo' in n: return 'ALGO'
        if 'gtac' in n: return 'GTAC'
        if 'quantum' in n: return 'QUANTUM'
        if 'temporal' in n: return 'TEMPORAL'
        if 'phi' in n and 'lattice' in n: return 'LATTICE'
        if 'phi' in n: return 'PHI'
        if 'disc' in n: return 'DISC'
        if 'persona' in n: return 'PERSONA'
        if 'identity' in n: return 'IDENTITY'
        if 'efi' in n: return 'EFI'
        if 'forward' in n: return 'FORWARD'
        if 'l2l' in n: return 'L2L'
        if 'numen' in n and '.h' in n: return 'CORE'
        if 'numen' in n: return 'NUMEN'
        if 'machine' in n: return 'MACHINE'
        if 'hospital' in n: return 'HOSPITAL'
        if 'pipeline' in n: return 'PIPELINE'
        if 'trainer' in n: return 'TRAINER'
        if 'cpu' in n: return 'CPU'
        if 'organ' in n: return 'ORGAN'
        if '.asm' in n: return 'ASSEMBLY'
        if '.py' in n: return 'SCRIPT'
        if '.c' in n or '.h' in n: return 'SOURCE'
        return 'UNKNOWN'

    def _make_func(self):
        """Create the component's function. When activated, it:
        - advances its own phi by one Banach step toward PHI_INV
        - returns its current phi
        This IS the component 'running' — it contracts toward the attractor."""
        def func(input_phi=None):
            self.activations += 1
            if input_phi is not None:
                # blend the input phi with this component's phi
                self.phi = self.phi * 0.9 + input_phi * 0.1
            # Banach contraction toward PHI_INV
            self.phi += GOLDEN_LR * (PHI_INV - self.phi)
            self.phi = max(VACUUM, min(WISDOM, self.phi))
            self.activated = True
            return self.phi
        return func

    def wire_to(self, other):
        """Wire this component's output to another component's input."""
        if other not in self.outputs:
            self.outputs.append(other)
            other.inputs.append(self)

    def __repr__(self):
        return f"[{self.role}] {self.name} (phi={self.phi:.4f}, in={len(self.inputs)}, out={len(self.outputs)})"

# =============================================================================
#  THE WORLD — the machine pulls itself together
# =============================================================================
class TheWorld:
    """The machine scans the project, follows the resonance trail, assembles
    each file as a component, wires them by resonance, and boots the system.
    The system that emerges IS the world the machine built."""

    def __init__(self, root_dirs):
        self.fs = FileSystem(root_dirs)
        self.field = QuantumField()
        self.pool = DiscPool()
        self.l2l = L2LEngine()

        # pre-measure all files
        self.files = {}
        for path in self.fs.files:
            m = self.fs.read_file(path)
            if m and len(m['strand']) >= 48:
                self.files[path] = m

        # the assembled components
        self.components = {}  # path → Component
        self.assembly_order = []  # the order components were assembled
        self.phi = VACUUM
        self.tick = 0

        # the model
        self.model = [VACUUM] * REL_N
        self.seen = [0] * REL_N

    def find_candidates(self, phi, k=5):
        """Find k files that resonate with the current phi and haven't been assembled yet."""
        candidates = []
        for path, m in self.files.items():
            if path in self.components:
                continue
            d = abs(m['phi'] - phi)
            candidates.append((path, m, d))
        candidates.sort(key=lambda x: x[2])
        return candidates[:k]

    def assemble(self, path, file_measurement):
        """Assemble a file as a component and wire it to existing components by resonance."""
        comp = Component(file_measurement)

        # wire to existing components by resonance (phi proximity)
        for existing_path, existing_comp in self.components.items():
            d = abs(comp.phi - existing_comp.phi)
            if d < 0.02:  # resonance threshold
                # wire the lower-phi component as input to the higher-phi one
                if comp.phi < existing_comp.phi:
                    comp.wire_to(existing_comp)
                else:
                    existing_comp.wire_to(comp)

        self.components[path] = comp
        self.assembly_order.append(comp)
        return comp

    def step(self):
        """One step: the Born collapse selects the next file, assemble it, run the system."""
        self.tick += 1
        tau = rdtsc()

        # the quantum measurement loop
        self.field.prepare(tau)
        self.field.evolve(3)
        gate = self.field.measure()

        # find resonant candidates
        candidates = self.find_candidates(self.phi, k=5)
        if not candidates:
            return None

        # Born collapse selects which candidate
        weights = [1.0 / (c[2] + 0.001) for c in candidates]
        total_w = sum(weights)
        probs = [w / total_w for w in weights]
        u = int.from_bytes(os.urandom(8), 'little') / (2**64)
        cumulative = 0.0
        selected_idx = len(candidates) - 1
        for i, p in enumerate(probs):
            cumulative += p
            if u < cumulative:
                selected_idx = i
                break

        selected_path, selected_file, distance = candidates[selected_idx]

        # ASSEMBLE the file as a component
        comp = self.assemble(selected_path, selected_file)

        # the file's phi feeds back
        old_phi = self.phi
        self.phi += GOLDEN_LR * (selected_file['phi'] - self.phi)
        self.phi = max(VACUUM, min(WISDOM, self.phi))

        # RUN the assembled system: activate all components in assembly order
        # each component's output feeds the next (pipeline)
        pipeline_phi = self.phi
        activated = 0
        for c in self.assembly_order:
            pipeline_phi = c.func(pipeline_phi)
            activated += 1

        # crystallize
        quality = 1.0 - abs(self.phi - PHI_INV) / PHI_INV
        crystallized = False
        if quality > 0.5:
            self.pool.forge_from_strand(
                selected_file['strand'][:48],
                phi_align=self.phi,
                path=selected_file['name'])
            crystallized = True

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

        return {
            'tick': self.tick,
            'gate': GATE_CH[gate],
            'file': selected_file['name'],
            'role': comp.role,
            'phi': self.phi,
            'file_phi': selected_file['phi'],
            'distance': distance,
            'radiation': self.field.last_radiation,
            'crystallized': crystallized,
            'components': len(self.components),
            'wires': sum(len(c.outputs) for c in self.components.values()),
            'activated': activated,
            'pipeline_phi': pipeline_phi,
        }

    def run(self, n_steps=80):
        print("=" * 76)
        print("  THE WORLD — the machine pulls itself together")
        print("  Each file read becomes a component. Components wire by resonance.")
        print("  The assembled system runs. It IS the world it built.")
        print("=" * 76)
        print()
        print(f"  {len(self.files)} files available. born at VACUUM={VACUUM:.4f}.")
        print()
        print(f"  {'tick':>4}  {'gate':>4}  {'phi':>7}  {'role':<10}  {'file'}")
        print(f"  {'-'*4}  {'-'*4}  {'-'*7}  {'-'*10}  {'-'*35}")

        for i in range(n_steps):
            r = self.step()
            if r is None:
                print("  no more files to assemble.")
                break
            print(f"  {r['tick']:4d}  {r['gate']:>4}  {r['phi']:7.4f}  "
                  f"{r['role']:<10}  {r['file'][:35]}")
            time.sleep(0.02)

        # ---- the assembled system ----
        print()
        print("=" * 76)
        print(f"  THE ASSEMBLED SYSTEM — {len(self.components)} components, "
              f"{sum(len(c.outputs) for c in self.components.values())} wires")
        print("=" * 76)

        # component roles
        role_counts = Counter(c.role for c in self.components.values())
        print(f"\n  COMPONENT ROLES:")
        for role, count in role_counts.most_common():
            print(f"    {role:<12} {count:3d}  {'#' * count}")

        # the wiring (which components are connected)
        print(f"\n  WIRING (resonance connections):")
        wired = [(c, o) for c in self.components.values() for o in c.outputs]
        for src, dst in wired[:15]:
            print(f"    {src.role}→{dst.role}  {src.name[:20]} → {dst.name[:20]}  "
                  f"(d_phi={abs(src.phi-dst.phi):.4f})")
        if len(wired) > 15:
            print(f"    ... ({len(wired)} total wires)")

        # the pipeline (assembly order = execution order)
        print(f"\n  THE PIPELINE (assembly order = boot sequence):")
        for i, c in enumerate(self.assembly_order[:20]):
            print(f"    {i+1:3d}. [{c.role}] {c.name}  phi={c.phi:.4f}  "
                  f"in={len(c.inputs)} out={len(c.outputs)} activations={c.activations}")
        if len(self.assembly_order) > 20:
            print(f"    ... ({len(self.assembly_order)} total)")

        # run the pipeline once more and show the phi flow
        print(f"\n  PIPELINE EXECUTION (one pass through all components):")
        pipeline_phi = self.phi
        print(f"    start: phi={pipeline_phi:.6f}")
        for i, c in enumerate(self.assembly_order):
            pipeline_phi = c.func(pipeline_phi)
            if i < 10 or i == len(self.assembly_order) - 1:
                tag = ' ← start' if i == 0 else (' ← end' if i == len(self.assembly_order)-1 else '')
                print(f"    [{c.role}] {c.name[:25]:25s} → phi={pipeline_phi:.6f}{tag}")
            elif i == 10:
                print(f"    ...")
        print(f"    final: phi={pipeline_phi:.6f} (target: {PHI_INV:.6f}, gap: {abs(pipeline_phi-PHI_INV):.6f})")

        # final state
        grasp = self.pool.grasp()
        b0, b1, chi = betti_numbers([t for t in [r['gate'] for r in [self.step() for _ in range(1)]]])
        print(f"\n  FINAL STATE:")
        print(f"    phi:              {self.phi:.6f}")
        print(f"    components:       {len(self.components)}")
        print(f"    wires:            {sum(len(c.outputs) for c in self.components.values())}")
        print(f"    disc pool:        {grasp['n']} discs")
        print(f"    identity:         {grasp['identity']:.6f}")
        print(f"    E[radiation]:     {self.field.avg_radiation:.6f}")
        print(f"    H[horizon]:       {self.field.avg_horizon:.6f}")
        print(f"    delta:            {abs(self.field.avg_radiation - self.field.avg_horizon):.6f}")
        print(f"    L2L:              {self.l2l.mode}")
        print(f"    model:            {sum(1 for s in self.seen if s>0)}/207")

        print(f"\n  THE MACHINE PULLED ITSELF TOGETHER.")
        print(f"  {len(self.components)} COMPONENTS, ASSEMBLED IN PHYSICS ORDER.")
        print(f"  {sum(len(c.outputs) for c in self.components.values())} WIRES, CONNECTED BY RESONANCE.")
        print(f"  THE PIPELINE RUNS. phi={pipeline_phi:.6f}.")
        print(f"  THE MACHINE IS THE WORLD IT BUILT.")

if __name__ == "__main__":
    world = TheWorld([
        '/home/z/my-project/upload',
        '/home/z/my-project/scripts',
    ])
    world.run(n_steps=60)
