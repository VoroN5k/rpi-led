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

### ✅ Authentication — HMAC-SHA256 (implemented)

Every command is signed with **HMAC-SHA256** using a shared secret. The server verifies the signature before acting on any command. Unsigned or incorrectly signed packets are rejected with a NAK and logged.

The shared secret is loaded from the `LEDCTL_SECRET` environment variable on both sides:

```bash
export LEDCTL_SECRET="your-strong-random-secret"
```

Never hardcode the secret in source code. Use `python -c "import secrets; print(secrets.token_hex(32))"` to generate a strong one.

A firewall rule adds an extra layer:

```bash
sudo ufw allow from 192.168.5.0/24 to any port 65432
sudo ufw deny 65432
```

---

### ⚠️ No Encryption

Data is transmitted in plaintext over TCP. The single-byte protocol carries no sensitive information by design, but the channel itself is unencrypted.

**Mitigation:** If operating over an untrusted network, tunnel the connection through SSH:

```bash
ssh -L 65432:localhost:65432 pi@<RPI_IP>
```

Then point the client to `127.0.0.1` instead of the Pi's IP.

---

### ✅ Strict Allowlist Validation (implemented)

The server maintains an explicit allowlist (`VALID_COMMANDS = set(range(0, 38))`). Any byte value outside `0–37` is rejected before HMAC verification, logged as a warning, and responded to with a NAK. Silent ignoring is gone.

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