import numpy as np

from user_func import bitstream_length_summary, load_bitstreams_from_file, write_bitstreams_to_file
from user_param import ANALYSIS_INPUT_PATH, VN_OUTPUT_PATH


def von_neumann_whiten(bits: np.ndarray) -> np.ndarray:
    pair_count = len(bits) // 2
    if pair_count == 0:
        return np.empty(0, dtype=np.uint8)

    pairs = bits[: 2 * pair_count].reshape(pair_count, 2)
    different = pairs[:, 0] != pairs[:, 1]

    return pairs[different, 0].astype(np.uint8, copy=False)


def main() -> None:
    print(f"Loading bitstreams from: {ANALYSIS_INPUT_PATH}")
    bitstreams = load_bitstreams_from_file(ANALYSIS_INPUT_PATH)
    print(f"Loaded {bitstream_length_summary(bitstreams)}")

    whitened_streams: list[np.ndarray] = []
    for idx, bits in enumerate(bitstreams, start=1):
        whitened = von_neumann_whiten(bits)
        whitened_streams.append(whitened)

        used_bits = 2 * (len(bits) // 2)
        discarded_odd_bit = len(bits) - used_bits
        kept_pairs = len(whitened)
        pair_count = used_bits // 2
        keep_ratio = kept_pairs / pair_count if pair_count else 0.0

        print(
            f"Bitstream {idx}/{len(bitstreams)}: input_bits={len(bits)}, "
            f"pairs={pair_count}, output_bits={len(whitened)}, "
            f"kept_pairs={100.0 * keep_ratio:.2f}%, discarded_odd_bit={discarded_odd_bit}"
        )

    write_bitstreams_to_file(VN_OUTPUT_PATH, whitened_streams)
    print(f"Saved Von Neumann whitened bits to: {VN_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
