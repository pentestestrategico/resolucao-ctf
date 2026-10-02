# PoC — A Star Trail 3 (Misc, 120 pts) — #56

**Flag:**
```
CSSCTF{itr6G8jMTXbOjCmClmMElZxQLqSXqnf53z1Z73liVas3ypn5CJZ4ZGlqZo6Fkc2onoJ6vx5SLfqqEyBotfjpxskQknpUgK9VMfBsFqzc0iEHDbMvv1hwXAo4U1NaimtTt9esb6mskMdUkbgBAjg3TTS1UeTSvf7LFZR0Vxf8KOgkzxHmvO0ifOFaVnwNgwUqpeo9}
```
("may not be easily recognisable" — flag longo tipo gibberish, por design.)

## Enunciado
`map2.zip` = **25.000** arquivos `.md` (um por corpo planetário), cada um com `Coords: x, y` mas com a lista de vizinhos **`[CORRUPTED]`** (as rotas foram destruídas). Reconstruir as rotas e entregar de **`iJ2ZcO`** a **`pJk9vy`**.

> "find patterns in your previous postal appointments" → a regra de geração das rotas vem das partes anteriores.

## A regra (vinda da Parte 2)
A flag da **A Star Trail 2** (#24) soletrava: *STAR MAP · DELAUNAY TRIANGULATION · DIJKSTRA · VORONOI · DETERMINANT · COLINEAR · LEE AND SCHACHTER · TANGENTS MERGE · CIRCUMCIRCLE · CONVEX HULL · GEOMETRY*. 
→ As rotas são geradas pela **triangulação de Delaunay** dos pontos. Então: reconstruir arestas = Delaunay(coords), peso = **distância euclidiana**, caminho mínimo por **Dijkstra/A\*** (série "A Star" = A*).

## Solução
```python
import os,re,math,heapq
import numpy as np
from scipy.spatial import Delaunay
ids=[]; pts=[]; pat=re.compile(r'Coords:\s*([\-0-9.]+)\s*,\s*([\-0-9.]+)')
for fn in os.listdir('map'):
    m=pat.search(open('map/'+fn).read()); ids.append(fn[:-3]); pts.append((float(m[1]),float(m[2])))
pts=np.array(pts); idx={n:i for i,n in enumerate(ids)}
tri=Delaunay(pts)                       # reconstrói as rotas
adj=[[] for _ in ids]
for s in tri.simplices:
    for a in range(3):
        for b in range(a+1,3):
            u,v=s[a],s[b]; d=math.hypot(*(pts[u]-pts[v]))
            adj[u].append((v,d)); adj[v].append((u,d))
# Dijkstra iJ2ZcO -> pJk9vy ...
# flag: parada i (0-indexed) contribui com a letra idx i%6 do seu ID (inclui origem e destino)
flag=''.join(path_ids[i][i%6] for i in range(len(path_ids)))
```

### Formato da flag (validado com o exemplo)
Parada `i` (1-indexed) → letra `((i-1) mod 6)` do seu ID, ciclando a cada 6, **incluindo origem e destino**.
Exemplo do enunciado: `ASTART,BCDEFG,hijklm,NOPQRS,tuvwxy,ZFINAL` → `A C j Q x L` = `ACjQxL` ✓.

## Resultado
- 25000 nós, Delaunay → **74970 arestas**.
- Caminho mínimo `iJ2ZcO → pJk9vy`: **196 paradas**, distância total **144.047**.
- Primeiras: iJ2ZcO, gtHQlo, c4rFDK, 7Yw6HF, Rvn5GS, Mk8XA8 … Últimas: … MeCNE2, hcoXhZ, pJk9vy.
- Flag = concatenação das letras `i%6` → string de 196 chars (acima).

## Lição
- Quando as arestas de um grafo geométrico "somem" mas os pontos ficam, o grafo de proximidade padrão é a **triangulação de Delaunay** (dual do diagrama de Voronoi). `scipy.spatial.Delaunay` resolve 25k pontos em <1 s.
- Caminho mínimo ponderado por distância euclidiana = Dijkstra/A*. A pista da regra estava na *flag da parte anterior* (meta-pista da série).

## Artefatos (scratchpad da sessão)
- `star3/map/` — 25000 nós; script inline de Delaunay + Dijkstra.
