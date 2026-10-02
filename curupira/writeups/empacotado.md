# Empacotado (membro residual em tar/cpio/zip gigantes)

Membro único não-ruído; conteúdo XOR (key `13800` p/ TN/CLM, `hold-key` p/ LIT).

## tn-occ.tar
```bash
tar -tf tn-occ.tar | grep -v metrics-       # se03-last.dat
tar -xOf tn-occ.tar se03-last.dat | python3 -c "import sys;b=sys.stdin.buffer.read();k=b'13800';print(bytes(c^k[i%len(k)] for i,c in enumerate(b)).decode())"
# src 10.50.10.88, gw tn-gw-se03, fc 6, flag CTF{tar-se03}
```

## lit-rec.cpio
```bash
cpio -tv < lit-rec.cpio | grep -v zone-     # hold-check.txt
cpio -i --to-stdout hold-check.txt < lit-rec.cpio | python3 -c "...k=b'hold-key'..."
# src 10.70.20.17, node lit-rec-01, qname status.litoral-dns.net, NXDOMAIN, CTF{cpio-hold}
```

## clm-batch.zip
```bash
unzip -l clm-batch.zip | grep pending       # pending/settlement_batch.apply
unzip -p clm-batch.zip pending/settlement_batch.apply | python3 -c "...k=b'13800'..."
# batch settlement_batch, target clearing_db, host clm-file-01, src 10.90.30.11, CTF{zip-apply}
```
