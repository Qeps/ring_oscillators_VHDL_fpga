from collections.abc import Sequence
from pathlib import Path

import numpy as np

from user_param import OUT_PREFIX, SAVE_PLOTS


def parse_bits_line(bit_text: str, line_no: int) -> np.ndarray:
    raw = bit_text.encode("ascii")
    data = np.frombuffer(raw, dtype=np.uint8)

    valid = (data == ord("0")) | (data == ord("1"))
    if not np.all(valid):
        raise ValueError(f"Invalid character in input file at line {line_no}. Allowed: '0'/'1'.")

    return (data - ord("0")).astype(np.uint8, copy=False)


def load_bitstreams_from_file(path: Path | str, require_equal_length: bool = False) -> list[np.ndarray]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    bitstreams: list[np.ndarray] = []
    expected_length: int | None = None

    with path.open("r", encoding="ascii") as f:
        for line_no, line in enumerate(f, start=1):
            bit_text = line.strip()
            if not bit_text or bit_text.startswith("#"):
                continue

            bits = parse_bits_line(bit_text, line_no)
            if require_equal_length:
                if expected_length is None:
                    expected_length = len(bits)
                elif len(bits) != expected_length:
                    raise ValueError(
                        "Inconsistent bitstream length in input file: "
                        f"line {line_no} has {len(bits)} bits, expected {expected_length}."
                    )

            bitstreams.append(bits)

    if not bitstreams:
        raise ValueError("No bitstreams found in input file.")

    return bitstreams


def bitstream_length_summary(bitstreams: Sequence[np.ndarray]) -> str:
    if not bitstreams:
        return "0 bitstreams."

    lengths = [len(bits) for bits in bitstreams]
    if len(lengths) == 1:
        return f"1 bitstream, {lengths[0]} bits."

    min_length = min(lengths)
    max_length = max(lengths)
    if min_length == max_length:
        return f"{len(lengths)} bitstreams, {min_length} bits each."

    return f"{len(lengths)} bitstreams, bit lengths min={min_length}, max={max_length}."


def build_output_path(suffix: str, bitstream_idx: int | None = None) -> Path | None:
    if not SAVE_PLOTS:
        return None

    if bitstream_idx is None:
        filename = f"{OUT_PREFIX.name}_{suffix}"
    else:
        filename = f"{OUT_PREFIX.name}_b{bitstream_idx:03d}_{suffix}"

    return OUT_PREFIX.parent / filename


def bits_to_ascii_line(bits: np.ndarray) -> str:
    bits = np.asarray(bits, dtype=np.uint8)
    valid = (bits == 0) | (bits == 1)
    if not np.all(valid):
        raise ValueError("Bit array can contain only 0/1 values.")

    return (bits + ord("0")).astype(np.uint8, copy=False).tobytes().decode("ascii")


def write_bitstreams_to_file(path: Path | str, bitstreams: Sequence[np.ndarray]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="ascii", newline="\n") as f:
        for bits in bitstreams:
            f.write(bits_to_ascii_line(bits))
            f.write("\n")
