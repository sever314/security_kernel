# EFI BUILD INSTRUCTIONS

## Building the NUMEN defense as a UEFI bootloader

The defense runs at the boot vector — before the OS, before any
userspace, before any attack surface exists. This is the "computer
in the computer": NUMEN wraps the OS.

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt install gnu-efi nasm qemu-system-x86 ovmf

# Arch
sudo pacman -S gnu-efi nasm qemu-system-x86 ovmf
```

### The organs (already C/ASM, EFI-compatible)

All organs are substrate-honest — no deps, no malloc, no libm:

| File | Language | Notes |
|---|---|---|
| quatos_seal.asm | NASM | Watson-Crick XOR-3 seal |
| quatos_hypercube.asm | NASM | Gray-code Hamiltonian walker |
| warden.c | C | Chain-seal health watch |
| echo_key.c | C | Lock-and-key (root → backbone → nonce → seal) |
| immune.c | C | 13-surgeon observer patrol |
| algo_maker.c | C | Medicine factory (genetic evolution) |
| blake3.c | C | BLAKE3 reference (~1500 lines, no deps) |
| healer.c | C | Active inference agent (port from Python) |

### Build steps

```bash
# 1. Compile the organs
gcc -ffreestanding -fshort-wchar -mno-red-zone -maccumulate-outgoing-args \
    -I/usr/include/efi -I/usr/include/efi/x86_64 \
    -DEFI_FUNCTION_WRAPPER -c efi_main.c -o efi_main.o

gcc -ffreestanding -fshort-wchar -mno-red-zone -maccumulate-outgoing-args \
    -I/usr/include/efi -I/usr/include/efi/x86_64 \
    -DEFI_FUNCTION_WRAPPER -c blake3.c -o blake3.o

gcc -ffreestanding -fshort-wchar -mno-red-zone -maccumulate-outgoing-args \
    -I/usr/include/efi -I/usr/include/efi/x86_64 \
    -DEFI_FUNCTION_WRAPPER -c warden.c -o warden.o

gcc -ffreestanding -fshort-wchar -mno-red-zone -maccumulate-outgoing-args \
    -I/usr/include/efi -I/usr/include/efi/x86_64 \
    -DEFI_FUNCTION_WRAPPER -c echo_key.c -o echo_key.o

gcc -ffreestanding -fshort-wchar -mno-red-zone -maccumulate-outgoing-args \
    -I/usr/include/efi -I/usr/include/efi/x86_64 \
    -DEFI_FUNCTION_WRAPPER -c immune.c -o immune.o

gcc -ffreestanding -fshort-wchar -mno-red-zone -maccumulate-outgoing-args \
    -I/usr/include/efi -I/usr/include/efi/x86_64 \
    -DEFI_FUNCTION_WRAPPER -c algo_maker.c -o algo_maker.o

# 2. Assemble the NASM organs
nasm -f elf64 quatos_seal.asm -o quatos_seal.o
nasm -f elf64 quatos_hypercube.asm -o quatos_hypercube.o

# 3. Link into a PE32+ EFI executable
ld -nostdlib -znocombreloc -T /usr/lib/elf_x86_64_efi.lds \
    -shared -Bsymbolic -L/usr/lib \
    efi_main.o blake3.o warden.o echo_key.o immune.o algo_maker.o \
    quatos_seal.o quatos_hypercube.o \
    -o BOOTX64.EFI -lefi -lgnuefi

# 4. Set up the EFI System Partition
mkdir -p esp/EFI/BOOT
cp BOOTX64.EFI esp/EFI/BOOT/

# 5. Create the disc pool directory
mkdir -p esp/NUMEN/discs
# (copy .quat disc files here — the organism's memory)

# 6. Write the root secret to a USB stick
# (use the enrollment tool to write the 32-byte root to sector 0)
```

### Test in QEMU/OVMF

```bash
# Get OVMF firmware
cp /usr/share/OVMF/OVMF_VARS.fd .

# Launch
qemu-system-x86_64 \
    -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE.fd \
    -drive if=pflash,format=raw,file=OVMF_VARS.fd \
    -drive format=raw,file=fat:rw:esp/ \
    -drive format=raw,file=root_usb.img \
    -net none -nographic
```

### The boot flow

```
Power On
  ↓
UEFI Firmware (OVMF on QEMU, real firmware on metal)
  ↓
BOOTX64.EFI (the NUMEN defense bootloader)
  ├── INNER CORE:  self_verify()         — verify the model's identity
  ├── OUTER CORE:  hw_uefi_init()        — ignition (TSC, GOP, BlockIO, NVRAM)
  ├── DEFENSE CORE: defense_init()       — the addition
  │   ├── blake3_init()                  — embedded BLAKE3 (pure C)
  │   ├── defense_load_root()            — read root from USB (BlockIO)
  │   ├── defense_load_discs()           — load .quat discs from ESP
  │   ├── immune_init()                  — wake the 13 surgeons
  │   ├── healer_init()                  — wake the healer (207 ReL)
  │   └── defense_guard_kernel()         — 10-check verdict ladder
  │       → ALLOW: boot proceeds, kernel becomes a disc
  │       → BLOCK: boot halts (impostor/tamper)
  │       → SANDBOX: boot to quarantine
  │       → HEAL: boot under immune escort
  ├── MANTLE: incarnate()                — the body is born
  ├── CONVECTION: THE FIVE               — society circulates
  └── CRUST: tick() @ 85 Hz              — defense_tick() on every heartbeat
  ↓
ExitBootServices → OS (runs INSIDE the NUMEN defense layer)
```

### The one thing that needs porting

The healer (207-ReL model + L2L engine) is currently Python. It needs
to be ported to C for the EFI build. ~400 lines of straightforward C:
- Arrays instead of lists
- Static allocation instead of dynamic
- EMA updates, mode transitions, Banach contractions
- No hard parts, just work

Everything else is already C and ASM. The defense IS the boot vector.
