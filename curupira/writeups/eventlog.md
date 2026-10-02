# Event Log EVTX

`tn-security.evtx` (ElfFile sintético) e `clm-security.etl` (EvtW sintético). Registros de tamanho fixo.

## tn-security.evtx (RecSize 128, SID table em SidOff)
```python
import struct,hashlib
# rec: magic 2a2a, EventID@4, RecNum@8, LogonId@16(8b), type@24, wksRID@28, SID RID@56, payload@64
# 1) achar 4624 (0x1210) type 3 wksRID 2100 SID RID 1002 -> LogonId a308120000000000, wks TN-FIN-WS042
# 2) 4662 (0x1236) mesmo LogonId -> GUID@64 adf63111079cd111f79f00c04fc2dcd2, RID 1002 (backup_svc)
# 3) 4672 (0x1240) mesmo LogonId -> payload AES key=SHA256(LogonId), iv=RecIv
```
```bash
openssl enc -d -aes-256-cbc -nopad -K $(python3 -c "import hashlib;print(hashlib.sha256(bytes.fromhex('a308120000000000')).hexdigest())") -iv <RecIv> -in rec4672.ct  # CTF{evtx_tn_relay}
```

## clm-security.etl (RecSize 112, ActivityId@8 16b, RID table em TabOff)
```python
# achar 4720 (0x1270) cujo target(f28)==1300 -> ActivityId 5a269d09621f2cadb1cc5159f2def988
# 4732 (0x127c) mesma ActId -> grupo alvo MESA-OPS
# 4624 (0x1210) mesma ActId -> computer CLM-FILE-01, target svc-wipe, payload AES key=SHA256(ActId) iv=EtwIv
```
Domain CLM.LOCAL · flag **CTF{etl_clm_relay}**
