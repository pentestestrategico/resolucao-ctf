# Ransomware

Cada .enc tem cabeçalho com KeyOff/BakOff/IVs. Chave montada de pedaços do arquivo.

## tn-occ.enc (AES-256-CBC)
```python
# key = KeyOff(24 bytes) || BakOff(8 bytes) = 32 bytes ; iv = EncIv
openssl enc -d -aes-256-cbc -nopad -K <key> -iv <EncIv> -in occ.ct
```
Setpoint 13800 · **CTF{IR-SE03-13800}**

## lit-zone.enc (AES-128-CBC, Kdf sha256)
```python
# key = SHA256(KeyOff(16) || BakOff(16))[:16] ; iv = ZnIv
openssl enc -d -aes-128-cbc -nopad -K <key16> -iv <ZnIv> -in zone.ct
```
Serial 2026081201 · **CTF{soa:2026081201}**

## clm-settle.enc (AES-256-CBC; KeyOff é isca PAYNOW, chave real em BakOff/VSS)
```python
# KeyOff[:6]=="PAYNOW" (isca) ; key real = BakOff (32 bytes, BakKind VSS) ; iv = BatIv
openssl enc -d -aes-256-cbc -nopad -K <bak32> -iv <BatIv> -in bat.ct
```
BatchId SB-20260812-014 · Amount 481500 · **CTF{VSS-OK-NOPAY}**
