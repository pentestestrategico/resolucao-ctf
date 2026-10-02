# Crypto

Cada arquivo tem cabeçalho ASCII com os parâmetros. Flags no plaintext.

## vendor_note.txt — hex(base64(texto))
```bash
sed -n '9,$p' vendor_note.txt | tr -d '\n ' | xxd -r -p | base64 -d
```
Encoding hex_of_base64 · Host TN-FIN-WS042 · Operator ops.cardoso · Channel vendor_update ·
Gateway tn-gw-se03 · Firmware 3.4.12 · Model ICG-4200 · C2 .../v1/heartbeat · IP 198.51.100.88 ·
Setpoint 13800 · Src 10.50.10.88 · Build R4200-184320 · Case IR-2026-0812-SE03 · **CTF{b64hex_relay}**

## heartbeat.xor — XOR de chave repetida (hex)
```bash
sed -n '9,$p' heartbeat.xor | tr -d '\n ' | xxd -r -p > hb.bin
python3 -c "k=b'ObsidianUpdater';d=open('hb.bin','rb').read();open('hb.plain','wb').write(bytes(b^k[i%len(k)] for i,b in enumerate(d)))"
```
Key ObsidianUpdater · UA ObsidianUpdater/2.1 · Path /v1/heartbeat · Interval 300 ·
Beacon update.induscom-cdn.net · Src 10.50.10.42 · Dst 198.51.100.88 · **CTF{xor_beacon_relay}**

## update.enc — AES-256-CBC pbkdf2, pass no cabeçalho (ICG-4200)
```bash
sed -n '10,$p' update.enc | tr -d '\n ' | xxd -r -p > up.bin
openssl enc -d -aes-256-cbc -pbkdf2 -in up.bin -pass pass:ICG-4200
```
URL .../payload/update.exe · Drop .../Downloads/update.exe · Hash a7c9...f80 · **CTF{aes_update_relay}**

## recovery.pem — RSA-2048 PKCS1 (chave privada no próprio arquivo)
```bash
sed -n '8,35p' recovery.pem > rsa.key
sed -n '38,45p' recovery.pem | tr -d '\n ' | xxd -r -p > rsa.bin
openssl pkeyutl -decrypt -inkey rsa.key -in rsa.bin -pkeyopt rsa_padding_mode:pkcs1
```
Gateway tn-gw-se03 · Firmware 3.4.12 · C2 .../v1/heartbeat · Src 10.50.10.88 ·
Station TN-FIN-WS042 · **CTF{rsa_recovery_relay}**
