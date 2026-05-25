import socket
import hmac
import hashlib
import os

# Configuration - must match server.py exactly

RPI_IP = "192.168.5.69"
PORT   = 65432

# Load from environment variable - never hardcode the real secret in source
SECRET = os.environ.get("LEDCTL_SECRET", "change-me-before-use").encode()

# HMAC helper

def sign(cmd_byte: int) -> bytes:
    """Return HMAC-SHA256(SECRET, cmd_byte) as 32 raw bytes."""
    return hmac.new(SECRET, bytes([cmd_byte]), hashlib.sha256).digest()

# Transport

def send_command(value: int) -> bool:
    """
    Send a signed command to the server.

    Packet layout:
        [1 byte]  command value
        [32 bytes] HMAC-SHA256 signature

    Returns True on ACK, False on NAK or error.
    """
    packet = bytes([value & 0xFF]) + sign(value & 0xFF)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((RPI_IP, PORT))
            s.sendall(packet)

            # Wait for ACK (0x01) or NAK (0x00)
            response = s.recv(1)
            if response == b"\x01":
                print(f"  ✓  ACK — command {value} accepted")
                return True
            else:
                print(f"  ✗  NAK — command {value} rejected by server")
                return False

    except socket.timeout:
        print("  ✗  Error: connection timed out")
        return False
    except ConnectionRefusedError:
        print(f"  ✗  Error: could not connect to {RPI_IP}:{PORT}")
        return False
    except Exception as e:
        print(f"  ✗  Error: {e}")
        return False

# CLI

COMMAND_HELP = """
Commands
────────────────────────────────
  0–32   Direct LED bitmask
           bit 0 → LED 0 (GPIO 27)
           bit 1 → LED 1 (GPIO 26)
           bit 2 → LED 2 (GPIO 17)
           bit 3 → LED 3 (GPIO 16)
           bit 4 → LED 4 (GPIO 19)
           e.g. 17 = 0b10001 → LED 0 + LED 4

  33     Chaser
  34     Bounce
  35     Alternating
  36     Heartbeat
  37     Neon

  q      Quit
────────────────────────────────
"""

if __name__ == "__main__":
    print("── RPi LED Controller ──")
    if SECRET == b"change-me-before-use":
        print("  Warning: using default secret. "
              "Set the LEDCTL_SECRET environment variable.\n")
    print(COMMAND_HELP)

    while True:
        user_input = input("Value (0-37, q to quit): ").strip()

        if user_input.lower() == "q":
            print("Bye.")
            break

        if not user_input.isdigit():
            print("  !  Enter a number between 0 and 37.")
            continue

        val = int(user_input)
        if not (0 <= val <= 37):
            print("  !  Value out of range. Enter a number between 0 and 37.")
            continue

        send_command(val)