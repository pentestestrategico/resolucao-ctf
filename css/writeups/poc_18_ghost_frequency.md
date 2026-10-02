# PoC — Ghost Frequency (Forensics, 115 pts) — #18

**Flag:** `CSSCTF{th3_gh0st_fr3qu3ncy_w4s_n3v3r_s1l3nt}`  ✅ (recuperada)

## Enunciado
`KBR17_blackbox.wav` (estéreo 48kHz, 115s). Dois canais de manutenção: um "visual", outro "telemetria de pacote low-rate"; uplink pode ter retransmitido dados stale.

## Cadeia de solução
### 1. Canal esquerdo = SSTV Martin M1
VIS code = 44 → Martin M1 (320×256). Decodificar a imagem revela o **manual de recuperação**:
- Bus **BELL202 / 1200 / 8N1**, DATA FIELD **Base64**, BLOCK=1024.
- ARCHIVE **GZIP** (MAGIC=1F8B), **ARCHIVE_BYTES=5757**.
- FEC: `PA = D0^D1^D2^D3`, `PB = D4^D5^D6^D7` (XOR byte-a-byte).
- **CRC32 autoritativo** de cada bloco D0–D7.

### 2. Canal direito = AFSK Bell 202 (1200 baud, 1200/2200 Hz)
Demodular por frequência instantânea + UART 8N1 com **resync por byte** (crucial p/ 96%+ limpo). Pacotes:
```
NXPK|SESSION=NX-771|TYPE=DATA|SEQ=n|RETRY=r|LEN=1024|WIRECRC=...|DATA=<base64>
NXPK|SESSION=NX-771|TYPE=PARITY|GROUP=A/B|...|DATA=<base64>
```

### 3. Seleção + FEC + reparo
- Descartar sessão stale (NX-770); validar cada bloco por `crc32(data)==WIRECRC`.
- Blocos limpos recebidos: D0, D1, D3, D4, D6, D7 + PARITY A/B.
- Recuperar faltantes via XOR: `D2 = PA^D0^D1^D3`, `D5 = PB^D4^D6^D7`.
- Concatenar D0..D7, `[:5757]`. O **magic gzip `1F 8B` foi zerado** na transmissão → restaurar (o SSTV informava MAGIC=1F8B) → gunzip → TAR → `final_message.txt`.

→ `CSSCTF{th3_gh0st_fr3qu3ncy_w4s_n3v3r_s1l3nt}`

## Lição
Multicanal: SSTV (visual) carrega o manual; AFSK (telemetria) carrega os dados. CRC + FEC XOR tornam robusto a retransmissões stale; cabeçalho corrompido (magic zerado) reconstruído a partir da metadata.
