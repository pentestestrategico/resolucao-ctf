# PoC — A Star Trail 1 (Misc, 20 pts) — #22

**Flag:** `CSSCTF{P1JT-21.0}`  ✅

## Enunciado
Mapa estelar (`A_Star_Trail.png`). Entregar de EARTH a LANCER-RXKRD seguindo os caminhos, em menos de 25 dias. Flag = 1ª letra de cada planeta no caminho + "-" + dias (1 decimal). "A Star Trail" = A*.

## Grafo (lido do mapa)
Arestas (dias): EARTH–BACONITE 5.0, EARTH–PALLUS 10.7, BACONITE–C3810 2.1, BACONITE–BARAT 9.8, C3810–BARAT 6.3, BARAT–JIP 1.4, BARAT–PALLUS 1.4, JIP–12PUCK 0.4, JIP–TAYLOR 5.5, PALLUS–12PUCK 1.8, PALLUS–HEMENS 2.5, 12PUCK–HEMENS 3.6, TAYLOR–LANCER 2.6, TAYLOR–TAMMY 3.2, TAMMY–LANCER 10.1, TAMMY–HEMENS 3.7, TAMMY–VERGINON 2.8, VERGINON–LANCER 8.5, VERGINON–SLATER 7.5, HEMENS–SLATER 6.0.

## Solução
Dijkstra: menor caminho = **EARTH→PALLUS-XA→12-PUCK-8→JIP-REIA→TAYLOR-3489→LANCER-RXKRD = 21.0 dias** (10.7+1.8+0.4+5.5+2.6).

**Detalhe-chave do formato:** o exemplo engana — os **extremos (EARTH e LANCER) NÃO entram** no código; só os planetas **intermediários**: PALLUS(P), 12-PUCK(1), JIP(J), TAYLOR(T) = `P1JT`.

→ `CSSCTF{P1JT-21.0}`
