# Reverse

## tn-upd.exe (PE32+)
```bash
objdump -f tn-upd.exe            # file format pei-x86-64 ; architecture i386:x86-64
objdump -p tn-upd.exe | grep Magic   # 020b (PE32+)
objdump -p tn-upd.exe | grep -A12 'Name Pointer Table'  # exports: campaign (ord0), family (ord1)
python3 -c "import re;d=open('tn-upd.exe','rb').read();print(re.search(r'CTF\{[^}]+\}',d.decode('utf-16-le','ignore')).group())"  # CTF{pe64-se03}
```

## lit-hold.so (ELF64 UPX)
```bash
readelf -h lit-hold.so | grep Class   # ELF64 (packed)
upx -l lit-hold.so                    # linux/amd64
upx -d lit-hold.so                    # descompacta
readelf -d lit-hold.so | grep SONAME  # lit-hold.so
objcopy -O binary --only-section=.obsid lit-hold.so /dev/stdout   # lit-hold
# .flag @ file offset -> UTF-16LE CTF{upx-hold}
```

## ClmSettle.class (Java 17 / major 61)
```bash
xxd -p -l4 ClmSettle.class           # cafebabe
javap -p -constants ClmSettle.class  # public class ClmSettle; FAMILY="ObsidianHold"
python3 -c "import re;d=open('ClmSettle.class','rb').read();print(re.search(rb'C\x00T\x00F\x00.*?\}\x00',d).group().decode('utf-16-le'))"  # CTF{cls-settle} (overlay)
```
