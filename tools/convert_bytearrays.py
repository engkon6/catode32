r"""
Convert bytearray([0x..., ...]) literals to b"\x..." byte string literals
in MicroPython asset files, so they can be stored in flash when frozen.

Run from the project root:
    python3 tools/convert_bytearrays.py [--dry-run]
"""

import re
import sys
import os

ASSET_FILES = [
    "src/assets/boot_img.py",
    "src/assets/character.py",
    "src/assets/effects.py",
    "src/assets/furniture.py",
    "src/assets/icons.py",
    "src/assets/items.py",
    "src/assets/minigame_assets.py",
    "src/assets/minigame_character.py",
    "src/assets/nature.py",
    "src/assets/store.py",
]

# Matches bytearray([...]) across single or multiple lines.
# [^\]]* matches anything except the closing bracket (works across newlines).
PATTERN = re.compile(r'bytearray\(\[([^\]]*)\]\)')


def bytearray_to_literal(match):
    r"""Replace bytearray([0x..., ...]) with b"\x..." literal."""
    inner = match.group(1)
    # Extract all integer tokens (handles 0x hex and decimal)
    tokens = re.findall(r'0x[0-9a-fA-F]+|\d+', inner)
    values = [int(t, 0) for t in tokens]

    # Verify values are valid bytes
    for v in values:
        if not 0 <= v <= 255:
            raise ValueError(f"Value out of byte range: {v}")

    # Build b"..." literal, always using \x escapes for readability
    escaped = ''.join(f'\\x{v:02x}' for v in values)
    return f'b"{escaped}"'


def convert_file(path, dry_run=False):
    with open(path, 'r') as f:
        original = f.read()

    converted = PATTERN.sub(bytearray_to_literal, original)

    count = len(PATTERN.findall(original))
    if count == 0:
        print(f"  {path}: no bytearrays found, skipped")
        return 0

    # Verify: eval all matches in original and converted produce identical data
    orig_matches = PATTERN.findall(original)
    # Re-find in converted output using bytes literal pattern
    bytes_pattern = re.compile(r'b"((?:\\x[0-9a-fA-F]{2})*)"')
    conv_matches = bytes_pattern.findall(converted)

    if len(orig_matches) != len(conv_matches):
        raise RuntimeError(
            f"{path}: match count mismatch: {len(orig_matches)} original vs {len(conv_matches)} converted"
        )

    for i, (orig_inner, conv_escaped) in enumerate(zip(orig_matches, conv_matches)):
        tokens = re.findall(r'0x[0-9a-fA-F]+|\d+', orig_inner)
        orig_values = bytes([int(t, 0) for t in tokens])
        conv_values = bytes([int(conv_escaped[j*4+2:j*4+4], 16)
                             for j in range(len(conv_escaped) // 4)])
        if orig_values != conv_values:
            raise RuntimeError(f"{path}: data mismatch at match #{i}")

    if dry_run:
        print(f"  {path}: {count} conversions (dry run, not written)")
    else:
        with open(path, 'w') as f:
            f.write(converted)
        print(f"  {path}: {count} conversions written")

    return count


def main():
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        print("DRY RUN — no files will be modified\n")

    total = 0
    errors = []
    for path in ASSET_FILES:
        if not os.path.exists(path):
            print(f"  {path}: NOT FOUND, skipped")
            continue
        try:
            total += convert_file(path, dry_run=dry_run)
        except Exception as e:
            errors.append((path, str(e)))
            print(f"  {path}: ERROR — {e}")

    print(f"\n{'DRY RUN: would convert' if dry_run else 'Converted'} {total} bytearrays total")
    if errors:
        print(f"\n{len(errors)} file(s) had errors:")
        for path, msg in errors:
            print(f"  {path}: {msg}")
        sys.exit(1)


if __name__ == '__main__':
    main()
