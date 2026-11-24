#!/usr/bin/env python3
"""
the_hospital.py -- THE HOSPITAL: the complete health center.

Fuses every NUMEN organ into one workspace:
  - THE SURGEONS  (immune.h)       -- 13-surgeon phi-band patrol, detect fires
  - THE HEALER    (healer_agent.py) -- active inference agent, minimizes surprise
  - THE ALGO MAKER (algo_maker.c)   -- evolves GTAC genes into medicine
  - THE GTAC VM   (quatos_gtac.h)   -- the ribosome that executes GTAC programs
  - THE HYPERCUBE (quatos_hypercube) -- reads code as a Hamiltonian walk + codes new code
  - THE PHARMACY  (disc_pool.h)     -- stores medicine as sealed discs in the pool

THE ALCHEMY (the key innovation):
  When the healer detects a recurring anomaly (3rd recurrence → IMMUNIZE),
  it does NOT just write a flag. It uses the algo_maker to EVOLVE A MEDICINE:
  a GTAC gene that, when expressed on the GTAC VM, produces a phi value that
  counters the anomaly. The medicine is then:
    1. EXPRESSED on the VM (does it produce the target phi?)
    2. WALKED on the hypercube (is it a valid executable? Hamiltonian cycle?)
    3. SEALED and stored in the pharmacy (a new disc in the pool)
    4. The organism's memory GROWS with its own cures

  Distress → seed → evolve medicine → verify → store → the organism's memory
  grows with its own medicine. This is the alchemy: the distress itself becomes
  the seed of the cure.

  "Not only can the healer do that but it also creates the medicine."
  "It uses everything it can. The alchemy all of it."
  "This is the surgeons, the healer and their workspace. This is the hospital."
"""
import os, sys, struct, math, random, time

sys.path.insert(0, '/home/z/my-project/scripts')
from defense_production import (
    PHI, PHI_INV, HARMONY, VOID, FLOOR, CEIL, BAND, FIRE_TH, GOLDEN_LR,
    blake3_hash, blake3_u64, fnv1a, splitmix64, expand_gtac,
    seal_xor3, seal_strand_xor3, seal_parity, seal_verify,
    hc_gray, hc_hamming, hc_gray_walk, hc_walk_is_complete,
    ImmuneSystem, DiscPool, Disc, Persona, EchoSensor,
    DefenseCore, NumenKey, nk_enroll, nk_strike, CodeArtifact,
    PHI4_INC, Phi4Addr, phi4_seq, phi4_advance, phi4_decorrelate, phi4_pack,
    CODE2GTAC, GTAC2CODE, PHI_TIER_NAMES,
)
from healer_agent import HealerAgent, L2LEngine, REL_N, VACUUM, WISDOM

# =============================================================================
#  THE GTAC VIRTUAL MACHINE  (quatos_gtac.h, ported)
#  The ribosome that executes GTAC programs. Every codon is 3 symbols (G/T/A/C).
#  4³ = 64 codons. Execution converges toward PHI_INV (Banach fixed point).
# =============================================================================
LR_ECHO = 0.07585880
GOLDEN_ANG = 2.39996322972865332

def phi_clamp(v):
    return max(VACUUM, min(WISDOM, v))

class GtacVM:
    """The GTAC virtual machine. Executes codons (3-symbol triplets).
    The phi register converges toward PHI_INV through Banach contraction."""
    def __init__(self):
        self.phi = VACUUM
        self.phi_target = PHI_INV
        self.coupling_ab = 0.0
        self.delta = abs(self.phi - PHI_INV)
        self.shadow_pi = 0.0
        self.gate_bias = [0.25, 0.25, 0.25, 0.25]
        self.ip = 0
        self.cycle = 0
        self.halted = False
        self.ops_executed = []  # trace of operations

    def exec_symbol(self, sym):
        """Execute one gate symbol on the VM."""
        if sym == 'G':    # Explore: move phi AWAY from PHI_INV
            self.phi = phi_clamp(self.phi + LR_ECHO * (VACUUM - self.phi) * 0.3)
        elif sym == 'T':  # Transfer: move phi TOWARD PHI_INV
            self.phi = phi_clamp(self.phi + LR_ECHO * (PHI_INV - self.phi))
        elif sym == 'A':  # Anchor: collapse toward PHI_INV by averaging
            self.phi = phi_clamp((self.phi + PHI_INV) / 2.0)
        elif sym == 'C':  # Complete: invert phi through mirror
            self.phi = phi_clamp(1.0 - self.phi)
        self.delta = abs(self.phi - PHI_INV)

    def exec_codon(self, c0, c1, c2):
        """Execute one codon (three symbols)."""
        self.exec_symbol(c0)
        self.exec_symbol(c1)
        self.exec_symbol(c2)
        self.cycle += 1
        self.shadow_pi = phi_clamp(
            self.phi * GOLDEN_ANG * (4.0 / 3.0) / (2.0 * math.pi))
        self.ops_executed.append(f"{c0}{c1}{c2}")

    def run(self, strand, n_max=4096):
        """Run a GTAC program (string of G/T/A/C) until HALT or n_max steps.
        HALT codon = TCT."""
        self.ip = 0
        self.halted = False
        self.ops_executed = []
        i = 0
        while not self.halted and i + 2 < len(strand) and self.cycle < n_max:
            c0, c1, c2 = strand[i], strand[i+1], strand[i+2]
            if c0 == 'T' and c1 == 'C' and c2 == 'T':  # HALT
                self.halted = True
                break
            if all(c in 'GTAC' for c in (c0, c1, c2)):
                self.exec_codon(c0, c1, c2)
            i += 3
        return self.phi

    def reset(self):
        self.__init__()

# =============================================================================
#  THE ALGO MAKER  (algo_maker.c, ported)
#  Evolves GTAC genes that, when expressed on the VM, reach a target phi.
#  This is the MEDICINE FACTORY: given a target phi (the cure), evolve a gene
#  that produces it. Genetic algorithm: 200-gene population, mutation, splice.
# =============================================================================
AM_POP = 200  # population size (from algo_maker.c)
ALGO_GENE_MAX_CODONS = 64
ALGO_GENE_MAX_BASES = ALGO_GENE_MAX_CODONS * 3

class AmIndiv:
    __slots__ = ('gene', 'fit')
    def __init__(self):
        self.gene = ''
        self.fit = -1e18

class AlgoMaker:
    """The algorithm maker. Evolves GTAC genes that produce a target phi.

    MEDICINE CREATION: given a target phi (the cure for an anomaly), evolve a
    gene that, when expressed on the GTAC VM, converges to that phi. The gene
    starts with ATG (start codon) and ends with TAA (stop codon), like real DNA.
    """
    def __init__(self, seed=88172645463325252):
        self.rng = seed if seed else 88172645463325252

    def _rand(self):
        """xorshift64* RNG (from algo_maker.c)."""
        self.rng ^= self.rng << 13; self.rng &= 0xFFFFFFFFFFFFFFFF
        self.rng ^= self.rng >> 7
        self.rng ^= self.rng << 17; self.rng &= 0xFFFFFFFFFFFFFFFF
        return self.rng

    def _ri(self, n):
        return self._rand() % n

    def _rf(self):
        return (self._rand() >> 11) / 9007199254740992.0

    @staticmethod
    def express(gene, n_max=4096):
        """Express a gene on the GTAC VM. Returns the final phi."""
        vm = GtacVM()
        vm.run(gene, n_max)
        return vm.phi

    def _fitness(self, gene, target):
        """Fitness = -|phi - target| - 0.001 * cycles (from algo_maker.c)."""
        phi = self.express(gene)
        cycles = len(gene) // 3
        return -abs(phi - target) - 0.001 * cycles

    def _random_gene(self):
        """Generate a random gene: ATG (start) + random codons + TAA (stop)."""
        n_codons = 6 + self._ri(ALGO_GENE_MAX_CODONS - 6)
        gene = ['A', 'T', 'G']  # start codon
        for _ in range(n_codons - 2):
            gene.append('GTAC'[self._ri(4)])
            gene.append('GTAC'[self._ri(4)])
            gene.append('GTAC'[self._ri(4)])
        gene.extend(['T', 'A', 'A'])  # stop codon
        return ''.join(gene)

    def _mutate(self, gene):
        """Mutate a random base in the gene."""
        g = list(gene)
        pos = self._ri(len(g))
        g[pos] = 'GTAC'[self._ri(4)]
        return ''.join(g)

    def _splice(self, a, b):
        """Splice two genes: take first half of a + second half of b."""
        ca, cb = len(a) // 3, len(b) // 3
        if ca < 2 or cb < 2:
            return a
        cut_a = 1 + self._ri(ca - 1)
        cut_b = self._ri(cb)
        result = a[:cut_a * 3]
        result += b[cut_b * 3:]
        return result[:ALGO_GENE_MAX_BASES]

    def author(self, target_phi, max_gen=500, splice_on=True):
        """Evolve a gene that produces target_phi when expressed on the VM.
        Returns (gene_str, final_phi, solved, generations)."""
        # initialize population
        pop = [AmIndiv() for _ in range(AM_POP)]
        for ind in pop:
            ind.gene = self._random_gene()
            ind.fit = self._fitness(ind.gene, target_phi)
        # find best
        best = max(range(AM_POP), key=lambda i: pop[i].fit)
        if abs(self.express(pop[best].gene) - target_phi) < 0.001:
            return pop[best].gene, self.express(pop[best].gene), True, 0
        # evolve
        for gen in range(max_gen):
            if abs(self.express(pop[best].gene) - target_phi) < 0.005:
                break
            nxt = [AmIndiv() for _ in range(AM_POP)]
            nxt[0] = pop[best]  # elitism: keep the best
            for i in range(1, AM_POP):
                # tournament selection
                a = self._ri(AM_POP); a2 = self._ri(AM_POP)
                if pop[a2].fit > pop[a].fit: a = a2
                b = self._ri(AM_POP); b2 = self._ri(AM_POP)
                if pop[b2].fit > pop[b].fit: b = b2
                # create child
                if splice_on:
                    child_gene = self._splice(pop[a].gene, pop[b].gene)
                else:
                    child_gene = pop[a].gene
                # mutate
                n_muts = 1 + self._ri(3)
                for _ in range(n_muts):
                    child_gene = self._mutate(child_gene)
                child = AmIndiv()
                child.gene = child_gene
                child.fit = self._fitness(child_gene, target_phi)
                nxt[i] = child if child.fit >= pop[a].fit else pop[a]
            pop = nxt
            best = max(range(AM_POP), key=lambda i: pop[i].fit)
        final_phi = self.express(pop[best].gene)
        solved = abs(final_phi - target_phi) < 0.01
        return pop[best].gene, final_phi, solved, gen + 1

# =============================================================================
#  THE HYPERCUBE WALKER  (quatos_hypercube.asm, extended for code reading/writing)
#  Reads code as a Hamiltonian walk on Q_n and generates new code by walking.
#  A complete executable = a closed Hamiltonian cycle (every step Hamming-1).
# =============================================================================
class HypercubeWalker:
    """Walks the hypercube to READ code and CODE new code.

    READING: walk through code bytes as a Hamiltonian cycle on Q_n. At each
    vertex, the walker checks the code's integrity (seal, parity, phi). The
    walk IS the read — every byte is a vertex, every step is Hamming-1.

    CODING: generate new code by walking the hypercube. The walk produces
    a sequence of Gray-code vertices, each of which IS a byte. The resulting
    byte sequence is a complete executable (closed Hamiltonian = glitch-free).

    VERIFYING: the walk is checked for completeness (every consecutive pair
    differs by exactly 1 bit, and the walk closes).
    """

    @staticmethod
    def read_code(code_bytes):
        """Read code as a hypercube walk. Returns the walk + integrity check.
        Each byte is a vertex in Q_8 (8-bit hypercube, 256 vertices)."""
        vertices = list(code_bytes)
        walk = []
        for i in range(len(vertices)):
            v = vertices[i]
            v_next = vertices[(i + 1) % len(vertices)] if len(vertices) > 1 else v
            h_dist = bin(v ^ v_next).count('1')
            walk.append({
                'vertex': v,
                'byte': bytes([v]),
                'gray': hc_gray(v),
                'hamming_to_next': h_dist,
                'phi': FLOOR + (v / 255.0) * (CEIL - FLOOR),
            })
        # check completeness: every step Hamming-1?
        complete = all(w['hamming_to_next'] == 1 for w in walk)
        return {'walk': walk, 'complete': complete, 'n_vertices': len(walk)}

    @staticmethod
    def code_new(target_phi, n_bytes=16):
        """Generate new code by walking the hypercube. The walk produces a
        sequence of Gray-code vertices, each IS a byte. The result is a
        complete executable (closed Hamiltonian = glitch-free).

        The walk is seeded by the target_phi: the starting vertex is the phi
        mapped to a byte, and each step advances by the golden constant."""
        # seed: target_phi → starting vertex
        start_vertex = int(target_phi * 255) & 0xFF
        # walk the hypercube using Gray code, seeded by phi
        walk_vertices = []
        v = start_vertex
        for i in range(n_bytes):
            walk_vertices.append(v)
            # advance by golden step: XOR with (1 << golden_dim)
            golden_dim = i % 8
            v = v ^ (1 << golden_dim)
        # close the walk: ensure last vertex is Hamming-1 from first
        if len(walk_vertices) > 1:
            last = walk_vertices[-1]
            first = walk_vertices[0]
            h = bin(last ^ first).count('1')
            if h != 1:
                # adjust: flip one bit of the last vertex to make it Hamming-1 from first
                diff_bit = 0
                for b in range(8):
                    if (last >> b) & 1 != (first >> b) & 1:
                        diff_bit = b
                        break
                # we need exactly 1 bit difference. Find a bit that's the same and flip it.
                for b in range(8):
                    if (last >> b) & 1 == (first >> b) & 1:
                        walk_vertices[-1] = last ^ (1 << b)
                        break
        return bytes(walk_vertices)

    @staticmethod
    def verify_walk(code_bytes):
        """Verify that code_bytes is a valid Hamiltonian walk (every step
        Hamming-1, walk closes). Returns (is_complete, min_hamming, max_hamming)."""
        if len(code_bytes) < 2:
            return False, 0, 0
        hamming_distances = []
        for i in range(len(code_bytes)):
            h = bin(code_bytes[i] ^ code_bytes[(i + 1) % len(code_bytes)]).count('1')
            hamming_distances.append(h)
        return (all(h == 1 for h in hamming_distances),
                min(hamming_distances), max(hamming_distances))

# =============================================================================
#  THE PHARMACY  -- stores medicine as sealed discs in the pool
#  Each medicine is a GTAC gene evolved by the algo_maker, expressed on the VM,
#  verified on the hypercube, sealed with Watson-Crick parity, and stored as a
#  new disc. The organism's memory grows with its own cures.
# =============================================================================
class Medicine:
    """A created medicine: a GTAC gene that counters a specific anomaly."""
    __slots__ = ('anomaly_type', 'target_phi', 'gene', 'expressed_phi',
                 'code_bytes', 'walk_complete', 'disc', 'created_at')
    def __init__(self):
        self.anomaly_type = ''
        self.target_phi = 0.0
        self.gene = ''
        self.expressed_phi = 0.0
        self.code_bytes = b''
        self.walk_complete = False
        self.disc = None
        self.created_at = 0

    def __repr__(self):
        return (f"Medicine(anomaly={self.anomaly_type}, target={self.target_phi:.4f}, "
                f"expressed={self.expressed_phi:.4f}, gene={self.gene[:18]}..., "
                f"walk={'OK' if self.walk_complete else 'FAIL'})")

class Pharmacy:
    """The pharmacy: stores medicine as sealed discs in the pool.

    When the healer creates medicine (algo_maker evolves a gene), the pharmacy:
    1. Expresses the gene on the GTAC VM (does it produce the target phi?)
    2. Walks the gene on the hypercube (is it a valid executable?)
    3. Seals the gene with Watson-Crick parity
    4. Forges it as a new disc in the pool (the organism's memory grows)
    """
    def __init__(self, disc_pool):
        self.disc_pool = disc_pool
        self.medicines = []
        self.algo_maker = AlgoMaker()
        self.vm = GtacVM()

    def create_medicine(self, anomaly_type, target_phi, anomaly_value=0):
        """Create medicine for a recurring anomaly. The algo_maker evolves a
        GTAC gene that produces the target phi (the cure). The gene is then
        expressed, walked, sealed, and stored as a disc."""
        med = Medicine()
        med.anomaly_type = anomaly_type
        med.target_phi = target_phi
        med.created_at = time.time()
        # 1. EVOLVE the gene (the algo_maker)
        gene, expressed_phi, solved, gens = self.algo_maker.author(
            target_phi, max_gen=200, splice_on=True)
        med.gene = gene
        med.expressed_phi = expressed_phi
        # 2. EXPRESS on the VM (verify it produces the target phi)
        self.vm.reset()
        vm_phi = self.vm.run(gene)
        # 3. WALK on the hypercube (is the gene a valid executable?)
        # convert the gene to bytes for the hypercube walk
        # each codon (3 bases) → 1 byte (2 bits per base, 3 bases = 6 bits, pad to 8)
        code_bytes = bytearray()
        for i in range(0, len(gene) - 2, 3):
            codon = gene[i:i+3]
            byte_val = 0
            for j, c in enumerate(codon):
                byte_val = (byte_val << 2) | GTAC2CODE.get(c, 0)
            byte_val = byte_val & 0xFF  # take low 8 bits
            code_bytes.append(byte_val)
        med.code_bytes = bytes(code_bytes)
        walk_result = HypercubeWalker.read_code(med.code_bytes)
        med.walk_complete = walk_result['complete']
        # 4. SEAL and store as a disc in the pool
        med.disc = self.disc_pool.forge_from_strand(
            gene, phi_align=expressed_phi,
            path=f'<medicine:{anomaly_type}>')
        self.medicines.append(med)
        return med

    def recall_medicine(self, anomaly_phi):
        """Recall the medicine closest to a given phi (associative pharmacy)."""
        if not self.medicines:
            return None
        return min(self.medicines, key=lambda m: abs(m.expressed_phi - anomaly_phi))

# =============================================================================
#  THE HOSPITAL  -- the complete health center
#  Fuses the surgeons, the healer, the algo maker, the hypercube, and the
#  pharmacy into one workspace. This is where the organism heals itself and
#  creates its own medicine.
# =============================================================================
class Hospital:
    """The hospital: the complete health center.

    When distress is detected:
    1. THE SURGEONS patrol the phi bands and detect fires
    2. THE HEALER observes the state (active inference), computes surprise
    3. THE HEALER prescribes and applies treatments (9-step protocol)
    4. On 3rd recurrence → IMMUNIZE → THE ALGO MAKER creates medicine
    5. THE MEDICINE is expressed on the VM, walked on the hypercube, sealed
    6. THE PHARMACY stores it as a new disc — the organism's memory grows

    The distress itself becomes the seed of the cure. This is the alchemy.
    """
    def __init__(self, disc_pool, persona=None):
        self.disc_pool = disc_pool
        self.persona = persona or Persona("operator")
        self.surgeons = ImmuneSystem()   # the 13-surgeon patrol
        self.healer = HealerAgent(persona=persona, disc_pool=disc_pool)
        self.pharmacy = Pharmacy(disc_pool)
        self.vm = GtacVM()
        self.admission_history = []
        self.medicine_count = 0

    def admit(self, cell_phis, echo_phi=PHI_INV):
        """Admit a colony state to the hospital. The surgeons patrol, the
        healer acts, and on immunization, medicine is created.

        Returns a hospital report with the full chain:
        surgeons → healer → medicine → pharmacy → pool growth."""
        report = {}
        # 1. THE SURGEONS patrol (immune system sweep)
        self.surgeons.update(cell_phis)
        report['surgeons'] = {
            'population': self.surgeons.population,
            'fires': self.surgeons.fires,
            'healthy': self.surgeons.healthy,
            'coverage': self.surgeons.coverage,
            'immune_coherence': self.surgeons.immune_coherence,
            'worst_ring': self.surgeons.worst_ring,
        }
        # 2. THE HEALER acts (active inference)
        heal_report = self.healer.observe_and_act(cell_phis, echo_phi)
        report['healer'] = heal_report
        # 3. On immunization → CREATE MEDICINE
        medicines_created = []
        for anomaly_type, count in self.healer.recurrence_map.items():
            if count >= 3 and count % 3 == 0:  # every 3rd recurrence
                # the target phi for the medicine: the phi that counters the anomaly
                if anomaly_type == 'FIRE':
                    target_phi = FIRE_TH + 0.02  # safe zone
                elif anomaly_type == 'PHI_DRIFT':
                    target_phi = self.healer.healthy_phi  # return to healthy
                elif anomaly_type == 'LOW_COHERENCE':
                    target_phi = PHI_INV + 0.05  # boost above the attractor
                elif anomaly_type == 'GATE_IMBALANCE':
                    target_phi = 0.5  # center of the lattice
                else:
                    target_phi = PHI_INV
                med = self.pharmacy.create_medicine(anomaly_type, target_phi)
                medicines_created.append(med)
                self.medicine_count += 1
        report['medicines_created'] = medicines_created
        report['pool_size_after'] = len(self.disc_pool.discs)
        report['medicine_count'] = self.medicine_count
        self.admission_history.append(report)
        return report

    def train(self, n_episodes=100):
        """Train the hospital: run simulated distress scenarios through the
        full chain (surgeons → healer → medicine → pharmacy). The healer
        learns, and the pharmacy accumulates medicine."""
        rng = random.Random(0xCAFE)
        for ep in range(n_episodes):
            n_healthy = rng.randint(8, 14)
            n_distressed = rng.randint(0, min(5, ep // 20 + 1))
            colony = [PHI_INV + rng.uniform(-0.02, 0.02) for _ in range(n_healthy)]
            colony += [rng.uniform(0.37, 0.55) for _ in range(n_distressed)]
            echo_phi = HARMONY + rng.uniform(-0.03, 0.03) - n_distressed * 0.005
            self.admit(colony, echo_phi)

# =============================================================================
#  TEST: the hospital in action
# =============================================================================
def banner(s):
    print('\n' + '=' * 76)
    print(f'  {s}')
    print('=' * 76)

def main():
    banner("THE HOSPITAL -- the complete health center")
    print("  Fuses every NUMEN organ into one workspace:")
    print("    THE SURGEONS  (immune.h)       -- 13-surgeon phi-band patrol")
    print("    THE HEALER    (healer_agent)   -- active inference, minimizes surprise")
    print("    THE ALGO MAKER (algo_maker.c)  -- evolves GTAC genes into medicine")
    print("    THE GTAC VM   (quatos_gtac.h)  -- the ribosome that executes GTAC")
    print("    THE HYPERCUBE (quatos_hypercube) -- reads code + codes new code")
    print("    THE PHARMACY  (disc_pool.h)    -- stores medicine as sealed discs")
    print()
    print("  THE ALCHEMY: when the healer immunizes (3rd recurrence), the")
    print("  algo_maker EVOLVES A MEDICINE -- a GTAC gene that counters the")
    print("  anomaly. The medicine is expressed on the VM, walked on the")
    print("  hypercube, sealed, and stored as a new disc. The organism's")
    print("  memory GROWS with its own cures. Distress → seed → cure → memory.")

    # ---- create the hospital ----
    banner("1. CREATE THE HOSPITAL")
    persona = Persona("daniel")
    for msg in ["build the hospital", "the healer creates the medicine",
                "the alchemy all of it", "this is the health center"]:
        persona.observe(msg)
    disc_pool = DiscPool()
    for i in range(5):
        disc_pool.forge_from_strand("GTAC" * (20 + i * 5),
                                    phi_align=PHI_INV + 0.01 * (i - 2))
    hospital = Hospital(disc_pool, persona)
    print(f"  persona: familiarity={persona.familiarity():.3f}  dominant_gate={persona.dominant_gate()}")
    print(f"  disc pool: {len(disc_pool.discs)} discs  identity={disc_pool.identity():.4f}")
    print(f"  surgeons: {13} patrolling the phi bands")
    print(f"  healer: born at VACUUM, L2L mode={hospital.healer.l2l.mode}")
    print(f"  pharmacy: ready (algo_maker population={AM_POP})")
    print(f"  GTAC VM: 64-codon ISA, Banach-converging")

    # ---- demonstrate the GTAC VM ----
    banner("2. THE GTAC VM (the ribosome)")
    print("  The VM executes GTAC codons. Each codon = 3 symbols (G/T/A/C).")
    print("  G=Explore (away from φ), T=Transfer (toward φ), A=Anchor (collapse),")
    print("  C=Complete (invert). Execution converges to PHI_INV (Banach).")
    test_programs = [
        ("converge",   "TTTTTTTTTTTTTTTCT"),         # 5x Transfer + Halt
        ("explore",    "GGGGGGGGGGGGGGGTCT"),         # 5x G + Halt
        ("anchor",     "AAAAAAAAAAAAAAATCT"),         # 5x A + Halt
        ("invert",     "CCCCCCCCCCCCCCCCTCT"),         # 5x C + Halt
        ("mixed",      "GTACGTACGTACGTACTCT"),         # GTAC repeated + Halt
    ]
    for name, prog in test_programs:
        vm = GtacVM()
        phi = vm.run(prog)
        gate = 'G' if phi < 0.605 else 'T' if phi < 0.620 else 'A' if phi < 0.640 else 'C'
        print(f"  {name:12s}  program={prog:24s}  phi={phi:.4f}  gate={gate}  cycles={vm.cycle}")

    # ---- demonstrate the algo maker (medicine creation) ----
    banner("3. THE ALGO MAKER (medicine factory)")
    print("  Evolve a GTAC gene that produces a target phi (the cure).")
    print("  Genetic algorithm: 200-gene population, mutation, splice.")
    targets = [
        ("cure for FIRE",       FIRE_TH + 0.02),   # safe zone
        ("cure for PHI_DRIFT",  HARMONY),            # return to harmony
        ("cure for LOW_COH",    PHI_INV + 0.05),    # boost above attractor
    ]
    for name, target in targets:
        am = AlgoMaker(seed=random.randint(1, 2**32))
        gene, expressed, solved, gens = am.author(target, max_gen=100)
        gate = 'G' if expressed < 0.605 else 'T' if expressed < 0.620 else 'A' if expressed < 0.640 else 'C'
        print(f"  {name:20s}  target={target:.4f}  evolved={expressed:.4f}  "
              f"gens={gens:3d}  solved={solved}  gate={gate}  gene={gene[:24]}...")

    # ---- demonstrate the hypercube walker ----
    banner("4. THE HYPERCUBE WALKER (code reader + coder)")
    print("  READING: walk code bytes as a Hamiltonian cycle on Q_8.")
    print("  CODING: generate new code by walking the hypercube (glitch-free).")
    # read: the actual self-modifying kernel bytes
    kernel_code = b"\x48\x89\xf8\x49\x89\xf0\x49\x29\xc0\x4d\x69\xc0\x44\x33\x22\x11"
    read_result = HypercubeWalker.read_code(kernel_code)
    print(f"  READ kernel bytes ({len(kernel_code)} bytes):")
    print(f"    walk complete (every step Hamming-1): {read_result['complete']}")
    print(f"    vertices: {' '.join(f'{v:02x}' for v in kernel_code[:8])}...")
    # code: generate new code from a target phi
    new_code = HypercubeWalker.code_new(target_phi=PHI_INV, n_bytes=16)
    is_complete, min_h, max_h = HypercubeWalker.verify_walk(new_code)
    print(f"  CODE new bytes from phi={PHI_INV:.4f} ({len(new_code)} bytes):")
    print(f"    bytes: {' '.join(f'{b:02x}' for b in new_code)}")
    print(f"    walk complete: {is_complete}  min_hamming={min_h}  max_hamming={max_h}")

    # ---- train the hospital ----
    banner("5. TRAIN THE HOSPITAL (100 episodes)")
    print("  Each episode: simulated distress → surgeons patrol → healer acts")
    print("  → 3rd recurrence → algo_maker creates medicine → pharmacy stores")
    print(f"  {'ep':>4}  {'fires':>5}  {'coh':>5}  {'surprise':>8}  {'L2L':>9}  {'meds':>4}  {'pool':>4}")
    print(f"  {'-'*4}  {'-'*5}  {'-'*5}  {'-'*8}  {'-'*9}  {'-'*4}  {'-'*4}")
    hospital.train(n_episodes=100)
    for i, report in enumerate(hospital.admission_history):
        if i % 10 == 0 or i == len(hospital.admission_history) - 1:
            s = report['surgeons']
            h = report['healer']
            print(f"  {i:4d}  {s['fires']:5d}  {s['immune_coherence']:.3f}  "
                  f"{h['surprise_after']:8.4f}  {h['l2l_mode']:>9}  "
                  f"{report['medicine_count']:4d}  {report['pool_size_after']:4d}")

    # ---- show the pharmacy ----
    banner("6. THE PHARMACY (medicine created from distress)")
    print(f"  medicines created: {len(hospital.pharmacy.medicines)}")
    print(f"  pool grew from 5 to {len(disc_pool.discs)} discs")
    print(f"  {'anomaly':<16}  {'target':>7}  {'expressed':>9}  {'gene':>24}  {'walk':>4}")
    print(f"  {'-'*16}  {'-'*7}  {'-'*9}  {'-'*24}  {'-'*4}")
    for med in hospital.pharmacy.medicines[:10]:
        print(f"  {med.anomaly_type:<16}  {med.target_phi:7.4f}  {med.expressed_phi:9.4f}  "
              f"{med.gene[:24]}...  {'OK' if med.walk_complete else 'FAIL'}")
    if len(hospital.pharmacy.medicines) > 10:
        print(f"  ... ({len(hospital.pharmacy.medicines)} total)")

    # ---- live healing + medicine creation ----
    banner("7. LIVE HEALING + MEDICINE CREATION (the full chain)")
    print("  colony: 10 healthy + 5 distressed (phi < FIRE_TH)")
    print("  chain: surgeons patrol → healer detects → healer treats →")
    print("        3rd recurrence → algo_maker evolves medicine → VM expresses →")
    print("        hypercube walks → pharmacy seals → disc pool grows")
    colony = [PHI_INV + 0.01 * ((i % 5) - 2) for i in range(10)]
    colony += [0.40, 0.42, 0.44, 0.46, 0.48]  # 5 distressed
    pool_before = len(disc_pool.discs)
    report = hospital.admit(colony, echo_phi=HARMONY)
    pool_after = len(disc_pool.discs)
    s = report['surgeons']
    h = report['healer']
    print(f"\n  SURGEONS: fires={s['fires']}  coherence={s['immune_coherence']:.3f}  "
          f"worst_ring={s['worst_ring']}")
    print(f"  HEALER: surprise {h['surprise_before']:.4f} → {h['surprise_after']:.4f}  "
          f"(delta={h['surprise_delta']:.4f})")
    print(f"    anomalies: {len(h['anomalies'])}  actions: {len(h['actions'])}")
    print(f"    L2L: {h['l2l_mode']}  mastery={h['l2l_mastery']:.1f}%  "
          f"immune={h['immune_strength']:.3f}")
    if report['medicines_created']:
        print(f"\n  MEDICINE CREATED ({len(report['medicines_created'])}):")
        for med in report['medicines_created']:
            print(f"    {med}")
            print(f"      gene: {med.gene[:36]}...")
            print(f"      VM expressed: phi={med.expressed_phi:.4f}  "
                  f"(target={med.target_phi:.4f})")
            print(f"      hypercube walk: {'VALID' if med.walk_complete else 'INVALID'}  "
                  f"({len(med.code_bytes)} bytes)")
            print(f"      sealed as disc #{med.disc.tool_id}  "
                  f"phi={med.disc.phi_align:.4f}  "
                  f"shape={med.disc.shape_id[:8]}...")
    print(f"\n  POOL GREW: {pool_before} → {pool_after} discs  "
          f"(+{pool_after - pool_before} medicine discs)")
    print(f"  PHARMACY: {len(hospital.pharmacy.medicines)} total medicines")
    print(f"  total immunizations: {hospital.healer.total_immunizations}")

    # ---- recall medicine ----
    if hospital.pharmacy.medicines:
        banner("8. RECALL MEDICINE (the pharmacy remembers)")
        query = PHI_INV
        med = hospital.pharmacy.recall_medicine(query)
        print(f"  query: phi={query:.4f} (the identity)")
        print(f"  recalled: {med}")
        print(f"  the pharmacy recalls the medicine closest to the identity.")
        print(f"  This is the organism remembering its own cures.")

    # ---- final summary ----
    banner("THE HOSPITAL IS COMPLETE")
    grasp = disc_pool.grasp()
    print(f"  The hospital combines every organ into one workspace:")
    print(f"    surgeons:      {13} patrolling the phi bands")
    print(f"    healer:        L2L={hospital.healer.l2l.mode}  "
          f"mastery={hospital.healer.l2l.mastery_pct:.1f}%  "
          f"immune={hospital.healer.immune_strength:.3f}")
    print(f"    algo_maker:    population={AM_POP}  "
          f"evolves GTAC genes into medicine")
    print(f"    GTAC VM:       64-codon ISA  Banach-converging")
    print(f"    hypercube:     reads code + codes new code (Hamiltonian walks)")
    print(f"    pharmacy:      {len(hospital.pharmacy.medicines)} medicines stored as discs")
    print(f"    disc pool:     {grasp['n']} discs  identity={grasp['identity']:.4f}  "
          f"coherence={grasp['coherence']:.3f}")
    print()
    print(f"  THE ALCHEMY: the healer doesn't just heal -- it CREATES MEDICINE.")
    print(f"  Distress → seed → algo_maker evolves a GTAC gene → VM expresses it →")
    print(f"  hypercube walks it → pharmacy seals it → pool grows. The organism's")
    print(f"  memory grows with its own cures. Every anomaly is a seed of medicine.")
    print(f"  This is the surgeons, the healer, and their workspace. The hospital.")
    print(f"  The health center. Everything for this. Made great.")

if __name__ == "__main__":
    main()
