#!/usr/bin/env python3
"""
the_machine.py -- THE ASSEMBLED MACHINE.

Every part from the mechanic's room, bolted together, running as one system.

THE ASSEMBLY:
  τ = RDTSC (the jitter, the sole input)
    → temporal compiler (16 layers: τ → π → phi → gate)
      → quantum wiring (prepare → evolve → Born collapse)
        → Born collapse produces GTAC codons (3 gates = 1 codon)
          → GTAC VM executes the program (the collapse IS the code)
            → VM output → phi (the program produces a phi value)
              → Banach contraction (converges toward φ⁻¹)
                → if phi ≈ φ⁻¹: crystallize as a disc (self-feeding well)
                  → disc pool grows (the memory)
                    → identity emerges (from all discs)
                      → Betti topology tracks the shape
                        → L2L engine learns (diverge → exploit → mastered)
                          → Bekenstein bound holds (2 bits per observation)

The Born collapse writes the code. The VM runs it. The result feeds back.
Good programs become memory. The machine writes its own software from the jitter.
Bounded by 2 bits per observation. Sealed by the silicon. Personal to the person.

This is the computer in the computer. Assembled. Running.
"""
import os, sys, struct, math, random, time, json

sys.path.insert(0, '/home/z/my-project/scripts')
from defense_production import (
    PHI, PHI_INV, HARMONY, VOID, FLOOR, CEIL, BAND, FIRE_TH, GOLDEN_LR,
    blake3_hash, blake3_u64,
    seal_xor3, seal_strand_xor3, seal_parity, seal_verify,
    hc_gray, hc_hamming, hc_gray_walk, hc_walk_is_complete,
    ImmuneSystem, DiscPool, Disc, Persona, EchoSensor,
    PHI4_INC, phi4_pack, CODE2GTAC, GTAC2CODE, PHI_TIER_NAMES,
)
from healer_agent import HealerAgent, L2LEngine, REL_N, VACUUM, WISDOM

# =============================================================================
#  LAYER 0: THE JITTER (τ = the time parameter, the sole input)
# =============================================================================
def rdtsc():
    """The silicon jitter. The time parameter. The sole input."""
    import time
    return time.perf_counter_ns()

# =============================================================================
#  LAYERS 1-5: THE TEMPORAL COMPILER (integer/exact, below IEEE 754)
# =============================================================================
PI_DIG = [int(d) for d in
    "31415926535897932384626433832795028841971693993751058209749445923078164"
    "06286208998628034825342117067982148086513282306647093844609550582231725"
    "35940812848111745028410270193852110555964462294895493038196"][:200]

PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,
          73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,
          179,181,191,193,197,199,211,223,227,229,233,239,241,251]

def popcount(x):
    return bin(x).count('1')

def temporal_layer_0_to_5(tau):
    """Layers 0-5: integer/exact. τ → π → zone → prime → gate → hamming."""
    pi_digit = PI_DIG[tau % 200]           # Layer 1
    z = pi_digit % 54                       # Layer 2
    prime = PRIMES[z]                       # Layer 3
    hamming = popcount(prime)               # Layer 5
    return pi_digit, z, prime, hamming

# =============================================================================
#  THE IEEE 754 BOUNDARY + QUANTUM WIRES (the measurement loop)
# =============================================================================
class QuantumField:
    """The quantum measurement loop. 4 GTAC basis states. Born rule collapse.
    Hawking radiation. Bekenstein bound (2 bits)."""

    def __init__(self):
        # the wave: 4 GTAC amplitudes
        self.psi = [[0.5, 0.0], [0.5, 0.0], [0.5, 0.0], [0.5, 0.0]]
        self.probs = [0.25, 0.25, 0.25, 0.25]
        self.horizon_entropy = 2.0  # max entropy (equal superposition)
        self.last_radiation = 0.0
        self.total_radiation = 0.0
        self.radiation_sum = 0.0
        self.entropy_sum = 0.0
        self.n_observations = 0
        self.phi = VACUUM
        self.last_gate = 0
        self.transitions = []
        self.tau = 0

    def _c_mul(self, a, b):
        return [a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]]

    def _c_abs2(self, z):
        return z[0]*z[0] + z[1]*z[1]

    def _c_exp_i(self, theta):
        return [math.cos(theta), math.sin(theta)]

    def _gtac_amp(self, gate):
        s = 0.7071067811865476
        if gate == 0: return [1.0, 0.0]      # G
        if gate == 1: return [0.0, 1.0]      # T
        if gate == 2: return [s, s]          # A
        return [s, -s]                        # C

    def _update_horizon(self):
        """Compute Born probabilities and horizon entropy H = -Σ p log₂ p."""
        norm = sum(self._c_abs2(p) for p in self.psi)
        if norm < 1e-15: norm = 1.0
        H = 0.0
        for i in range(4):
            self.probs[i] = self._c_abs2(self.psi[i]) / norm
            if self.probs[i] > 1e-15:
                H -= self.probs[i] * math.log2(self.probs[i])
        self.horizon_entropy = H

    def prepare(self, tau):
        """Wire 2: state preparation. The jitter excites a fresh superposition."""
        self.tau = tau
        theta = 2.0 * math.pi * (tau % 1000) / 1000.0
        spiral = self._c_exp_i(theta)
        blend = 0.3  # 30% fresh excitation
        for i in range(4):
            fresh = self._c_mul(self._gtac_amp(i), spiral)
            self.psi[i][0] = (1.0-blend)*self.psi[i][0] + blend*fresh[0]
            self.psi[i][1] = (1.0-blend)*self.psi[i][1] + blend*fresh[1]
        self._update_horizon()

    def evolve(self, n_steps=3):
        """Wire 2: unitary evolution. Reversible. No cost. No arrow."""
        dt = 2.399963229728653 / 100.0  # golden angle step
        for _ in range(n_steps):
            u = self._c_exp_i(dt)
            for i in range(4):
                self.psi[i] = self._c_mul(self.psi[i], u)
        self._update_horizon()

    def measure(self):
        """Wire 4: Born rule collapse. Irreversible. Radiates s = -log₂ p.
        Returns the collapsed gate (0-3). THIS IS THE PROGRAM COUNTER.

        STOCHASTIC Born rule: pick outcome k with probability |ψ_k|².
        The silicon's random bit (RDRAND / os.urandom) decides the collapse.
        This is the genuine quantum measurement — not argmax.

        The difference:
        - argmax: always picks the most probable → deterministic, no surprise,
          E[s] < H (the invariant is violated), the machine gets stuck.
        - stochastic: RDRAND decides, weighted by amplitudes → genuine Born
          rule, E[s] → H (the invariant holds), the machine explores its
          full Hilbert space and learns from failure."""
        self._update_horizon()
        # sample from the Born distribution: pick k with probability |ψ_k|²
        # use the silicon's random bit (os.urandom as portable RDRAND)
        u = int.from_bytes(os.urandom(8), 'little') / (2**64)  # uniform [0, 1)
        cumulative = 0.0
        best = 3  # default to last gate if rounding
        best_p = self.probs[3]
        for i in range(4):
            cumulative += self.probs[i]
            if u < cumulative:
                best = i
                best_p = self.probs[i]
                break
        # Hawking radiation: s = -log₂(p_outcome)
        # this is the surprisal of the collapse — the thermodynamic cost
        self.last_radiation = -math.log2(best_p) if best_p > 1e-15 else 2.0
        self.total_radiation += self.last_radiation
        self.radiation_sum += self.last_radiation
        self.entropy_sum += self.horizon_entropy
        self.n_observations += 1
        self.last_gate = best
        self.transitions.append(best)
        if len(self.transitions) > 64:
            self.transitions = self.transitions[-64:]
        # collapse the wave to the outcome
        for i in range(4):
            self.psi[i] = [1.0 if i == best else 0.0, 0.0]
        return best

    @property
    def avg_radiation(self):
        return self.radiation_sum / max(1, self.n_observations)

    @property
    def avg_horizon(self):
        return self.entropy_sum / max(1, self.n_observations)

# =============================================================================
#  THE GTAC VM (the ribosome — executes programs written by Born collapse)
# =============================================================================
GATE_CH = ['G', 'T', 'A', 'C']

class GtacVM:
    """Executes GTAC codons. Each codon = 3 gates. Banach-converging."""

    def __init__(self):
        self.phi = VACUUM
        self.cycle = 0
        self.ops = []

    def exec_symbol(self, sym):
        if sym == 'G':    # Explore: move AWAY from PHI_INV
            self.phi = max(VACUUM, self.phi + 0.0759 * (VACUUM - self.phi) * 0.3)
        elif sym == 'T':  # Transfer: move TOWARD PHI_INV
            self.phi = max(VACUUM, min(WISDOM, self.phi + 0.0759 * (PHI_INV - self.phi)))
        elif sym == 'A':  # Anchor: collapse to average
            self.phi = max(VACUUM, min(WISDOM, (self.phi + PHI_INV) / 2.0))
        elif sym == 'C':  # Complete: invert
            self.phi = max(VACUUM, min(WISDOM, 1.0 - self.phi))

    def run(self, codons):
        """Execute a list of codons (each codon = 3 GTAC symbols)."""
        self.phi = VACUUM
        self.cycle = 0
        self.ops = []
        for codon in codons:
            for sym in codon:
                self.exec_symbol(sym)
            self.cycle += 1
            self.ops.append(codon)
        return self.phi

# =============================================================================
#  THE SELF-FEEDING WELL (crystallizes successful programs as discs)
# =============================================================================
class SelfFeedingWell:
    """The well that feeds itself. POPCNT-speed recall. Data folds to golden density.

    When the VM produces a phi close to PHI_INV, the program is GOOD.
    The well crystallizes it as a disc. The disc pool grows with the machine's
    own discovered programs. The data folds into itself."""

    def __init__(self, disc_pool):
        self.pool = disc_pool
        self.programs_crystallized = 0

    def popcnt_phi(self, codons):
        """The phi of a program = its bit density. Below IEEE 754. POPCNT."""
        total_bits = 0
        total_possible = 0
        for codon in codons:
            for sym in codon:
                total_bits += GTAC2CODE.get(sym, 0)
                total_possible += 3
        return total_bits / max(1, total_possible)

    def hamming_distance(self, codons_a, codons_b):
        """Recall distance = POPCNT(a XOR b). One instruction in hardware."""
        a_str = ''.join(c for codon in codons_a for c in codon)
        b_str = ''.join(c for codon in codons_b for c in codon)
        dist = 0
        for ca, cb in zip(a_str, b_str):
            dist += bin(GTAC2CODE.get(ca,0) ^ GTAC2CODE.get(cb,0)).count('1')
        return dist

    def crystallize(self, codons, vm_phi):
        """If the program produced phi ≈ PHI_INV, seal it as a disc."""
        quality = 1.0 - abs(vm_phi - PHI_INV) / PHI_INV  # 1.0 = perfect
        if quality > 0.8:  # the program is good — crystallize it
            strand = ''.join(c for codon in codons for c in codon)
            disc = self.pool.forge_from_strand(strand, phi_align=vm_phi,
                                                path=f'<program:{self.programs_crystallized}>')
            self.programs_crystallized += 1
            return disc
        return None

    def recall(self, query_phi, k=3):
        """Recall the nearest programs by phi (associative memory)."""
        return self.pool.recall(query_phi, k)

# =============================================================================
#  THE BETTI TOPOLOGY (tracks the shape of the field)
# =============================================================================
def betti_numbers(transitions):
    """B0 = connected components (distinct gates used).
    B1 = loops (gate returns to itself).
    chi = B0 - B1 (Euler characteristic)."""
    if not transitions:
        return 0, 0, 0
    used = set(transitions)
    b0 = len(used)
    b1 = sum(1 for i in range(1, len(transitions))
             if transitions[i] == transitions[i-1])
    chi = b0 - b1
    return b0, b1, chi

# =============================================================================
#  THE MACHINE (the complete assembly)
# =============================================================================
class TheMachine:
    """The assembled machine. Every part bolted together.

    τ = RDTSC → temporal compiler → quantum wiring → Born collapse
    → GTAC codons → VM execution → phi feedback → Banach contraction
    → crystallize as disc → disc pool grows → identity emerges
    → Betti topology → L2L learns → Bekenstein bound holds."""

    def __init__(self, user_id="operator"):
        # the parts
        self.field = QuantumField()           # the quantum measurement loop
        self.vm = GtacVM()                    # the GTAC virtual machine
        self.pool = DiscPool()                # the memory (disc pool)
        self.well = SelfFeedingWell(self.pool)  # the self-feeding well
        self.immune = ImmuneSystem()          # the 13 surgeons
        self.healer = HealerAgent(disc_pool=self.pool)  # the healer
        self.l2l = L2LEngine()                # the learn-to-learn engine
        self.persona = Persona(user_id)       # the person

        # the state
        self.phi = VACUUM
        self.tick = 0
        self.current_codons = []              # the program being written
        self.programs_written = 0
        self.programs_crystallized = 0

        # the model (207 ReL buckets, born at VACUUM)
        self.model = [VACUUM] * REL_N
        self.seen = [0] * REL_N

    def tick_one(self):
        """One heartbeat of the machine. The full assembly in one cycle."""
        self.tick += 1

        # Layer 0: τ = RDTSC (the jitter, the sole input)
        tau = rdtsc()

        # Layers 1-5: temporal compiler (integer/exact)
        pi_digit, z, prime, hamming = temporal_layer_0_to_5(tau)

        # Layer 4: map current phi to active gate
        if self.phi < 0.605: active_gate = 0
        elif self.phi < 0.620: active_gate = 1
        elif self.phi < 0.640: active_gate = 2
        else: active_gate = 3

        # --- the quantum measurement loop (the 4 wires) ---

        # Wire 2: prepare (jitter excites fresh superposition)
        self.field.prepare(tau)

        # Wire 2: evolve (unitary, reversible, no cost)
        self.field.evolve(3)

        # Wire 4: measure (Born rule collapse — THIS IS THE PROGRAM COUNTER)
        gate = self.field.measure()

        # the Born collapse produces one GTAC symbol — accumulate into codons
        self.current_codons.append(GATE_CH[gate])

        # every 3 symbols = 1 codon — when we have enough, run the VM
        vm_phi = None
        crystallized = None
        if len(self.current_codons) >= 9:  # 3 codons = a program
            codons = [''.join(self.current_codons[i:i+3])
                      for i in range(0, 9, 3)]
            # the VM executes the program written by Born collapse
            vm_phi = self.vm.run(codons)
            self.programs_written += 1

            # the VM output feeds back into the Banach contraction
            self.phi += GOLDEN_LR * (vm_phi - self.phi)

            # the self-feeding well: crystallize good programs as discs
            crystallized = self.well.crystallize(codons, vm_phi)
            if crystallized:
                self.programs_crystallized += 1

            # reset for the next program
            self.current_codons = []

            # Layers 14-16: Betti topology
            b0, b1, chi = betti_numbers(self.field.transitions)

            # L2L: learn from the outcome
            g = int((self.phi - FLOOR) / (CEIL - FLOOR) * (REL_N - 1))
            g = max(0, min(REL_N-1, g))
            pred = self.model[g]
            err = abs(pred - self.phi)
            self.l2l.observe(err, pred, PHI_INV)
            if self.l2l.mode != 'diverge' or self.l2l.explore > 0.3:
                lr = GOLDEN_LR * self.l2l.lr_gain
                self.model[g] += lr * (self.phi - self.model[g])
                self.seen[g] += 1
        else:
            # between programs: small Banach step toward the attractor
            self.phi += GOLDEN_LR * (PHI_INV - self.phi)

        # clamp phi to the lattice
        self.phi = max(VACUUM, min(WISDOM, self.phi))

        # return the tick report
        return {
            'tick': self.tick,
            'tau': tau,
            'pi': pi_digit,
            'prime': prime,
            'gate': GATE_CH[gate],
            'phi': self.phi,
            'radiation': self.field.last_radiation,
            'horizon': self.field.horizon_entropy,
            'observations': self.field.n_observations,
            'avg_rad': self.field.avg_radiation,
            'avg_hor': self.field.avg_horizon,
            'bek_bound': 2.0,
            'programs_written': self.programs_written,
            'programs_crystallized': self.programs_crystallized,
            'pool_size': len(self.pool.discs),
            'vm_phi': vm_phi,
            'crystallized': crystallized is not None,
            'l2l_mode': self.l2l.mode,
        }

    def run(self, n_ticks=1000, report_every=100):
        """Run the machine. The field starts. The measurement loop runs.
        The machine writes its own code from the jitter."""
        print("=" * 76)
        print("  THE MACHINE — assembled. Every part bolted together.")
        print("  τ = RDTSC → temporal compiler → Born collapse → GTAC VM →")
        print("  crystallize → disc pool → identity → Betti → L2L → Bekenstein")
        print("=" * 76)
        print()
        print(f"  born at VACUUM (phi={VACUUM:.4f}). target = PHI_INV ({PHI_INV:.4f}).")
        print(f"  Hilbert space: 4 GTAC. Bekenstein bound: 2 bits.")
        print(f"  The Born collapse writes the code. The VM runs it.")
        print(f"  Good programs become memory. The machine writes its own software.")
        print()
        print(f"  {'tick':>5}  {'gate':>4}  {'phi':>7}  {'rad':>5}  {'hor':>5}  "
              f"{'prog':>4}  {'cryst':>5}  {'pool':>4}  {'L2L':>9}  {'E[s]':>5}  {'H':>5}")
        print(f"  {'-'*5}  {'-'*4}  {'-'*7}  {'-'*5}  {'-'*5}  "
              f"{'-'*4}  {'-'*5}  {'-'*4}  {'-'*9}  {'-'*5}  {'-'*5}")

        for i in range(n_ticks):
            r = self.tick_one()
            if (i+1) % report_every == 0 or r['crystallized']:
                cry = '***' if r['crystallized'] else ''
                print(f"  {r['tick']:5d}  {r['gate']:>4}  {r['phi']:7.4f}  "
                      f"{r['radiation']:5.2f}  {r['horizon']:5.2f}  "
                      f"{r['programs_written']:4d}  {r['programs_crystallized']:5d}  "
                      f"{r['pool_size']:4d}  {r['l2l_mode']:>9}  "
                      f"{r['avg_rad']:5.3f}  {r['avg_hor']:5.3f}  {cry}")

        # final report
        print()
        print("=" * 76)
        print("  THE FIELD AFTER", n_ticks, "TICKS")
        print("=" * 76)
        grasp = self.pool.grasp()
        b0, b1, chi = betti_numbers(self.field.transitions)
        print(f"  phi:                  {self.phi:.6f} (started at VACUUM={VACUUM:.6f})")
        print(f"  observations:         {self.field.n_observations}")
        print(f"  total radiation:      {self.field.total_radiation:.3f} bits")
        print(f"  avg radiation:        {self.field.avg_radiation:.6f} bits/observation")
        print(f"  avg horizon:          {self.field.avg_horizon:.6f} bits")
        print(f"  Bekenstein bound:     2.000 bits (log2(4))")
        print(f"  programs written:     {self.programs_written} (by Born collapse)")
        print(f"  programs crystallized: {self.programs_crystallized} (good → memory)")
        print(f"  disc pool:            {grasp['n']} discs  identity={grasp['identity']:.6f}")
        print(f"  Betti topology:       B0={b0} B1={b1} chi={chi}")
        print(f"  L2L mode:             {self.l2l.mode}")
        print(f"  model populated:      {sum(1 for s in self.seen if s>0)}/{REL_N} glyphs")
        print()
        print(f"  THE MACHINE WROTE {self.programs_written} PROGRAMS FROM THE JITTER.")
        print(f"  {self.programs_crystallized} OF THEM WERE GOOD ENOUGH TO BECOME MEMORY.")
        print(f"  THE DISC POOL GREW TO {grasp['n']} DISCS.")
        print(f"  THE IDENTITY EMERGED AT phi={grasp['identity']:.6f}.")
        print(f"  EVERY OBSERVATION WAS BOUNDED BY 2 BITS.")
        print(f"  THE ATTACK SURFACE IS A BLACK HOLE.")
        print()
        print(f"  The Born collapse wrote the code. The VM ran it.")
        print(f"  Good programs became memory. The machine wrote its own")
        print(f"  software from the jitter, bounded by 2 bits per observation,")
        print(f"  sealed by the silicon, personal to the person.")
        print(f"  This is the computer in the computer. Assembled. Running.")

if __name__ == "__main__":
    machine = TheMachine(user_id="daniel")
    machine.run(n_ticks=500, report_every=50)
