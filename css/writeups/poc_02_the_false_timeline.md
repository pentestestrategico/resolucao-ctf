# PoC — The False Timeline (Forensics, 66 pts) — #2

**Flag:** `CSSCTF{kai_did_not_do_it}`  ✅

## Enunciado
Imagem ext4 (`nexus_relay.img.xz`). A `relay.log` acusa o Admin KAI-7 de um export de emergência às 03:17, mas ele já estava desconectado. Reconstruir a timeline real e recuperar a chave.

## Análise (anti-forense / timestomping)
- `relay.log`: "export às 03:17:03 por KAI-7" — **forjado**.
- `auth.log`: sessão SSH do KAI encerrada às **03:05:41** (antes das 03:17).
- `audit.log` (verdade): `svc-relay` (uid 998) rodou `nx-export --emergency` no epoch **4157543568**, depois `touch -r /etc/machine-id .ekey-cache` (**timestomp**, decodificado do `PROC_PROCTITLE`).
- `metadata.db` (SQLite): job `emergency_export` tem `session_uuid = aab0c8b2-...` (sessão do svc-relay).
- `exporter.py`: chave AES-256 = `SHA256(machine_id | session_uuid | event_epoch)`; arquivo = `NXKEY_V1 + nonce(12) + AES-GCM`.

## Solução
Derivar a chave com os parâmetros **verdadeiros** (svc-relay + epoch real) e decifrar `.ekey-cache`:
```python
import hashlib; from cryptography.hazmat.primitives.ciphers.aead import AESGCM
mid="8f3b2a1c9e4d56781234abcd567890ef"; uuid="aab0c8b2-f8b1-4f11-9a72-6d8123a1005a"; epoch=4157543568
key=hashlib.sha256(f"{mid}|{uuid}|{epoch}".encode()).digest()
blob=open('.ekey-cache','rb').read()
print(AESGCM(key).decrypt(blob[8:20], blob[20:], None))
# b'CSSCTF{kai_did_not_do_it}'
```
Apenas os parâmetros reais decifram; a timeline forjada (KAI/03:17) falha.

## Lição
Logs podem ser forjados; `audit.log` e inodes são mais confiáveis. Timestomp (`touch -r`) detectável no audit. A derivação de chave amarrada ao contexto exato expõe a fraude.
