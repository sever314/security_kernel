#!/bin/bash
# build_efi.sh -- build the temporal compiler as an EFI bootloader
#
# This IS the EFI. The measurement loop IS the boot vector.
#
# Prerequisites (Ubuntu/Debian):
#   sudo apt install gnu-efi gcc nasm qemu-system-x86 ovmf
#
# Usage:
#   ./build_efi.sh          # build the EFI binary
#   ./build_efi.sh test     # build + run in QEMU/OVMF
#   ./build_efi.sh native   # build + run natively (test the core without EFI)

set -e
cd "$(dirname "$0")"

MODE=${1:-native}

case "$MODE" in
    native)
        echo "=== NATIVE BUILD (test the core measurement loop) ==="
        echo "    This is the same code as the EFI, just compiled for Linux."
        echo "    The math is identical. If it runs here, it runs in EFI."
        echo ""
        gcc -O2 -o temporal_compiler_native efi_temporal.c -lm
        echo "BUILD OK. Running 120 ticks at 85 Hz..."
        echo ""
        ./temporal_compiler_native 120 85
        ;;

    test)
        echo "=== EFI BUILD + QEMU/OVMF TEST ==="
        # check prerequisites
        if [ ! -f /usr/include/efi/efi.h ]; then
            echo "ERROR: gnu-efi not installed. Run: sudo apt install gnu-efi"
            exit 1
        fi
        if ! command -v qemu-system-x86_64 &>/dev/null; then
            echo "ERROR: qemu not installed. Run: sudo apt install qemu-system-x86 ovmf"
            exit 1
        fi

        # compile for EFI
        echo "[1/3] Compiling efi_temporal.c for EFI..."
        gcc -ffreestanding -fshort-wchar -mno-red-zone -maccumulate-outgoing-args \
            -I/usr/include/efi -I/usr/include/efi/x86_64 \
            -DEFI_FUNCTION_WRAPPER -D__EFI__ \
            -c efi_temporal.c -o efi_temporal.o

        # link as PE32+ EFI binary
        echo "[2/3] Linking BOOTX64.EFI..."
        ld -nostdlib -znocombreloc -T /usr/lib/elf_x86_64_efi.lds \
            -shared -Bsymbolic -L/usr/lib \
            efi_temporal.o -o BOOTX64.EFI -lefi -lgnuefi

        # set up the ESP
        echo "[3/3] Setting up EFI System Partition..."
        mkdir -p esp/EFI/BOOT
        cp BOOTX64.EFI esp/EFI/BOOT/

        # find OVMF firmware
        OVMF_CODE=""
        for f in /usr/share/OVMF/OVMF_CODE.fd /usr/share/edk2-ovmf/OVMF_CODE.fd; do
            [ -f "$f" ] && OVMF_CODE="$f" && break
        done
        OVMF_VARS=""
        for f in /usr/share/OVMF/OVMF_VARS.fd /usr/share/edk2-ovmf/OVMF_VARS.fd; do
            [ -f "$f" ] && OVMF_VARS="$f" && break
        done

        if [ -z "$OVMF_CODE" ] || [ -z "$OVMF_VARS" ]; then
            echo "ERROR: OVMF firmware not found. Run: sudo apt install ovmf"
            exit 1
        fi

        # copy OVMF_VARS (writable copy)
        cp "$OVMF_VARS" OVMF_VARS.fd

        echo ""
        echo "=== BOOTING IN QEMU ==="
        echo "    The measurement loop starts at power-on."
        echo "    Layer 0 (RDTSC) begins. The field exists."
        echo ""
        qemu-system-x86_64 \
            -drive if=pflash,format=raw,readonly=on,file="$OVMF_CODE" \
            -drive if=pflash,format=raw,file=OVMF_VARS.fd \
            -drive format=raw,file=fat:rw:esp/ \
            -net none -nographic
        ;;

    efi)
        echo "=== EFI BUILD ONLY ==="
        if [ ! -f /usr/include/efi/efi.h ]; then
            echo "ERROR: gnu-efi not installed. Run: sudo apt install gnu-efi"
            exit 1
        fi
        gcc -ffreestanding -fshort-wchar -mno-red-zone -maccumulate-outgoing-args \
            -I/usr/include/efi -I/usr/include/efi/x86_64 \
            -DEFI_FUNCTION_WRAPPER -D__EFI__ \
            -c efi_temporal.c -o efi_temporal.o
        ld -nostdlib -znocombreloc -T /usr/lib/elf_x86_64_efi.lds \
            -shared -Bsymbolic -L/usr/lib \
            efi_temporal.o -o BOOTX64.EFI -lefi -lgnuefi
        echo "BUILD OK: BOOTX64.EFI"
        ls -la BOOTX64.EFI
        ;;

    *)
        echo "Usage: $0 {native|test|efi}"
        echo "  native  - build + run natively (test the core, no EFI needed)"
        echo "  test    - build EFI + run in QEMU/OVMF"
        echo "  efi     - build EFI binary only"
        exit 1
        ;;
esac
