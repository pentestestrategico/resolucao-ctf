# Acervo (residual em bases/arquivos ~180-210MB)

## tn-hist.db (SQLite)
```bash
sqlite3 tn-hist.db "select src,unit,holding,gw,quote(blob) from hist where fc=6 and val=13800"
# 10.50.10.88 | 1 | 40081 | tn-gw-se03 | blob 72677E4B... (XOR 13800) -> CTF{sqlite-se03}
```

## lit-nms.warc (WARC 1.0)
```bash
grep -a -B40 '409 Conflict' lit-nms.warc | grep WARC-Target-URI | tail -1  # http://status.litoral-dns.net/hold-check
# resposta 409: X-Src 10.70.20.17, X-Node lit-rec-01, X-Rcode NXDOMAIN, X-Txt 2b3b2a1f... (XOR hold-key) -> CTF{warc-hold}
```

## clm-wal.bin (WAL binário, magic CLMW)
```python
d=open('clm-wal.bin','rb').read(); i=d.find(b'CLMW\x03\x02'); rec=d[i:i+96]
# batch settlement_batch, target clearing_db, host clm-file-01
# IP bytes 70-73 = 0a5a1e0b = 10.90.30.11
# flag blob 72677e4b... XOR "13800" -> CTF{wal-apply}
```
