# Mídia (residual em ISO/BMP/NetFlow gigantes)

## tn-last.iso
```bash
# PVD (offset 0x8000): Volume set id RELAYDUMP, prep tn-occ-hmi, vol size 92342 setores
7z x -oisox tn-last.iso; md5sum isox/lastack.dat   # bcd23a4531e01d0a35f0911faa04cd27
cat isox/lastack.dat                                # base32 -> CTF{iso-lastack}
python3 -c "import base64;print(base64.b32decode('INKEM63JONXS23DBON2GCY3LPU======'))"
```

## lit-hold.bmp (4096 x 17066, 24bpp, xppm 44122)
```python
# pixel único RGB 255,0,88 em X=88 (marcador)
# flag escondida no canal B de pixels consecutivos na linha 9386, x=200.. :
# bytes 43 54 46 7b 62 6d 70 2d 68 6f 6c 64 7d -> CTF{bmp-hold}
```

## clm-flows.nf5 (NetFlow v5)
```python
# header: unix_secs 1786511111, sysUpTime 90422188
# flow prot=47 (GRE): src 10.90.30.11, src_as 64512, dst 198.51.100.88
# flag nos campos dPkts/dOctets/first do registro GRE, XOR 0xFF (NOT):
# bcabb984 9199cad2 988d9a82 ^ FF -> CTF{nf5-gre}
```
