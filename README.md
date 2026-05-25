# RPi LED Controller

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Open Source](https://img.shields.io/badge/Open%20Source-100%25-brightgreen?logo=opensourceinitiative&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-C51A4A?logo=raspberrypi&logoColor=white)

A TCP-based LED control system for Raspberry Pi, featuring both direct pin control and animated lighting modes.

---

## Overview

This project consists of two components:

- **`server.py`** — runs on the Raspberry Pi, listens for incoming byte commands and drives 5 LEDs accordingly
- **`client.py`** — runs on any machine on the same network, sends single-byte commands to the server

---

## Hardware

| GPIO Pin | LED Index |
|----------|-----------|
| GPIO 27  | 0         |
| GPIO 26  | 1         |
| GPIO 17  | 2         |
| GPIO 16  | 3         |
| GPIO 19  | 4         |

> Connect each LED between the GPIO pin and GND via a current-limiting resistor (~220Ω).

---

## Requirements

### Raspberry Pi (server)

```bash
pip install gpiozero
```

### Client machine

No external dependencies — uses Python's built-in `socket` module.

---

## Usage

### 1. Start the server on the Raspberry Pi

```bash
python server.py
```

The server binds to `0.0.0.0:65432` and begins listening for connections.

### 2. Run the client on your machine

```bash
python client.py
```

Enter a value between `0` and `255` when prompted. Press `q` to quit.

---

## Command Protocol

A single byte is sent per command. The server interprets it as follows:

### Direct LED Control — values `0–32`

The byte is treated as a **bitmask**. Each bit corresponds to one LED:

| Bit | LED |
|-----|-----|
| 0   | LED 0 (GPIO 27) |
| 1   | LED 1 (GPIO 26) |
| 2   | LED 2 (GPIO 17) |
| 3   | LED 3 (GPIO 16) |
| 4   | LED 4 (GPIO 19) |

**Examples:**

```
0b00001  (1)  → LED 0 only
0b10001  (17) → LED 0 + LED 4
0b00000  (0)  → All LEDs off
```

### Animation Modes — values `33–37`

| Value | Mode        | Description                              |
|-------|-------------|------------------------------------------|
| 33    | Chaser      | LEDs light up one by one in sequence     |
| 34    | Bounce      | LED sweeps back and forth                |
| 35    | Alternating | Odd/even LEDs alternate                  |
| 36    | Heartbeat   | All LEDs pulse in a heartbeat pattern    |
| 37    | Neon        | LEDs flicker randomly                    |

To stop an animation, send any value `≤ 32`.

---

## Configuration

Edit the following constants in `client.py` to match your setup:

```python
RPI_IP = '192.168.5.69'   # IP address of your Raspberry Pi
PORT   = 65432             # Must match the server port
```

---

## Project Structure

```
.
├── server.py   # Raspberry Pi LED server
├── client.py   # Command-line client
└── README.md
```

---

## License

MIT
