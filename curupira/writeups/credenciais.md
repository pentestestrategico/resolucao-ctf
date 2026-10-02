# Credenciais

## tn-ntds.bin — dump sintético NTDS (SYSKEY -> bootkey -> PEK -> hashes)
```python
import re,hashlib
d=open('tn-ntds.bin','rb').read()
# cabeçalho: PekOff/PekLen/HashOff/HashLen/PekIv/HashIv
kv=dict(re.findall(rb'([A-Za-z0-9]+)=([0-9a-f]{8})', d[512:66048]))
bootkey=b''.join(bytes.fromhex(kv[n].decode()) for n in (b'JD',b'Skew1',b'GBG',b'Data'))
pekkey=hashlib.sha256(bootkey).digest()
```
```bash
# PEK = AES-256-CBC(pekkey, PekIv) do PekOff ; tabela = AES-256-CBC(PEK, HashIv) do HashOff
openssl enc -d -aes-256-cbc -K <pekkey> -iv <PekIv> -in pek.ct   # PEK=2a4b...448d
openssl enc -d -aes-256-cbc -K <PEK> -iv <HashIv> -in hash.ct    # tabela user:rid:lm:nt
```
bootkey c6348ff6d16ac3b6366eb15e7ec5ff12 · pekkey b2e4...e1aa · PEK 2a4b...448d ·
NT ops.cardoso 5d5bb3c1b2098c1bc260ca47a6776891 · RID backup_svc 1002 ·
reuso NT: indus.vendor (mesmo NT de backup_svc) · **CTF{ntds_tn_relay}**

## dns-svc.ccache — ticket AES-256 (chave = SHA256 do SPN)
```bash
# cabeçalho: Realm LITORAL.LOCAL, Kdc LIT-DC-01, Count 72, TicketIv ...
# record DNS-SVC@LITORAL.LOCAL Off=17712 Len=144 SPN=DNS/LIT-NMS-02.LITORAL.LOCAL
KEY=$(printf 'DNS/LIT-NMS-02.LITORAL.LOCAL' | sha256sum | cut -d' ' -f1)
dd if=dns-svc.ccache bs=1 skip=17712 count=144 > tkt.ct
openssl enc -d -aes-256-cbc -K $KEY -iv <TicketIv> -in tkt.ct    # C2 .../litoral-dns, CTF{ccache_lit_relay}
```
chave cc89...6a5b

## marina.pfx — PKCS12, senha = SHA256(harvestPass + Account)
```bash
PASS=$(printf 'SE03-13800SVC-WIPE' | sha256sum | cut -d' ' -f1)   # 63ea...2bb1
dd if=marina.pfx bs=1 skip=512 count=2712 > marina.p12
openssl pkcs12 -in marina.p12 -nokeys -passin pass:$PASS          # CN marina.alves, OU SVC-WIPE, friendlyName CTF{pfx_clm_relay}
```
