# Intel

## tn-intel.xls (OLE + blob OpenSSL "Salted__" @6144)
```bash
# celulas = iscas. Blob real cifrado; senha = credencial coletada no phishing (SE03-13800)
dd if=tn-intel.xls bs=1 skip=6144 count=512 > xls.blob
openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:SE03-13800 -in xls.blob
# family=ObsidianUpdater campaign=RELE-SE03 c2=198.51.100.88 host=tn-occ-hmi flag=CTF{xls-rele}
```

## lit-intel.doc (OLE + overlay "HOLDGZ" gzip)
```python
import zlib
d=open('lit-intel.doc','rb').read(); i=d.find(b'\x1f\x8b\x08',d.find(b'HOLD'))
print(zlib.decompressobj(31).decompress(d[i:i+2000]))
# TLV: title HoldNote, family ObsidianHold, vendor IndusCom, target lit-rec-01, flag CTF{doc-hold}
```

## clm-intel.mmdb (MaxMind DB; campos codificados)
```python
import maxminddb
r=maxminddb.open_database('clm-intel.mmdb')
r.metadata().database_type       # hex -> CTF{mmdb-infra}
r.get('198.51.100.88')
# country.names.en (hex) Obsidian-Infra ; city.names.en (hex) clm-file-01
# autonomous_system_organization (ROT13 VaqhfPbz) IndusCom
# autonomous_system_number 173678091 -> IPv4 10.90.30.11
```
