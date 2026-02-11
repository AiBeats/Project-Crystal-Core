
import numpy as np
from PIL import Image
import argparse
import os

class CrystalEncoder:
    """
    Project Crystal: 5D Optical Storage Encoder (Python Implementation)
    Encodes digital bitstreams into 5D nanostructured silica optical lattices.
    """
    def __init__(self, ecc_bytes=32):
        self.ecc_bytes = ecc_bytes
        # 5D Mapping Logic: 2 bits per voxel
        self.mapping = {
            '00': (0, 0, 0),      # NULL / No Polarization
            '01': (255, 0, 0),    # Angle X (45°)
            '10': (0, 255, 0),    # Angle Y (90°)
            '11': (0, 0, 255)     # Angle Z (135°)
        }

    def text_to_bits(self, text):
        """Converts UTF-8 text to a binary string."""
        return ''.join(format(b, '08b') for b in text.encode('utf-8'))

    def encode_lattice(self, text, output_file="lattice.png"):
        """Generates a PNG representing the nanostructured silica lattice."""
        bit_stream = self.text_to_bits(text)
        
        # ECC Padding (Simulation)
        # In production, use 'reedsolo' library: rs = RSCodec(self.ecc_bytes)
        # For simulation parity, we add empty bits to match the terminal logic
        bit_stream += '0' * (self.ecc_bytes * 8)
        
        if len(bit_stream) % 2 != 0:
            bit_stream += '0'

        pixels = []
        for i in range(0, len(bit_stream), 2):
            chunk = bit_stream[i:i+2]
            pixels.append(self.mapping.get(chunk, (0, 0, 0)))

        # Determine square dimensions
        side = int(np.ceil(np.sqrt(len(pixels))))
        while len(pixels) < side * side:
            pixels.append((0, 0, 0))

        # Build image
        img_data = np.array(pixels, dtype=np.uint8).reshape((side, side, 3))
        img = Image.fromarray(img_data, 'RGB')
        img.save(output_file)
        
        print(f"[SUCCESS] Lattice generated: {output_file}")
        print(f"[INFO] Dimensions: {side}x{side} voxels")
        print(f"[INFO] Total bits stored: {len(bit_stream)}")

def main():
    parser = argparse.ArgumentParser(description="Project Crystal 5D CLI")
    parser.add_argument("--write", type=str, required=True, help="Text data to encode")
    parser.add_argument("--out", type=str, default="crystal_output.png", help="Output PNG filename")
    
    args = parser.parse_args()
    
    encoder = CrystalEncoder()
    encoder.encode_lattice(args.write, args.out)

if __name__ == "__main__":
    main()
