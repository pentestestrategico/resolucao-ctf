# LOG

Arquivos: `syslog.log`, `access.log`, `defender.log`, `modbus.log`.

## syslog.log (VPN tn-vpn-01)
```bash
grep -o 'host=[^ ]*' syslog.log | sort -u                    # tn-vpn-01
grep event=failed_password syslog.log | grep -o 'src=[^ ]*' | sort | uniq -c | sort -rn  # 198.51.100.88 (412)
grep event=invalid_user syslog.log | grep -o 'user=[^ ]*' | sort | uniq -c | sort -rn    # oracle (mais frequente)
grep 'src=198.51.100.88' syslog.log | grep accepted_password  # backup_svc, port=44122, pid=19001, 04:12:08Z
grep event=sudo syslog.log                                    # user=backup_svc cmd=/usr/bin/chmod tty=pts/0
grep event=notice syslog.log                                  # msg=CTF{vpn_side_door}
```
Respostas: host tn-vpn-01 · brute 198.51.100.88 · conta backup_svc · src_host update.induscom-cdn.net ·
porta 44122 · hora 2026-08-12T04:12:08Z · pid 19001 · sudo backup_svc / /usr/bin/chmod · tty pts/0 ·
cwd /home/backup_svc · user inventado oracle · scan interno 10.50.10.88 · volume 412 · facility auth ·
vpn_connect ops.cardoso de 10.50.10.42 tun0 · pubkey 10.50.10.42 -> ops.cardoso · cron root ·
link state up · unit openvpn.service · flag notice CTF{vpn_side_door}

## access.log (Apache)
```bash
grep 'auth/login' access.log            # POST 10.50.10.42 ops.cardoso 200, referer .../login, next=/occ
grep heartbeat access.log               # /v1/heartbeat, UA ObsidianUpdater/2.1, 1o 10:04:00Z, 8x
awk '$8==404{print $1}' access.log | sort | uniq -c | sort -rn   # 10.50.10.88 (186) UA curl/8.5.0
awk '$8==401' access.log                # /relay/status tools.transnorte.local user monitor
grep '^198.51.100.88' access.log        # GET /vendor/sync.php cmd=id
grep '/vendor/.sync/build' access.log   # CTF{apache_occ_trace} na query string
```
UA updater CTF{ObsidianUpdater/2.1} · release notes /vendor/IndusCom_ReleaseNotes.txt (files.transnorte.local,175 bytes)

## defender.log
```bash
grep 'event=malware_detected' defender.log | grep Obsidian    # Trojan:Win32/ObsidianUpdater.A
# path C:/ProgramData/IndusCom/update.exe sha256 a7c9...f80 pid 4820 parent explorer.exe
# action quarantine severity high engine 1.1.24080.9 sig 1.411.412.0, 6 linhas, 1a 10:04:01Z
grep network_block defender.log         # url .../v1/heartbeat dest 198.51.100.88
grep -i releasenotes defender.log        # notes=CTF{defender_caught_relay}
```
webshell HackTool:PHP/WebShell.B, C:/inetpub/wwwroot/vendor/sync.php sha256 bb11...ff55 · PUA:Win32/OfferCore

## modbus.log (gateway tn-gw-se03, ICG-4200, SE-03, porta 502)
```bash
grep event=write_single modbus.log | grep 'src=10.50.10.88'   # unit1 fc6 addr40081 value13800 (9x), 1a 10:18:44Z txn 0x4a21
grep event=poll_ok modbus.log | grep -o 'src=[^ ]*'|sort|uniq -c   # mestre 10.60.10.5 -> 10.60.10.31
grep -E 'write_coil|exception|session_probe|diag' modbus.log
# write_coil fc5 addr3 value FF00; exception=02 unit=247; session_probe src 198.51.100.88; diag notes=CTF{modbus_se03_relay}
```
