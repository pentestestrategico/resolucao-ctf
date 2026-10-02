# PoC — Signal Fracture (Forensics, 100 pts) — #19

**Flag:** `CSSCTF{fragment_t3ll_th3_st0ry}`  ✅

## Enunciado
`Signal_Fracture.zip` = `KBR17_relay.img` (2 partições) + `KBR17_uplink.pcap`. Fragmentos com retransmissões (duplicatas); "scheduler catalog intacto, spool index purgado".

## Análise
- Partição 1 (ext4): `fragment-format.txt` (formato NXFR: magic + session + seq + total + plen + crc + payload), `scheduler/relay.db` (catálogo com **SHA-256 esperado** de cada payload), 3 `.blob` (cache).
- Partição 2: raw ring buffer (SPOOL purgado mas não zerado).
- pcap: fragmentos UDP:4711 (UPLINK), com retransmissões.
- Sessão `6E2C17A9` (emergency_burst_17): 8 fragmentos seq 0–7, cada um com fonte CACHE/SPOOL/UPLINK e estado.

## Solução
Parsear registros `NXFR` de **todas as fontes** (pcap, blobs, raw da partição 2), computar SHA-256 do payload e casar com o catálogo autoritativo (desambigua duplicatas/stale). Reassemblar seq 0–7:
```python
# scan b'NXFR' em pcap payloads + blobs + p2.img; sha256(payload) == expected[seq] -> found[seq]
blob=b''.join(found[s] for s in range(8))  # gzip
```
Resultado: gzip → tar `emergency_burst_17.tar` → `final_message.txt`:
```
CSSCTF{fragment_t3ll_th3_st0ry}
```

## Lição
Dados deletados persistem no ring buffer; CRC/SHA do catálogo permite reassemblar e deduplicar retransmissões.
