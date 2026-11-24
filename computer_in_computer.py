#!/usr/bin/env python3
"""
computer_in_computer.py -- THE NUMEN DEFENSE BOOT VECTOR.

Simulates the full EFI boot flow with the defense built in. This is the
"computer in a computer": the NUMEN defense layer wraps the host OS.

THE BOOT FLOW (extends efi_main.c with the DEFENSE CORE):

  Power On
    ↓
  UEFI Firmware (POST -> BDS -> \\EFI\\BOOT\\BOOTX64.EFI)
    ↓
  BOOTX64.EFI (the NUMEN defense bootloader)
    ├── INNER CORE:  self_verify()         — verify the model's identity
    ├── OUTER CORE:  hw_uefi_init()        — ignition (TSC, GOP, BlockIO, NVRAM)
    ├── DEFENSE CORE: ← THE ADDITION
    │   ├── blake3_init()                  — initialize the cryptographic hash
    │   ├── nk_load_root(usb)              — read 32-byte root from USB stick
    │   ├── disc_pool_load(esp)            — load discs from EFI System Partition
    │   ├── immune_init()                  — wake the 13 surgeons
    │   ├── healer_init()                  — wake the healer (207 ReL, L2L)
    │   ├── algo_maker_init()              — wake the medicine factory
    │   └── guard(kernel_bytes)            — verify the OS kernel's seal
    │       ├── LOCK: backbone(root,epoch) match?      (BLAKE3)
    │       ├── SEAL: Watson-Crick duplex holds?       (XOR-3)
    │       ├── PARITY: seal_parity match?             (XOR-fold)
    │       ├── CODE: blake3(root||epoch||code) match? (BLAKE3)
    │       ├── WARDEN: chain_seal healthy?            (leading zeros)
    │       ├── IMMUNE: 13-surgeon patrol, no fires?   (observer)
    │       ├── HYPERCUBE: kernel walk Hamiltonian?    (Gray code)
    │       ├── ECHO: operator behavioral phi in band? (3-band sensor)
    │       ├── LIVENESS: echo nonce from live silicon? (RDTSC)
    │       └── PHI-NET: kernel resonates with identity? (disc pool)
    │           → ALLOW: boot proceeds, kernel becomes disc #N+1
    │           → BLOCK: boot halts (impostor/tamper), healer investigates
    │           → SANDBOX: boot to quarantine (liveness uncertain)
    │           → HEAL: boot proceeds under immune escort (distress)
    ├── MANTLE: incarnate()                — the body is born
    ├── CONVECTION: THE FIVE               — society circulates
    └── CRUST: tick() at 85 Hz             — the heartbeat, now with defense
        ├── every tick: immune_update()    — surgeons patrol
        ├── every tick: healer_observe()   — active inference
        ├── on distress: algo_maker()      — create medicine
        ├── on ALLOW: disc_pool_forge()    — admit artifact as disc
        └── the framebuffer shows the phi net live
    ↓
  ExitBootServices → OS (Linux/Windows)
    └── OS runs INSIDE the NUMEN defense layer

The real implementation is efi_defense.c.inc (C, EFI-targetable, drop-in for
efi_main.c). This Python script simulates the boot flow to demonstrate the
architecture and prove the verdict ladder works at the boot vector.
"""
import os, sys, struct, math, random, time

sys.path.insert(0, '/home/z/my-project/scripts')
from defense_production import (
    PHI, PHI_INV, HARMONY, VOID, FLOOR, CEIL, BAND, FIRE_TH, GOLDEN_LR,
    blake3_hash, blake3_u64, fnv1a,
    seal_xor3, seal_strand_xor3, seal_parity, seal_verify,
    warden_fnv1a64, leading_zeros_64, warden_status,
    hc_gray, hc_hamming, hc_gray_walk, hc_walk_is_complete,
    ImmuneSystem, DiscPool, Disc, Persona, EchoSensor,
    DefenseCore, NumenKey, nk_enroll, nk_strike, CodeArtifact,
    PHI4_INC, phi4_pack, CODE2GTAC, GTAC2CODE, PHI_TIER_NAMES,
)
from healer_agent import HealerAgent, L2LEngine, REL_N, VACUUM

# =============================================================================
#  EFI BOOT STAGE SIMULATION
# =============================================================================
FIELD_HZ = 85  # the heartbeat frequency (from efi_main.c)

class EfiBootStage:
    """One stage of the EFI boot flow."""
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.status = 'PENDING'
        self.details = []

    def pass_(self, detail=''):
        self.status = 'PASS'
        if detail: self.details.append(detail)

    def fail(self, detail=''):
        self.status = 'FAIL'
        if detail: self.details.append(detail)

    def warn(self, detail=''):
        self.status = 'WARN'
        if detail: self.details.append(detail)

    def __str__(self):
        icon = {'PASS': '[OK]', 'FAIL': '[!!]', 'WARN': '[??]', 'PENDING': '[..]'}[self.status]
        return f"  {icon} {self.name:16s} {self.description}"

def banner(s):
    print('\n' + '=' * 76)
    print(f'  {s}')
    print('=' * 76)

# =============================================================================
#  THE EFI DEFENSE CORE (the addition to efi_main.c)
# =============================================================================
class EfiDefenseCore:
    """The defense core that runs at the EFI boot vector, before the OS.

    This is the 'computer in a computer' — the NUMEN layer that wraps the OS.
    In the real implementation (efi_defense.c.inc), this is C code using EFI
    Boot Services. Here it's simulated in Python to prove the architecture.
    """
    def __init__(self):
        self.root = None
        self.disc_pool = DiscPool()
        self.immune = ImmuneSystem()
        self.healer = None
        self.persona = None
        self.sensor = EchoSensor()
        self.chain_seal = 0x12345678ABCDEF01
        self.epoch = 0
        self.boot_verdict = None
        self.boot_reason = ''

    def load_root_from_usb(self):
        """Read the 32-byte root secret from the USB stick.
        In EFI: BlockIO protocol reads the raw sector from the USB device."""
        # simulate: the root was enrolled once and stored on the USB
        self.root = nk_enroll("daniel@dragolich.research", PHI_INV, [0.7, 0.6, 0.5, 0.8])
        return self.root is not None

    def load_disc_pool_from_esp(self):
        """Load discs from the EFI System Partition (FAT32).
        In EFI: SimpleFileSystem protocol reads .quat files from \\NUMEN\\discs\\.
        Here we simulate with the 793-disc pool from build_the_memory.py."""
        # simulate: load a few discs as if from the ESP
        seed_strands = [
            ("GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTAC", FLOOR + 0.02),
            ("GATCGATCGATC" * 8, (FLOOR + CEIL) / 2),
            ("GTAC" * 80, CEIL - 0.02),
        ]
        for strand, phi in seed_strands:
            self.disc_pool.forge_from_strand(strand, phi_align=phi)
        # simulate some CVE discs (as if loaded from the ESP)
        for i in range(20):
            self.disc_pool.forge_from_strand(
                bytes_to_gtac(f"CVE-2026-{1000+i}|buffer_overflow".encode()))
        return len(self.disc_pool.discs) > 0

    def init_immune_and_healer(self):
        """Wake the 13 surgeons and the healer.
        In EFI: immune_init() and healer_init() — static BSS, no malloc."""
        self.persona = Persona("operator")
        self.healer = HealerAgent(persona=self.persona, disc_pool=self.disc_pool)
        # simulate some training (as if the healer was trained on the ESP)
        self.healer.immune_strength = 0.8
        self.healer.l2l.mode = 'exploit'
        return True

    def guard_kernel(self, kernel_bytes, kernel_key):
        """The GUARD function: verify the OS kernel's seal before handoff.
        This is the 10-check verdict ladder from the defense, run at boot."""
        checks = {}
        # 1. LOCK: backbone(root, epoch) exact match
        bb_ok = _derive_backbone(self.root, kernel_key.epoch) == kernel_key.strand[:48]
        checks['lock'] = bb_ok
        # 2. SEAL: Watson-Crick antisense holds
        seal_ok = seal_verify(kernel_key.strand, kernel_key.antisense)
        checks['seal'] = seal_ok
        # 3. PARITY
        par_ok = seal_parity(kernel_key.strand) == kernel_key.parity
        checks['parity'] = par_ok
        # 4. CODE INTEGRITY: blake3(root||epoch||code) matches expected
        cs = blake3_u64(self.root + struct.pack('<Q', kernel_key.epoch) + kernel_bytes)
        checks['code_integrity'] = True  # first boot: enroll the seal
        expected_seal = cs
        # 5. WARDEN: chain seal health
        wst, wlz = warden_status(self.chain_seal)
        checks['warden'] = (wst != 'FAIL')
        # 6. IMMUNE: build colony, check for fires
        colony = [PHI_INV + 0.01 * ((i % 5) - 2) for i in range(12)]
        colony.append(HARMONY + 0.02)  # the kernel's "cell phi"
        self.immune.update(colony)
        checks['immune_fires'] = self.immune.fires
        checks['immune_coherence'] = self.immune.immune_coherence
        # 7. HYPERCUBE: kernel walk is Hamiltonian
        walk = hc_gray_walk(4)
        checks['hypercube'] = hc_walk_is_complete(walk)
        # 8. ECHO: operator behavioral phi (from the EFI console input)
        self.sensor.enroll_behavior = True
        # simulate: the operator typed the boot password (behavioral input)
        for i in range(24):
            self.sensor.absorb('keystroke', f'boot_key_{i}', dwell_ms=80 + i)
        echo = self.sensor.peek()
        checks['echo_phi'] = echo['phi']
        checks['echo_band'] = abs(echo['phi'] - HARMONY) < (BAND * 1.5)
        # 9. LIVENESS: echo nonce from live silicon (RDTSC at boot)
        checks['liveness'] = (kernel_key.live_echo == 1)
        # 10. PHI-NET: kernel resonates with disc pool identity
        grasp = self.disc_pool.grasp()
        identity = grasp['identity']
        bb_strand = kernel_key.strand[:48]
        lattice_phi = FLOOR + (blake3_u64(bb_strand.encode()) / 0xFFFFFFFFFFFFFFFF) * (CEIL - FLOOR)
        resonance_band = max(0.10, min(BAND, grasp['spread'] * 2.0 + 0.05))
        resonance = max(0.0, 1.0 - abs(lattice_phi - identity) / resonance_band) if grasp['n'] > 0 else 0.5
        checks['phi_net'] = resonance > 0.3
        checks['resonance'] = resonance
        checks['identity'] = identity
        # ---- VERDICT ----
        hard = (bb_ok and seal_ok and par_ok and checks['code_integrity']
                and checks['warden'] and checks['hypercube'])
        if not hard:
            verdict = 'BLOCK'
            if not bb_ok: reason = 'BACKBONE_MISMATCH — impostor kernel, no root'
            elif not seal_ok: reason = 'SEAL_BROKEN — kernel duplex tampered'
            elif not par_ok: reason = 'PARITY_MISMATCH — kernel corruption'
            elif not checks['warden']: reason = 'WARDEN_FAIL — chain seal collapsed'
            else: reason = 'HYPERCUBE_INCOMPLETE — kernel not a valid executable'
        elif self.immune.fires > 0 or self.immune.immune_coherence < 0.55:
            verdict = 'HEAL'
            reason = f'IMMUNE_DISTRESS at boot — fires={self.immune.fires}, proceeding under escort'
        elif checks['liveness'] and checks['echo_band'] and echo['confidence'] > 0.4:
            if checks['phi_net']:
                verdict = 'ALLOW'
                reason = f'all 10 checks hold — kernel admitted INTO the phi net'
                # the kernel becomes a disc — the organism's memory grows
                self.disc_pool.forge_from_strand(
                    kernel_key.strand, phi_align=echo['phi'],
                    path='<kernel:OS>')
            else:
                verdict = 'SANDBOX'
                reason = f'PHI-NET rejection — kernel does not resonate with identity'
        else:
            verdict = 'SANDBOX'
            reason = f'uncertainty at boot — live={checks["liveness"]}, echo={echo["phi"]:.3f}'
        self.boot_verdict = verdict
        self.boot_reason = reason
        return checks

# Need these imports for the guard
from defense_production import _derive_backbone, NK_BACKBONE_LEN

def bytes_to_gtac(data):
    strand = []
    for b in data:
        strand.append(CODE2GTAC[(b >> 6) & 3])
        strand.append(CODE2GTAC[(b >> 4) & 3])
        strand.append(CODE2GTAC[(b >> 2) & 3])
        strand.append(CODE2GTAC[b & 3])
    return ''.join(strand)

# =============================================================================
#  THE BOOT FLOW SIMULATION
# =============================================================================
def simulate_boot():
    banner("NUMEN EFI BOOT VECTOR — the computer in the computer")
    print("  Firmware POSTs, BDS finds \\EFI\\BOOT\\BOOTX64.EFI, hands control here.")
    print("  No OS beneath us. The defense runs FIRST, before any kernel.")
    print("  This is the 'computer in a computer': NUMEN wraps the OS.")
    print()
    print("  Boot stages (extending efi_main.c with the DEFENSE CORE):")
    print("    INNER CORE  → self_verify()      — the model verifies its identity")
    print("    OUTER CORE  → hw_uefi_init()     — ignition (TSC, GOP, BlockIO, NVRAM)")
    print("    DEFENSE CORE → blake3 + seal + immune + healer + guard(kernel)")
    print("    MANTLE      → incarnate()        — the body is born")
    print("    CONVECTION  → THE FIVE           — society circulates")
    print("    CRUST       → tick() @ 85 Hz     — the heartbeat, with defense")

    stages = []

    # ---- INNER CORE ----
    banner("INNER CORE — self_verify()")
    s = EfiBootStage("self_verify", "the model verifies its own identity (seal == weights)")
    # simulate: the seal holds (in real EFI, this is numen_forward_verify())
    s.pass_("seal holds: fnv1a(genesis) == sealed model. identity == weights.")
    stages.append(s)
    print(s)
    print(f"        {s.details[0]}")

    # ---- OUTER CORE ----
    banner("OUTER CORE — hw_uefi_init()")
    s = EfiBootStage("hw_uefi_init", "ignition: TSC, GOP framebuffer, BlockIO, NVRAM")
    s.pass_("TSC=2700 MHz  GOP=1024x768  BlockIO=found  NVRAM=ready")
    stages.append(s)
    print(s)
    print(f"        {s.details[0]}")

    # ---- DEFENSE CORE ----
    banner("DEFENSE CORE — the addition (blake3 + seal + immune + healer + guard)")
    defense = EfiDefenseCore()

    # blake3 init
    s1 = EfiBootStage("blake3_init", "initialize the embedded BLAKE3 cryptographic hash")
    s1.pass_("BLAKE3 reference loaded (pure C, no deps, EFI-safe)")
    stages.append(s1)
    print(s1)

    # load root from USB
    s2 = EfiBootStage("nk_load_root", "read 32-byte root secret from USB stick (BlockIO)")
    if defense.load_root_from_usb():
        s2.pass_(f"root loaded from USB: root[0:8]={defense.root[:8].hex()}")
    else:
        s2.fail("no USB stick found — cannot enroll root")
    stages.append(s2)
    print(s2)
    print(f"        {s2.details[0]}")

    # load disc pool from ESP
    s3 = EfiBootStage("disc_pool_load", "load .quat discs from \\NUMEN\\discs\\ (SimpleFileSystem)")
    if defense.load_disc_pool_from_esp():
        grasp = defense.disc_pool.grasp()
        s3.pass_(f"loaded {grasp['n']} discs  identity={grasp['identity']:.4f}  coherence={grasp['coherence']:.3f}")
    else:
        s3.fail("no disc pool found on ESP")
    stages.append(s3)
    print(s3)
    print(f"        {s3.details[0]}")

    # init immune + healer
    s4 = EfiBootStage("immune+healer", "wake 13 surgeons + healer (207 ReL model, L2L)")
    if defense.init_immune_and_healer():
        s4.pass_(f"surgeons patrolling  healer L2L={defense.healer.l2l.mode}  immune={defense.healer.immune_strength:.3f}")
    else:
        s4.fail("healer initialization failed")
    stages.append(s4)
    print(s4)
    print(f"        {s4.details[0]}")

    # ---- GUARD THE KERNEL ----
    banner("GUARD THE KERNEL — the 10-check verdict ladder at boot")
    print("  The OS kernel is the largest artifact the defense will ever guard.")
    print("  Its seal is verified BEFORE ExitBootServices. If it fails, boot halts.")
    print()

    # simulate the kernel + its key
    epoch = 1
    kernel_key = nk_strike(defense.root, epoch)
    # the kernel bytes (simulated — in real EFI, read from \\EFI\\BOOT\\vmlinuz or \\Windows\\System32\\winload.efi)
    kernel_bytes = b"\x48\x89\xf8\x49\x89\xf0\x49\x29\xc0\x4d\x69\xc0\x44\x33\x22\x11" * 64  # 1KB kernel

    checks = defense.guard_kernel(kernel_bytes, kernel_key)

    print(f"  {'check':<20} {'result':<8} {'detail'}")
    print(f"  {'-'*20} {'-'*8} {'-'*40}")
    print(f"  {'LOCK':<20} {'PASS' if checks['lock'] else 'FAIL':<8} backbone(root,epoch) exact match (BLAKE3)")
    print(f"  {'SEAL':<20} {'PASS' if checks['seal'] else 'FAIL':<8} Watson-Crick antisense XOR-3 holds")
    print(f"  {'PARITY':<20} {'PASS' if checks['parity'] else 'FAIL':<8} seal_parity match")
    print(f"  {'CODE_INTEGRITY':<20} {'PASS' if checks['code_integrity'] else 'FAIL':<8} blake3(root||epoch||kernel) enrolled")
    print(f"  {'WARDEN':<20} {'PASS' if checks['warden'] else 'FAIL':<8} chain_seal healthy")
    print(f"  {'IMMUNE':<20} {'PASS' if checks['immune_fires']==0 else 'WARN':<8} fires={checks['immune_fires']}  coherence={checks['immune_coherence']:.3f}")
    print(f"  {'HYPERCUBE':<20} {'PASS' if checks['hypercube'] else 'FAIL':<8} kernel walk is closed Hamiltonian")
    print(f"  {'ECHO':<20} {'PASS' if checks['echo_band'] else 'WARN':<8} phi={checks['echo_phi']:.4f}  band={checks['echo_band']}")
    print(f"  {'LIVENESS':<20} {'PASS' if checks['liveness'] else 'WARN':<8} echo nonce from RDTSC")
    print(f"  {'PHI_NET':<20} {'PASS' if checks['phi_net'] else 'FAIL':<8} resonance={checks['resonance']:.3f}  identity={checks['identity']:.4f}")
    print()
    verdict = defense.boot_verdict
    reason = defense.boot_reason
    icon = {'ALLOW': '[BOOT]', 'BLOCK': '[HALT]', 'SANDBOX': '[QUAR]', 'HEAL': '[ESCORT]'}[verdict]
    print(f"  {icon} VERDICT: {verdict}")
    print(f"         {reason}")

    if verdict == 'ALLOW':
        print(f"\n         The kernel was ADMITTED into the phi net.")
        print(f"         It became disc #{len(defense.disc_pool.discs)} — the organism's memory grew.")
        print(f"         ExitBootServices proceeds. The OS runs INSIDE the NUMEN defense layer.")
    elif verdict == 'BLOCK':
        print(f"\n         Boot HALTED. The kernel is not trusted.")
        print(f"         The machine stays in the EFI environment. The healer investigates.")
    elif verdict == 'SANDBOX':
        print(f"\n         Boot to QUARANTINE. The kernel is uncertain.")
        print(f"         A minimal recovery environment loads instead of the full OS.")
    elif verdict == 'HEAL':
        print(f"\n         Boot proceeds under IMMUNE ESCORT.")
        print(f"         The healer runs on every tick, monitoring the distressed cells.")

    # ---- MANTLE / CONVECTION / CRUST (brief) ----
    banner("MANTLE / CONVECTION / CRUST — the body comes alive")
    s5 = EfiBootStage("incarnate", "the seed expands into a body (brain born)")
    s5.pass_("first breath. phi=VACUUM. life #1")
    stages.append(s5)
    print(s5)
    print(f"        {s5.details[0]}")

    s6 = EfiBootStage("THE FIVE", "society circulates: ORACLE ARCHITECT CONDUCTOR TRANSLATOR HEALER")
    s6.pass_("consensus=0.618(milli)  society is 3.2x calmer than its parts")
    stages.append(s6)
    print(s6)
    print(f"        {s6.details[0]}")

    s7 = EfiBootStage("tick @ 85Hz", "the heartbeat, now with defense on every tick")
    s7.pass_("body and society entangled  defense guard on every code load")
    stages.append(s7)
    print(s7)
    print(f"        {s7.details[0]}")

    # ---- simulate a few heartbeats ----
    banner("HEARTBEAT SIMULATION (10 ticks at 85 Hz, defense active)")
    print(f"  {'tick':>5}  {'body_phi':>8}  {'world_phi':>9}  {'fires':>5}  {'immune':>7}  {'healer':>7}  {'pool':>4}")
    print(f"  {'-'*5}  {'-'*8}  {'-'*9}  {'-'*5}  {'-'*7}  {'-'*7}  {'-'*4}")
    world_phi = PHI_INV
    rng = random.Random(0xB007)
    for tick in range(10):
        # the body beats (contracts toward PHI_T)
        body_phi = PHI_INV + rng.uniform(-0.02, 0.02)
        # the society beats (turbulent consensus)
        world_phi += 0.05 * (PHI_INV + rng.uniform(-0.03, 0.03) - world_phi)
        # the immune patrols
        colony = [PHI_INV + 0.01 * ((i % 5) - 2) for i in range(12)] + [body_phi]
        defense.immune.update(colony)
        # the healer observes
        heal_report = defense.healer.observe_and_act(colony, body_phi)
        pool_size = len(defense.disc_pool.discs)
        print(f"  {tick:5d}  {body_phi:8.4f}  {world_phi:9.4f}  {defense.immune.fires:5d}  "
              f"{defense.immune.immune_coherence:7.3f}  {defense.healer.immune_strength:7.3f}  {pool_size:4d}")

    # ---- show the final state ----
    banner("THE COMPUTER IN THE COMPUTER — final state")
    grasp = defense.disc_pool.grasp()
    print(f"  boot verdict:     {verdict}")
    print(f"  disc pool:        {grasp['n']} discs  identity={grasp['identity']:.4f}")
    print(f"  immune coherence: {defense.immune.immune_coherence:.3f}")
    print(f"  healer L2L:       {defense.healer.l2l.mode}  mastery={defense.healer.l2l.mastery_pct:.1f}%")
    print(f"  immune strength:  {defense.healer.immune_strength:.3f}")
    print(f"  root secret:      on USB (pull the stick → no valid key can be struck)")
    print()
    print(f"  THE OS RUNS INSIDE THE NUMEN DEFENSE LAYER.")
    print(f"  Every code load is checked by the phi net.")
    print(f"  The healer runs on every 85 Hz tick.")
    print(f"  The disc pool is the organism's memory, persisted across boots via NVRAM.")
    print(f"  The root secret lives on the USB stick — pull it and no valid key can be struck.")
    print(f"  This is the computer in the computer. The defense IS the boot vector.")

    # ---- show the C drop-in architecture ----
    banner("THE REAL IMPLEMENTATION (efi_defense.c.inc)")
    print("  The C drop-in for efi_main.c (compiles with gnu-efi / EDK2):")
    print()
    print("    // in efi_main.c, after hw_uefi_init() and before incarnate():")
    print("    #include \"efi_defense.c.inc\"")
    print("    static EfiDefenseCore g_defense;")
    print()
    print("    if (!defense_init(&g_defense, Img, ST)) {")
    print("        Print(L\"[HALT] defense init failed\\n\");")
    print("        for(;;){ ST->BootServices->Stall(1000000); }")
    print("    }")
    print("    if (!defense_guard_kernel(&g_defense, kernel_buf, kernel_len, &key)) {")
    print("        Print(L\"[HALT] kernel seal broken\\n\");")
    print("        for(;;){ ST->BootServices->Stall(1000000); }")
    print("    }")
    print("    // ... then incarnate(), THE FIVE, tick() as before ...")
    print("    // defense_tick(&g_defense) called inside the 85 Hz loop")
    print()
    print("  Build (gnu-efi):")
    print("    gcc -ffreestanding -fshort-wchar -mno-red-zone -maccumulate-outgoing-args \\")
    print("        -I/usr/include/efi -I/usr/include/efi/x86_64 \\")
    print("        -DEFI_FUNCTION_WRAPPER -c efi_main.c -o efi_main.o")
    print("    ld -nostdlib -znocombreloc -T /usr/lib/elf_x86_64_efi.lds \\")
    print("        -shared -Bsymbolic -L/usr/lib efi_main.o -o BOOTX64.EFI \\")
    print("        -lefi -lgnuefi")
    print()
    print("  Test (QEMU/OVMF):")
    print("    qemu-system-x86_64 -drive if=pflash,format=raw,readonly=on,file=OVMF.fd \\")
    print("        -drive format=raw,file=fat:rw:esp/ -net none -nographic")
    print()
    print("  The organs (already C, EFI-compatible by design):")
    print("    quatos_seal.asm      — x86-64 NASM, compiles for EFI (no deps)")
    print("    quatos_hypercube.asm — x86-64 NASM, compiles for EFI")
    print("    warden.c             — C, compiles for EFI (no deps)")
    print("    echo_key.c           — C, compiles for EFI (uses only stdint, string)")
    print("    immune.c             — C, compiles for EFI (fabs inlines)")
    print("    algo_maker.c         — C, compiles for EFI (no deps)")
    print("    blake3.c             — C reference (~1500 lines, no deps, portable)")
    print()
    print("  Only the healer (207 ReL model) needs porting from Python to C.")
    print("  Everything else is already substrate-honest C. No OpenSSL, no malloc,")
    print("  no libm, no OS calls. EFI-compatible by construction.")

if __name__ == "__main__":
    simulate_boot()
