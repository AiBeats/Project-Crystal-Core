# Project Crystal – 5D Optical Storage File Specification (`.cryst`)

## 1. Overview

The **`.cryst`** format defines a virtual "5D optical storage frame" intended to simulate data written into fused silica using color- and polarization-based encoding. It is designed as a reference format for experimentation, teaching, and future physical implementations of 5D optical storage.

Core properties:  
- Container for a single encoded data payload (text or binary).
- Uses Reed-Solomon error correction over a binary message.
- Represents protected bits as a 2D RGB image, where colors simulate polarization states.
- Supports simulated damage and full data recovery via decoding.

This document specifies how raw data becomes a `.cryst` image and how a compliant decoder reconstructs the original payload.

***

## 2. High‑Level Data Flow

1. Input payload (UTF‑8 text or arbitrary bytes) is read.
2. Payload is segmented into Reed-Solomon codewords and encoded with parity symbols.
3. The resulting protected bitstream is padded to a multiple of 2 bits and mapped into 2‑bit symbols.
4. Each 2‑bit symbol is mapped to one RGB pixel.
5. Pixels are arranged into a 2D lattice and stored as an image (e.g., PNG) plus a small header/metadata block.
6. To decode, the process is reversed, and Reed-Solomon corrects symbol errors introduced by corruption.

***

## 3. File Container and MIME Type

A `.cryst` file is conceptually:

- A container holding:
  - A header with metadata (format version, dimensions, RS parameters, etc.).  
  - A raster image storing the voxel matrix as an RGB grid.

A minimal, interoperable implementation may serialize this as:

- A JSON or binary header, followed by  
- A lossless image (PNG) containing the lattice pixels.

Suggested (non‑binding) MIME type: `application/x-cryst`.

***

## 4. Header Specification

The header must provide enough information to reconstruct the bitstream from the pixels and configure the Reed-Solomon decoder.

Recommended fields:

- `magic`: fixed ASCII `"CRYST1"` (6 bytes) to identify the format.  
- `version`: 16‑bit unsigned int, starting at `0x0001`.  
- `width`: 32‑bit unsigned int, pixel width of the lattice.  
- `height`: 32‑bit unsigned int, pixel height of the lattice.  
- `payload_length_bytes`: 64‑bit unsigned int, original payload length before encoding.  
- `rs_n`: 16‑bit unsigned int, Reed-Solomon codeword length $$n$$.
- `rs_k`: 16‑bit unsigned int, Reed-Solomon message length $$k$$.
- `rs_symbol_bits`: 8‑bit unsigned int, bits per RS symbol (e.g., 8).
- `endianness`: 8‑bit flag (0 = big‑endian bit ordering, 1 = little‑endian).  
- `encoding_flags`: 32‑bit bitfield for future extensions (e.g., alternative color maps).  
- `reserved`: bytes reserved for future use (must be zero).

The header must appear before the image payload in the file. Implementations are free to choose a specific container (e.g., custom binary, PNG metadata chunk), as long as these fields are logically present.

***

## 5. Payload Encoding and Reed-Solomon Parameters

### 5.1 Input Payload

- Input is an arbitrary byte array.  
- For text, UTF‑8 encoding is recommended but not enforced.

### 5.2 Reed-Solomon Code

The reference profile uses a classic RS code over $$GF(2^{8})$$ to protect against burst errors (e.g., central "scratch" damage).

Recommended default:

- $$ n = 255 $$, $$ k = 223 $$, symbols over $$GF(2^{8})$$ (RS(255,223)).
- Each symbol is 8 bits.  
- Maximum correctable symbol errors per codeword: $$ t = \lfloor (n - k) / 2 \rfloor = 16 $$.

Process:

1. Split the payload into chunks of $$k$$ bytes (223 for the reference profile).  
2. For the last chunk, pad with zero bytes if shorter than $$k$$.  
3. Apply RS encoding to each chunk, producing codewords of length $$n$$ (255 bytes).
4. Concatenate all codewords into a single protected bitstream.

Other RS parameters are allowed, but any non‑default profile must record its `rs_n`, `rs_k`, and `rs_symbol_bits` values in the header.

***

## 6. Bitstream to Pixel Mapping

### 6.1 Bit Packing

- Concatenate all RS codewords into a single bitstream in the order they were generated.
- Bits are packed most‑significant‑bit first within each byte (for the reference profile).  
- If the total bit length is not divisible by 2, append one zero bit as padding.  

Let $$B$$ be the total number of bits. Then:

- Number of 2‑bit symbols $$S = B / 2$$.

### 6.2 2‑Bit Symbol to Color Map

Each 2‑bit symbol encodes one "polarization state" and maps to a single RGB pixel.

Canonical mapping:

- `00` → Black: `(R,G,B) = (0, 0, 0)`  
- `01` → Red: `(R,G,B) = (255, 0, 0)`  
- `10` → Green: `(0, 255, 0)`  
- `11` → Blue: `(0, 0, 255)`

These four states can be interpreted as discrete polarization orientations:

- `00`: NULL (0°)  
- `01`: ANGLE‑X (45°)  
- `10`: ANGLE‑Y (90°)  
- `11`: ANGLE‑Z (135°)

Implementations MAY extend this with brightness/intensity channels to emulate retardation in a fuller 5D model, but the base `.cryst` spec treats each pixel as a pure 2‑bit code.

### 6.3 2D Lattice Layout

Given $$S$$ symbols and chosen dimensions $$(W, H)$$:

- $$W \times H \geq S$$.  
- The recommended layout fills the lattice row‑major:

  - Symbol index $$i$$ maps to position:
    - $$x = i \bmod W$$  
    - $$y = \lfloor i / W \rfloor$$

- Any unused pixels (if $$W \times H > S$$) must be filled with `00` → black.  

The chosen $$W$$ and $$H$$ must be recorded in the header.

***

## 7. Decoding Process (Normative)

To reconstruct the original payload:

1. Parse the header and verify `magic` and `version`.  
2. Load the lattice image ($$W \times H$$ pixels).  
3. Traverse pixels row‑major, mapping RGB back to 2‑bit symbols:

   - `(0, 0, 0)` → `00`  
   - `(255, 0, 0)` → `01`  
   - `(0, 255, 0)` → `10`  
   - `(0, 0, 255)` → `11`  
   - Any other color should be treated as an error symbol to be corrected by RS, or mapped to the nearest valid color with a well‑defined policy.

4. Concatenate 2‑bit symbols into a single bitstream.  
5. Drop trailing padding bits so total length is a multiple of 8.  
6. Reconstruct bytes from bits according to the `endianness` field.  
7. Partition the bytes into RS codewords according to `rs_n` and `rs_symbol_bits`.
8. Run RS decoding on each codeword, correcting as many symbol errors as allowed by the chosen $$(n, k)$$.
9. Concatenate the decoded message bytes (length $$k$$ per codeword).  
10. Truncate the result to `payload_length_bytes` to remove padding.  

If any codeword is uncorrectable, the decoder should surface a clear error and optionally provide partial recovery.

***

## 8. Damage and Error Model

The `.cryst` format is designed to tolerate localized corruption (e.g., "scratches" or flicker).

Typical simulated damage patterns:

- Solid overwrite: contiguous region of pixels set to white `(255, 255, 255)`.  
- Flicker: random subset of pixels toggled between valid colors and white.  
- Color shift: perturbation of RGB values around valid color centers.

Because Reed-Solomon works at the symbol level and is robust to burst errors, a properly chosen $$(n, k)$$ can reconstruct the original payload even when a large contiguous area is corrupted, as long as the total number of corrupted symbols per codeword does not exceed its correction capability.

***

## 9. Reference Profile: `CRYST-RS255-223`

To encourage interoperability, the following reference profile is defined:

- `magic`: `"CRYST1"`  
- `version`: `0x0001`  
- `rs_n`: 255  
- `rs_k`: 223  
- `rs_symbol_bits`: 8  
- `endianness`: 0 (big‑endian bits)  
- Color map: as defined in Section 6.2  
- Layout: row‑major, minimal height where $$W$$ is user‑selected and $$H = \lceil S / W \rceil$$.  

Any implementation that supports this profile and adheres to Sections 4–7 is considered `.cryst`‑compliant.

***

## 10. Extensibility

The `.cryst` spec is intentionally minimal and is expected to evolve. Future extensions may include:

- Multiple frames (3D stacks) per file for volumetric lattices.  
- Additional "dimensions" encoded as intensity gradients or alpha channels.  
- Alternative RS parameters (e.g., RS(128,122) over GF(128)).  
- Explicit damage maps or integrity metadata.

All extensions must preserve backward compatibility by:

- Keeping the `magic` field,  
- Incrementing `version` when breaking changes are introduced,  
- Clearly documenting any new bit‑packing or color‑mapping rules.

***
