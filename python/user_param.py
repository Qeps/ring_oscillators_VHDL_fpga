"""User-configurable parameters for UART RNG capture and analysis.

UART_PORT: Serial port name used to open the UART connection.
UART_BAUD: UART speed in bits per second.
UART_BYTESIZE: Number of data bits per UART frame.
UART_PARITY: UART parity mode.
UART_STOPBITS: Number of stop bits in each UART frame.
UART_XONXOFF: Enable software flow control if needed.
UART_RTSCTS: Enable RTS/CTS hardware flow control if needed.
UART_DSRDTR: Enable DSR/DTR hardware flow control if needed.
UART_TIMEOUT_S: Read timeout (seconds) for serial read operations.
READ_CHUNK_SIZE: Number of bytes requested from UART per read call.
UART_BIT_ORDER: Bit order used when unpacking "raw_bytes":
    - "msb": most-significant bit first in each byte.
    - "lsb": least-significant bit first in each byte.
CAPTURE_BITS: Number of bits captured from UART.
CAPTURE_OUTPUT_PATH: Output path for captured series file (one series per line).

MAX_LAG: Maximum lag used in the autocorrelation calculation.
MAP2D_WORD_SIZES: Word sizes used for 2D delay maps.
MAP2D_TAUS: Delay values used for 2D delay maps.
STEP: Bit step between consecutive extracted words for 2D maps.
ANALYSIS_INPUT_PATH: Input path used by the analysis scripts.

MAP2D_BINS: Number of histogram bins for 2D map (None = auto).
BIAS_ALPHA: Significance level used by bias.py for PASS/FAIL.

SAVE_PLOTS: Save plots to files when True; otherwise show interactive windows.
OUT_PREFIX: Prefix used to build output plot filenames.

PROGRESS_EVERY_PERCENT: Progress print interval as percentage points.
"""

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
UART_TIMEOUT_S = 1.0
READ_CHUNK_SIZE = 4096
UART_BIT_ORDER = "msb"  # "msb" or "lsb"
CAPTURE_BITS = 10485760
CAPTURE_OUTPUT_PATH = Path(__file__).resolve().parent.parent / "captured_bits.txt"

MAX_LAG = 15
MAP2D_WORD_SIZES = (4, 8)
MAP2D_TAUS = tuple(range(9))
STEP = None  # None = use step equal to current word size
ANALYSIS_INPUT_PATH = CAPTURE_OUTPUT_PATH

MAP2D_BINS = None
BIAS_ALPHA = 0.01

SAVE_PLOTS = True
OUT_PREFIX = Path(__file__).resolve().parent.parent / "results" / "uart_rng"

PROGRESS_EVERY_PERCENT = 5
