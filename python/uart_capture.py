from pathlib import Path
import time

import numpy as np
import serial

from user_param import (
    CAPTURE_BITS,
    CAPTURE_OUTPUT_PATH,
    PROGRESS_EVERY_PERCENT,
    READ_CHUNK_SIZE,
    UART_BAUD,
    UART_BIT_ORDER,
    UART_BYTESIZE,
    UART_DSRDTR,
    UART_PARITY,
    UART_PORT,
    UART_RTSCTS,
    UART_STOPBITS,
    UART_TIMEOUT_S,
    UART_XONXOFF,
)


def decode_uart_chunk_to_bits(raw: bytes, bit_order: str) -> np.ndarray:
    if not raw:
        return np.empty(0, dtype=np.uint8)

    data = np.frombuffer(raw, dtype=np.uint8)
    unpack_order = "big" if bit_order == "msb" else "little"
    return np.unpackbits(data, bitorder=unpack_order)


def bits_to_ascii_line(bits: np.ndarray) -> str:
    return (bits + ord("0")).astype(np.uint8).tobytes().decode("ascii")


def capture_one_series(
    ser: serial.Serial,
    target_bits: int,
    chunk_size: int,
    bit_order: str,
    progress_every_percent: int,
) -> np.ndarray:
    bits = np.empty(target_bits, dtype=np.uint8)
    collected = 0
    last_report = 0
    start = time.time()

    while collected < target_bits:
        raw = ser.read(chunk_size)
        if not raw:
            continue

        chunk_bits = decode_uart_chunk_to_bits(raw=raw, bit_order=bit_order)
        if chunk_bits.size == 0:
            continue

        remaining = target_bits - collected
        take = min(remaining, int(chunk_bits.size))
        bits[collected : collected + take] = chunk_bits[:take]
        collected += take

        percent = int((collected * 100) / target_bits)
        if percent >= last_report + progress_every_percent or collected == target_bits:
            elapsed = time.time() - start
            rate = collected / elapsed if elapsed > 0 else 0.0
            print(f"{collected}/{target_bits} bits ({percent}%), ~{rate:.0f} bit/s")
            last_report = percent

    return bits


def validate_config() -> None:
    if CAPTURE_BITS <= 0:
        raise ValueError("CAPTURE_BITS must be > 0.")
    if READ_CHUNK_SIZE <= 0:
        raise ValueError("READ_CHUNK_SIZE must be > 0.")
    if UART_BAUD <= 0:
        raise ValueError("UART_BAUD must be > 0.")
    if not UART_PORT:
        raise ValueError("UART_PORT must not be empty.")
    if PROGRESS_EVERY_PERCENT < 1 or PROGRESS_EVERY_PERCENT > 100:
        raise ValueError("PROGRESS_EVERY_PERCENT must be in range 1..100.")
    if UART_BIT_ORDER not in {"msb", "lsb"}:
        raise ValueError("UART_BIT_ORDER must be one of: msb, lsb.")


def main() -> None:
    validate_config()
    CAPTURE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(
        "UART capture started: "
        f"port={UART_PORT}, baud={UART_BAUD}, "
        f"bytesize={UART_BYTESIZE}, parity={UART_PARITY}, stopbits={UART_STOPBITS}, "
        f"xonxoff={UART_XONXOFF}, rtscts={UART_RTSCTS}, dsrdtr={UART_DSRDTR}, "
        f"bits={CAPTURE_BITS}, "
        f"bit_order={UART_BIT_ORDER}"
    )

    total_start = time.time()
    total_bits = CAPTURE_BITS

    with (
        serial.Serial(
            port=UART_PORT,
            baudrate=UART_BAUD,
            timeout=UART_TIMEOUT_S,
            bytesize=UART_BYTESIZE,
            parity=UART_PARITY,
            stopbits=UART_STOPBITS,
            xonxoff=UART_XONXOFF,
            rtscts=UART_RTSCTS,
            dsrdtr=UART_DSRDTR,
        ) as ser,
        CAPTURE_OUTPUT_PATH.open("w", encoding="ascii", newline="\n") as out_file,
    ):
        bits = capture_one_series(
            ser=ser,
            target_bits=CAPTURE_BITS,
            chunk_size=READ_CHUNK_SIZE,
            bit_order=UART_BIT_ORDER,
            progress_every_percent=PROGRESS_EVERY_PERCENT,
        )
        out_file.write(bits_to_ascii_line(bits))
        out_file.write("\n")

    total_elapsed = time.time() - total_start
    total_rate = total_bits / total_elapsed if total_elapsed > 0 else 0.0
    print(f"Saved {CAPTURE_BITS} bits to: {CAPTURE_OUTPUT_PATH}")
    print(f"Total: {total_bits} bits in {total_elapsed:.2f}s, ~{total_rate:.0f} bit/s")


if __name__ == "__main__":
    main()
