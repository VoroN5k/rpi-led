# Security Policy

## Supported Versions

This project is a single-version hobby/embedded project. Security fixes are applied to the latest code only.

| Version | Supported |
|---------|-----------|
| latest  | ✅        |
| older   | ❌        |

---

## Known Security Considerations

This project is designed for use on **trusted local networks only**. Before deploying, be aware of the following:

### ⚠️ No Authentication

The TCP server accepts commands from **any host** that can reach port `65432`. There is no handshake, token, or credential check. Anyone on the same network can send commands to your Raspberry Pi.

**Mitigation:** Restrict access using a firewall rule, for example with `ufw`:

```bash
sudo ufw allow from 192.168.5.0/24 to any port 65432
sudo ufw deny 65432
```

Replace `192.168.5.0/24` with your actual subnet.

---

### ⚠️ No Encryption

Data is transmitted in plaintext over TCP. The single-byte protocol carries no sensitive information by design, but the channel itself is unencrypted.

**Mitigation:** If operating over an untrusted network, tunnel the connection through SSH:

```bash
ssh -L 65432:localhost:65432 pi@<RPI_IP>
```

Then point the client to `127.0.0.1` instead of the Pi's IP.

---

### ⚠️ No Input Sanitisation Beyond Range Check

The server accepts any byte value `0–255`. Values outside the defined protocol range (`0–37`) are silently ignored, but there is no strict allowlist enforcement.

**Mitigation:** If extending the protocol, validate all incoming values explicitly before acting on them.

---

### ⚠️ GPIO Access Requires Elevated Privileges

Running `server.py` requires access to GPIO hardware, which may need `sudo` or membership in the `gpio` group depending on your OS configuration.

**Mitigation:** Add the `pi` user (or your user) to the `gpio` group instead of running as root:

```bash
sudo usermod -aG gpio $USER
```

---

## Reporting a Vulnerability

This is a personal/educational project without a formal security team. If you find a vulnerability:

1. **Do not open a public issue** if the finding could be exploited by others.
2. Contact the maintainer directly via the repository's contact method (e.g. email or private message).
3. Include a clear description of the issue, steps to reproduce, and potential impact.
4. Allow reasonable time for a response before any public disclosure.

---

## Scope

Given the nature of this project (local network, physical hardware, no user data), the primary threat model is:

- Unauthorized control of GPIO pins on a local network
- Denial-of-service via connection flooding

Out of scope: data exfiltration, authentication bypass (there is none by design), cryptographic weaknesses.

---

> **TL;DR** — Do not expose port `65432` to the internet. Use this on a private, trusted network only.
