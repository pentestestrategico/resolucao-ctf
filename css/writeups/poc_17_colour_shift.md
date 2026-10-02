# PoC — Colour Shift (Steganography, 45 pts) — #17

**Flag:** `CSSCTF{SHINE_ON}`  ✅

## Enunciado
`colorshiftctf.bmp` (capa do "Dark Side of the Moon" — prisma → arco-íris). Dica: *"In 1666 Isaac Newton split light into their composite wavelengths. Can you?"*

## Solução
"Separar a luz em comprimentos de onda" = **separar os canais RGB**. O texto está escondido em **baixíssimo contraste no canal vermelho** (faixa inferior da imagem).
```python
from PIL import Image, ImageOps
import numpy as np
a=np.array(Image.open('colorshiftctf.bmp').convert('RGB'))
R=Image.fromarray(a[:,:,0])
ImageOps.equalize(R).save('red_eq.png')   # equalização revela o texto
```
Ao equalizar o canal vermelho, aparece o texto na faixa ~y=405–455: **CSSCTF{SHINE_ON}**.

## Lição
Esteganografia por baixo contraste em um único canal de cor; equalização/autocontraste por canal revela.
