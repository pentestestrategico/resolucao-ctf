# Disco

`tn-disk.img` (NTFS), `lit-disk.img` (ext4), `clm-disk.dd` (MBR+NTFS). Sleuthkit/debugfs.

## tn-disk.img (NTFS)
```bash
fsstat tn-disk.img | grep -i 'volume name'      # TN-FIN-WS042
fls -r -p tn-disk.img
icat tn-disk.img 76                              # Startup\ObsidianUpdater.cmd -> C:\...\IndusCom\update.bin
icat tn-disk.img 69 | sha256sum                  # update.bin d511...280b
icat tn-disk.img 88 | tail -c +29 | iconv -f utf-16le -t utf-8   # $I -> C:\Users\ops.cardoso\Downloads\channel.txt
icat tn-disk.img 87                              # $R -> C2 .../v1/heartbeat
icat tn-disk.img 84                              # ADS Q3-report.txt:hidden -> CTF{ntfs_tn_relay}
```
perfil ops.cardoso · Startup ObsidianUpdater.cmd · path Users/ops.cardoso/AppData/Local/IndusCom/update.bin ·
Firmware 3.4.12 · Setpoint 13800 · SID S-1-5-21-2209041147-3361044348-30300820-1001

## lit-disk.img (ext4)
```bash
debugfs -R 'cat /etc/hostname' lit-disk.img      # LIT-NMS-02
debugfs -R 'cat /etc/passwd'; debugfs -R 'cat /etc/hosts'
debugfs -R 'cat /etc/cron.d/induscom-dns'        # /usr/lib/induscom/dns-update.bin
icat lit-disk.img 33 | sha256sum                 # dns-update.bin 1225...1177
fls -rd lit-disk.img                             # apagado inode 26
icat lit-disk.img 26                             # CTF{ext4_lit_relay}, C2 .../litoral-dns
```
Volume LITNMS02 · UID1000 carla.dias · unit induscom-dns.service · C2 dns.conf .../v1/heartbeat ·
hosts 198.51.100.88

## clm-disk.dd (MBR -> NTFS off 2048)
```bash
mmls clm-disk.dd                                 # NTFS 0x07 start 2048
fls -r -p -o 2048 clm-disk.dd
icat -o 2048 clm-disk.dd 71 | sha256sum          # clm-agent.bin 6d51...b8a0
icat -o 2048 clm-disk.dd 74                       # desk.cred Pass SE03-13800
icat -o 2048 clm-disk.dd 77 | strings            # clm-wipe.bin State staged Trigger market_close Target settlement_batch CTF{mbr_clm_relay}
```
Volume CLM-MESA-014 · perfil marina.alves · HTA clm-login.hta · agente Users/marina.alves/AppData/Local/IndusCom/clm-agent.bin
