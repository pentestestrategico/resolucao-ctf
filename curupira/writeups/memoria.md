# Memória

`tn-mem.bin`/`lit-mem.bin` (RMEM) e `clm-mem.bin` (CLMD). Cabeçalho ASCII com offsets.

## RMEM (TN/LIT) — região RWX gzip + tabela de sockets
```python
import re,gzip,hashlib
d=open('tn-mem.bin','rb').read()
m=re.search(rb'Image=(\S+) Off=(\d+) Len=(\d+) Prot=RWX Pack=gzip',d)
off,ln=int(m[2]),int(m[3]); dec=gzip.decompress(d[off:off+ln])
print(hashlib.sha256(dec).hexdigest(), dec.find(b'MZ'))    # MZ em 4096
# PE tem C2/Flag reais (o decoy tem CTF{not_this_one}); socket record: PID LE d4120000 -> IP nos bytes seguintes
```
TN: PID 4820, Off 59904, Len 793639, sha b81d...7dc8, MZ 4096, C2 .../v1/heartbeat,
socket 198.51.100.88:80, **CTF{rmem_tn_relay}**
LIT: PID 5108, Off 59904, Len 793690, sha e57a...fb09, C2 .../litoral-dns, 198.51.100.88:80, **CTF{rmem_lit_relay}**

## CLMD — SLOT cfg AES + socket 20 bytes
```bash
dd if=clm-mem.bin bs=1 skip=27489 count=12208 > cfg.enc
openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:CLMClient -S c1e10e0ec1e10e0e -in cfg.enc
```
Station CLM-MESA-014 · User marina.alves · KeyHint CLMClient · Salt c1e10e0ec1e10e0e ·
SockOff 8448 SockStride 20 · SLOT json aes Off 27489 Len 12208 ·
hta .../clm-login.hta · pass SE03-13800 · c2 .../clm-login · socket PID 6280 (BE) IP 198.51.100.88 ·
**CTF{rmem_clm_relay}**
