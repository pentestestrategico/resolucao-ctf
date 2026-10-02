# Interceptação

## tn-c2.cms (CMS SignedData)
```bash
openssl asn1parse -inform DER -in tn-c2.cms
# contentType pkcs7-signedData ; digestAlgorithm sha256 ; CN update.induscom-cdn.net
# eContent OCTET STRING = "SETPOINT\n" + UTF-16LE "CTF{cms-setpt}"
```

## lit-c2.ws (frames WebSocket)
```python
# frame0: op1(text) "HOLD" ; frame1: op1 mask=1 key c2010b51 "lit-rec-01" ;
# frame2: op2(bin) len24 UTF-16LE "CTF{ws-hold}"
```
opcode 1 · masking-key c2010b51 · len 24

## clm-c2.grpc (gRPC framing + protobuf)
```python
# byte compressão 0 ; len uint32 BE 54 ; protobuf f1=WipeBatch f2=clearing_db f3=UTF-16LE CTF{grpc-wipe}
```
