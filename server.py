import socket
import time
import random
import hmac
import hashlib
import os
import logging
from gpiozero import LED
 

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ledctl.log"),
    ],
)
log = logging.getLogger(__name__)

# Configuration - edit these to match your setup
BIND_IP = "192.168.5.69"
PORT = 65432

# Shared secret - must match the client exactly
# Best practice - load from environment variable so it never appears in source
# export LEDCTL_SECRET="your-secret-key"
SECRET = os.environ.get("LEDCTL_SECRET", "change-me-before-use").encode()

# Exact set of valid command bytes - anything else is rejected
VALID_COMMANDS = set(range(0, 38))  # 0-32 bitmask, 33-37 game modes

# HMAC digest size in bytes
DIGEST_SIZE = 32  # SHA256 produces 32-byte digests

leds = [LED(27), LED(26), LED(17), LED(16), LED(19)]

current_game = 0
animation_step = 0


def turn_off_all_leds():
   for led in leds:
       led.off()

#HMAC Helpers
def verify_hmac(cmd_byte: int, received_digest: bytes) -> bool:
    """Return True if received_digest is a valid HMAC-SHA256 for cmd_byte."""
    expected = hmac.new(SECRET, bytes([cmd_byte]), hashlib.sha256).digest()
    # Constant-time comparison - prevents timing attacks
    return hmac.compare_digest(expected, received_digest)


def run_game_step():
   global animation_step
   if current_game == 0:
       return
  
   turn_off_all_leds()
  
   if current_game == 33:    # Chaser
       leds[animation_step % len(leds)].on()
       animation_step += 1
      
   elif current_game == 34:  # Bounce
       sequence = [0, 1, 2, 3, 4, 3, 2, 1]
       leds[sequence[animation_step % len(sequence)]].on()
       animation_step += 1
      
   elif current_game == 35:  # Alternating
       if animation_step % 2 == 0:
           leds[0].on(); leds[4].on()
       else:
           leds[1].on(); leds[2].on(), leds[3].on()
       animation_step += 1
      
   elif current_game == 36:  # Heartbeat
       if (animation_step % 4) in [0, 2]:
           for led in leds: led.on()
       animation_step += 1
      
   elif current_game == 37:  # Neon
       for led in leds:
           if random.choice([True, False]):
               led.on()

# Protocol handler
def handle_connection(conn, addr):
    """
    Packet format (33 bytes total):
        [1 byte]  command
        [32 bytes] HMAC-SHA256(SECRET, command)
    """
    global current_game, animation_step
 
    with conn:
        # Read exactly 33 bytes (1 cmd + 32 HMAC)
        data = b""
        while len(data) < 1 + DIGEST_SIZE:
            chunk = conn.recv(1 + DIGEST_SIZE - len(data))
            if not chunk:
                log.warning("Connection closed before full packet received from %s", addr)
                return
            data += chunk
 
        cmd_byte       = data[0]
        received_digest = data[1:]
 
        # 1. Allowlist check
        if cmd_byte not in VALID_COMMANDS:
            log.warning("Rejected unknown command 0x%02X from %s", cmd_byte, addr)
            conn.sendall(b"\x00")   # NAK
            return
 
        # 2. HMAC verification
        if not verify_hmac(cmd_byte, received_digest):
            log.warning("HMAC verification failed for command 0x%02X from %s", cmd_byte, addr)
            conn.sendall(b"\x00")   # NAK
            return
 
        # 3. Execute
        log.info("Accepted command 0x%02X from %s", cmd_byte, addr)
        conn.sendall(b"\x01")       # ACK
 
        if cmd_byte > 32:
            current_game   = cmd_byte
            animation_step = 0
        else:
            current_game = 0
            turn_off_all_leds()
            for i in range(len(leds)):
                if cmd_byte & (1 << i):
                    leds[i].on()

def start_server():
    if SECRET == b"change-me-before-use":
        log.warning(
            "Using default secret! Set the LEDCTL_SECRET environment variable "
            "before exposing this server on the network."
        )
 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((BIND_IP, PORT))
        s.listen()
        s.settimeout(0.05)
        log.info("Server listening on %s:%d", BIND_IP, PORT)
 
        try:
            while True:
                try:
                    conn, addr = s.accept()
                    log.info("Connection from %s", addr)
                    handle_connection(conn, addr)
                except socket.timeout:
                    run_game_step()
                    time.sleep(0.1)
        except KeyboardInterrupt:
            log.info("Shutting down server...")
            turn_off_all_leds()
 
 
if __name__ == "__main__":
    start_server()