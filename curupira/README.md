# Curupira 3.0 - Militar — Writeups

Evento CTF GoHacking (Operação Relé). Cenário: comprometimento em cadeia de
**Transnorte (TN)**, **Litoral Telecom (LIT)** e **Câmara de Liquidação Mercantil (CLM)**
pelo grupo **Obsidian**, via updates falsos da **IndusCom** (C2 `update.induscom-cdn.net` / `198.51.100.88`).

Todos os arquivos vêm de `https://download.gohacking.com.br/curupira3/`.

## Índice de categorias (ordem oficial da plataforma)
1. [PCAP](writeups/pcap.md) — DHCP/FTP/HTTP/DNS/TLS/ICMP
2. [LOG](writeups/log.md) — syslog / access.log / defender.log / modbus.log
3. [SQLite](writeups/sqlite.md) — history.db / historian.db / vpn.db
4. [Stego](writeups/stego.md) — PDF/JPG/DOCX/WAV
5. [Crypto](writeups/crypto.md) — hex/b64 / XOR / AES / RSA
6. [Warmup](writeups/warmup.md) — zip/gzip/ELF/firmware/ndjson
7. [Phishing](writeups/phishing.md) — eml/mbox
8. [Cadeia](writeups/cadeia.md) — deb/rpm/apt-repo
9. [Dropper](writeups/dropper.md) — iso/lnk/hta
10. [Endpoint](writeups/endpoint.md) — Sysmon jsonl
11. [Memória](writeups/memoria.md) — dumps RMEM/CLMD
12. [Disco](writeups/disco.md) — NTFS/ext4/MBR
13. [Bloodhound](writeups/bloodhound.md) — SharpHound/BHCE
14. [Credenciais](writeups/credenciais.md) — NTDS/ccache/pfx
15. [Event Log EVTX](writeups/eventlog.md) — evtx/etl
16. [Persistência](writeups/persistencia.md) — pol/atjobs/wmi
17. [Ransomware](writeups/ransomware.md) — .enc
18. [OT/SCADA](writeups/ot-scada.md) — Modbus/IEC104/DNP3
19. [Firmware](writeups/firmware.md) — uImage/initramfs/jffs2
20. [Telecom](writeups/telecom.md) — dnstap/MRT/SNMP
21. [Wiper](writeups/wiper.md) — FAT12/cramfs/WIM
22. [Reverse](writeups/reverse.md) — PE/ELF-UPX/Java
23. [Interceptação](writeups/interceptacao.md) — CMS/WebSocket/gRPC
24. [Intel](writeups/intel.md) — xls/doc/mmdb
25. [Final](writeups/final.md) — p7m/dns-update/p12
26. [Volume](writeups/volume.md) — residual XOR em arquivos ~180–230 MB
27. [Acervo](writeups/acervo.md) — residual em bases/arquivos ~180–210 MB
28. [Empacotado](writeups/empacotado.md) — membro residual em tar/cpio/zip gigantes
29. [Mídia](writeups/midia.md) — residual em ISO/BMP/NetFlow gigantes
30. **Fecho** — *(categoria sem writeup neste acervo)*

> **Scripts:** [`scripts/decifrar_brasilia.py`](scripts/decifrar_brasilia.py) (decifra AES com senha coletada),
> [`scripts/jhon.py`](scripts/jhon.py) (ataque de dicionário ao criptograma).
> Referência: [`tutorial_seclists.md`](tutorial_seclists.md).
>
> **~117 flags** `CTF{...}` distribuídas pelas categorias (ver cada writeup).

## Nota metodológica
A maioria dos artefatos são formatos **sintéticos**: um cabeçalho ASCII no topo
descreve offsets/IVs/cipher, seguido de um blob e de padding aleatório (~720 KB).
Flags aparecem em texto, hex, Base64, UTF-16LE, ou dentro de blobs cifrados cuja
senha é uma credencial coletada em outra etapa (ex.: `SE03-13800`).
