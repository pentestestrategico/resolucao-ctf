# Relatório — CSS CTF Semester 2 2026 ("Return of Nexus")

- **Plataforma:** https://ctf.cybersecurity.sydney/ (CTFd)
- **Resultado atual:** 19 flags recuperadas de 23 desafios (4 em aberto)
- PoCs detalhadas por desafio em `css/poc_*.md` (e notas de tentativa nos não-resolvidos)

> ✅ = submetida e confirmada (antes da instrução de não enviar).
> 🔎 = **encontrada, NÃO submetida** (a pedido do usuário).

## Placar

| # | Desafio | Categoria | Pts | Status | Flag |
|---|---------|-----------|-----|--------|------|
| 34 | Welcome to Nexus | Welcome | 10 | ✅ | `CSSCTF{noodle_is_the_best}` |
| 38 | Welcome to Star City | Web | 15 | ✅ | `CSSCTF{we_BU1LT_this_city_from_r0ck_and_R011}` |
| 40 | Secret Supernovas | Web | 50 | ✅ | `CSSCTF{we_l000ve_grafs}` |
| 20 | Chrono I | Cryptography | 25 | ✅ | `CSSCTF{every_second_hides_a_secret}` |
| 21 | Chrono II | Cryptography | 100 | ✅ | `CSSCTF{th3_cl0ck_r3m3mb3rs_3very_s3c0nd}` |
| 17 | Colour Shift | Steganography | 45 | ✅ | `CSSCTF{SHINE_ON}` |
| 35 | Lamp Drill | HW RE | 15 | ✅ | `CSSCTF{css}` |
| 22 | A Star Trail 1 | Misc | 20 | ✅ | `CSSCTF{P1JT-21.0}` |
| 2 | The False Timeline | Forensics | 66 | ✅ | `CSSCTF{kai_did_not_do_it}` |
| 19 | Signal Fracture | Forensics | 100 | ✅ | `CSSCTF{fragment_t3ll_th3_st0ry}` |
| 18 | Ghost Frequency | Forensics | 115 | 🔎 | `CSSCTF{th3_gh0st_fr3qu3ncy_w4s_n3v3r_s1l3nt}` |
| 24 | A Star Trail 2 | Misc | 75 | 🔎 | `CSSCTF{STARmaPdElAUNaYTriaNGulATioNDIjKStrAVoRonoiGrAPHSdetERmiNaNTcolineaRALGOrITHmSLeEandsCHAcHTERTANgEnTSmErGECirCuMcIrcLEcOnVEXhuLLgeOMeTRy}` |
| 5 | Dead Faction Servers | OSINT | 10 | 🔎 | `CSSCTF{u_g0t_130d_508}` |
| 47 | After hours... | AI/ML Security | 20 | 🔎 | `CSSCTF{n0_b4dg3_just_4_g00d_st0ry}` |
| 3 | Dockside Ticket Office | PWN | 25 | 🔎 | `CSSCTF{us3_4ft3r_fr33_d0cks1d3}` |
| 48 | 2(-1) Senses | OSINT/Stego | 30 | 🔎 | `CSSCTF{WHOS_THIS_FLUFFMASTER_MR_Chinaski}` |
| 1 | Echoes of the Relay | Forensics | 33 | 🔎 | `CSSCTF{d3l3t3d_d03snt_m34n_g0n3}` |
| 46 | prince walk | Reverse Eng. | 50 | 🔎 | `CSSCTF{P12INC3_0R_P1NC3?}` |
| 49 | Maintenance Log | PWN | 50 | 🔎 | `CSSCTF{Duh_m4t3_1_4m_sl33py}` |

## Pendentes (4)

| # | Desafio | Categoria | Pts | Situação |
|---|---------|-----------|-----|----------|
| 27 | FLAPPY BOARD | Reverse Eng. | 80 | Jogo GUI (X11) + protocolo servidor (`:8765`, /api/attempt,/complete) com validação server-side. Precisa reconstruir/forjar o protocolo. |
| 28 | Severed Symmetry | Cryptography | 200 | MQ quártico (GF(17)). Ataque degree-falling validado (isola 16 quadráticas da camada w), mas inversão completa é nível-pesquisa e sem CAS. Ver `poc_28_*_PROGRESS.md`. |
| 31 | Silicon Snare | HW RE | 250 | Circuito lógico radial em SVG, projetado p/ resistir a software. Tipos de porta e geometria extraídos; netlist automático não fechou. |
| 37 | Server Juice | OSINT | 15 | Flag no Instagram @cybersecuritysydney — requer **login** (somente o usuário). |

## Resumo técnico por desafio resolvido

Ver os arquivos individuais em `css/`:
- `poc_01_echoes_of_relay.md` — inode deletado + PNG/ZIP polyglot (senha no inode).
- `poc_03_dockside_ticket.md` — UAF, sobrescrita de fptr → open_gate.
- `poc_05_dead_faction_servers.md` — segredo em histórico git + branch; base64; iscas.
- `poc_46_prince_walk.md` — chamar a função geradora da flag via gdb.
- `poc_47_after_hours.md` — jailbreak/engenharia social de LLM.
- `poc_48_2minus1_senses.md` — texto no espectrograma ("usar só a visão").
- `poc_49_maintenance_log.md` — off-by-one no RBP + leak → pivot → ROP → award.
- `Welcome_to_Star_City_writeup.md`, `Secret_Supernovas_writeup.md` — Web.
- (Os demais da 1ª rodada documentados neste relatório-mestre.)

### Técnicas da 1ª rodada (resumo)
- **Star City (Web):** flag em comentário CSS (base64+urlencode).
- **Secret Supernovas (Web):** GraphQL introspection → campos ocultos `owner.description`.
- **Chrono I (Crypto):** Vigenère com chave = dígitos do timestamp.
- **Chrono II (Crypto):** one-time-pad indexado por tempo; remontado por known-plaintext/overlap de 60 capturas.
- **Colour Shift (Stego):** texto de baixo contraste no canal vermelho (Dark Side of the Moon).
- **Lamp Drill (HW):** porta lógica AND; cada linha vira 1 byte → "css".
- **A Star Trail 1/2 (Misc):** menor caminho (A*/Dijkstra); flag = letras por posição dos nós (excluindo extremos no #1; grafo de 10k nós por distância euclidiana no #2).
- **The False Timeline (Forensics):** anti-forense/timestomp; chave AES derivada de machine_id|session|epoch reais (audit.log) vs timeline forjada.
- **Signal Fracture (Forensics):** remontar fragmentos NXFR de pcap+cache+raw-ring por SHA-256 do catálogo → gzip/tar.
- **Ghost Frequency (Forensics):** SSTV Martin M1 (canal L) dá o manual; canal R = AFSK Bell202 1200/8N1 → pacotes NXPK → seleção por CRC + FEC XOR + restaurar magic gzip.
