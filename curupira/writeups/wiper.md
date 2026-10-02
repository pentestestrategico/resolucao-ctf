# Wiper

## tn-wipe.ima (FAT12)
```bash
dd if=tn-wipe.ima bs=1 skip=3 count=8     # OEM INDUSCOM
dd if=tn-wipe.ima bs=1 skip=43 count=11   # Volume Label SE03WIPE
7z x -ofatx tn-wipe.ima; cat fatx/target.txt fatx/trigger.txt   # se03-boot / outage_window
strings -el fatx/flag.bin                 # CTF{fat12-se03}
```

## lit-wipe.cramfs (CramFS)
```bash
xxd -p -l4 lit-wipe.cramfs                 # 453dcd28 (magic)
dd if=lit-wipe.cramfs bs=1 skip=48 count=16 # Label LIT-REC-WIP
7z x -ocrx lit-wipe.cramfs; cat crx/mtd/name crx/wipe/when   # mtdblock0 / dns_hold
strings -el crx/rom/token                  # CTF{cram-mtd0}
```

## clm-wipe.wim (WIM v1.13)
```bash
xxd -l24 clm-wipe.wim                       # version @0x0c 000d0100 -> 1.13
7z x -owimx clm-wipe.wim; cat wimx/etc/hostname wimx/settle/target wimx/settle/trigger
# clm-file-01 / settlement_batch / market_close
strings -el wimx/lib/token                  # CTF{wim-settle}
```
