# PCAP

3 capturas: `captura.pcap` (TN-FIN), `captura2.pcap` (Litoral), `captura3.pcap` (CLM).

## Técnica geral
```bash
tshark -r captura.pcap -Y "dhcp" -T fields -e dhcp.option.hostname -e dhcp.ip.your \
  -e dhcp.option.router -e dhcp.option.domain_name_server -e dhcp.option.domain_name
```

## captura.pcap (Transnorte / TN-FIN-WS042)
| Item | Comando/filtro | Resposta |
|---|---|---|
| Hostname DHCP | `dhcp.option.hostname` | TN-FIN-WS042 |
| Lease (yiaddr) | `dhcp.option.dhcp==5` -> `dhcp.ip.your` | 10.50.10.42 |
| MAC | `eth.src` de `ip.src==10.50.10.42` | 00:1a:2b:3c:4d:42 |
| Gateway | `dhcp.option.router` | 10.50.10.1 |
| DNS | `dhcp.option.domain_name_server` | 10.50.10.10 |
| Domínio | `dhcp.option.domain_name` | transnorte.local |
| FTP USER/PASS | `ftp` | backup_svc / Relay!2024Bk |
| RETR | `ftp.request.command==RETR` | substation_map_v3.pdf |
| Host FTP | ip.dst | 10.50.10.30 |
| Beacon UA | `http.user_agent` não-browser | CTF{ObsidianUpdater/2.1} |
| Host beacon | `http.host` | update.induscom-cdn.net |
| URI beacon | `http.request.uri` | /v1/heartbeat |
| Flag ReleaseNotes | `http.file_data` do GET /vendor/IndusCom_ReleaseNotes.txt | CTF{relays_are_not_updates} |
| POST senha OCC | `http.request.method==POST` file_data | WinterGrid#19 |
| TXT litoral | `dns.txt` | CTF{backbone_hold_ok} |
| cdn-sync FQDN / IP | `dns.qry.name contains cdn-sync` | cdn-sync.induscom-support.net / 198.51.100.88 |
| DNS b64 label | label Q1RG... base64 -d | CTF{dns_sidechannel_ok} |
| SNI TLS | `tls.handshake.extensions_server_name` p/ 198.51.100.91 | relay-api.obsidian-cdn.net |
| ICMP flag | `data.data` de icmp p/ 198.51.100.50 | CTF{echo_is_not_dead} |
| Cookie OCC | `http.cookie` /occ/dashboard | 7f3c9a21e04b18d6 |
| Basic OT | `http.authorization` (base64 -d) | monitor:Rel3Aux-OT |
| Server httpd | `http.server` | IndusCom-HTTPD/0.9 |
| Host WPAD | `http.host` de /wpad.dat | wpad.transnorte.local |
| Scan p/ 10.50.10.20 | SYN sem ACK, contagem de portas distintas por src | 10.50.10.88 |

## captura2.pcap (Litoral / LT-NMS-07)
Hostname LT-NMS-07, lease 10.70.20.17, MAC 00:1c:df:70:20:17, GW 10.70.20.1,
DNS 10.70.20.53, domínio litoral-telecom.net.
- MX `dns.qry.type==15`: mail.litoral-telecom.net
- SMTP AUTH LOGIN (base64): nms.relay / MailSpan9 ; RCPT occ-alerts@transnorte.local
- HTTP 302 Location: http://vendor-login.induscom-support.net/sso
- token /api/tickets: 9f2c18ab44e1
- syslog flag: CTF{syslog_span_ok}
- SNMP community `snmp.community`: Rel3Read
- SNI p/ 198.51.100.76: telemetry.obsidian-cdn.net
- CNAME www: portal.litoral-telecom.net ; PDF /files/backbone_runbook.pdf
- POP3 USER/PASS: nina.vargas / NightSpan7
- SSH banner 10.70.20.22: SSH-2.0-IndusCom_Dropbear_2024
- UA LitoralNMS: CTF{LitoralNMS/3.4} ; cookie NMSSESS=a1b2c3d4e5f60789
- edge-check FQDN/IP: edge-check.induscom-support.net / 198.51.100.77
- Referer: http://portal.litoral-telecom.net/nms ; Server: LitoralEdge/2.1

## captura3.pcap (CLM / CLM-OPS-WS11)
Hostname CLM-OPS-WS11, lease 10.90.30.11, MAC 00:0c:29:90:30:11, GW 10.90.30.1,
DNS 10.90.30.10, domínio clm.local.
- LDAP simple bind: cn=svc.bind,ou=ops,dc=clm,dc=local / ClearBind8
- TFTP RRQ: settlement_batch.csv
- RADIUS User-Name: clm-radius-ops
- MQTT CONNECT user/clientid/pass: bus.clm / clm-ops-ws11 / MqttGrid7
- SRV _ldap._tcp.clm.local: ldap.clm.local:389
- Bearer/apikey: clm_live_8e4a91 ; X-Forwarded-For: 10.90.30.200
- SNI p/ 198.51.100.66: settle-api.obsidian-cdn.net
- ICMP flag: CTF{clm_echo_ok} ; cookie CLMSESS=c0ffee11aabb09
- batch-sync FQDN/IP: batch-sync.induscom-support.net / 198.51.100.67
- UA ClmDesk: CTF{ClmDesk/1.6} ; Host api.clm.local ; Server ClmGateway/4.0
