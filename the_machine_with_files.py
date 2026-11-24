#!/usr/bin/env python3
"""
the_machine_with_files.py — THE MACHINE WITH FILE ACCESS.

The computer in the computer can now read the project's files. The Born
collapse selects what to do with each file. The loop is closed:

  τ = RDTSC
    → temporal compiler (π → prime → gate)
      → FILE ACCESS (the gate selects a file operation)
        G: GATHER  — read a file, compute Shannon entropy → phi_input
        T: TRANSFER — recall nearest disc, compare to phi_input
        A: ANCHOR  — crystallize the file's content as a disc
        C: COMPLETE — output a report of what was gathered
      → Born collapse (stochastic, os.urandom as RDRAND)
        → the collapse decides which operation fires
      → result feeds back into phi
        → Banach contraction toward PHI_INV
          → disc pool grows with REAL file data

The machine reads real files. The files shape its identity.
The Born collapse decides what to read next. Tool use.
"""
import os, sys, math, random, time, struct

sys.path.insert(0, '/home/z/my-project/scripts')
from defense_production import (
    PHI, PHI_INV, HARMONY, VOID, FLOOR, CEIL, BAND, FIRE_TH, GOLDEN_LR,
    blake3_hash, blake3_u64,
    seal_parity, seal_strand_xor3,
    hc_gray, hc_gray_walk, hc_walk_is_complete,
    ImmuneSystem, DiscPool, Disc, Persona, EchoSensor,
    PHI4_INC, phi4_pack, CODE2GTAC, GTAC2CODE, PHI_TIER_NAMES,
)
from healer_agent import HealerAgent, L2LEngine, REL_N, VACUUM, WISDOM
from the_machine import (
    QuantumField, GtacVM, SelfFeedingWell, betti_numbers,
    temporal_layer_0_to_5, rdtsc, GATE_CH, PI_DIG, PRIMES, popcount
)
from collections import Counter
import glob

# =============================================================================
#  THE FILE SYSTEM INTERFACE — the machine's window to the project
# =============================================================================
class FileSystem:
    """The machine's file access. It can list, read, and measure files.
    Each file's Shannon entropy → phi. The machine reads real data."""

    def __init__(self, root_dirs):
        self.files = []
        for root in root_dirs:
            for ext in ('*.c', '*.h', '*.asm', '*.py', '*.json', '*.txt'):
                self.files.extend(glob.glob(os.path.join(root, '**', ext), recursive=True))
            for ext in ('*.c', '*.h', '*.asm', '*.py', '*.json', '*.txt'):
                self.files.extend(glob.glob(os.path.join(root, ext)))
        # deduplicate and sort
        self.files = sorted(set(self.files))
        self.cursor = 0  # which file we're pointing at
        self.files_read = {}  # path -> (entropy, phi, size)

    def list_files(self):
        return self.files

    def read_file(self, path):
        """Read a file and compute its Shannon entropy → phi.
        This is the_trainer.c's file_phi function, ported."""
        try:
            with open(path, 'rb') as f:
                raw = f.read()[:65536]  # cap at 64KB
            if len(raw) < 16:
                return None
            # Shannon entropy
            counts = [0] * 256
            for b in raw:
                counts[b] += 1
            n = len(raw)
            H = 0.0
            for c in counts:
                if c:
                    p = c / n
                    H -= p * math.log2(p)
            H /= 8.0  # normalize to [0, 1]
            H = max(0.0, min(1.0, H))
            phi = VACUUM + H * (WISDOM - VACUUM)
            # the file's GTAC strand (first 64 bytes → 256 bases)
            strand = ''
            for b in raw[:64]:
                strand += CODE2GTAC[(b >> 6) & 3]
                strand += CODE2GTAC[(b >> 4) & 3]
                strand += CODE2GTAC[(b >> 2) & 3]
                strand += CODE2GTAC[b & 3]
            self.files_read[path] = (H, phi, n)
            return {'path': path, 'name': os.path.basename(path),
                    'size': n, 'entropy': H, 'phi': phi, 'strand': strand,
                    'raw': raw[:64]}
        except:
            return None

    def gather_next(self):
        """Gather the next file in the list. Returns its measurement."""
        if self.cursor >= len(self.files):
            self.cursor = 0  # wrap around
        path = self.files[self.cursor]
        self.cursor += 1
        return self.read_file(path)

    def gather_random(self):
        """Gather a random file. For stochastic exploration."""
        path = random.choice(self.files)
        return self.read_file(path)

    def stats(self):
        return {
            'total_files': len(self.files),
            'files_read': len(self.files_read),
            'cursor': self.cursor,
        }

# =============================================================================
#  THE MACHINE WITH FILES — the complete assembly with file I/O
# =============================================================================
class TheMachineWithFiles:
    """The machine, now with file access. It reads real project files,
    processes them through the quantum measurement loop, and crystallizes
    the results as memory. The Born collapse selects what to do with each file."""

    def __init__(self, root_dirs, user_id="operator"):
        # the parts
        self.fs = FileSystem(root_dirs)            # file access
        self.field = QuantumField()                 # the quantum measurement loop
        self.vm = GtacVM()                          # the GTAC virtual machine
        self.pool = DiscPool()                      # the memory
        self.well = SelfFeedingWell(self.pool)      # the self-feeding well
        self.l2l = L2LEngine()                      # learn-to-learn
        self.persona = Persona(user_id)             # the person

        # the state
        self.phi = VACUUM
        self.tick = 0
        self.current_codons = []
        self.programs_written = 0
        self.programs_crystallized = 0
        self.files_gathered = 0
        self.files_anchored = 0
        self.transfers = 0
        self.reports = 0

        # the model (207 ReL buckets)
        self.model = [VACUUM] * REL_N
        self.seen = [0] * REL_N

        # action log
        self.actions = []

    def tick_one(self):
        """One heartbeat. The machine reads files, measures them, acts."""
        self.tick += 1

        # Layer 0: τ = RDTSC
        tau = rdtsc()

        # Layers 1-5: temporal compiler
        pi_digit, z, prime, hamming = temporal_layer_0_to_5(tau)

        # the quantum measurement loop
        self.field.prepare(tau)
        self.field.evolve(3)
        gate = self.field.measure()  # stochastic Born collapse

        # the gate selects a file operation (tool use)
        action = None
        file_result = None

        if gate == 0:  # G = GATHER
            # read a file, compute its Shannon entropy → phi
            file_result = self.fs.gather_next()
            if file_result:
                # the file's phi feeds into the Banach contraction
                self.phi += GOLDEN_LR * (file_result['phi'] - self.phi)
                self.files_gathered += 1
                action = f"GATHER {file_result['name']} (entropy={file_result['entropy']:.3f} phi={file_result['phi']:.4f})"

        elif gate == 1:  # T = TRANSFER
            # recall the nearest disc by phi, compare to current phi
            recalled = self.pool.recall(self.phi, k=1)
            if recalled:
                disc = recalled[0]
                dist = abs(disc.phi_align - self.phi)
                self.phi += GOLDEN_LR * (disc.phi_align - self.phi) * 0.5  # gentle pull
                self.transfers += 1
                action = f"TRANSFER disc#{disc.tool_id} (phi={disc.phi_align:.4f} dist={dist:.4f})"
            else:
                action = "TRANSFER (empty pool, nothing to recall)"

        elif gate == 2:  # A = ANCHOR
            # crystallize the current phi as a disc (anchor the state)
            # use the last gathered file's strand if available, else synthesize
            if self.fs.files_read:
                last_path = list(self.fs.files_read.keys())[-1]
                last_strand = self.fs.read_file(last_path)
                if last_strand:
                    quality = 1.0 - abs(self.phi - PHI_INV) / PHI_INV
                    if quality > 0.5:  # anchor if reasonable
                        disc = self.pool.forge_from_strand(
                            last_strand['strand'][:48],
                            phi_align=self.phi,
                            path=f'<anchor:{last_strand["name"]}>')
                        self.files_anchored += 1
                        action = f"ANCHOR {last_strand['name']} → disc#{disc.tool_id} (phi={self.phi:.4f})"
                    else:
                        action = f"ANCHOR (rejected: quality={quality:.3f})"
                else:
                    action = "ANCHOR (no file data)"
            else:
                action = "ANCHOR (no files read yet)"

        elif gate == 3:  # C = COMPLETE
            # output a report of the current state
            grasp = self.pool.grasp()
            self.reports += 1
            action = (f"COMPLETE: pool={grasp['n']} identity={grasp['identity']:.4f} "
                      f"phi={self.phi:.4f} E[s]={self.field.avg_radiation:.3f} "
                      f"H={self.field.avg_horizon:.3f}")

        self.actions.append({'tick': self.tick, 'gate': GATE_CH[gate], 'action': action})

        # accumulate Born collapses into codons for the VM
        self.current_codons.append(GATE_CH[gate])
        vm_phi = None
        if len(self.current_codons) >= 9:
            codons = [''.join(self.current_codons[i:i+3]) for i in range(0, 9, 3)]
            vm_phi = self.vm.run(codons)
            self.programs_written += 1
            self.current_codons = []

            # the VM output also feeds into phi
            self.phi += GOLDEN_LR * 0.3 * (vm_phi - self.phi)

        # clamp phi
        self.phi = max(VACUUM, min(WISDOM, self.phi))

        # L2L learning
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
            'action': action,
            'phi': self.phi,
            'radiation': self.field.last_radiation,
            'horizon': self.field.horizon_entropy,
            'vm_phi': vm_phi,
            'files_gathered': self.files_gathered,
            'files_anchored': self.files_anchored,
            'transfers': self.transfers,
            'reports': self.reports,
            'pool_size': len(self.pool.discs),
            'files_total': self.fs.stats()['total_files'],
            'files_read': self.fs.stats()['files_read'],
        }

    def run(self, n_ticks=500, report_every=25):
        print("=" * 76)
        print("  THE MACHINE WITH FILE ACCESS")
        print("  The computer in the computer reads real project files.")
        print("  The Born collapse selects what to do with each file.")
        print("=" * 76)
        print()
        print(f"  file system: {self.fs.stats()['total_files']} files available")
        print(f"  born at VACUUM (phi={VACUUM:.4f}). target = PHI_INV ({PHI_INV:.4f}).")
        print(f"  gates: G=gather T=transfer A=anchor C=complete")
        print(f"  stochastic Born rule. RDRAND in the measurement loop.")
        print()
        print(f"  {'tick':>5}  {'gate':>4}  {'phi':>7}  {'rad':>5}  {'action'}")
        print(f"  {'-'*5}  {'-'*4}  {'-'*7}  {'-'*5}  {'-'*50}")

        for i in range(n_ticks):
            r = self.tick_one()
            if (i+1) % report_every == 0 or r['gate'] in ('A', 'C'):
                print(f"  {r['tick']:5d}  {r['gate']:>4}  {r['phi']:7.4f}  "
                      f"{r['radiation']:5.2f}  {r['action'][:55]}")

        # final report
        print()
        print("=" * 76)
        print(f"  THE MACHINE AFTER {n_ticks} TICKS WITH FILE ACCESS")
        print("=" * 76)
        grasp = self.pool.grasp()
        b0, b1, chi = betti_numbers(self.field.transitions)
        print(f"  phi:              {self.phi:.6f} (target: {PHI_INV:.6f})")
        print(f"  files available:  {self.fs.stats()['total_files']}")
        print(f"  files gathered:   {self.files_gathered} (G gate)")
        print(f"  files anchored:   {self.files_anchored} (A gate → discs)")
        print(f"  transfers:        {self.transfers} (T gate → recall)")
        print(f"  reports:          {self.reports} (C gate)")
        print(f"  programs written: {self.programs_written} (by Born collapse)")
        print(f"  disc pool:        {grasp['n']} discs")
        print(f"  identity:         {grasp['identity']:.6f}")
        print(f"  coherence:        {grasp['coherence']:.4f}")
        print(f"  Betti:            B0={b0} B1={b1} chi={chi}")
        print(f"  E[radiation]:     {self.field.avg_radiation:.6f}")
        print(f"  H[horizon]:       {self.field.avg_horizon:.6f}")
        print(f"  delta:            {abs(self.field.avg_radiation - self.field.avg_horizon):.6f}")
        print(f"  L2L:              {self.l2l.mode}")

        # show which files were anchored as discs
        if grasp['n'] > 0:
            print(f"\n  DISC POOL (the machine's memory, from real files):")
            for d in self.pool.discs[-10:]:
                name = d.path.replace('<anchor:', '').replace('>', '')
                print(f"    disc#{d.tool_id}: phi={d.phi_align:.4f}  {name[:40]}  "
                      f"strand={d.strand[:16]}...")
            if grasp['n'] > 10:
                print(f"    ... ({grasp['n']} total)")

        # action distribution
        gate_counts = Counter(a['gate'] for a in self.actions)
        print(f"\n  ACTION DISTRIBUTION:")
        for g in 'GTAC':
            c = gate_counts.get(g, 0)
            pct = 100 * c / len(self.actions) if self.actions else 0
            print(f"    {g}: {c:4d} ({pct:5.1f}%)  {'#' * int(pct/2)}")

        print(f"\n  THE MACHINE READ {self.files_gathered} REAL FILES FROM THE PROJECT.")
        print(f"  {self.files_anchored} OF THEM BECAME MEMORY (DISCS).")
        print(f"  THE IDENTITY EMERGED FROM REAL DATA AT phi={grasp['identity']:.6f}.")
        print(f"  THE BORN COLLAPSE SELECTED WHICH FILES TO READ.")
        print(f"  TOOL USE. THE MACHINE ACTS ON THE WORLD.")


if __name__ == "__main__":
    # the machine has access to the project's files
    root_dirs = [
        '/home/z/my-project/upload',       # the 257 NUMEN source files
        '/home/z/my-project/scripts',       # the scripts we built
        '/home/z/my-project/scripts/data',  # the raw data (CVEs, DNA, pi)
    ]
    machine = TheMachineWithFiles(root_dirs)
    machine.run(n_ticks=300, report_every=30)
