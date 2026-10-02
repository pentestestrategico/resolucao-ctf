<h1 align="center">🛰️ CSS CTF 2026 — <em>Return of Nexus</em></h1>

<p align="center">
  <strong>Cybersecurity Society · University of Sydney</strong><br>
  Write-ups, exploits &amp; solvers — Semester 2, 2026
</p>

<p align="center">
  <img alt="Solved" src="https://img.shields.io/badge/solved-30%2F31-brightgreen?style=for-the-badge">
  <img alt="Categories" src="https://img.shields.io/badge/categories-12-blue?style=for-the-badge">
  <img alt="Platform" src="https://img.shields.io/badge/platform-ctf.cybersecurity.sydney-8A2BE2?style=for-the-badge">
</p>

<p align="center">
  <img alt="Pwn" src="https://img.shields.io/badge/PWN-ret2win%20%7C%20UAF%20%7C%20ROP-red">
  <img alt="Crypto" src="https://img.shields.io/badge/CRYPTO-LCG%20%7C%20lattice-orange">
  <img alt="Web" src="https://img.shields.io/badge/WEB-SSRF%E2%86%92GCP-yellow">
  <img alt="Blockchain" src="https://img.shields.io/badge/BLOCKCHAIN-Solidity-lightgrey">
  <img alt="Forensics" src="https://img.shields.io/badge/FORENSICS-carving%20%7C%20DSP-informational">
</p>

---

## 📖 Sobre

Repositório com os **write-ups** (prova de conceito) e **scripts de exploração** do time
**`COPCIBER-DSI`** no CSS CTF *Return of Nexus* (Semestre 2, 2026).

Cada desafio tem um PoC em `writeups/poc_NN_*.md` com: enunciado, análise, solução passo a
passo e a lição aprendida. Flags completas em [`FLAGS.txt`](FLAGS.txt).

> ⚠️ Conteúdo **educacional / pós-evento**. Técnicas de exploração usadas apenas no contexto
> autorizado do CTF.

---

## 🗂️ Estrutura

```
.
├── README.md             ← você está aqui
├── FLAGS.txt             ← todas as flags, na ordem das categorias do site
├── writeups/             ← PoCs por desafio (poc_NN_*.md) + write-ups longos
└── scripts/              ← solvers / exploits em Python
```

---

## 🏁 Placar por categoria

> `✅` resolvido · `🔄` em aberto

### 👋 Welcome
| # | Desafio | Pts | Status |
|---|---------|:---:|:---:|
| 34 | Welcome to Nexus | 10 | ✅ |

### 🔎 OSINT
| # | Desafio | Pts | Status |
|---|---------|:---:|:---:|
| 5  | Dead Faction Servers | 10 | ✅ |
| 48 | 2(-1) Senses | 30 | ✅ |
| 37 | Server Juice | 15 | ✅ *flag nos comentários do Instagram* |

### 💥 PWN
| # | Desafio | Pts | Status | Técnica |
|---|---------|:---:|:---:|---------|
| 50 | Kuiper Belt Relay Core | 15 | ✅ | ret2win (`gets` overflow) |
| 3  | Dockside Ticket Office | 25 | ✅ | Use-after-free |
| 49 | Maintenance Log | 50 | ✅ | ROP (`pop rdi`/`pop rsi`) |

### 🔧 Hardware: Reverse Engineering
| # | Desafio | Pts | Status |
|---|---------|:---:|:---:|
| 35 | Lamp Drill | 15 | ✅ |
| 31 | Silicon Snare | 250 | ✅ *(netlist → lógica)* |

### 🌐 Web
| # | Desafio | Pts | Status | Técnica |
|---|---------|:---:|:---:|---------|
| 38 | Welcome to Star City | 15 | ✅ | — |
| 40 | Secret Supernovas | 50 | ✅ | GraphQL |
| 55 | Cloudy with a Chance of Spaceships | 67 | ✅ | SSRF → GCP metadata |

### 🧩 Misc
| # | Desafio | Pts | Status | Técnica |
|---|---------|:---:|:---:|---------|
| 22 | A Star Trail 1 | 20 | ✅ | — |
| 24 | A Star Trail 2 | 75 | ✅ | — |
| 56 | A Star Trail 3 | 120 | ✅ | — |
| 57 | The Astrolabe Overwrite | 250 | ✅ | PWN + RE (Ouroboros) |
| 51 | Orthogonal Singularity | 750 | 🔄 | *estágio 1 OK; 2–3 pendentes* |

### 🤖 AI/ML Security
| # | Desafio | Pts | Status |
|---|---------|:---:|:---:|
| 47 | After hours... | 20 | ✅ |

### 🔐 Cryptography
| # | Desafio | Pts | Status |
|---|---------|:---:|:---:|
| 20 | Chrono I | 25 | ✅ |
| 54 | Chimera Vault | 65 | ✅ |
| 21 | Chrono II | 100 | ✅ |
| 28 | Severed Symmetry | 200 | ✅ |

### 🔬 Forensics
| # | Desafio | Pts | Status |
|---|---------|:---:|:---:|
| 1  | Echoes of the Relay | 33 | ✅ |
| 2  | The False Timeline | 66 | ✅ |
| 19 | Signal Fracture | 100 | ✅ |
| 18 | Ghost Frequency | 115 | ✅ |

### 🖼️ Steganography
| # | Desafio | Pts | Status |
|---|---------|:---:|:---:|
| 17 | Colour Shift | 45 | ✅ *(canal R + equalização)* |

### ⛓️ Blockchain
| # | Desafio | Pts | Status |
|---|---------|:---:|:---:|
| 52 | Gateway | 50 | ✅ |
| 53 | Lottery | 100 | ✅ |

### ⚙️ Reverse Engineering
| # | Desafio | Pts | Status |
|---|---------|:---:|:---:|
| 46 | prince walk | 50 | ✅ |
| 27 | FLAPPY BOARD | 80 | ✅ |

---

## ✨ Destaques

- **Silicon Snare (HW RE, 250)** — reconstrução da lógica a partir do *netlist*/esquemático
  do circuito. Write-up longo em [`writeups/writeup-silicon-snare.md`](writeups/writeup-silicon-snare.md).
- **The Astrolabe Overwrite (Misc, 250)** — cadeia "Ouroboros" combinando reversão e
  corrupção de memória (técnica PWN + RE).
- **Cloudy with a Chance of Spaceships (Web, 67)** — SSRF escalando até o *metadata server*
  do GCP.
- **Severed Symmetry (Crypto, 200)** — quebra de esquema simétrico; solver em
  [`scripts/solve.py`](scripts/solve.py) sobre [`scripts/source.py`](scripts/source.py).

---

## 🚀 Reproduzir um solver

```bash
cd scripts/
python3 solve_the_relay.py          # Kuiper Belt Relay Core — ret2win remoto
python3 exploit_49_maintenance_log.py
```

---

<p align="center"><sub>Feito pelo time <strong>COPCIBER-DSI</strong> · CSS CTF 2026</sub></p>
