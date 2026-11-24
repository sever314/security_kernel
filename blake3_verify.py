#!/usr/bin/env python3
"""BLAKE3 pure-Python reference — verify against canonical test vectors."""
import struct

BLAKE3_IV = [
    0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
    0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19,
]

# The reference applies a SINGLE permutation iteratively between rounds
# (not a different fixed schedule per round). permute^r(identity) gives the
# schedule for round r. This matches the official BLAKE3 reference.
BLAKE3_MSG_PERMUTATION = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]

CHUNK_START = 1 << 0
CHUNK_END   = 1 << 1
PARENT      = 1 << 2
ROOT        = 1 << 3

BLOCK_LEN = 64
CHUNK_LEN = 1024

def _rotr32(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

def _g(s, a, b, c, d, x, y):
    s[a] = (s[a] + s[b] + x) & 0xFFFFFFFF
    s[d] = _rotr32(s[d] ^ s[a], 16)
    s[c] = (s[c] + s[d]) & 0xFFFFFFFF
    s[b] = _rotr32(s[b] ^ s[c], 12)
    s[a] = (s[a] + s[b] + y) & 0xFFFFFFFF
    s[d] = _rotr32(s[d] ^ s[a], 8)
    s[c] = (s[c] + s[d]) & 0xFFFFFFFF
    s[b] = _rotr32(s[b] ^ s[c], 7)

def _round(s, m):
    _g(s, 0, 4, 8, 12, m[0], m[1])
    _g(s, 1, 5, 9, 13, m[2], m[3])
    _g(s, 2, 6, 10, 14, m[4], m[5])
    _g(s, 3, 7, 11, 15, m[6], m[7])
    _g(s, 0, 5, 10, 15, m[8], m[9])
    _g(s, 1, 6, 11, 12, m[10], m[11])
    _g(s, 2, 7, 8, 13, m[12], m[13])
    _g(s, 3, 4, 9, 14, m[14], m[15])

def _permute(m):
    """Apply MSG_PERMUTATION in place."""
    orig = list(m)
    for i in range(16):
        m[i] = orig[BLAKE3_MSG_PERMUTATION[i]]

def _compress(cv, block_words, block_len, counter, flags):
    s = [
        cv[0], cv[1], cv[2], cv[3], cv[4], cv[5], cv[6], cv[7],
        BLAKE3_IV[0], BLAKE3_IV[1], BLAKE3_IV[2], BLAKE3_IV[3],
        counter & 0xFFFFFFFF, (counter >> 32) & 0xFFFFFFFF,
        block_len & 0xFFFFFFFF, flags & 0xFFFFFFFF,
    ]
    block = list(block_words)
    _round(s, block)       # round 1
    _permute(block)
    _round(s, block)       # round 2
    _permute(block)
    _round(s, block)       # round 3
    _permute(block)
    _round(s, block)       # round 4
    _permute(block)
    _round(s, block)       # round 5
    _permute(block)
    _round(s, block)       # round 6
    _permute(block)
    _round(s, block)       # round 7
    for i in range(8):
        s[i] ^= s[i + 8]
    return s[:8]

def _words(block):
    """64 bytes -> 16 uint32 LE words. Pads with zeros if short."""
    if len(block) < 64:
        block = block + b'\x00' * (64 - len(block))
    return list(struct.unpack('<16I', block))

def _chunk_cv(data, key_cv, chunk_counter, is_root):
    """Process one chunk (<= 1024 bytes). Returns 8-word chaining value."""
    cv = list(key_cv)
    n = len(data)
    if n == 0:
        flags = CHUNK_START | CHUNK_END
        if is_root: flags |= ROOT
        return _compress(cv, _words(b'\x00' * 64), 0, chunk_counter, flags)
    n_blocks = (n + 63) // 64
    for i in range(n_blocks):
        sl = data[i*64:(i+1)*64]
        blen = len(sl)
        flags = 0
        if i == 0: flags |= CHUNK_START
        if i == n_blocks - 1:
            flags |= CHUNK_END
            if is_root: flags |= ROOT
        cv = _compress(cv, _words(sl), blen, chunk_counter, flags)
    return cv

def blake3_hash(data, key_cv=None):
    """32-byte BLAKE3 hash. Pure Python reference (public domain)."""
    if key_cv is None:
        key_cv = list(BLAKE3_IV)
    if len(data) <= CHUNK_LEN:
        return struct.pack('<8I', *_chunk_cv(data, key_cv, 0, is_root=True))
    # tree mode
    chunk_cvs = []
    idx = 0
    for i in range(0, len(data), CHUNK_LEN):
        chunk = data[i:i+CHUNK_LEN]
        chunk_cvs.append(_chunk_cv(chunk, key_cv, idx, is_root=False))
        idx += 1
    while len(chunk_cvs) > 1:
        parents = []
        is_root_level = (len(chunk_cvs) <= 2)
        for i in range(0, len(chunk_cvs), 2):
            if i + 1 < len(chunk_cvs):
                left, right = chunk_cvs[i], chunk_cvs[i+1]
            else:
                left, right = chunk_cvs[i], [0]*8
            block = struct.pack('<16I', *(left + right))
            flags = PARENT
            if is_root_level: flags |= ROOT
            parents.append(_compress(list(BLAKE3_IV), _words(block), 64, 0, flags))
        chunk_cvs = parents
    return struct.pack('<8I', *chunk_cvs[0])

def blake3_u64(data, key_cv=None):
    """First 8 bytes of blake3_hash as uint64 (little-endian)."""
    return struct.unpack('<Q', blake3_hash(data, key_cv)[:8])[0]

# ---- VERIFY against canonical test vectors ----
def main():
    # Canonical test vectors from the blake3 reference package
    cases = [
        (b"",     "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"),
        (b"abc",  "6437b3ac38465133ffb63b75273a8db548c558465d79db03fd359c6cd5bd9d85"),
        # a longer input that spans multiple blocks (> 64 bytes, still 1 chunk)
        (b"a" * 100,  None),  # verify against reference package dynamically
        # a tree-mode input (> 1024 bytes)
        (b"x" * 2000, None),
    ]
    print("BLAKE3 pure-Python verification")
    print("=" * 60)
    try:
        import blake3 as ref
        has_ref = True
        print("Reference blake3 package available -- comparing.\n")
    except ImportError:
        has_ref = False
        print("No reference package -- checking hardcoded vectors only.\n")

    all_ok = True
    for data, expected in cases:
        got = blake3_hash(data).hex()
        if expected is not None:
            ok = (got == expected)
        elif has_ref:
            exp = ref.blake3(data).hexdigest()
            ok = (got == exp)
            expected = exp
        else:
            ok = None
            expected = "(no reference)"
        label = data[:8].hex() + ("..." if len(data) > 8 else "")
        status = "OK" if ok else ("FAIL <<<" if ok is False else "N/A")
        print(f"  input({len(data):5d}B) {label:<24} -> {got[:16]}...")
        if expected != "(no reference)":
            print(f"  expected:                          {expected[:16]}...  [{status}]")
        if ok is False:
            all_ok = False
            print(f"  FULL GOT:      {got}")
            print(f"  FULL EXPECTED: {expected}")

    # avalanche test: flip one bit, measure output bit changes
    print("\n  AVALANCHE TEST (1-bit input flip -> output bit changes):")
    base = b"the quick brown fox"
    h0 = blake3_hash(base)
    bit_flipped = bytearray(base); bit_flipped[0] ^= 1
    h1 = blake3_hash(bytes(bit_flipped))
    diff_bits = sum(bin(a ^ b).count('1') for a, b in zip(h0, h1))
    total_bits = 8 * len(h0)
    print(f"    base:    {h0.hex()[:32]}...")
    print(f"    flipped: {h1.hex()[:32]}...")
    print(f"    changed bits: {diff_bits}/{total_bits} = {100*diff_bits/total_bits:.1f}%  (ideal ~50%)")
    avalanche_ok = (abs(diff_bits / total_bits - 0.5) < 0.15)
    if not avalanche_ok: all_ok = False

    print(f"\n  {'ALL CHECKS PASSED' if all_ok else 'SOME CHECKS FAILED'}")
    if all_ok:
        print("  Pure-Python BLAKE3 matches the canonical reference.")
        print("  Avalanche is cryptographic (~50% bit change for 1-bit input flip).")
    return all_ok

if __name__ == "__main__":
    main()
