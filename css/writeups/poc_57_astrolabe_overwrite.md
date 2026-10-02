# PoC — The Astrolabe Overwrite / Ouroboros (Misc, 250 pts — técnica PWN + RE) — #57

**Flag:** `CSSCTF{0ur0b0r0s_g00d_j0b_b01s_heh3_67}`

## Enunciado
`ouroboros.7z` → `nexus_core` (ELF64 PIE stripped, Full RELRO/Canary/NX/FORTIFY), servido por `socat` em `nc 34.116.80.78 7654`. "The council's instruction consumes and rewrites its own memory." 3 anéis do Astrolabe (permutação / recorrência de onda / coordenadas projetivas) + janela de decaimento.

## Visão geral
`main`: `alarm(45)`; inicializa um **struct de estado de VM**; imprime `BEACON = time() mod 0xfff1` (muda por conexão); lê um **payload hex (≤512 bytes)** que é decodificado para dentro do struct e executado por uma **VM self-modifying** (`fcn.000013e0`).

### Struct de estado (`param_1`)
| off | campo |
|-----|-------|
| +0,+2,+4,+6 | R0..R3 (ushort) |
| +8 | PC (ushort) |
| +0x0a | hash H (byte), init `0x5a` |
| +0x0c | ciclos (uint) |
| +0x10 | run flag |
| +0x12 | beacon |
| +0x14 | **perm** (S-box de opcodes, 8 bytes) = `10 20 30 35 40 50 7f ff` |
| +0x1c | **código** = nosso payload |

### VM (cada instrução = 4 bytes `b0 b1 b2 b3`)
- `opcode = perm[(b0 ^ H) & 7]`; `rd=b1&3`, `rs=b2&3`, `imm16=(b2<<8)|b3`.
- Após decodificar: `PC+=4`; `H = (H*0x1f + R0.low) & 0xff`.
- Ops: `0x10` LOAD `R[rd]=imm%p` (+1 ciclo); `0x20` MOV (+1); `0x30` ADD mod p (+2); `0x35` SUB mod p (+2); `0x40` XOR (+2); `0x50` JMP rel `PC=PC+4+int8(b3)` (+3); `0x7f` **CHECK/WIN** (+10); outro → ILLEGAL (halt).
- **Self-modifying:** depois de cada op, swap `perm[R0.low&7] ↔ perm[R1&7]` (o multiset nunca muda → qualquer opcode é sempre emitível escolhendo `b0`).
- Loop enquanto `ciclos < 129`.

### CHECK / 3 anéis (`0x7f`) — p = 65521
Exige `ciclos ∈ [112,128]` (após +10), senão COHERENCE (cold) / THERMAL (runaway). Depois:
- **Ring 1:** `w[i] = (R[i] − beacon) mod p` (i=0..3).
- **Ring 2:** `f(w) = (rotl16(pow(w^0x5aa5, 17, p), 7) ^ 0x1337) mod p`.
- **Ring 3:** `a=w1+f(w0)`, `b=w2+f(w1)`, `c=w3+f(w2)`, `d=w0+f(w3)` (mod p), e as gates:
  - `b² ≡ a³+17a+43`, `d² ≡ c³+17c+43` (curva elíptica E) — *"projective coordinates"*.
  - `a²+f0·b−d ≡ 40414`, `b²+f1·c−a ≡ 12506`, `c²+f2·d−b ≡ 4535`, `d²+f3·a−c ≡ 39941` (mod p) — *"coupled wave recurrence"*. As comparações `expr·K+C ≤ T` com `K` ímpar são **igualdades mod p disfarçadas** (os `expr` válidos formam PA de passo p; `expr0 = (−C)·K⁻¹ mod 2⁶⁴`).

## Solução
1. **Registradores (independe do beacon):** busca vetorizada (numpy) — fixa `w0`, varre `w1`, deriva `a`, `b`(curva), `c`(G2), `w2,w3,d`, filtra por G6,G1,G3,G4. Solução: **`w = [1, 218, 59611, 783]`** (a,b,c,d = 37319,30037,44410,40061). Verificado com a semântica exata de 64 bits.
2. **Bytecode:** reimplementei a VM (sim exato) e um emitter incremental. Como a execução é determinística (beacon só é lido no CHECK), simulo passo a passo e escolho `b0` para emitir o opcode desejado. Payload = **104×MOV (padding de ciclos) + 4×LOAD (R_i) + CHECK**, totalizando ciclos 108 → +10 = 118 ∈ [112,128].
3. **Por conexão:** ler o beacon → `R[i] = (w[i] + beacon) mod p` → emitir → enviar hex. (Validado por gdb: perm inicial correta = `10 20 30 35 40 50 7f ff`.)

```python
# exploit: emit.build(R, beacon, pad=104) -> hex ; R=[(w+beacon)%p for w in [1,218,59611,783]]
```

## Resultado
```
[remote] beacon=0x1714 R=[5909, 6126, 65519, 6691]
[+] TELEMETRY STABILIZED. OVERWRITING SYSTEM MASTER KEY...
CSSCTF{0ur0b0r0s_g00d_j0b_b01s_heh3_67}
```

## Lição
- VM self-modifying (perm estilo RC4 + hash dependente de R0) cujo *decode* muda a cada passo: a chave é notar que a execução é **determinística** e simular/emitir incrementalmente.
- MBA `expr*ODD + C <= T` = igualdade `expr ≡ expr0 (mod p)`.
- O "harmonic resonance" são 2 pontos numa curva elíptica `y²=x³+17x+43 mod 65521` acoplados por 4 congruências — resolúvel por busca O(p) vetorizada.
- A janela de ciclos [112,128] exige controlar o custo exato das instruções antes do CHECK.

## Artefatos (scratchpad)
- `emit.py` (sim+emitter), `pwn_ouro.py` (exploit local/remoto), `solve_regs.py` (busca dos registradores), `decomp.c` (Ghidra/pyghidra).
