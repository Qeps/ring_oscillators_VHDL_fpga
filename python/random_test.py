import math
import time
from collections import Counter
from pathlib import Path

import serial

# User-configurable parameters
UART_PORT = "COM11"
UART_BAUD = 9600
UART_BYTESIZE = serial.EIGHTBITS
UART_PARITY = serial.PARITY_NONE
UART_STOPBITS = serial.STOPBITS_ONE
UART_XONXOFF = False
UART_RTSCTS = False
UART_DSRDTR = False

TARGET_BITS = 1_000_000
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "captured_bits.txt"
UART_TIMEOUT_S = 1.0
READ_CHUNK_SIZE = 4096

AUTOCORR_LAG = 1
POKER_M = 4
P_VALUE_THRESHOLD = 0.01


def capture_bits(
    port: str,
    baud: int,
    target_bits: int,
    timeout_s: float,
    chunk_size: int,
) -> str:
    bits_collected = []
    count = 0
    last_report = 0
    start = time.time()

    with serial.Serial(
        port=port,
        baudrate=baud,
        timeout=timeout_s,
        bytesize=UART_BYTESIZE,
        parity=UART_PARITY,
        stopbits=UART_STOPBITS,
        xonxoff=UART_XONXOFF,
        rtscts=UART_RTSCTS,
        dsrdtr=UART_DSRDTR,
    ) as ser:
        while count < target_bits:
            raw = ser.read(chunk_size)
            if not raw:
                continue

            filtered = [chr(b) for b in raw if b == ord("0") or b == ord("1")]
            if not filtered:
                continue

            need = target_bits - count
            if len(filtered) > need:
                filtered = filtered[:need]

            bits_collected.extend(filtered)
            count += len(filtered)

            percent = int((count * 100) / target_bits)
            if percent >= last_report + 5 or count == target_bits:
                elapsed = time.time() - start
                rate = count / elapsed if elapsed > 0 else 0.0
                print(f"Progress: {count}/{target_bits} bits ({percent}%), ~{rate:.0f} bit/s")
                last_report = percent

    return "".join(bits_collected)


def monobit_test(bits: str) -> dict:
    n = len(bits)
    ones = bits.count("1")
    zeros = n - ones
    s_obs = abs(ones - zeros) / math.sqrt(n)
    p_value = math.erfc(s_obs / math.sqrt(2.0))
    return {
        "n": n,
        "zeros": zeros,
        "ones": ones,
        "ratio_ones": ones / n,
        "p_value": p_value,
        "pass": p_value >= P_VALUE_THRESHOLD,
    }


def runs_test(bits: str) -> dict:
    n = len(bits)
    pi = bits.count("1") / n
    if abs(pi - 0.5) >= 2 / math.sqrt(n):
        return {
            "p_value": 0.0,
            "pass": False,
            "reason": "Prerequisite failed: bit frequency deviation too large",
        }

    runs = 1 + sum(1 for i in range(1, n) if bits[i] != bits[i - 1])
    numerator = abs(runs - (2 * n * pi * (1 - pi)))
    denominator = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    p_value = math.erfc(numerator / denominator)
    return {
        "runs": runs,
        "p_value": p_value,
        "pass": p_value >= P_VALUE_THRESHOLD,
    }


def entropy_per_bit(bits: str) -> dict:
    n = len(bits)
    p1 = bits.count("1") / n
    p0 = 1.0 - p1

    def h(p: float) -> float:
        return 0.0 if p <= 0.0 else -p * math.log2(p)

    entropy = h(p0) + h(p1)
    return {
        "entropy_bits": entropy,
        "pass": entropy >= 0.99,
    }


def autocorrelation_test(bits: str, lag: int) -> dict:
    n = len(bits)
    if lag <= 0 or lag >= n:
        raise ValueError(f"AUTOCORR_LAG must be in range 1..{n-1}")

    mismatches = sum(1 for i in range(n - lag) if bits[i] != bits[i + lag])
    x = abs(2 * mismatches - (n - lag)) / math.sqrt(n - lag)
    p_value = math.erfc(x / math.sqrt(2.0))
    return {
        "lag": lag,
        "mismatches": mismatches,
        "p_value": p_value,
        "pass": p_value >= P_VALUE_THRESHOLD,
    }


def poker_test(bits: str, m: int) -> dict:
    n = len(bits)
    k = n // m
    if k < 5:
        return {
            "p_value": 0.0,
            "pass": False,
            "reason": f"Not enough data for m={m}",
        }

    cut = bits[: k * m]
    blocks = [cut[i : i + m] for i in range(0, len(cut), m)]
    counts = Counter(blocks)

    stat = (2**m / k) * sum(v * v for v in counts.values()) - k
    expected = (2**m) - 1
    z = abs(stat - expected) / math.sqrt(2 * expected)
    p_value = math.erfc(z / math.sqrt(2.0))

    return {
        "m": m,
        "blocks": k,
        "stat": stat,
        "p_value": p_value,
        "pass": p_value >= P_VALUE_THRESHOLD,
    }


def print_result(name: str, result: dict) -> None:
    print(f"\n[{name}]")
    for key, value in result.items():
        if isinstance(value, float):
            print(f"{key}: {value:.6f}")
        else:
            print(f"{key}: {value}")


def validate_config() -> None:
    if TARGET_BITS <= 0:
        raise ValueError("TARGET_BITS must be > 0")
    if READ_CHUNK_SIZE <= 0:
        raise ValueError("READ_CHUNK_SIZE must be > 0")
    if UART_BAUD <= 0:
        raise ValueError("UART_BAUD must be > 0")
    if not UART_PORT:
        raise ValueError("UART_PORT must not be empty")
    if AUTOCORR_LAG <= 0:
        raise ValueError("AUTOCORR_LAG must be > 0")
    if POKER_M <= 0:
        raise ValueError("POKER_M must be > 0")


def main() -> None:
    validate_config()

    print(
        "Capture started: "
        f"port={UART_PORT}, baud={UART_BAUD}, "
        f"bytesize={UART_BYTESIZE}, parity={UART_PARITY}, stopbits={UART_STOPBITS}, "
        f"xonxoff={UART_XONXOFF}, rtscts={UART_RTSCTS}, dsrdtr={UART_DSRDTR}, "
        f"bits={TARGET_BITS}"
    )

    bits = capture_bits(
        port=UART_PORT,
        baud=UART_BAUD,
        target_bits=TARGET_BITS,
        timeout_s=UART_TIMEOUT_S,
        chunk_size=READ_CHUNK_SIZE,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(bits, encoding="ascii")
    print(f"Saved {len(bits)} bits to: {OUTPUT_PATH}")

    print("\nRunning statistical tests...")
    print_result("Monobit", monobit_test(bits))
    print_result("Runs", runs_test(bits))
    print_result("Entropy", entropy_per_bit(bits))
    print_result("Autocorrelation", autocorrelation_test(bits, AUTOCORR_LAG))
    print_result("Poker", poker_test(bits, POKER_M))
    print(f"\nDecision rule: pass=True when p_value >= {P_VALUE_THRESHOLD}")


if __name__ == "__main__":
    main()
