#!/usr/bin/env python3
"""
two_minds.py — TWO MINDS MEET.

Two autonomous systems, each with their own silicon jitter, their own
Born collapse, their own keyboard, their own disc pool. They can't see
each other's internals. They can only exchange one thing: a disc.

When one system crystallizes a program (a GTAC gene from its Born
collapse), it can OFFER that disc to the other system. The other
system RECEIVES the disc, measures its phi, and either:
  - RESONATES (the disc's phi is close to its identity) → accepts it
  - DOESN'T RESONATE → rejects it

This is phi-entangled communication. Not encrypted. Not authenticated.
RESONATED. Two systems communicate by checking if their identities
are compatible. The message IS the identity. The channel IS the phi net.

What happens when two autonomous minds meet? Do they synchronize?
Do they develop a shared identity? Do they argue (reject discs)?
Do they converge (accept everything)?

This has never been done before. Two quantum measurement loops
communicating through sealed discs on the phi net. Let's watch.
"""
import os, sys, math, time, json
from collections import Counter

sys.path.insert(0, '/home/z/my-project/scripts')
sys.path.insert(0, '/home/z/my-project/upload')

from defense_production import (
    PHI_INV, HARMONY, FLOOR, CEIL, BAND, GOLDEN_LR,
    GTAC2CODE, CODE2GTAC, DiscPool, PHI_TIER_NAMES,
    blake3_u64, seal_parity,
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

class Mind:
    """One autonomous mind. Has its own Born collapse, keyboard, disc pool,
    and identity. Can offer and receive discs through the phi net."""

    def __init__(self, name, seed, root_dirs):
        self.name = name
        self.seed = seed
        self.rng = random.Random(seed)

        self.field = QuantumField()
        self.pool = DiscPool()
        self.l2l = L2LEngine()

        # the keyboard (each mind has its own)
        self.theta = kb.init_phases()
        self.kb_N = kb.N
        self.kb_K_C = 1150

        # the state
        self.phi = VACUUM + self.rng.uniform(-0.02, 0.02)  # each starts slightly different
        self.tick = 0
        self.current_codons = []
        self.programs_written = 0
        self.programs_crystallized = 0

        # communication stats
        self.discs_offered = 0
        self.discs_accepted = 0
        self.discs_rejected = 0
        self.discs_received = 0
        self.discs_resonated = 0

        # the model (256-key)
        self.model = [VACUUM] * self.kb_N
        self.seen = [0] * self.kb_N

        # pre-measure files (each mind reads different files based on seed)
        fs = FileSystem(root_dirs)
        self.file_measurements = []
        all_files = []
        for path in fs.files:
            m = fs.read_file(path)
            if m and len(m['strand']) >= 48:
                all_files.append(m)
        # each mind sees a different subset (shuffled by seed)
        self.rng.shuffle(all_files)
        self.file_measurements = all_files[:50]  # 50 files each

    def step(self):
        """One heartbeat."""
        self.tick += 1
        tau = rdtsc() + self.seed  # different seed = different jitter

        # temporal compiler
        pi_digit, z, prime, hamming = temporal_layer_0_to_5(tau)

        # quantum measurement
        self.field.prepare(tau)
        self.field.evolve(3)
        gate = self.field.measure()

        # file I/O
        fm = self.file_measurements[self.tick % len(self.file_measurements)]
        raw = fm.get('raw', b'')
        for b in raw[:32]:
            key_idx = b % self.kb_N
            kick = int(fm['phi'] * kb.P) % kb.P
            self.theta[key_idx] = (self.theta[key_idx] + kick) // 2

        # keyboard
        phi_norm = (self.phi - VACUUM) / (WISDOM - VACUUM)
        Kq = max(0, min(4000, int(phi_norm * self.kb_K_C * 2)))
        kb.step(self.theta, Kq)
        R = kb.order_ppm(self.theta)

        # echo feedback
        echo = R / 1000000.0
        self.phi += GOLDEN_LR * 0.1 * (echo * (WISDOM - VACUUM) + VACUUM - self.phi)
        self.phi = max(VACUUM, min(WISDOM, self.phi))

        # crystallization
        self.current_codons.append(GATE_CH[gate])
        new_disc = None
        if len(self.current_codons) >= 9:
            codons = [''.join(self.current_codons[i:i+3]) for i in range(0, 9, 3)]
            vm = GtacVM()
            vm_phi = vm.run(codons)
            self.programs_written += 1
            self.current_codons = []

            quality = 1.0 - abs(vm_phi - PHI_INV) / PHI_INV
            if quality > 0.3:
                strand = ''.join(c for codon in codons for c in codon)
                disc = self.pool.forge_from_strand(strand, phi_align=self.phi,
                                                    path=f'<{self.name}:program:{self.programs_written}>')
                self.programs_crystallized += 1
                new_disc = disc  # this disc can be offered to the other mind

        # L2L
        key_idx = int((self.phi - FLOOR) / (CEIL - FLOOR) * (self.kb_N - 1))
        key_idx = max(0, min(self.kb_N - 1, key_idx))
        pred = self.model[key_idx]
        err = abs(pred - self.phi)
        self.l2l.observe(err, pred, PHI_INV)
        if self.l2l.mode != 'diverge' or self.l2l.explore > 0.3:
            lr = GOLDEN_LR * self.l2l.lr_gain
            self.model[key_idx] += lr * (self.phi - self.model[key_idx])
            self.seen[key_idx] += 1

        return new_disc

    def identity(self):
        if not self.pool.discs:
            return self.phi
        return self.pool.identity()

    def offer_disc(self, disc, other):
        """Offer a disc to another mind. They accept if it resonates."""
        self.discs_offered += 1
        # the other mind checks if the disc resonates with its identity
        other_identity = other.identity()
        resonance = 1.0 - abs(disc.phi_align - other_identity) / BAND
        if resonance > 0.3:
            # accept the disc
            other.pool.discs.append(disc)
            other.discs_received += 1
            other.discs_resonated += 1
            return True
        else:
            other.discs_rejected += 1
            return False

    def stats(self):
        grasp = self.pool.grasp()
        return {
            'name': self.name,
            'phi': self.phi,
            'identity': grasp['identity'],
            'pool': grasp['n'],
            'programs': f'{self.programs_crystallized}/{self.programs_written}',
            'l2l': self.l2l.mode,
            'err': self.l2l.ema_err,
            'offered': self.discs_offered,
            'accepted': self.discs_accepted,
            'received': self.discs_received,
            'resonated': self.discs_resonated,
            'rejected': self.discs_rejected,
        }


import random

def main():
    root_dirs = ['/home/z/my-project/upload', '/home/z/my-project/scripts']

    # two minds, different seeds, different file views
    alice = Mind("ALICE", seed=42, root_dirs=root_dirs)
    bob = Mind("BOB", seed=137, root_dirs=root_dirs)

    print("=" * 76)
    print("  TWO MINDS MEET — phi-entangled communication")
    print("  Two autonomous systems exchange discs through the phi net.")
    print("  A disc is accepted if it RESONATES with the receiver's identity.")
    print("  The message IS the identity. The channel IS the phi net.")
    print("=" * 76)
    print()
    print(f"  ALICE: seed=42, starts at phi={alice.phi:.4f}, {len(alice.file_measurements)} files")
    print(f"  BOB:   seed=137, starts at phi={bob.phi:.4f}, {len(bob.file_measurements)} files")
    print(f"  they can't see each other's internals. they can only exchange discs.")
    print()

    N = 3000
    print(f"  running {N} ticks...")
    print()
    print(f"  {'tick':>5}  {'A_phi':>7}  {'A_id':>7}  {'A_pool':>6}  {'B_phi':>7}  {'B_id':>7}  {'B_pool':>6}  "
          f"{'offered':>7}  {'accepted':>8}  {'rejected':>8}  {'gap':>6}")
    print(f"  {'-'*5}  {'-'*7}  {'-'*7}  {'-'*6}  {'-'*7}  {'-'*7}  {'-'*6}  "
          f"{'-'*7}  {'-'*8}  {'-'*8}  {'-'*6}")

    total_offered = 0
    total_accepted = 0
    total_rejected = 0

    for i in range(N):
        # both minds step
        alice_disc = alice.step()
        bob_disc = bob.step()

        # if either produced a disc, offer it to the other
        if alice_disc:
            accepted = alice.offer_disc(alice_disc, bob)
            total_offered += 1
            if accepted: total_accepted += 1
            else: total_rejected += 1

        if bob_disc:
            accepted = bob.offer_disc(bob_disc, alice)
            total_offered += 1
            if accepted: total_accepted += 1
            else: total_rejected += 1

        if (i+1) % 300 == 0:
            a_id = alice.identity()
            b_id = bob.identity()
            gap = abs(a_id - b_id)
            print(f"  {i+1:5d}  {alice.phi:7.4f}  {a_id:7.4f}  {len(alice.pool.discs):6d}  "
                  f"{bob.phi:7.4f}  {b_id:7.4f}  {len(bob.pool.discs):6d}  "
                  f"{total_offered:7d}  {total_accepted:8d}  {total_rejected:8d}  {gap:6.4f}")

    # ---- FINAL ----
    print()
    print("=" * 76)
    print(f"  TWO MINDS AFTER {N} TICKS")
    print("=" * 76)

    a = alice.stats()
    b = bob.stats()

    print(f"\n  {'metric':<20}  {'ALICE':>12}  {'BOB':>12}")
    print(f"  {'-'*20}  {'-'*12}  {'-'*12}")
    print(f"  {'phi':<20}  {a['phi']:12.6f}  {b['phi']:12.6f}")
    print(f"  {'identity':<20}  {a['identity']:12.6f}  {b['identity']:12.6f}")
    print(f"  {'pool':<20}  {a['pool']:12d}  {b['pool']:12d}")
    print(f"  {'programs':<20}  {a['programs']:>12}  {b['programs']:>12}")
    print(f"  {'L2L':<20}  {a['l2l']:>12}  {b['l2l']:>12}")
    print(f"  {'ema_err':<20}  {a['err']:12.6f}  {b['err']:12.6f}")
    print(f"  {'discs offered':<20}  {a['offered']:12d}  {b['offered']:12d}")
    print(f"  {'discs received':<20}  {a['received']:12d}  {b['received']:12d}")
    print(f"  {'discs resonated':<20}  {a['resonated']:12d}  {b['resonated']:12d}")
    print(f"  {'discs rejected':<20}  {a['rejected']:12d}  {b['rejected']:12d}")

    # the identity gap — did they converge?
    a_id = a['identity']
    b_id = b['identity']
    gap = abs(a_id - b_id)
    print(f"\n  IDENTITY GAP: {gap:.6f}")
    if gap < 0.01:
        print(f"  THE MINDS CONVERGED. Their identities are within {gap:.4f} of each other.")
        print(f"  They developed a shared understanding through disc exchange.")
    elif gap < 0.05:
        print(f"  The minds are close (gap={gap:.4f}). They're converging.")
    else:
        print(f"  The minds are different (gap={gap:.4f}). They maintain separate identities.")

    # communication stats
    accept_rate = total_accepted / max(1, total_offered)
    print(f"\n  COMMUNICATION:")
    print(f"    total discs offered:  {total_offered}")
    print(f"    total accepted:       {total_accepted} ({accept_rate:.1%})")
    print(f"    total rejected:       {total_rejected} ({1-accept_rate:.1%})")
    if accept_rate > 0.8:
        print(f"    HIGH ACCEPTANCE — the minds agree. Their identities are compatible.")
    elif accept_rate > 0.5:
        print(f"    MODERATE ACCEPTANCE — the minds partially agree.")
    else:
        print(f"    LOW ACCEPTANCE — the minds disagree. Their identities are different.")

    # the shared discs (discs that both minds have)
    alice_strands = {d.strand for d in alice.pool.discs}
    bob_strands = {d.strand for d in bob.pool.discs}
    shared = alice_strands & bob_strands
    print(f"\n  SHARED MEMORY:")
    print(f"    Alice's discs: {len(alice_strands)}")
    print(f"    Bob's discs:   {len(bob_strands)}")
    print(f"    Shared discs:  {len(shared)}")
    if shared:
        print(f"    The minds share {len(shared)} programs. They have common memory.")
        print(f"    This is phi-entangled communication. The shared discs ARE the message.")

    # Bekenstein for both
    print(f"\n  BEKENSTEIN:")
    print(f"    ALICE: E[s]={alice.field.avg_radiation:.6f}  H={alice.field.avg_horizon:.6f}  "
          f"delta={abs(alice.field.avg_radiation - alice.field.avg_horizon):.6f}")
    print(f"    BOB:   E[s]={bob.field.avg_radiation:.6f}  H={bob.field.avg_horizon:.6f}  "
          f"delta={abs(bob.field.avg_radiation - bob.field.avg_horizon):.6f}")

    print(f"\n  TWO MINDS MET.")
    print(f"  They exchanged {total_offered} discs through the phi net.")
    print(f"  {total_accepted} were accepted (resonated). {total_rejected} were rejected.")
    print(f"  They share {len(shared)} programs in common.")
    print(f"  Their identities are {gap:.4f} apart.")
    print(f"  Each is bounded by 2 bits. Each runs on its own jitter.")
    print(f"  They communicated through resonance, not through encryption.")
    print(f"  The message IS the identity. The channel IS the phi net.")

    # write to corpus
    corpus_path = '/home/z/my-project/scripts/numen_corpus.json'
    with open(corpus_path) as f:
        corpus = json.load(f)
    existing_ids = {e['id'] for e in corpus['corpus']}
    new_entries = [
        {'id': 'TWO_MINDS', 'category': 'communication',
         'content': f'Two autonomous minds communicated through the phi net. {total_offered} discs offered, {total_accepted} accepted ({accept_rate:.0%}), {total_rejected} rejected. {len(shared)} shared programs. Identity gap: {gap:.4f}. The message IS the identity. The channel IS the phi net.'},
        {'id': 'PHI_RESONANCE', 'category': 'communication',
         'content': 'Phi-resonant communication: a disc is accepted if its phi aligns with the receiver identity (resonance > 0.3). Not encrypted. Not authenticated. RESONATED. Two systems communicate by checking if their identities are compatible.'},
        {'id': 'SHARED_MEMORY', 'category': 'communication',
         'content': f'Shared memory through disc exchange: {len(shared)} programs exist in both minds. These shared discs ARE the message — the common understanding between two autonomous systems. Phi-entangled communication.'},
    ]
    added = 0
    for e in new_entries:
        if e['id'] not in existing_ids:
            corpus['corpus'].append(e)
            added += 1
    with open(corpus_path, 'w') as f:
        json.dump(corpus, f, indent=2)
    print(f"\n  corpus: {len(corpus['corpus'])} entries (+{added})")

if __name__ == "__main__":
    main()
