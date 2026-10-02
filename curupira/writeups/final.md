# Final

## tn-revoke.p7m — CMS EnvelopedData (RESOLVIDO)
O arquivo traz a **chave privada RSA embutida** (magic `KPRIV`, PKCS8 PBES2
aes-256-cbc) protegida pela senha **`13800`** (a mesma "senha do setpoint").
```bash
# 1) extrair o PKCS8 (SEQUENCE 30 82 05 2d após "KPRIV") e abrir com a senha
openssl pkcs8 -inform DER -in kpriv.der -passin pass:13800 -out priv.pem
# 2) CEK = RSA-decrypt do encryptedKey (256 bytes, offset 99 no p7m)
openssl pkeyutl -decrypt -inkey priv.pem -in cek.enc   # -> CEK
# 3) conteúdo = AES-256-CBC(CEK, IV=C655F88D64878551C0279E308E241A05)
openssl enc -d -aes-256-cbc -K <CEK> -iv C655...1A05 -in cont.enc
```
Resultado: `cmd=KILLUPD gw=tn-gw-se03 fw=3.4.12 c2=198.51.100.88 flag=CTF{p7m-se03}`

## lit-unhold.dns — DNS UPDATE (RESOLVIDO)
opcode 5 · action UNHOLD · node lit-rec-01 · TSIG hold-key · CTF{dns-unhold}
(TXT records em hex; label do TSIG "686f6c642d6b6579" -> hold-key)

## clm-abort.p12 — container "P12GO" + PKCS12 + blob AES1 (RESOLVIDO)
```bash
dd if=clm-abort.p12 bs=1 skip=2629 > p12b.blob   # OpenSSL Salted__ AES-256-CBC pbkdf2
# TLV alvo: target/action/vendor/trigger/flag
```
Cabeçalho: SEQUENCE{ 0x2A, 0x07EA(2026), 0x35E8(13800), 0x0C } + magic "P12GO",
friendlyName "portal", MacData (salt 5a8c360fb2dc7a98, iter 2048, sha256).
Passos:
```bash
# 1) senha do PKCS12 = INTEGER setpoint do prefixo = 0x35E8 = 13800
python3 -c "d=open('clm-abort.p12','rb').read();i=d.find(b'P12GO')+5;ln=int.from_bytes(d[i+2:i+4],'big');open('portal.p12','wb').write(d[i:i+4+ln])"
openssl pkcs12 -in portal.p12 -passin pass:13800 -nokeys -clcerts | openssl x509 -noout -modulus
# Modulus=891B3B58BB513373989B19F3452248F8...
# 2) chave AES = primeiros 32 hex do modulus, como passphrase openssl -pbkdf2
dd if=clm-abort.p12 bs=1 skip=2629 > p12b.blob
openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:891B3B58BB513373989B19F3452248F8 -in p12b.blob
```
TLV: target clearing_db · action ABORT · vendor IndusCom · trigger pre-settle · **CTF{p12-abort}**
