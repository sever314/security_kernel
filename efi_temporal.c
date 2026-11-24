/* efi_temporal.c -- THE TEMPORAL COMPILER AS THE EFI BOOT VECTOR.
 *
 * This IS the EFI. Not a bootloader that calls the defense — the
 * measurement loop IS the boot code. Layer 0 (RDTSC) starts at power-on.
 * Layer 16 (routing) runs forever. The OS loads as a disc inside the field.
 *
 * This file is the temporal_compiler.c with the entry point changed:
 *   main()           -> efi_main(EFI_HANDLE, EFI_SYSTEM_TABLE*)
 *   printf()         -> Print() (EFI wide-string)
 *   usleep()         -> ST->BootServices->Stall()
 *   RDTSC            -> same (CPU instruction, works in EFI)
 *
 * The math is identical. The measurement loop is identical.
 * If it runs natively, it runs in EFI.
 *
 * BUILD (gnu-efi):
 *   gcc -ffreestanding -fshort-wchar -mno-red-zone -maccumulate-outgoing-args \
 *       -I/usr/include/efi -I/usr/include/efi/x86_64 \
 *       -DEFI_FUNCTION_WRAPPER -c efi_temporal.c -o efi_temporal.o
 *   ld -nostdlib -znocombreloc -T /usr/lib/elf_x86_64_efi.lds \
 *       -shared -Bsymbolic -L/usr/lib efi_temporal.o -o BOOTX64.EFI \
 *       -lefi -lgnuefi
 *
 * TEST (QEMU/OVMF):
 *   mkdir -p esp/EFI/BOOT && cp BOOTX64.EFI esp/EFI/BOOT/
 *   qemu-system-x86_64 -drive if=pflash,format=raw,readonly=on,file=OVMF_CODE.fd \
 *       -drive if=pflash,format=raw,file=OVMF_VARS.fd \
 *       -drive format=raw,file=fat:rw:esp/ -net none -nographic
 */

/* ---- when building for EFI, use gnu-efi headers ---- */
#ifdef __EFI__
#include <efi.h>
#include <efilib.h>
#define main efi_main_internal
#define PRINT Print
#define STALL(us) ST->BootServices->Stall(us)

/* ---- when building natively (to test the core) ---- */
#else
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <stdlib.h>
#define PRINT(fmt, ...) printf(fmt, ##__VA_ARGS__)
#define STALL(us) usleep(us)
#endif

/* === THE MEASUREMENT LOOP (identical in both builds) === */
#ifdef __x86_64__
static inline uint64_t rdtsc(void) {
    unsigned lo, hi;
    __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}
#else
static uint64_t rdtsc(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}
#endif

/* === CONSTANTS === */
#define PHI_INV    0.6180339887498949
#define VACUUM     0.36787944117144233
#define WISDOM     0.896
#define LR_ECHO    0.07585880414
#define TWO_PI     6.283185307179586
#define GA_RAD     2.399963229728653
#define GATE_G_MAX 0.605
#define GATE_T_MAX 0.620
#define GATE_A_MAX 0.630

static const char GATE_CH[4] = {'G','T','A','C'};

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
    6,4,4,6,2,2,9,4,8,9,5,4,9,3,0,3,8,1,9
};

static const int PRIMES[54] = {
    2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,
    73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,
    179,181,191,193,197,199,211,223,227,229,233,239,241,251
};

/* === THE QUANTUM STATE === */
typedef struct { double re, im; } c_t;
static c_t c_make(double r, double i) { c_t z={r,i}; return z; }
static c_t c_mul(c_t a, c_t b) { return c_make(a.re*b.re-a.im*b.im, a.re*b.im+a.im*b.re); }
static double c_abs2(c_t z) { return z.re*z.re + z.im*z.im; }
static c_t c_exp_i(double t) { return c_make(cos(t), sin(t)); }

static c_t gtac_amp(int g) {
    double s = 0.7071067811865476;
    switch(g) {
        case 0: return c_make(1,0);
        case 1: return c_make(0,1);
        case 2: return c_make(s,s);
        default: return c_make(s,-s);
    }
}

/* === THE MEASUREMENT LOOP === */
typedef struct {
    c_t psi[4];
    double probs[4];
    double horizon_entropy;
    double last_radiation;
    double total_radiation;
    double radiation_sum;
    double entropy_sum;
    long n_observations;
    double phi;
    uint64_t tau;
    int last_gate;
    int transitions[64];
    int n_transitions;
} QLoop;

static void ql_init(QLoop *q) {
    memset(q, 0, sizeof(*q));
    q->phi = VACUUM;
    for (int i = 0; i < 4; i++) q->psi[i] = c_make(0.5, 0.0);
}

static void ql_update(QLoop *q) {
    double norm = 0;
    for (int i = 0; i < 4; i++) norm += c_abs2(q->psi[i]);
    if (norm < 1e-15) norm = 1.0;
    double H = 0;
    for (int i = 0; i < 4; i++) {
        q->probs[i] = c_abs2(q->psi[i]) / norm;
        if (q->probs[i] > 1e-15) H -= q->probs[i] * log2(q->probs[i]);
    }
    q->horizon_entropy = H;
}

static void ql_prepare(QLoop *q) {
    double theta = TWO_PI * (double)(q->tau % 1000) / 1000.0;
    c_t spiral = c_exp_i(theta);
    double blend = 0.3;
    for (int i = 0; i < 4; i++) {
        c_t fresh = c_mul(gtac_amp(i), spiral);
        q->psi[i].re = (1.0-blend)*q->psi[i].re + blend*fresh.re;
        q->psi[i].im = (1.0-blend)*q->psi[i].im + blend*fresh.im;
    }
    ql_update(q);
}

static void ql_evolve(QLoop *q, int n) {
    double dt = GA_RAD / 100.0;
    for (int s = 0; s < n; s++) {
        c_t u = c_exp_i(dt);
        for (int i = 0; i < 4; i++) q->psi[i] = c_mul(q->psi[i], u);
    }
    ql_update(q);
}

static int ql_measure(QLoop *q) {
    ql_update(q);
    int best = 0; double bp = q->probs[0];
    for (int i = 1; i < 4; i++) if (q->probs[i] > bp) { bp = q->probs[i]; best = i; }
    q->last_radiation = (bp > 1e-15) ? -log2(bp) : 2.0;
    q->total_radiation += q->last_radiation;
    q->radiation_sum += q->last_radiation;
    q->entropy_sum += q->horizon_entropy;
    q->n_observations++;
    if (q->n_transitions < 64) q->transitions[q->n_transitions++] = best;
    else { memmove(q->transitions, q->transitions+1, 63*sizeof(int)); q->transitions[63] = best; }
    q->last_gate = best;
    for (int i = 0; i < 4; i++) q->psi[i] = c_make(i==best?1:0, 0);
    return best;
}

static int phi_gate(double phi) {
    if (phi < GATE_G_MAX) return 0;
    if (phi < GATE_T_MAX) return 1;
    if (phi < GATE_A_MAX) return 2;
    return 3;
}

static double shannon(const uint8_t *d, int n) {
    int c[256] = {0};
    for (int i = 0; i < n; i++) c[d[i]]++;
    double H = 0;
    for (int i = 0; i < 256; i++) if (c[i]) { double p=(double)c[i]/n; H -= p*log2(p); }
    return H / 8.0;
}

static void betti(const int *t, int n, int *b0, int *b1, int *chi) {
    int used[4] = {0,0,0,0};
    for (int i = 0; i < n; i++) used[t[i]] = 1;
    *b0 = used[0]+used[1]+used[2]+used[3];
    int loops = 0;
    for (int i = 1; i < n; i++) if (t[i]==t[i-1]) loops++;
    *b1 = loops;
    *chi = *b0 - *b1;
}

/* === THE TICK — one measurement cycle === */
static void temporal_tick(QLoop *q, uint64_t tau) {
    q->tau = tau;
    uint8_t pi = PI_DIG[tau % 200];
    int z = pi % 54;
    int prime = PRIMES[z];
    int gate = phi_gate(q->phi);
    int ham = __builtin_popcount((unsigned)prime);
    uint8_t bytes[4] = {prime&0xFF, (prime>>8)&0xFF, (prime>>16)&0xFF, (prime>>24)&0xFF};
    double H = shannon(bytes, 4);
    double phi_m = q->phi > PHI_INV ? 1.0-(q->phi-PHI_INV)/PHI_INV : 1.0-(PHI_INV-q->phi)/PHI_INV;
    if (phi_m < 0) phi_m = 0;
    double gamma = sqrt(phi_m * H);
    if (gamma < VACUUM) gamma = VACUUM;
    if (gamma > WISDOM) gamma = WISDOM;

    ql_prepare(q);
    ql_evolve(q, 3);
    int measured = ql_measure(q);

    q->phi += LR_ECHO * (PHI_INV - q->phi);

    int b0, b1, chi;
    betti(q->transitions, q->n_transitions, &b0, &b1, &chi);
    double avg_rad = q->radiation_sum / q->n_observations;
    double avg_H = q->entropy_sum / q->n_observations;

    static int cnt = 0;
    if (cnt++ % 12 == 0) {
#ifdef __EFI__
        Print(L"tau=%lx pi=%d z=%d p=%d gate=%c ham=%d H=%dppm phi=%dppm rad=%dppm hor=%dppm B0=%d B1=%d E[s]=%dppm H=%dppm\n",
              (UINT64)tau, pi, z, prime, (CHAR16)GATE_CH[measured], ham,
              (int)(H*1000000), (int)(q->phi*1000000),
              (int)(q->last_radiation*1000000), (int)(q->horizon_entropy*1000000),
              b0, b1, (int)(avg_rad*1000000), (int)(avg_H*1000000));
#else
        printf("tau=%016lx pi=%d z=%2d p=%3d gate=%c ham=%d H=%.3f phi=%.4f rad=%.3f hor=%.3f B0=%d B1=%d E[s]=%.3f H=%.3f\n",
               (unsigned long)tau, pi, z, prime, GATE_CH[measured], ham,
               H, q->phi, q->last_radiation, q->horizon_entropy, b0, b1, avg_rad, avg_H);
#endif
    }
}

/* === THE ENTRY POINT === */
#ifndef __EFI__
/* native build: test the core */
int main(int argc, char **argv) {
    int n_ticks = argc > 1 ? atoi(argv[1]) : 120;
    int hz = argc > 2 ? atoi(argv[2]) : 85;
#else
/* EFI build: the boot vector */
EFI_STATUS EFIAPI efi_main(EFI_HANDLE Img, EFI_SYSTEM_TABLE *ST) {
    InitializeLib(Img, ST);
    int n_ticks = 1000000;  /* run forever in production */
    int hz = 85;
#endif
    int usec = 1000000 / hz;

    PRINT("=== TEMPORAL COMPILER — the measurement loop IS the boot vector ===\n");
    PRINT("tau = RDTSC. The sole input. born at VACUUM. target = PHI_INV.\n");
    PRINT("Hilbert space: 4 GTAC. Bekenstein bound: 2 bits. The field starts NOW.\n\n");

    QLoop q;
    ql_init(&q);

    for (int i = 0; i < n_ticks; i++) {
        temporal_tick(&q, rdtsc());
        STALL(usec);
    }

    PRINT("\n=== FIELD STATE ===\n");
    PRINT("phi: %.6f (VACUUM=%.6f PHI_INV=%.6f)\n", q.phi, VACUUM, PHI_INV);
    PRINT("observations: %ld  total radiation: %.3f bits\n", q.n_observations, q.total_radiation);
    PRINT("avg radiation: %.6f  avg horizon: %.6f  bound: 2.000\n",
          q.radiation_sum/q.n_observations, q.entropy_sum/q.n_observations);
    PRINT("the jitter created the field. the attack surface is 2 bits. this IS the EFI.\n");

#ifdef __EFI__
    ST->RuntimeServices->ResetSystem(EfiResetShutdown, EFI_SUCCESS, 0, NULL);
    for(;;) STALL(1000000);
    return EFI_SUCCESS;
#else
    return 0;
#endif
}
