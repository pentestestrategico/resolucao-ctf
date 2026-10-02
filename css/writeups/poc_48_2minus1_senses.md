# PoC — 2(-1) Senses (OSINT/Stego, 30 pts) — #48

**Flag:** `CSSCTF{WHOS_THIS_FLUFFMASTER_MR_Chinaski}`  ✅ (confirmada)

## Enunciado
"Um som veio do espaço profundo... se tocar, baixe o volume." Arquivo `2senses_puzzle.wav` (mono, 44.1kHz, 17s).

## Insight: "2(-1) Senses" = combinar DOIS sentidos
A flag está dividida: metade nos **metadados** (leitura) e metade no **espectrograma** (visão). O áudio alto (6–16 kHz, 12–15s) é uma **armadilha para a audição** (o aviso de volume).

### Sentido 1 — Metadados do WAV (chunks LIST/id3)
```bash
python3 -c "d=open('2senses_puzzle.wav','rb').read(); print(d[1499444:])"
# IART / TPE1:  CSSCTF{WHOS_THIS_FLUFFMASTER_MR...
# ICMT / COMM:  }
```
→ template: `CSSCTF{WHOS_THIS_FLUFFMASTER_MR...}` (com "..." censurado).

### Sentido 2 — Espectrograma (visão)
```python
import wave,numpy as np,matplotlib.pyplot as plt
w=wave.open('2senses_puzzle.wav'); data=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)
plt.specgram(data,NFFT=2048,Fs=w.getframerate(),noverlap=1536); plt.ylim(2200,4200); plt.savefig('t.png')
```
→ desenhada em ~3 kHz: a palavra **`chinaski`**.

### Combinar
Substituir "..." pela palavra do espectrograma → "Mr. **Chinaski**" (Henry Chinaski, de Bukowski):
```
CSSCTF{WHOS_THIS_FLUFFMASTER_MR_Chinaski}
```
(detalhe de formato: resto em MAIÚSCULO, mas o nome próprio **"Chinaski"** com C maiúsculo; separador `_`.)

## Lição
Nem sempre o espectrograma é a flag toda — aqui ele completa a parte censurada ("...") que estava nos metadados. Áudio alto pode ser isca para o sentido errado.
