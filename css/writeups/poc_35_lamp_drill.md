# PoC — Lamp Drill (Hardware RE, 15 pts) — #35

**Flag:** `CSSCTF{css}`  ✅

## Enunciado
`lampDrill.png` / `lampDrill.svg`. "Warm-up. No spaces."

## Análise
A imagem mostra a legenda de uma **porta lógica AND**:
- `●●→●`, `●○→○`, `○●→○`, `○○→○`  (●=1, ○=0; saída 1 só quando ambos são 1).

Há 3 linhas de 8 caixas; cada caixa tem 2 círculos → AND → 1 bit. 8 caixas = 1 byte por linha.

## Solução
Detectar preenchimento dos círculos (filled vs hollow) via área dos componentes conexos, aplicar AND por caixa:
```python
from PIL import Image; import numpy as np; from scipy import ndimage
a=np.array(Image.open('lampDrill.png').convert('L'))
# componentes escuros; fill ratio alto = preenchido(1), baixo = oco(0)
# AND de cada par -> 8 bits por linha -> ASCII
```
Linha 1 → `01100011` = `c`; linha 2 → `01110011` = `s`; linha 3 → `s`. → **"css"**.

## Lição
Puzzle de lógica digital; ler ●/○ como bits e aplicar a porta da legenda.
