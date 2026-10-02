# Telecom

## lit-dns.dnstap (frame-streams + protobuf Dnstap)
```python
# frames: prefixo BE de 4 bytes; controle = len 0. Dnstap.message = field 14.
# Message: type1, family2, proto3, qaddr4, raddr5, query_port6, query_message10, response_message14
# achar resposta com rcode==2 (SERVFAIL)
```
identity lit-rec-01 · SERVFAIL qname occ.transnorte.local · query_port 53100 · rcode SERVFAIL ·
TXT de hold.litoral.local (UTF-16LE) **CTF{dtap-rcode2}**

## tn-rib.mrt (MRT BGP4MP)
```python
# header: ts(4) type(2)@4=0x10 subtype(2)@6=0x04 len(4)
# UPDATE de withdraw: peer_as 0000fbf4=64500; withdrawn = 180a3c0a (24 + 10.60.10.0)
# path attribute opcional (type 0x63) UTF-16LE CTF{wdraw-se03}
```
(plataforma aceitou type/subtype como 10 / 4, sem zeros)

## clm-qos.snmp (BER SNMPv2c SetRequest)
```bash
# community "qosHold"; sysName 1.3.6.1.2.1.1.5.0 = clm-pe-01
# ifDescr.14 = settle; ifSpeed.14 = 0x00fa00 = 64000 (CIR)
# enterprise 1.3.6.1.4.1.4200 OCTET STRING UTF-16LE = CTF{cir-64k}
```
