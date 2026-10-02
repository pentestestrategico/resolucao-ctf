# PoC (PARCIAL) — Orthogonal Singularity (Misc, 750 pts) — #51

**Status:** Estágio 1 ✅ resolvido · Estágio 2 🔄 em análise · Estágio 3 ⏳ não alcançado
**Flag:** ainda não capturada.

## Enunciado
> Somewhere listening posts along the galactic rim have intercepted a telemetry beacon broadcasting near the event horizon. To stabilize the link and extract the core telemetry, you must:
> 1. Pass the handshake gate before the uplink decays.
> 2. Track the carrier's 16 kHz trajectory through the noise and lock the frequency bounds.
> 3. Trace the topology of the underlying topological braid to collapse the singularity.
>
> `nc 34.116.80.78 7878` — Flag: `CSSCTF{...}`

Tudo acontece numa **única conexão** (há "decaimento"/timeout). O serviço é instável no primeiro contato (precisa de retry).

---

## Estágio 1 — Handshake (Proof of Work) ✅
```
POW: SHA256(<prefix24hex> + nonce) leading_zero_bits >= 24
nonce>
```
Achar `nonce` (inteiro em string) tal que `SHA256(prefix+nonce)` comece com 24 bits zero (3 bytes `00`). O `prefix` muda a cada conexão.

**Solução:** brute-force multiprocessing (4 cores), ~1.3M h/s por core → resolve em **2–5 s**.
Pontos de implementação importantes:
- Em Python 3.14 forçar `multiprocessing.set_start_method('fork')` (o default `forkserver` reimporta o módulo e quebra sockets no top-level).
- No worker, **não** chamar `q.empty()` a cada iteração (IPC caríssimo → caiu para ~370k h/s e o uplink decaiu); checar a cada 50k hashes.

Script: `orth2.py` / `stage2.py` (pasta scratchpad da sessão).

## Estágio 2 — `f_bounds [hex]>` 🔄
Após o nonce o servidor envia:
```
[+] ACCESS PIPELINE OPEN
--- EMISSION BURST ---
<hex de 64000 chars = 32000 bytes>
--- END BURST ---
f_bounds [hex]>
```

**Análise do burst (confirmada):**
- 32000 bytes = **16000 amostras `int16` little-endian**.
- Assumindo **fs = 16000 Hz** (16000 amostras = exatamente 1 s — única leitura que dá duração "limpa"; "carrier ≈16 kHz" exigiria fs não-padrão, descartado).
- Uma **portadora varre o espectro de forma acelerante** (trajetória convexa, tipo chirp exponencial/random-walk) imersa em ruído leve. SNR do ridge ~21 dB.
- Ridge via `scipy.signal.spectrogram(nperseg=1024, noverlap=1024-64)` → `argmax` por frame é o rastreador mais confiável.
- `f_bounds` = provavelmente `[freq_mín, freq_máx]` da trajetória (em Hz; como fs=N=16000, bin da FFT == Hz).

**Problema central — ZERO feedback:** qualquer resposta errada **ou inválida** (até `zzz`) faz o servidor **fechar a conexão sem mensagem**. Impossível distinguir "formato errado" de "valor errado". Cada tentativa custa um PoW novo + burst novo (aleatório).

**Tentativas feitas (todas → conexão fechada, resp vazia):**
| Formato enviado | Exemplo | Resultado |
|---|---|---|
| hex + espaço | `87c 1240` | fechou |
| `0x` + espaço | `0x5ec 0x1230` | fechou |
| hex + vírgula | `3f8,1444` | fechou |

Valores usados = `ridge.min()`/`ridge.max()` do burst daquela conexão.

**Hipóteses em aberto (próximos passos):**
1. **Valores fora da tolerância.** O `argmax` pode pegar picos de ruído (inflando max/deflacionando min). Testar rastreador de ridge contínuo (rejeitando saltos) e estimadores corrigidos de borda (extrapolação / janela curta `nperseg=256`). Estimadores já prototipados divergem ~200–600 Hz no extremo alto → essa é a maior incerteza.
2. **Tolerância pode ser tight** → talvez os limites sejam **exatamente** recuperáveis (ex.: sinal é soma de subportadoras *ortogonais* em bins exatos da FFT — casa com o título "Orthogonal" — e `f_bounds` = bin mais baixo e mais alto ocupados, que têm bordas nítidas). Revisar se em cada instante o sinal é banda-estreita (portadora única varrendo) vs banda-larga estática.
3. **Formato ainda não testado:** valor único combinado, ordem invertida (hi lo), decimal, ou **dois prompts sequenciais** (enviar lo, ler, enviar hi).
4. Sem writeup público (CTF privado) — resolver por DSP.

## Estágio 3 — "topological braid" ⏳
Não alcançado (depende do 2). Provável análise de grupo de tranças (braid group) sobre dados a receber.

---

## Artefatos (scratchpad da sessão)
- `orth2.py`, `stage2.py` — cliente PoW + captura de burst + envio de resposta
- `fmt_brute.py` — brute de formato (1 conexão/variante, log em `fmt.log`)
- `burst.hex`, `burst_live.hex`, `burst_s2.hex` — bursts capturados p/ análise offline
- Estimadores de limites (ridge / extrapolação / janela curta / ajuste de fase)

## Lição parcial
Desafio de DSP sem feedback: a dificuldade real não é o DSP em si, é que **não há oráculo** — exige reproduzir exatamente a convenção do autor (formato + definição de "bounds" + tolerância). Próximo passo mais produtivo: assumir tolerância generosa e varrer formatos **com um rastreador de ridge robusto**, OU reinterpretar como subportadoras ortogonais (bordas de banda exatas).

---
## Atualização (análise aprofundada do Estágio 2)

**Dica oficial recebida:** "The carrier displays non-linear **parabolic** frequency modulation... isolating the **asymptotic frequency limits** from the noise floor against the receiver's baseband... serialized as a **standard two-byte network register** representing the **terminal and initial** channel states."

**Confirmado:**
- Sinal = **16000 int16 reais**, **clipado** (±32767, ~79 amostras), chirp **parabólico** (freq instantânea quadrática em t, vértice em t≈0 → `f(t)=f0+c2·t²`). Ajuste não-linear do sinal: resíduo ~1.4 Hz (medição confiável de f0; f1 um pouco menos).
- Resposta = **uint16 big-endian = (terminal<<8)|initial**, cada byte 0–255. terminal=f(T)=máx, initial=f(0)=mín.

**O que FALHOU (todas fecham a conexão, sem feedback):**
- Escalas `byte=f/passo` para passo ∈ {15.625, 25, 31.25, 32, 40, 50, 62.5, 64, 100, 128}, **nas duas ordens**, em `%04x`.
- Formatos: `%04x`, `%02x %02x`, `%d` (uint16), `%d %d`, `0x%04x`, `%04X`, `%02x,%02x`.
- Re-testes de ÷31.25 (o "óbvio", ×512) em 8 conexões distintas — todas fecham.
- A sessão compartilhada (outro Claude) esgotou: IQ (×256/×512), real (×512), 4 convenções fftshift.

**Prova de que não é `f/passo` simples:** medindo f0 (inicial, o valor mais preciso) com alta resolução em 10 bursts, as partes fracionárias de `f0/31.25` (e de qualquer passo testado) ficam espalhadas (.0–.9), não perto de inteiro. Logo a grade real não é um divisor simples.

**Bloqueio:** a convenção exata freq↔byte é específica do autor e o servidor **não dá feedback** (fecha em erro). Sem o fonte do servidor (como no Chimera), não dá para fixar a convenção. **Pendente:** obter o handout/`server.py` deste desafio, se existir.

**Infra de exploit já pronta (scratchpad):** `capmulti.py` (PoW+captura), `tryer.py` (PoW+captura+submit+detecção de sucesso), `sweep.py`/`brute_fmt.py`/`retry31.py` (varreduras de convenção), ajuste não-linear do chirp.
