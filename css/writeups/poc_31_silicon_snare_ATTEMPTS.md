# Tentativas — Silicon Snare (Hardware RE, 250 pts) — #31  [NÃO RESOLVIDO]

## Enunciado
SVG (`schematic.svg`) de uma "optical routing matrix" radial. 32 entradas I00–I31 num círculo (I00 às 12h, horário), portas em anéis concêntricos convergindo ao nó central **OVERRIDE**. Achar o padrão de **32 bits** (I00..I31) que leva OVERRIDE a 1. Flag: `CSSCTF{<32 bits>}`. Explicitamente: *"Software won't help you much here. The only thing to follow is the wire."*

## O que foi extraído (progresso real)
- **Tipos de porta** (da legenda), decodificados:
  - `f##` = **Flow** = AND (Y = A AND B) — 20 portas
  - `n##` = **Negate** = NOT (Y = NOT A) — 6 portas
  - `m##` = **Merge** = XOR (Y = A XOR B) — 35 portas
  - `s##` = **Shift**: Y0 = A OR B, Y1 = A AND NOT B (2 entradas/2 saídas) — 13 portas
- **Rótulos** (I00–I31, m/f/n/s, OVERRIDE) e posições extraídos via comentários `<!-- -->` + `transform=translate(x y)`.
- **Modelo de pino correto descoberto:** os `<path>` **pretos (#1b1b1b) são o DESENHO do símbolo** da porta; os fios de sinal são só os **coloridos** (`<g id="line2d_N">`). Cada porta tem seus pinos = endpoints dos fios coloridos que ali terminam (validado visualmente: m00 = XOR de I00(vermelho)+I02(verde) → saída oliva).
- **Regra de fluxo:** sinal flui de fora (r~325) p/ dentro (OVERRIDE, centro) → fonte de cada net = terminal de maior raio.
- **Símbolos pretos por porta** extraídos; contagem de pinos parcialmente validada (n=2 OK; f=3 maioria OK).

## Bloqueio
- A extração **automática do netlist** não fechou de forma consistente:
  - Casar endpoints de fios aos pinos corretos falha por causa dos **arcos concêntricos sobrepostos** que passam perto dos rótulos/símbolos (muitos falsos pinos).
  - **Shift gates (13×)** têm 4 terminais com A/B/Y0/Y1 dependentes da orientação (ponta vs. base) — desambiguação geométrica frágil.
  - 7 cores são reusadas por 2 nets (ambiguidade).
  - OVERRIDE e algumas entradas conectam em "dots" deslocados dos rótulos (não detectados com tolerância fixa).
- É exatamente o desafio **projetado para resistir a software** (overlaps intencionais).

## Próximos passos sugeridos
- Extrair os pinos a partir dos **símbolos pretos** (não dos rótulos), com raio bem apertado a partir do centroide do símbolo, usando SÓ fios coloridos.
- Distinguir **nó (dot preenchido)** de **cruzamento** pela coincidência de endpoints (junções compartilham endpoints; cruzamentos são pontos interiores).
- Tratar shift gates por geometria (ponta/base) individualmente.
- Montar o netlist booleano e resolver com **z3** para OVERRIDE=1; a **unicidade da solução** (o enunciado garante "só um padrão liga o centro") serve de validação.
- Alternativa: traçado visual manual setor a setor (muito trabalhoso, mas é o método "intencionado").
