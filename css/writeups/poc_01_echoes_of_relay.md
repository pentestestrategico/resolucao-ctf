# PoC — Echoes of the Relay (Forensics, 33 pts) — #1

**Flag:** `CSSCTF{d3l3t3d_d03snt_m34n_g0n3}`  *(encontrada, não submetida)*

## Enunciado
Imagem de storage `relay_backup.img` (ext4 "KUIPER_RELAY"). O operador "tentou preservar algo" antes do shutdown. Arquivos visíveis são inúteis.

## Passos
1. **Listar arquivos deletados** com debugfs:
   ```bash
   debugfs -R "lsdel" relay_backup.img
   # Inode 25, size 303, deleted
   debugfs -R "cat <25>" relay_backup.img
   ```
   A nota recuperada (inode 25) revela:
   - `archive password = severance2101`
   - *"I attached the recovery package to the diagnostic image... Look beyond what the image viewer shows you."*
2. **Extrair a PNG** `operator/Pictures/relay_status.png` e detectar dados anexados:
   ```bash
   debugfs -R "dump /operator/Pictures/relay_status.png relay_status.png" relay_backup.img
   binwalk relay_status.png
   # Zip archive (encrypted) em offset 0x4B4A (19274): transmission/manifest.txt, core_recovery.txt
   ```
3. **Carvar e descriptografar** o ZIP anexado (PNG+ZIP polyglot):
   ```bash
   dd if=relay_status.png of=hidden.zip bs=1 skip=19274
   unzip -P severance2101 hidden.zip
   cat transmission/core_recovery.txt
   ```

## Resultado
```
The Nexus remembers what the filesystem forgets.
CSSCTF{d3l3t3d_d03snt_m34n_g0n3}
```

## Lição
Arquivos deletados persistem em inodes até serem sobrescritos (`lsdel`/`cat <inode>`). Dados podem ser anexados após o `IEND` de um PNG (polyglot PNG+ZIP), invisíveis a um visualizador de imagens.
