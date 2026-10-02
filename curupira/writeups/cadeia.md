# Cadeia (supply chain)

## cg4200.deb
```bash
dpkg-deb -I cg4200.deb; dpkg-deb -c cg4200.deb
dpkg-deb -x cg4200.deb x; cat x/etc/induscom/icg4200.conf x/usr/share/induscom/icg4200/channel.txt
```
Package induscom-icg4200 3.4.12 · Maintainer support@induscom.com · Homepage .../firmware ·
XB-Host TN-FIN-WS042 · conf ./etc/induscom/icg4200.conf (C2 .../v1/heartbeat) ·
dropper ./usr/lib/induscom/update.bin · **CTF{deb_icg4200_relay}**

## dns.rpm
```bash
rpm -qip dns.rpm; rpm -qlp dns.rpm
rpm2cpio dns.rpm | cpio -idm; cat etc/induscom/dns.conf usr/share/induscom/dns/channel.txt
```
induscom-dns 3.4.12 · Vendor IndusCom · URL .../litoral-dns · Packager support@induscom-secure.net ·
BuildHost LIT-NMS-02 · conf /etc/induscom/dns.conf · /usr/lib/induscom/dns-update.bin · **CTF{rpm_dns_relay}**

## clm-repo.tar (repositório apt)
```bash
tar -xf clm-repo.tar -C repo; cat repo/InRelease
sha256sum repo/Packages                         # confere InRelease
grep -A6 induscom-clm repo/Packages             # Filename pool/clm-agent.bin
strings repo/pool/clm-agent.bin | grep CTF      # CTF{repo_clm_relay}
```
Origin IndusCom · Label CLM-Liquidacao · Suite relay · Codename se03 · Hash SHA512 ·
Package induscom-clm entre ~1800 pacotes-ruído
