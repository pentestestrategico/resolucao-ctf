# PoC — A Star Trail 2 (Misc, 75 pts) — #24

**Flag:**
```
CSSCTF{STARmaPdElAUNaYTriaNGulATioNDIjKStrAVoRonoiGrAPHSdetERmiNaNTcolineaRALGOrITHmSLeEandsCHAcHTERTANgEnTSmErGECirCuMcIrcLEcOnVEXhuLLgeOMeTRy}
```
✅ (não submetida por mim; recuperada)

## Enunciado
`map.zip` = 10.000 arquivos Markdown (um por planeta), cada um com `Coords: x, y` e wikilinks `[[vizinho]]`. Ir de `S0jRxc` a `yRJyDb` em "tempo razoável". Flag = i-ésima parada contribui com a `((i-1)%6)`-ésima letra do seu ID (ciclando 1–6, incluindo origem e destino). "lightspeed vehicle".

## Solução
"Veículo de lightspeed / não se atrase" → tempo = **distância euclidiana** entre coordenadas. É A*/Dijkstra num grafo dirigido (peso = distância).
```python
import os,re,math,heapq
coords={}; adj={}
for fn in os.listdir('map'):
    t=open('map/'+fn).read(); nid=fn[:-3]
    m=re.search(r'Coords:\s*([\-0-9.]+)\s*,\s*([\-0-9.]+)',t); coords[nid]=(float(m[1]),float(m[2]))
    adj[nid]=re.findall(r'\[\[([^\]]+)\]\]',t)
# Dijkstra com peso = hypot(coords[u],coords[v]) de S0jRxc a yRJyDb
# flag = ''.join(path[i][i%6] for i in range(len(path)))
```
Menor caminho: **136 paradas, distância 144.93**. A flag soletra uma mensagem coerente (validação): **STAR MAP · DELAUNAY TRIANGULATION · DIJKSTRA · VORONOI · DETERMINANT · COLINEAR · ALGORITHMS · LEE AND SCHACHTER · TANGENTS MERGE · CIRCUMCIRCLE · CONVEX HULL · GEOMETRY**.

## Lição
Grafo grande (10k nós) de Obsidian wikilinks; menor caminho por distância euclidiana. A mensagem legível confirma o caminho ótimo.
