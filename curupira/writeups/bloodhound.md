# Bloodhound

`tn-ad.json` (SharpHound v5), `lit-ad.zip` (SharpHound v5), `clm-ad.json` (BHCE).

## Transnorte (tn-ad.json) — obtido via retry do link direto
```bash
jq -c '.meta' tn-ad.json                              # domain TRANSNORTE.LOCAL
jq -r '.computers[]|select(.Properties.isdc==true)|.Properties.name'                # TN-DC-01
jq -r '.computers[]|select(.Properties.unconstraineddelegation and .Properties.isdc!=true)|.Properties.name'  # TN-JMP-01
jq -c '.users[]|select(.Properties.name=="OPS.CARDOSO@TRANSNORTE.LOCAL")|{ObjectIdentifier,MemberOf}'
jq -c '.domains[0].Aces'                               # GetChangesAll -> BACKUP_SVC
jq -c '.users[]|select(.Properties.name=="BACKUP_SVC@TRANSNORTE.LOCAL")|.Aces'      # GenericAll -> HELP_DESK
jq -r '.gpos[]|select(.Properties.description|test("CTF"))|.Properties'             # CTF{bh_tn_relay}
```
SID ops.cardoso ...-1001 · sessão TN-FIN-WS042 -> OPS.CARDOSO · grupo extra HELP_DESK · GPO INDUSCOM-FINANCE

## Litoral (lit-ad.zip)
```bash
unzip lit-ad.zip; jq .meta.type *_users.json
jq -c '.data[]|select(.Properties.name=="CARLA.DIAS@LITORAL.LOCAL")|{ObjectIdentifier,MemberOf}' *_users.json
jq -c '.data[]|select(.Properties.name=="LIT-NMS-02.LITORAL.LOCAL")|{Sessions,LocalAdmins}' *_computers.json
jq -c '.data[]|select(.Properties.hasspn and .Properties.enabled)|{name,spn:.Properties.serviceprincipalnames}' *_users.json
jq -c '.data[]|select(.Properties.name=="NMS@LITORAL.LOCAL")|.Properties' *_ous.json  # CTF{bh_lit_relay}
```
domain LITORAL.LOCAL · json 20260812112200_users.json · SID carla.dias ...-1104 · grupo DNS ADMINS ·
roastable DNS-SVC SPN DNS/LIT-NMS-02.LITORAL.LOCAL · OU OU=NMS,OU=Infra,DC=litoral,DC=local

## CLM (clm-ad.json — BHCE graph)
```bash
jq .metadata clm-ad.json; jq '.graph.nodes|length' clm-ad.json    # domain CLM.LOCAL, source BHCE, 3478
jq -r '(.graph.nodes|map({key:.id,value:.properties.name})|from_entries) as $n|.graph.edges[]|select(.kind=="ForceChangePassword" or .kind=="AdminTo")|.kind+": "+$n[.start.value]+" -> "+$n[.end.value]' clm-ad.json
# MESA-OPS -ForceChangePassword-> SVC-WIPE ; SVC-WIPE -AdminTo-> CLM-FILE-01
jq -c '.graph.nodes[]|select(.properties.name=="SVC-WIPE@CLM.LOCAL")|.properties' clm-ad.json  # CTF{bh_clm_relay}
```
SID marina ...-6208 · sessão CLM-MESA-014 -> MARINA.ALVES · grupo MESA-OPS · kinds de aresta = 4
