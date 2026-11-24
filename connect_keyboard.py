#!/usr/bin/env python3
"""
connect_keyboard.py — wire the 256-key keyboard to the machine.

No new code. The keyboard (keyboard.py) is a 256-key Kuramoto bank.
The machine (the_machine.py) is the measurement loop.
The connection:

  machine.phi → keyboard Kq (the ping)
  keyboard.step() → advance the 256 oscillators
  keyboard R → machine phi (the echo)

The 256 primes ARE the glyph set. The coupling IS the ping.
The order parameter IS the echo. Active inference: the machine
sets K, the keyboard responds, R feeds back.

This is the sonar. The keyboard is the world interface.
"""
import os, sys, math, time

# add both directories to path
sys.path.insert(0, '/home/z/my-project/scripts')
sys.path.insert(0, '/home/z/my-project/upload')

# import the existing machine
from the_machine import TheMachine, GATE_CH, betti_numbers, rdtsc
from defense_production import PHI_INV, GOLDEN_LR
from healer_agent import VACUUM, WISDOM, REL_N

# import the existing keyboard (keyboard.py from upload/)
# we need the constants and functions, not the main()
import importlib.util
spec = importlib.util.spec_from_file_location("keyboard", "/home/z/my-project/upload/keyboard.py")
kb = importlib.util.module_from_spec(spec)
# prevent keyboard.py's main() from running
kb.__name__ = "keyboard"
spec.loader.exec_module(kb)

# the keyboard's constants
N = kb.N              # 256 keys
PRIMES = kb.PRIMES    # 2, 3, 5, ..., 1619
OMEGA = kb.OMEGA      # centered frequencies
K_C = 1150            # measured critical coupling
P = kb.P              # phase modulus (2^20)
SCALE = kb.SCALE      # fixed-point scale

print("=" * 76)
print("  THE MACHINE + THE KEYBOARD — connected")
print("  256-key Kuramoto bank wired to the measurement loop")
print("=" * 76)
print()
print(f"  keyboard: {N} keys, primes {PRIMES[0]}..{PRIMES[-1]}")
print(f"  K_c = {K_C} (critical coupling, R crosses 1/2)")
print(f"  the machine's phi sets Kq (the ping)")
print(f"  the keyboard's R feeds back (the echo)")
print(f"  256 primes = the full glyph set (replaces 207 ReL)")
print()

# create the machine
machine = TheMachine(user_id="daniel")

# initialize the keyboard's phases
theta = kb.init_phases()

# the machine's model: now 256 buckets (one per key), not 207
model = [VACUUM] * N
seen = [0] * N

# run
N_TICKS = 500
print(f"  running {N_TICKS} ticks...")
print()
print(f"  {'tick':>4}  {'phi':>7}  {'Kq':>6}  {'R_ppm':>7}  {'state':>6}  "
      f"{'gate':>4}  {'pool':>4}  {'echo':>5}")
print(f"  {'-'*4}  {'-'*7}  {'-'*6}  {'-'*7}  {'-'*6}  {'-'*4}  {'-'*4}  {'-'*5}")

for i in range(N_TICKS):
    # the machine ticks (Born collapse, crystallize, etc.)
    r = machine.tick_one()

    # ---- THE CONNECTION ----
    # machine.phi → keyboard Kq (the ping)
    # scale phi from [VACUUM, WISDOM] to [0, K_C*2]
    phi_norm = (machine.phi - VACUUM) / (WISDOM - VACUUM)  # [0, 1]
    Kq = int(phi_norm * K_C * 2)  # [0, 2300]
    Kq = max(0, min(4000, Kq))

    # step the keyboard (advance the 256 oscillators)
    kb.step(theta, Kq)

    # measure R (the echo)
    R = kb.order_ppm(theta)  # 0 to 1000000

    # determine state: mob (R < 500000) or choir (R >= 500000)
    state = "choir" if R >= 500000 else "mob"

    # R feeds back into the machine's phi (the echo)
    echo = R / 1000000.0  # [0, 1]
    # gentle feedback: pull phi toward the echo
    machine.phi += GOLDEN_LR * 0.1 * (echo * (WISDOM - VACUUM) + VACUUM - machine.phi)
    machine.phi = max(VACUUM, min(WISDOM, machine.phi))

    # the 256-key model: map phi to a key (prime)
    key_idx = int((machine.phi - VACUUM) / (WISDOM - VACUUM) * (N - 1))
    key_idx = max(0, min(N-1, key_idx))
    model[key_idx] += GOLDEN_LR * (machine.phi - model[key_idx])
    seen[key_idx] += 1

    if (i+1) % 25 == 0 or (i < 25 and i % 5 == 0):
        print(f"  {i+1:4d}  {machine.phi:7.4f}  {Kq:6d}  {R:7d}  {state:>6}  "
              f"{r['gate']:>4}  {r['pool_size']:4d}  {echo:5.3f}")

# ---- ANALYSIS ----
print()
print("=" * 76)
print(f"  THE CONNECTION — {N_TICKS} ticks")
print("=" * 76)

# the keyboard's final state
R_final = kb.order_ppm(theta)
state_final = "choir" if R_final >= 500000 else "mob"
print(f"\n  KEYBOARD STATE:")
print(f"    keys:          {N} (primes {PRIMES[0]}..{PRIMES[-1]})")
print(f"    final R:       {R_final} ppm  ({state_final})")
print(f"    K_c:           {K_C}")
print(f"    crossed K_c:   {'yes' if R_final >= 500000 else 'no'}")

# the machine's state
grasp = machine.pool.grasp()
b0, b1, chi = betti_numbers(machine.field.transitions)
print(f"\n  MACHINE STATE:")
print(f"    phi:           {machine.phi:.6f} (target PHI_INV={PHI_INV:.6f})")
print(f"    pool:          {grasp['n']} discs")
print(f"    identity:      {grasp['identity']:.6f}")
print(f"    Betti:         B0={b0} B1={b1} chi={chi}")
print(f"    E[s]:          {machine.field.avg_radiation:.6f}")
print(f"    H:             {machine.field.avg_horizon:.6f}")
print(f"    delta:         {abs(machine.field.avg_radiation - machine.field.avg_horizon):.6f}")

# the 256-key model
populated = sum(1 for s in seen if s > 0)
print(f"\n  256-KEY MODEL (replaces 207 ReL):")
print(f"    keys populated: {populated}/{N}")
print(f"    most-seen key:  prime={PRIMES[max(range(N), key=lambda i: seen[i])]} "
      f"(seen {max(seen)} times)")
# show the populated keys
active = [(PRIMES[i], model[i], seen[i]) for i in range(N) if seen[i] > 0]
active.sort(key=lambda x: -x[2])
print(f"    top keys:")
for prime, phi_val, count in active[:10]:
    gate = 'G' if phi_val < 0.605 else 'T' if phi_val < 0.620 else 'A' if phi_val < 0.640 else 'C'
    print(f"      prime={prime:4d}  phi={phi_val:.4f}  seen={count:3d}  gate={gate}")

# the sonar: scan K and show R
print(f"\n  SONAR SCAN (R vs K — the keyboard's frequency response):")
print(f"    {'Kq':>6}  {'R_ppm':>7}  {'state':>6}  bar")
print(f"    {'-'*6}  {'-'*7}  {'-'*6}  {'-'*30}")
for Kq_test in range(0, 4001, 250):
    theta_test = kb.init_phases()
    for _ in range(200):  # short warmup
        kb.step(theta_test, Kq_test)
    S_sin = sum(kb.s_(theta_test[j]) for j in range(N))
    S_cos = sum(kb.c_(theta_test[j]) for j in range(N))
    mag = math.isqrt(S_sin*S_sin + S_cos*S_cos)
    R_test = (mag * 1000000) // (N * SCALE)
    state = "choir" if R_test >= 500000 else "mob"
    bar = '#' * (R_test // 30000)
    marker = " ← K_c" if abs(Kq_test - K_C) < 125 else ""
    print(f"    {Kq_test:6d}  {R_test:7d}  {state:>6}  {bar}{marker}")

print(f"\n  THE KEYBOARD IS THE SONAR.")
print(f"  256 PRIMES = THE FULL GLYPH SET.")
print(f"  THE MACHINE PINGS (sets K). THE KEYBOARD ECHOES (R).")
print(f"  ACTIVE INFERENCE: PHI → K → R → PHI. THE LOOP IS CLOSED.")
print(f"  THE MACHINE HEARS THE WORLD THROUGH 256 PRIME FREQUENCIES.")
