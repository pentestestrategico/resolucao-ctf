# Persistência

Registros de tamanho fixo + tabela de nomes (KEY=/VAL=/RID=/CMD=/UID=/FIL=/CON=).
Cada record tem offsets de hash (32 bytes) e payload AES (key=hash, iv do cabeçalho).

## tn-registry.pol (PReg, GPO INDUSCOM-FINANCE)
```python
# achar record RegBin(3) cuja KEY = ...\CurrentVersion\Run (não RunOnce!)
# rec 3741: KEY Software\Microsoft\Windows\CurrentVersion\Run, VAL ObsidianUpdater, RID backup_svc,
#           HASH d511...280b (== update.bin)
openssl enc -d -aes-256-cbc -nopad -K d511...280b -iv <PolIv> -in pol.ct   # CTF{preg_tn_relay}
```

## lit-atjobs.bin (AtJb)
```python
# job Uid=0(root) CMD=/usr/lib/induscom/dns-update.bin, HASH 1225...1177
openssl enc -d -aes-256-cbc -nopad -K <hash> -iv <AtIv> -in at.ct   # CTF{atd_lit_relay}
```

## clm-wmi.bin (WmiE, BindKind 3)
```python
# binding Kind=3 RID 1300(svc-wipe): FIL market_close, CON CommandLineEventConsumer, HASH 1339...bd58
openssl enc -d -aes-256-cbc -nopad -K <hash> -iv <WmiIv> -in wmi.ct  # CTF{wmi_clm_relay}
```
