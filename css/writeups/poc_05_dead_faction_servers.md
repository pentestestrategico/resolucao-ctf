# PoC — Dead Faction Servers (OSINT, 10 pts) — #5

**Flag:** `CSSCTF{u_g0t_130d_508}`  *(encontrada, não submetida)*

## Enunciado
Trace inicial: `bobdev508`. Chave real dividida em 2 metades em 2 locais, uma "scrambled", com várias iscas.

## Passos
1. Perfil GitHub **bobdev508** → 2 repos: `dashboard-app`, `decoy-project` (isca).
2. `dashboard-app` tem commits suspeitos: *"Add local env file"* e *"Remove committed secrets, oops"*.
   O segredo removido persiste no histórico git:
   ```bash
   curl -s https://api.github.com/repos/bobdev508/dashboard-app/commits/be82c694
   # .env.local:  SECRET_PART=Q1NTQ1RGe3VfZzA=
   ```
   Base64 (a peça "scrambled beyond plain sight"):
   ```bash
   echo -n 'Q1NTQ1RGe3VfZzA=' | base64 -d   # -> CSSCTF{u_g0
   ```
3. Branch **`experimental/auth-rework`** contém `auth_notes.md`:
   ```
   bypass_suffix = "t_130d_508}"
   ```
4. Concatenar metade 1 + metade 2.

## Iscas (ignoradas)
- `dashboard-app/app.py`: `CTF{n0t_qu1t3_1t}`
- `dashboard-app/utils.py`: `CTF{4ls0_n0t_r34l}`
- `decoy-project/old_config.txt`: `CTF{th1s_1s_n0t_th3_r34l_fl4g}`

## Resultado
`CSSCTF{u_g0` + `t_130d_508}` = **`CSSCTF{u_g0t_130d_508}`**

## Lição
Segredos removidos permanecem no histórico git (e em branches não-default). Sempre auditar `git log --all`, branches e diffs de commits.
