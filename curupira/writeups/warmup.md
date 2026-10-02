# Warmup

## evidence.zip — README engana; flag real em vendor/sync.txt
```bash
unzip -p evidence.zip README.txt      # manda abrir invoice.txt (CTF{not_this_one})
unzip -p evidence.zip vendor/sync.txt # CTF{readme_lies_relay}
unzip -z evidence.zip                 # comentário evidence_TN-FIN-WS042
```
SHA256 sync.txt 27d6...4f26 · downloads=222

## notes.txt — na verdade gzip (magic 1f8b), nome scratch.txt
```bash
file notes.txt; xxd -p -l2 notes.txt   # 1f8b
gzip -lN notes.txt; zcat notes.txt     # CTF{magic_gzip_relay}
```

## updater.bin — ELF64, seção .qr com PNG (QR)
```bash
readelf -S -W updater.bin              # .qr off 0x3037 size 0x142
dd if=updater.bin of=qr.bin bs=1 skip=$((0x3037)) count=$((0x142))
python3 -c "import cv2;im=cv2.imread('qr.bin');im=cv2.copyMakeBorder(im,40,40,40,40,0,value=(255,255,255));im=cv2.resize(im,None,fx=4,fy=4,interpolation=0);print(cv2.QRCodeDetector().detectAndDecode(im)[0])"  # CTF{elf_qr_relay}
strings updater.bin | grep -E 'C2|UA|Host|Version|Product|Section'
```
(offset/size aceitos como 3037 / 142, sem zeros à esquerda)

## firmware.bin — cabeçalho ICFW (magic 49434657) + payload gzip
```bash
OFF=512;LEN=1100534; tail -c +$((OFF+1)) firmware.bin | head -c $LEN > payload.gz
sha256sum payload.gz            # confere PayloadSha256 5e09...72a4
gzip -dc payload.gz             # Gateway tn-gw-se03, Site SE-03, C2..., CTF{icfw_blob_relay}
```

## telemetry.ndjson — 18036 objetos, flag no evento vendor_sync
```bash
jq -s length telemetry.ndjson                              # 18036
jq -r .event telemetry.ndjson | sort | uniq -c            # 8 tipos
jq -s '[.[]|select(.event=="heartbeat" and .host=="TN-FIN-WS042")]|length'  # 23
jq -c 'select(.event=="vendor_sync")' telemetry.ndjson     # dst 198.51.100.88, interval 90, flag CTF{jq_ndjson_relay}
```
