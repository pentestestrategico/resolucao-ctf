# PoC — Chrono II (Cryptography, 100 pts) — #21

**Flag:** `CSSCTF{th3_cl0ck_r3m3mb3rs_3very_s3c0nd}`  ✅

## Enunciado
Serviço `http://34.116.80.78:8001` transmite 60 cifras (1 Hz), cada uma com timestamp UTC. Endpoint `/capture.json`. "A cifra muda sempre."

## Análise
Cada registro é `{timestamp, ciphertext}` com prefixo `CSSCTF{` conhecido. É um **one-time-pad indexado por tempo**: há um **pad mestre fixo** e cada registro lê a partir de um offset (função embaralhada do timestamp). Descoberto porque janelas de registros diferentes se **sobrepõem** (overlaps de 5 valores exatos).

## Solução
1. Baixar `capture.json` (60 registros).
2. Com o known-plaintext `CSSCTF` (6 letras) de cada registro, computar 6 valores do keystream por registro.
3. **Remontar o pad mestre** por sobreposição das 60 janelas + votação por consenso (union-find nos offsets relativos).
4. Decifrar qualquer registro: `plain[i] = cipher[i] - pad[offset+i]` (letras mod 26, dígitos mod 10, separadores preservados).

Resultado consistente em todos os registros → `CSSCTF{th3_cl0ck_r3m3mb3rs_3very_s3c0nd}` ("the clock remembers every second").

## Lição
Reuso de keystream (OTP indexado por tempo) + known-plaintext permite reconstruir o pad por sobreposição.
