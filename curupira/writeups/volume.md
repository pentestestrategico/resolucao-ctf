# Volume (residual em arquivos gigantes ~180-230MB)

Uma única entrada "residual" escondida em enorme volume de ruído. Flags XOR-encoded (hex).

## tn-span.pcap (POST residual)
```bash
tshark -r tn-span.pcap -Y 'http.request.method==POST' -T fields -e ip.src -e http.host -e http.request.uri -e http.user_agent -e http.file_data
```
src 10.50.10.42 · host update.induscom-cdn.net · uri /v1/last-ack · UA IndusCom-Sync/3.4.12
Body hex XOR key "13800" -> `cmd=LASTACK gw=tn-gw-se03 c2=198.51.100.88 flag=CTF{span-last}`

## lit-queries.jsonl (query TXT NXDOMAIN)
```bash
grep -a '"qtype":"TXT"' lit-queries.jsonl | grep NXDOMAIN
# {qname status.litoral-dns.net, src 10.70.20.17, node lit-rec-01, txt "2b3b2a1f..."}
python3 -c "b=bytes.fromhex('2b3b2a1f47180a170442040b410f18');k=b'hold-key';print(bytes(c^k[i%len(k)] for i,c in enumerate(b)))"  # CTF{jsonl-hold}
```

## clm-audit.ndjson (APPLY pending)
```bash
grep -a '"op":"APPLY"' clm-audit.ndjson | grep '"status":"pending"'
# batch settlement_batch, target clearing_db, trigger pre-settle, host clm-file-01, meta "72677e4b..."
python3 -c "b=bytes.fromhex('72677e4b5e55594b5f5e1c5248405c484e');k=b'13800';print(bytes(c^k[i%len(k)] for i,c in enumerate(b)))"  # CTF{ndjson-apply}
```
**Dica:** chaves XOR recorrentes = `13800` e `hold-key`.
