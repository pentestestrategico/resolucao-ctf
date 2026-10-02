# Stego

`IndusCom_ReleaseNotes.pdf`, `se03.jpg`, `report.docx`, `se03_radio.wav`.
Padrão: metadados + arquivo escondido (zip colado após EOF / stream extra).

## PDF
```bash
pdfinfo IndusCom_ReleaseNotes.pdf                 # 36 pág, PDF 1.7, letter 612x792
strings IndusCom_ReleaseNotes.pdf | grep -E '/Manager|/Station|/Gateway|/Build'
pdftotext IndusCom_ReleaseNotes.pdf - | grep -E 'Model|Site|C2|Setpoint'
pdfdetach -saveall -o out IndusCom_ReleaseNotes.pdf; cat out/*   # vendor_sync.txt -> sync.php
python3 -c "d=open('...pdf','rb').read();z=d.find(b'PK\x03\x04');open('t.zip','wb').write(d[z:])"
unzip -p t.zip relay.txt                            # CTF{pdf_notes_relay}
```
Title IndusCom_ReleaseNotes · Author release.eng · Manager ops.cardoso · Station TN-FIN-WS042 ·
Gateway tn-gw-se03 · Firmware 3.4.12 · Build R4200-184320 · Model ICG-4200 · Site SE-03 ·
C2 .../v1/heartbeat · IP 198.51.100.88 · Setpoint 13800

## JPG (EXIF + zip)
```bash
exiftool -n -GPSLatitude -GPSLongitude -GPSAltitude se03.jpg   # -3.1195 / -60.0218 / 87
# zip colado: field.txt -> CTF{jpeg_se03_relay}
```
ImageDescription SE-03_bay2_relay · Make IndusCom · Model IC-CAM-4200 · Software IndusCom_Capture_3.4.12 ·
DateTimeOriginal 2026:08:12 10:18:44 · Artist ops.cardoso · HostComputer TN-FIN-WS042 ·
Serial IC4200-SE03-042 · Copyright Transnorte_Energia · Comment setpoint_13800 · Width 2560

## DOCX (OOXML zip)
```bash
unzip -p report.docx docProps/core.xml     # title OCC_SE03_incident, creator ops.cardoso, etc
unzip -p report.docx docProps/app.xml       # Company Transnorte_Energia, Application Microsoft_Word
unzip -p report.docx word/document.xml | sed 's/<[^>]*>/\n/g' | grep ': '  # Setpoint/Gateway/Src/C2/Firmware/Station
unzip -z report.docx                         # comentário IndusCom_ICG-4200
unzip -p report.docx word/media/vendor.hint  # CTF{docx_occ_relay}
```

## WAV (RIFF INFO + zip)
```bash
python3 -c "import wave;w=wave.open('se03_radio.wav');print(w.getnframes(),w.getframerate(),w.getnchannels(),w.getsampwidth()*8)" # 1764000 44100 1 16
# zip colado: radio.txt -> CTF{wav_se03_relay}
```
Title SE-03_OCC_radio · Artist ops.cardoso · Engineer tn-gw-se03 · Genre Campaign_Relay · Product ICG-4200 ·
Technician TN-FIN-WS042 · Subject SE-03_bay2_relay · Date 2026:08:12
