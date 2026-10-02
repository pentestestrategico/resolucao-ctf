# Firmware

## icg4200-3.4.12.fw (uImage + squashfs)
```bash
xxd -l 80 icg4200-3.4.12.fw          # ih_name@32 "ICG-4200", ih_load@0x10 80008000
dd if=... of=fw.squashfs bs=1 skip=64  # squashfs em offset 64, magic hsqs, comp id 4 (xz)
unsquashfs -d fwroot fw.squashfs; cat fwroot/etc/hostname   # tn-gw-se03
strings -el fwroot/usr/lib/induscom/channel | grep CTF       # CTF{hsqs-se03}
```

## lit-nms.initramfs (gzip -> cpio newc)
```bash
python3 -c "d=open('lit-nms.initramfs','rb').read();print(d[10:d.index(b0,10)])"  # FNAME nms.cpio
gzip -dc lit-nms.initramfs > nms.cpio; xxd -p -l6 nms.cpio    # 303730373031 (070701)
mkdir r;cd r;cpio -idm < ../nms.cpio; cat etc/hostname        # lit-nms-02
grep -i serial etc/bind/named.conf                            # 2026081201
strings -el usr/lib/litoral/token | grep CTF                  # CTF{cpio-hold}
```

## clm-meter.jffs2 (parser manual, sem jefferson)
```python
# nós: DIRENT 0xe001 (nome/ino), INODE 0xe002 (csize@48 dsize@52 compr@56 data@68, COMPR_NONE=0)
# magic 8519 (0x1985 LE), hostname ino 6, dnp3.dst=50, crob.idx=7, token CTF{jffs2-idx7}
```
