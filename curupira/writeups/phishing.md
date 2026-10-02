# Phishing

## bulletin.eml
```bash
# cabeçalhos: To ops.cardoso@transnorte.energia, From support@induscom.com (spoof),
# Return-Path relay@induscom-secure.net, Reply-To support@induscom-secure.net,
# Subject "ICG-4200 firmware bulletin", Message-ID relay-0812-se03@induscom-secure.net,
# recebido de 198.51.100.88. Corpo: Portal http://induscom-secure.net/firmware, CTF{phish_bulletin_relay}
```

## helpdesk.mbox (181 mensagens)
```bash
python3 -c "import mailbox;print(len(mailbox.mbox('helpdesk.mbox')))"   # 181
# msg da campanha: From support@induscom-secure.net, To carla.dias@litoral.telecom,
# Return-Path relay@induscom-secure.net, Reply-To ..., Message-ID relay-0812-lit@...,
# Received IP 198.51.100.88, Portal http://induscom-secure.net/litoral-dns, CTF{litoral_mbox_relay}
```

## harvest.eml (kit -> coletor; anexo form.dat)
```bash
python3 -c "import email;m=email.message_from_file(open('harvest.eml')); [print(p.get_filename(),p.get_payload(decode=True)) for p in m.walk()]"
```
To inbox@induscom-secure.net · From kit@induscom-secure.net · Subject "CLM capture" ·
Portal http://induscom-secure.net/clm-login ·
form.dat: User marina.alves@clm.liquidacao / Pass **SE03-13800** / Host CLM-MESA-014 / UA CLMClient/3.4 ·
**CTF{clm_harvest_relay}**  (a senha SE03-13800 reaparece para decifrar blobs em Intel/Final)
