# Project Crystal – 5D Optical Storage Core

Project Crystal is an experimental toolkit for simulating 5D optical data storage in software using Reed-Solomon error correction and a color-encoded "voxel" image format called `.cryst`.

The goal is to define a practical, open standard for mapping digital bits into a 2D RGB lattice that behaves like a 5D fused-silica storage medium: resilient to scratches, noise, and localized corruption while remaining fully decodable.

## Features

- **`.cryst` file format** for 5D-inspired optical storage frames (spec in `SPEC.md`).
- Reed-Solomon encoding/decoding over GF(2^8) (reference profile: RS(255,223)).
- Bitstream → 2‑bit symbols → RGB mapping (00/01/10/11 → black/red/green/blue).
- Row‑major 2D lattice layout with configurable width/height.
- Support for simulated "damage" (scratches, flicker, color drift) and error‑correcting recovery.

## How It Works (High Level)

1. You provide an input payload (text or binary).
2. The encoder splits it into fixed‑size chunks and applies Reed-Solomon to add parity symbols.
3. The protected bytes become a single bitstream, padded to a multiple of 2 bits.
4. Each 2‑bit symbol is mapped to one RGB pixel in a fixed color table (black/red/green/blue).
5. Pixels are laid out in a rectangular lattice and written as a lossless image plus header fields recorded in `.cryst`.
6. A decoder reverses this process and uses RS to reconstruct the original payload, even if a region of pixels is corrupted.

For exact rules (header fields, color table, layout, RS params), see `SPEC.md`.

## The `.cryst` Specification

The canonical `.cryst` spec for Project Crystal is defined in `SPEC.md`. It currently specifies:

- `magic` value (`"CRYST1"`) and versioning rules.
- Header fields for lattice dimensions, RS parameters, payload length, and flags.
- Reference Reed-Solomon profile `CRYST-RS255-223` (RS(255,223), 8‑bit symbols).
- Exact bit‑packing and RGB mapping for 2‑bit symbols.
- A normative decoding procedure and damage/error model.

Any implementation that follows `SPEC.md` should be able to read and write `.cryst` frames that are mutually compatible.

## Getting Started

### Requirements

- Python 3.10+
- `pip` for installing dependencies

Install dependencies:

```bash
pip install -r requirements.txt
```

### Basic Usage

Assuming the main interface is `crystal_interface.py`, a typical workflow might look like:

```bash
# Encode a file into a .cryst frame
python crystal_interface.py encode \
  --input input.bin \
  --output frame.cryst

# Decode a .cryst frame back to the original payload
python crystal_interface.py decode \
  --input frame.cryst \
  --output recovered.bin
```

You can then open the underlying lattice image in any image viewer to see your encoded data as a 2D color grid.

## License

This project is licensed under the Apache License 2.0 (see `LICENSE`).

Apache 2.0 is a permissive, business‑friendly license that:

- Allows commercial and non‑commercial use, modification, and distribution.
- Includes an explicit patent grant from contributors, with a termination clause if someone initiates patent litigation over the code.

If you prefer a strong copyleft model (where improvements must remain open), you could alternatively release under GPLv3, which requires modified versions to be distributed under the same license terms.

## Prior Art and Defensive Publication

This repository, together with `SPEC.md` and any linked "Project Crystal" blog posts or whitepapers, is intended to act as:

- Timestamped proof of creation for the `.cryst` format and its reference implementation (via public commits).
- Technical prior art describing "A Method for 5D Optical Data Error Correction using Reed-Solomon Algorithms," which can be cited during patent examination.

If you publish additional technical disclosures (e.g., on Medium or Substack), you can link them here to strengthen the defensive record.
