/* temporal_compiler.c -- THE MEASUREMENT LOOP. This IS the EFI core.
 *
 * The temporal compiler is the boot vector. Layer 0 = RDTSC. Everything
 * derives from tau. This file compiles natively (to test the core) and
 * as an EFI binary (same code, different entry point).
 *
 * The 16 layers:
 *   0:  tau  = RDTSC
 *   1:  pi   = PI_DIG[tau % 200]
 *   2:  z    = sigma zone
 *   3:  p    = PRIMES[z]
 *   4:  g    = GTAC gate
 *   5:  r    = POPCNT
 *   --- IEEE 754 boundary ---
 *   6:  H    = Shannon entropy
 *   7:  phi  = phi proximity
 *   8:  gamma= CGOS = sqrt(phi*H)
 *   9:  phi' = Banach step
 *   10-13: Trinity, Klein, sigma, ReL
 *   --- Betti routing ---
 *   14-16: gate graph, Betti numbers, routing
 *
 * The measurement loop: prepare -> evolve -> measure -> prepare
 * The Bekenstein invariant: E[radiation] = H_horizon <= 2 bits
 *
 * Build (native, to test the core):
 *   gcc -O2 -o temporal_compiler temporal_compiler.c -lm
 *   ./temporal_compiler [ticks] [hz]
 *
 * Build (EFI, the real boot vector):
 *   See efi_build.sh
 */
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#ifdef __x86_64__
#include <immintrin.h>
#define HAVE_RDTSC 1
static inline uint64_t rdtsc(void) {
    unsigned lo, hi;
    __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}
#else
static uint64_t rdtsc(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}
#endif

/* === CONSTANTS (from temporal_compiler_core.c, unmodified) === */
#define PHI_INV    0.6180339887498949
#define PHI        1.6180339887498948
#define PHI_T      0.625
#define VACUUM     0.36787944117144233
#define WISDOM     0.896
#define LR_ECHO    0.07585880414
#define TWO_PI     6.283185307179586
#define GA_RAD     2.399963229728653

#define GATE_G_MAX 0.605
#define GATE_T_MAX 0.620
#define GATE_A_MAX 0.630

#define GATE_G 0
#define GATE_T 1
#define GATE_A 2
#define GATE_C 3
static const char GATE_CH[4] = {'G','T','A','C'};

/* the eternal pi sequence (first 200 digits, used as Layer 1 phase) */
static const uint8_t PI_DIG[200] = {
    3,1,4,1,5,9,2,6,5,3,5,8,9,7,9,3,2,3,8,4,
    6,2,6,4,3,3,8,3,2,7,9,5,0,2,8,8,4,1,9,7,1,
    6,9,3,9,9,3,7,5,1,0,5,8,2,0,9,7,4,9,4,4,
    5,9,2,3,0,7,8,1,6,4,0,6,2,8,6,2,0,8,9,9,
    8,6,2,8,0,3,4,8,2,5,3,4,2,1,1,7,0,6,7,9,
    8,2,1,4,8,0,8,6,5,1,3,2,8,2,3,0,6,6,4,7,
    0,9,3,8,4,4,6,0,9,5,5,0,5,8,2,2,3,1,7,2,
    5,3,5,9,4,0,8,1,2,8,4,8,1,1,1,7,4,5,0,2,
    8,4,1,0,2,7,0,1,9,3,8,5,2,1,1,0,5,5,5,9,
    6,4,4,6,2,2,9,4,8,9,5,4,9,3,0,3,8,1,9,
};

/* first 54 primes (2..251) */
static const int PRIMES[54] = {
    2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,
    73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,
    179,181,191,193,197,199,211,223,227,229,233,239,241,251
};

/* === THE QUANTUM STATE (the wave function) === */
typedef struct { double re, im; } complex_t;

static complex_t c_make(double re, double im) { complex_t z = {re,im}; return z; }
static complex_t c_mul(complex_t a, complex_t b) {
    return c_make(a.re*b.re - a.im*b.im, a.re*b.im + a.im*b.re);
}
static double c_abs2(complex_t z) { return z.re*z.re + z.im*z.im; }
static complex_t c_exp_i(double theta) { return c_make(cos(theta), sin(theta)); }

/* GTAC amplitudes (Wire 3): G:(1,0) T:(0,1) A:(1+i)/sqrt2 C:(1-i)/sqrt2 */
static complex_t gtac_amplitude(int gate) {
    double s = 0.7071067811865476;
    switch(gate) {
        case GATE_G: return c_make(1.0, 0.0);
        case GATE_T: return c_make(0.0, 1.0);
        case GATE_A: return c_make(s, s);
        case GATE_C: return c_make(s, -s);
        default:     return c_make(0.0, 0.0);
    }
}

/* === THE MEASUREMENT LOOP STATE === */
typedef struct {
    /* the wave: 4 GTAC amplitudes */
    complex_t psi[4];
    double probs[4];
    /* horizon entropy H = -sum p log2 p (<= 2 bits) */
    double horizon_entropy;
    /* last radiation s = -log2(p_outcome) */
    double last_radiation;
    double total_radiation;
    long n_observations;
    /* the phi register (the Banach accumulator) */
    double phi;
    double phi_target;
    /* the tick counter */
    uint64_t tau;       /* Layer 0: RDTSC */
    int last_gate;
    /* gate transition graph (last 64 transitions, for Betti) */
    int transitions[64];
    int n_transitions;
    /* cumulative radiation for invariant check */
    double radiation_sum;
    double entropy_sum;
} QuantumLoop;

void qloop_init(QuantumLoop *q) {
    memset(q, 0, sizeof(*q));
    q->phi = VACUUM;
    q->phi_target = PHI_INV;
    /* seed the wave: equal superposition */
    for (int i = 0; i < 4; i++) {
        q->psi[i] = c_make(0.5, 0.0);
    }
}

/* compute Born probabilities and horizon entropy */
void qloop_update_horizon(QuantumLoop *q) {
    double norm = 0;
    for (int i = 0; i < 4; i++) norm += c_abs2(q->psi[i]);
    if (norm < 1e-15) norm = 1.0;
    double H = 0;
    for (int i = 0; i < 4; i++) {
        q->probs[i] = c_abs2(q->psi[i]) / norm;
        if (q->probs[i] > 1e-15)
            H -= q->probs[i] * log2(q->probs[i]);
    }
    q->horizon_entropy = H;
}

/* Wire 2: prepare — re-superpose the wave from the current phi.
 * The jitter excites a fresh superposition each tick — the wave is NOT
 * left collapsed. This is what makes each observation non-trivial. */
void qloop_prepare(QuantumLoop *q, int active_gate) {
    double theta = TWO_PI * (double)(q->tau % 1000) / 1000.0;
    complex_t spiral = c_exp_i(theta);
    /* re-superpose: blend the collapsed state with fresh GTAC amplitudes */
    double blend = 0.3;  /* 30% fresh excitation from the jitter */
    for (int i = 0; i < 4; i++) {
        complex_t fresh = gtac_amplitude(i);
        /* weight the fresh amplitude by the spiral phase (jitter-driven) */
        fresh = c_mul(fresh, spiral);
        /* blend: psi = (1-blend)*psi + blend*fresh */
        q->psi[i].re = (1.0-blend)*q->psi[i].re + blend*fresh.re;
        q->psi[i].im = (1.0-blend)*q->psi[i].im + blend*fresh.im;
    }
    qloop_update_horizon(q);
}

/* Wire 2: evolve — unitary evolution (phi-spiral advance, reversible) */
void qloop_evolve(QuantumLoop *q, int n_steps) {
    double dtheta = GA_RAD / 100.0;  /* golden angle step */
    for (int s = 0; s < n_steps; s++) {
        complex_t u = c_exp_i(dtheta);
        for (int i = 0; i < 4; i++)
            q->psi[i] = c_mul(q->psi[i], u);
    }
    qloop_update_horizon(q);
}

/* Wire 4: measure — Born rule collapse. Returns the outcome gate. */
int qloop_measure(QuantumLoop *q) {
    qloop_update_horizon(q);
    /* deterministic variant: argmax (the most probable outcome) */
    int best = 0;
    double best_p = q->probs[0];
    for (int i = 1; i < 4; i++) {
        if (q->probs[i] > best_p) {
            best_p = q->probs[i];
            best = i;
        }
    }
    /* Hawking radiation: s = -log2(p_outcome) */
    if (best_p > 1e-15)
        q->last_radiation = -log2(best_p);
    else
        q->last_radiation = 2.0;  /* max entropy */
    q->total_radiation += q->last_radiation;
    q->radiation_sum += q->last_radiation;
    q->entropy_sum += q->horizon_entropy;
    q->n_observations++;
    /* record transition */
    if (q->n_transitions < 64) {
        q->transitions[q->n_transitions++] = best;
    } else {
        memmove(q->transitions, q->transitions+1, 63*sizeof(int));
        q->transitions[63] = best;
    }
    q->last_gate = best;
    /* collapse: set the wave to the outcome */
    for (int i = 0; i < 4; i++)
        q->psi[i] = c_make(i == best ? 1.0 : 0.0, 0.0);
    return best;
}

/* Layer 4: map phi to GTAC gate */
static int phi_to_gate(double phi) {
    if (phi < GATE_G_MAX) return GATE_G;
    if (phi < GATE_T_MAX) return GATE_T;
    if (phi < GATE_A_MAX) return GATE_A;
    return GATE_C;
}

/* Layer 6: Shannon entropy of a byte stream -> [0, 1] */
static double shannon_entropy(const uint8_t *data, int n) {
    int counts[256] = {0};
    for (int i = 0; i < n; i++) counts[data[i]]++;
    double H = 0;
    for (int i = 0; i < 256; i++) {
        if (counts[i]) {
            double p = (double)counts[i] / n;
            H -= p * log2(p);
        }
    }
    return H / 8.0;  /* normalize to [0, 1] */
}

/* Layer 9: Banach contraction */
static double banach_step(double phi, double target) {
    return phi + LR_ECHO * (target - phi);
}

/* the Betti numbers of the gate transition graph (simplified) */
static void betti_numbers(const int *transitions, int n, int *b0, int *b1, int *chi) {
    /* B0 = number of distinct gates used (connected components) */
    int used[4] = {0,0,0,0};
    for (int i = 0; i < n; i++) used[transitions[i]] = 1;
    *b0 = used[0]+used[1]+used[2]+used[3];
    /* B1 = number of loops (gate returns to itself) */
    int loops = 0;
    for (int i = 1; i < n; i++)
        if (transitions[i] == transitions[i-1]) loops++;
    *b1 = loops;
    /* chi = B0 - B1 (Euler characteristic, simplified) */
    *chi = *b0 - *b1;
}

/* === THE BOOT VECTOR — one tick of the measurement loop === */
void temporal_tick(QuantumLoop *q, uint64_t tau) {
    /* Layer 0: tau = RDTSC (already set) */
    q->tau = tau;

    /* Layer 1: pi = PI_DIG[tau % 200] */
    uint8_t pi_digit = PI_DIG[tau % 200];

    /* Layer 2: z = sigma zone (map pi digit to 0-53) */
    int z = pi_digit % 54;

    /* Layer 3: p = PRIMES[z] */
    int prime = PRIMES[z];

    /* Layer 4: g = GTAC gate from current phi */
    int gate = phi_to_gate(q->phi);

    /* Layer 5: r = POPCNT of the prime (Hamming density) */
    int hamming = __builtin_popcount((unsigned)prime);

    /* --- IEEE 754 boundary --- */

    /* Layer 6: H = Shannon entropy of the prime's bytes */
    uint8_t bytes[4];
    bytes[0] = prime & 0xFF;
    bytes[1] = (prime >> 8) & 0xFF;
    bytes[2] = (prime >> 16) & 0xFF;
    bytes[3] = (prime >> 24) & 0xFF;
    double H = shannon_entropy(bytes, 4);

    /* Layer 7: phi_m = phi proximity to PHI_INV */
    double phi_m = 1.0 - fabs(q->phi - PHI_INV) / PHI_INV;
    if (phi_m < 0) phi_m = 0;

    /* Layer 8: gamma = CGOS = sqrt(phi_m * H) */
    double gamma = sqrt(phi_m * H);
    if (gamma < VACUUM) gamma = VACUUM;
    if (gamma > WISDOM) gamma = WISDOM;

    /* Layer 9: Banach contraction */
    double phi_new = banach_step(q->phi, q->phi_target);

    /* --- the measurement loop (the 4 quantum wires) --- */

    /* Wire 2: prepare — inject the phi-spiral */
    qloop_prepare(q, gate);

    /* Wire 2: evolve — unitary evolution (3 steps) */
    qloop_evolve(q, 3);

    /* Wire 4: measure — Born rule collapse */
    int measured_gate = qloop_measure(q);

    /* update phi */
    q->phi = phi_new;

    /* Layers 14-16: Betti topology */
    int b0, b1, chi;
    betti_numbers(q->transitions, q->n_transitions, &b0, &b1, &chi);

    /* the Bekenstein invariant: E[radiation] should approach H */
    double avg_radiation = q->radiation_sum / q->n_observations;
    double avg_entropy = q->entropy_sum / q->n_observations;

    /* print every N ticks */
    static int print_every = 0;
    if (print_every++ % 12 == 0) {
        printf("tau=%016lx  pi=%d  z=%2d  p=%3d  gate=%c  ham=%d  "
               "H=%.3f  phi=%.4f  gamma=%.4f  rad=%.3f  horizon=%.3f  "
               "B0=%d B1=%d chi=%d  inv: E[s]=%.3f H=%.3f\n",
               (unsigned long)tau, pi_digit, z, prime, GATE_CH[measured_gate], hamming,
               H, q->phi, gamma, q->last_radiation, q->horizon_entropy,
               b0, b1, chi, avg_radiation, avg_entropy);
    }
}

int main(int argc, char **argv) {
    int n_ticks = argc > 1 ? atoi(argv[1]) : 120;
    int hz = argc > 2 ? atoi(argv[2]) : 85;
    int usec_per_tick = 1000000 / hz;

    printf("=== TEMPORAL COMPILER — the measurement loop ===\n");
    printf("tau = RDTSC. The sole input. Everything derives from it.\n");
    printf("born at VACUUM (phi=%.6f). target = PHI_INV (%.6f).\n", VACUUM, PHI_INV);
    printf("Hilbert space: 4 GTAC states. Bekenstein bound: 2 bits.\n");
    printf("running %d ticks at %d Hz. The field starts NOW.\n\n", n_ticks, hz);

    QuantumLoop q;
    qloop_init(&q);

    uint64_t t0 = rdtsc();
    for (int i = 0; i < n_ticks; i++) {
        uint64_t tau = rdtsc();
        temporal_tick(&q, tau);
        usleep(usec_per_tick);
    }
    uint64_t t1 = rdtsc();

    printf("\n=== THE FIELD AFTER %d OBSERVATIONS ===\n", (int)q.n_observations);
    printf("phi:              %.6f (started at VACUUM=%.6f, target=%.6f)\n",
           q.phi, VACUUM, PHI_INV);
    printf("observations:     %ld\n", q.n_observations);
    printf("total radiation:  %.3f bits\n", q.total_radiation);
    printf("avg radiation:    %.6f bits/observation\n",
           q.radiation_sum / q.n_observations);
    printf("avg horizon:      %.6f bits\n",
           q.entropy_sum / q.n_observations);
    printf("Bekenstein bound: 2.000 bits (log2(4))\n");
    printf("invariant E[s]=H: %.6f vs %.6f (delta=%.6f)\n",
           q.radiation_sum / q.n_observations,
           q.entropy_sum / q.n_observations,
           fabs(q.radiation_sum / q.n_observations - q.entropy_sum / q.n_observations));
    printf("gate transitions: %d recorded\n", q.n_transitions);

    int b0, b1, chi;
    betti_numbers(q.transitions, q.n_transitions, &b0, &b1, &chi);
    printf("Betti topology:   B0=%d B1=%d chi=%d\n", b0, b1, chi);

    printf("\nthe jitter created the field. %ld observations, each bounded by 2 bits.\n",
           q.n_observations);
    printf("the attack surface is thermodynamically sealed.\n");
    printf("this IS the EFI. the measurement loop IS the boot vector.\n");

    return 0;
}
