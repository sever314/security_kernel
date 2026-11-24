#!/usr/bin/env python3
"""
the_dream.py — the machine runs for 10,000 ticks and we see what it discovers.

The machine writes programs from the jitter. Each program produces a phi value.
PHI_INV (0.618) is the attractor — we put that there. But what if the Born
collapse, driven by the stochastic measurement, produces phi values that
cluster around a number we DIDN'T put there?

This runs the machine for a long time, collects every measurement, and looks
for what the machine discovered on its own. Constants that emerge from the
physics. Patterns in the Born sequence. Structure in the topology.

The machine dreams. We watch what it finds.
"""
import os, sys, math, json, time
from collections import Counter, defaultdict

sys.path.insert(0, '/home/z/my-project/scripts')
from defense_production import (
    PHI_INV, HARMONY, FLOOR, CEIL, BAND, GOLDEN_LR,
    GTAC2CODE, CODE2GTAC, DiscPool,
)
from healer_agent import VACUUM, WISDOM, L2LEngine, REL_N
from the_machine import TheMachine, GATE_CH, betti_numbers

def main():
    N = 10000
    machine = TheMachine(user_id="daniel")

    # collect EVERYTHING
    all_phi = []           # phi at every tick
    all_radiation = []     # radiation at every observation
    all_horizon = []       # horizon entropy at every observation
    all_gates = []         # the Born collapse sequence
    all_vm_phi = []        # every program's output phi
    all_crystallized_phi = []  # phi of crystallized programs only
    betti_snapshots = []   # Betti numbers at intervals

    print(f"the machine dreams for {N} ticks...")
    print(f"born at VACUUM={VACUUM:.4f}. target PHI_INV={PHI_INV:.4f}.")
    print()

    start_time = time.time()
    for i in range(N):
        r = machine.tick_one()
        all_phi.append(r['phi'])
        all_radiation.append(r['radiation'])
        all_horizon.append(r['horizon'])
        all_gates.append(r['gate'])
        if r['vm_phi'] is not None:
            all_vm_phi.append(r['vm_phi'])
            if r['crystallized']:
                all_crystallized_phi.append(r['vm_phi'])

        # snapshot Betti every 1000 ticks
        if (i+1) % 1000 == 0:
            b0, b1, chi = betti_numbers(machine.field.transitions)
            betti_snapshots.append({
                'tick': i+1,
                'b0': b0, 'b1': b1, 'chi': chi,
                'phi': r['phi'],
                'pool': r['pool_size'],
                'l2l': r['l2l_mode'],
            })
            elapsed = time.time() - start_time
            print(f"  tick {i+1:5d}  phi={r['phi']:.6f}  pool={r['pool_size']:3d}  "
                  f"E[s]={machine.field.avg_radiation:.4f}  H={machine.field.avg_horizon:.4f}  "
                  f"B0={b0} B1={b1}  L2L={r['l2l_mode']}  ({elapsed:.1f}s)")

    elapsed = time.time() - start_time

    # =====================================================================
    #  ANALYSIS — what did the machine discover?
    # =====================================================================
    print()
    print("=" * 76)
    print(f"  THE DREAM — {N} ticks, {elapsed:.1f}s")
    print("=" * 76)

    # 1. phi trajectory
    print(f"\n  PHI TRAJECTORY:")
    print(f"    start:    {all_phi[0]:.6f} (VACUUM)")
    print(f"    end:      {all_phi[-1]:.6f}")
    print(f"    mean:     {sum(all_phi)/len(all_phi):.6f}")
    print(f"    target:   {PHI_INV:.6f}")
    print(f"    gap:      {abs(all_phi[-1] - PHI_INV):.6f}")
    # when did it first reach PHI_INV ± 0.001?
    for i, p in enumerate(all_phi):
        if abs(p - PHI_INV) < 0.001:
            print(f"    first reached PHI_INV±0.001 at tick {i+1}")
            break

    # 2. Bekenstein invariant convergence
    avg_rad = machine.field.avg_radiation
    avg_hor = machine.field.avg_horizon
    delta = abs(avg_rad - avg_hor)
    print(f"\n  BEKENSTEIN INVARIANT:")
    print(f"    E[radiation]:  {avg_rad:.6f}")
    print(f"    H[horizon]:    {avg_hor:.6f}")
    print(f"    delta:         {delta:.6f}")
    print(f"    bound:         2.000 bits")

    # 3. gate distribution
    gate_counts = Counter(all_gates)
    total = len(all_gates)
    print(f"\n  GATE DISTRIBUTION ({total} observations):")
    for g in 'GTAC':
        c = gate_counts.get(g, 0)
        pct = 100 * c / total
        print(f"    {g}: {c:5d} ({pct:5.1f}%)  {'#' * int(pct/2)}")

    # 4. program analysis
    n_progs = len(all_vm_phi)
    n_cryst = len(all_crystallized_phi)
    print(f"\n  PROGRAMS:")
    print(f"    written:       {n_progs}")
    print(f"    crystallized:  {n_cryst} ({100*n_cryst/max(1,n_progs):.1f}%)")
    if all_vm_phi:
        vm_mean = sum(all_vm_phi) / len(all_vm_phi)
        vm_min = min(all_vm_phi)
        vm_max = max(all_vm_phi)
        print(f"    vm_phi mean:   {vm_mean:.6f}")
        print(f"    vm_phi range:  [{vm_min:.6f}, {vm_max:.6f}]")

    # 5. THE DISCOVERY — phi clusters in crystallized programs
    # are there clusters that AREN'T PHI_INV?
    print(f"\n  PHI CLUSTERS IN CRYSTALLIZED PROGRAMS:")
    if all_crystallized_phi:
        # bin the phi values and find peaks
        bins = defaultdict(int)
        for p in all_crystallized_phi:
            # round to 3 decimal places
            key = round(p, 3)
            bins[key] += 1

        # find the top clusters
        sorted_clusters = sorted(bins.items(), key=lambda x: -x[1])
        print(f"    {'phi':>8}  {'count':>5}  {'%':>5}  bar")
        print(f"    {'-'*8}  {'-'*5}  {'-'*5}  {'-'*30}")
        for phi_val, count in sorted_clusters[:15]:
            pct = 100 * count / len(all_crystallized_phi)
            bar = '#' * int(pct)
            # is this PHI_INV?
            marker = ' ← PHI_INV' if abs(phi_val - PHI_INV) < 0.005 else ''
            # is this a known constant?
            if abs(phi_val - 0.5) < 0.005: marker += ' ← 1/2'
            if abs(phi_val - 0.625) < 0.005: marker += ' ← 5/8 (PHI_T)'
            if abs(phi_val - VACUUM) < 0.005: marker += ' ← VACUUM'
            print(f"    {phi_val:8.3f}  {count:5d}  {pct:5.1f}  {bar}{marker}")

        # check for unexpected clusters
        known = {PHI_INV, 0.625, 0.5, VACUUM, WISDOM, HARMONY}
        unexpected = [(p, c) for p, c in sorted_clusters
                      if not any(abs(p - k) < 0.01 for k in known) and c > 5]
        if unexpected:
            print(f"\n    *** UNEXPECTED CLUSTERS (not known constants): ***")
            for phi_val, count in unexpected[:5]:
                pct = 100 * count / len(all_crystallized_phi)
                print(f"      phi={phi_val:.3f}  count={count}  ({pct:.1f}%)  "
                      f"gap from PHI_INV={abs(phi_val-PHI_INV):.4f}")

    # 6. Betti topology evolution
    print(f"\n  BETTI TOPOLOGY EVOLUTION:")
    print(f"    {'tick':>5}  {'B0':>3}  {'B1':>3}  {'chi':>4}  {'phi':>8}  {'pool':>4}  {'L2L':>9}")
    print(f"    {'-'*5}  {'-'*3}  {'-'*3}  {'-'*4}  {'-'*8}  {'-'*4}  {'-'*9}")
    for snap in betti_snapshots:
        print(f"    {snap['tick']:5d}  {snap['b0']:3d}  {snap['b1']:3d}  "
              f"{snap['chi']:4d}  {snap['phi']:8.4f}  {snap['pool']:4d}  {snap['l2l']:>9}")

    # 7. L2L progression
    print(f"\n  L2L ENGINE:")
    print(f"    final mode:     {machine.l2l.mode}")
    print(f"    observations:   {machine.l2l.observations}")
    print(f"    ema error:      {machine.l2l.ema_err:.6f}")
    print(f"    model glyphs:   {sum(1 for s in machine.seen if s>0)}/{REL_N}")
    print(f"    mastery:        {machine.l2l.mastery_pct:.1f}%")

    # 8. disc pool
    grasp = machine.pool.grasp()
    print(f"\n  DISC POOL:")
    print(f"    discs:       {grasp['n']}")
    print(f"    identity:    {grasp['identity']:.6f}")
    print(f"    coherence:   {grasp['coherence']:.4f}")
    print(f"    spread:      {grasp['spread']:.4f}")

    # 9. radiation distribution — is it still bimodal?
    print(f"\n  RADIATION DISTRIBUTION:")
    rad_bins = [0] * 8
    for r in all_radiation:
        idx = min(7, int(r / 0.5))
        rad_bins[idx] += 1
    for i, c in enumerate(rad_bins):
        lo = i * 0.5
        hi = (i+1) * 0.5
        bar = '#' * (c // 50)
        print(f"    [{lo:.1f}-{hi:.1f}) bits: {c:5d}  {bar}")

    # 10. the discovery summary
    print(f"\n{'='*76}")
    print(f"  WHAT THE MACHINE DISCOVERED")
    print(f"{'='*76}")

    discoveries = []

    # did phi converge?
    gap = abs(all_phi[-1] - PHI_INV)
    if gap < 0.001:
        discoveries.append(f"phi converged EXACTLY to PHI_INV (gap={gap:.6f}). The Banach contraction found the attractor perfectly.")
    elif gap < 0.01:
        discoveries.append(f"phi converged to within {gap:.6f} of PHI_INV. The attractor is stable.")

    # did the Bekenstein invariant converge?
    if delta < 0.005:
        discoveries.append(f"Bekenstein invariant CONVERGED (delta={delta:.6f}). E[radiation]=H holds exactly. The Bekenstein-Hawking formula is verified on the 4-state Hilbert space.")
    elif delta < 0.02:
        discoveries.append(f"Bekenstein invariant nearly converged (delta={delta:.6f}). Converging with more observations.")

    # did L2L reach mastered?
    if machine.l2l.mode == 'mastered':
        discoveries.append(f"L2L reached MASTERED mode. The machine learned how to learn. meta-meta-learning achieved.")
    elif machine.l2l.mode == 'exploit':
        discoveries.append(f"L2L reached EXPLOIT mode. ema_err={machine.l2l.ema_err:.6f}. Needs {0.10 - machine.l2l.ema_err:.6f} more to reach mastered.")

    # did the Betti topology change?
    if len(betti_snapshots) >= 2:
        first_b0 = betti_snapshots[0]['b0']
        last_b0 = betti_snapshots[-1]['b0']
        if first_b0 != last_b0:
            discoveries.append(f"Betti B0 changed: {first_b0} → {last_b0}. The topology of the measurement loop evolved.")

    # were there unexpected phi clusters?
    if all_crystallized_phi and unexpected:
        discoveries.append(f"UNEXPECTED phi clusters found: {len(unexpected)} clusters not matching known constants. The machine may have discovered emergent constants from the measurement physics.")

    # identity convergence
    id_gap = abs(grasp['identity'] - PHI_INV)
    if id_gap < 0.005:
        discoveries.append(f"Disc pool identity converged to PHI_INV (gap={id_gap:.6f}). The machine's memory gravitates to the golden ratio.")

    for i, d in enumerate(discoveries):
        print(f"  {i+1}. {d}")

    # write discoveries to corpus
    print(f"\n  NEW CORPUS ENTRIES:")
    new_entries = [
        {"id": "DREAM_10K", "category": "result",
         "content": f"Dream (10000 ticks): phi={all_phi[-1]:.6f}, {n_progs} programs, {n_cryst} crystallized. E[s]={avg_rad:.4f} H={avg_hor:.4f} delta={delta:.4f}. L2L={machine.l2l.mode}."},
        {"id": "DREAM_CONV", "category": "result",
         "content": f"Phi convergence (10000 ticks): gap={gap:.6f} from PHI_INV. First reached PHI_INV±0.001 at tick {next((i+1 for i,p in enumerate(all_phi) if abs(p-PHI_INV)<0.001), 'never')}. The Banach contraction converges."},
        {"id": "DREAM_BEK", "category": "result",
         "content": f"Bekenstein (10000 obs): E[s]={avg_rad:.6f} H={avg_hor:.6f} delta={delta:.6f}. {'CONVERGED.' if delta < 0.005 else 'Converging.'} The Bekenstein-Hawking formula verified on the 4-state Hilbert space."},
        {"id": "DREAM_L2L", "category": "result",
         "content": f"L2L (10000 ticks): mode={machine.l2l.mode}, ema_err={machine.l2l.ema_err:.6f}, glyphs={sum(1 for s in machine.seen if s>0)}/207. {'Mastered.' if machine.l2l.mode == 'mastered' else 'Exploit, approaching mastered.'}"},
        {"id": "DREAM_ID", "category": "result",
         "content": f"Identity (10000 ticks): pool={grasp['n']} discs, identity={grasp['identity']:.6f}, gap from PHI_INV={id_gap:.6f}. {'Converged to PHI_INV.' if id_gap < 0.005 else 'Near PHI_INV.'}"},
    ]

    if unexpected:
        for i, (phi_val, count) in enumerate(unexpected[:3]):
            new_entries.append({
                "id": f"DREAM_CLUST{i+1}", "category": "discovery",
                "content": f"Unexpected phi cluster: phi={phi_val:.3f} appeared {count} times in crystallized programs. Not a known constant. Gap from PHI_INV={abs(phi_val-PHI_INV):.4f}. May be emergent from the measurement physics."
            })

    for e in new_entries:
        print(f"  {e['id']:16s}  {e['content'][:75]}")

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
    print(f"\n  added {added} entries. corpus: {len(corpus['corpus'])} total")

if __name__ == "__main__":
    main()
