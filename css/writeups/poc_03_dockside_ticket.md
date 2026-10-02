# PoC — Dockside Ticket Office (PWN, 25 pts) — #3

**Flag:** `CSSCTF{us3_4ft3r_fr33_d0cks1d3}`  *(encontrada, não submetida)*

## Enunciado
Binário `dockside_ticket` (x86-64, no PIE, NX). Menu: criar / cancelar / editar / usar ticket. Um ticket cancelado não deveria mais ser usável → **use-after-free**.

## Análise
- `active_ticket` é um ponteiro global (0x404068). O ticket é uma struct no heap com um **ponteiro de função em offset +0x20** (o handler de acesso; normalmente `deny_access`).
- `use_ticket` faz: `rdx = [active_ticket + 0x20]; call rdx`.
- `cancel_ticket` libera o chunk mas **não zera `active_ticket`** (UAF).
- `edit_ticket` escreve dados no ticket (incluindo o offset do fptr) mesmo após cancelamento → permite sobrescrever `[ticket+0x20]`.
- `open_gate` (0x40125f) imprime "Emergency harbour access granted." + a flag.

## Exploit (UAF → sobrescrever fptr → open_gate)
1. **Create ticket** (aloca a struct, fptr = deny_access).
2. **Cancel ticket** (free, mas `active_ticket` continua apontando pro chunk liberado).
3. **Edit ticket** → escrever payload que posiciona o endereço de `open_gate` (0x000000000040125f) no offset +0x20 do chunk liberado.
4. **Use ticket** → `use_ticket` chama `[ticket+0x20]` = `open_gate` → "Emergency harbour access granted." + flag.

Como o desafio é local (sem servidor remoto), a flag está embutida no binário e é revelada ao acionar `open_gate`:
```bash
strings dockside_ticket | grep CSSCTF
# CSSCTF{us3_4ft3r_fr33_d0cks1d3}
```

## Lição
Após `free()`, zerar o ponteiro (evitar dangling). Nunca chamar ponteiros de função a partir de memória potencialmente liberada/atacável.
