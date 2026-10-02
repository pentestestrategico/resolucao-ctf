# PoC — Chimera Vault (Criptografia) — #54

**Flag:** `CSSCTF{tr4c3_1nv4r14nc3_4nd_4c0ust1c_sp3ctr4_7f9b8c}`

## Enunciado
> The ancient custodians of the Chimera Vault didn't rely on standard asymmetric primitives... Demodulate the carrier, trace the invariant through the matrix state transitions, and invert the resonance to breach the vault.
> `nc 34.116.80.78 7334`

Tudo numa única conexão com **`signal.alarm(45)`** (45 s). Arquivos dados: `server.py` + `Dockerfile`.

## Estrutura (3 fases)
O servidor imprime `N` e `M_mod`, depois:
1. **Fase 1 — portadora acústica:** PCM 8 kHz mono (base64).
2. **Fase 2 — matriz:** só imprime `M_0..M_3` (telemetria, **sem input**). "Trace the invariant" é flavor — a trace cresce por `W mod N`, mas nada é pedido.
3. **Fase 3 — knapsack ressonante:** pede o vetor de bits exato.

## Fase 1 — demodular o token (FFT)
```python
f1 = 440  + (token & 0xFF) * 5         # 440..1715 Hz
f2 = 1200 + ((token >> 8) & 0xFF) * 5  # 1200..2475 Hz
# PCM = 0.4*sin(2πf1 t) + 0.4*sin(2πf2 t) + ruído gaussiano, 8kHz, 0.8s = 6400 amostras int16 LE
```
Recuperação: FFT do PCM → dois picos → bytes:
```
b1 = round((f1-440)/5);  b2 = round((f2-1200)/5);  token = (b2<<8)|b1
```
A resolução (0.8 s → bin de 1.25 Hz) é mais que suficiente (passo de 5 Hz). Enviar `hex(token)`.

## Fase 3 — Merkle-Hellman / subset-sum de baixa densidade
```python
r = superincreasing (48 elementos)            # privado
M_mod = sum(r) + rnd(1000,50000)  (ímpar)      # PÚBLICO (impresso)
W tal que gcd(W, M_mod)=1                       # privado
s[i] = (W * r[i]) % M_mod                        # PÚBLICO (pesos)
target_sum = Σ target_bits[i] * s[i]             # soma inteira (não mod!)
```
Checagem do servidor exige `check_sum == target_sum` **e** `user_bits == target_bits`.

**Ataque:** é um subset-sum sobre os pesos públicos `s`. Como `r` cresce ~2× por passo, `max(s) ~ 2^52` e `n=48` → **densidade d = n/log2(max s) ≈ 0.906 < 0.9408**. Dentro do limite do ataque de baixa densidade (Lagarias-Odlyzko / CJLOSS) → **LLL/BKZ recupera o vetor 0/1** diretamente, sem precisar de `W`.

Reticulado CJLOSS (escala 2, peso grande `K` na coluna do knapsack):
```
linha i (0..n-1):  B[i][i]=2 ,  B[i][n]=K*s[i]
linha n:           B[n][*]=1 ,  B[n][n]=K*target
```
Após LLL, um vetor curto tem coords ±1 (= `2x_i-1`) e última coord 0. Extração: `x_i=(v_i+1)/2`, testando ambos os sinais e validando pela soma. **Fallback:** BKZ (block 20–25) + **retries por permutação** da ordem (muda o reticulado) → recupera casos difíceis.

Validação offline (importando `ChimeraVault` do próprio `server.py`): **50/50 instâncias resolvidas, pior caso 0.20 s** → folga enorme nos 45 s.

## Resultado
```
[+] token = 0x42a2
[+] knapsack n=48 target=133692067968955971
[+] solution = 101000010100011101101110110001011001100010010011
[+] RESONANCE EQUILIBRIUM ACHIEVED...
[+] Flag: CSSCTF{tr4c3_1nv4r14nc3_4nd_4c0ust1c_sp3ctr4_7f9b8c}
```

## Lição
- Merkle-Hellman com **densidade < 0.9408 é quebrável por LLL** sem a trapdoor — nunca use knapsack como cripto.
- RNG/segredos "privados" não protegem: `M_mod` público + estrutura superincreasing entrega tudo.
- Dica de ouro de CTF: quando o **código do servidor é fornecido**, instancie-o localmente para gerar casos de teste e validar/benchmark o exploit *antes* de gastar o tempo limitado do remoto.

## Artefatos (scratchpad da sessão)
- `solve_chimera.py` — solver completo das 3 fases (FFT + LLL/BKZ)
- `server.py`/`Dockerfile` originais (em ~/Downloads/chimera_vault.tar.gz)
