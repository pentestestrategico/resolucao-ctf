# SQLite

`history.db` (Chrome), `historian.db` (SCADA), `vpn.db` (OpenVPN AAA).

```bash
sqlite3 history.db ".schema"
sqlite3 history.db "select * from meta"
sqlite3 history.db "select url,title,visit_count,typed_count,hidden from urls order by visit_count desc"
sqlite3 history.db "select * from downloads"
sqlite3 history.db "select * from keyword_search_terms"
```
## history.db
meta: host TN-FIN-WS042, user ops.cardoso, ip 10.50.10.42, browser Chrome,
profile C:/Users/ops.cardoso/AppData/Local/Google/Chrome/User_Data/Default.
Página top /occ/dashboard (OCC_Dashboard, 847, typed 2, login typed 14).
Beacon http://update.induscom-cdn.net/v1/heartbeat, 1a visita 2026-08-12T10:04:00Z,
transition GENERATED, 48 visitas. Webshell .../vendor/sync.php.
Download update.exe: C:/Users/ops.cardoso/Downloads/update.exe de
http://update.induscom-cdn.net/payload/update.exe, mime application/x-msdownload,
danger allow, referrer ReleaseNotes, 184320 bytes, 2026-08-12T09:19:40Z.
Busca "IndusCom updater". downloads=222 linhas.
**URL hidden=1 title = CTF{chrome_hist_relay}**

## historian.db
meta: host tn-gw-se03, site SE-03, IndusCom_Historian, ICG-4200, fw 3.4.12,
master 10.60.10.5, slave 10.60.10.31.
```sql
select name,address,unit_id from tags;        -- SE03_SETPOINT addr 40081 unit 1; SE03_BRK_TRIP addr 3
select src,count(*) from samples group by 1;  -- telemetria 10.60.10.5
select * from commands;                        -- 10.50.10.88 fc6 40081 13200->13800 (10x), 1a 10:18:44Z txn 0x4a21
select * from alarms;                          -- critical CTF{historian_se03_relay}; samples 13800 quality suspect
```
tags=12 · SE03_V_AB addr 40011 · coil ts 2026-08-12T10:22:11Z

## vpn.db
meta host tn-vpn-01, product OpenVPN_AAA, realm transnorte.local, proto openvpn, pool 10.50.200.0/24.
```sql
select src,count(*) from auth_events where result='failed' group by 1 order by 2 desc;  -- 198.51.100.88 (412), scanner 10.50.10.88 (root)
select * from auth_events where src='198.51.100.88' and result='accepted';  -- backup_svc port44122 pid19001 04:12:08Z password
select * from sessions where username in('backup_svc','ops.cardoso');
-- backup_svc src 198.51.100.88 assigned 10.50.200.88 bytes 94812 end 17:40:00Z dur 48472 grp svc_backup status enabled note CTF{vpn_aaa_relay}
-- ops.cardoso src 10.50.10.42 assigned 10.50.200.42 pubkey
```
sessions=7002 · alvo brute backup_svc
