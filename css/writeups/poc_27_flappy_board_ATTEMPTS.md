# Tentativas — FLAPPY BOARD (Reverse Engineering, 80 pts) — #27  [NÃO RESOLVIDO]

## Enunciado
Binário `flappy_board` (ELF x86-64 PIE, stripped). Clone de Flappy Bird; a "flap key" muda após cada pipe/ponto; passar por 3 setores antes do fim da conexão de 20 min; recuperar a access key.

## O que foi descoberto (recon estático)
- Libs: **libX11** (GUI gráfica), **libcurl** (rede), libm, libc.
- Strings relevantes:
  - `FLAPPY / BOARD`, `FLAP KEY [ %c ]`, `TAP THE SHOWN LETTER TO FLAP`.
  - Servidor hardcoded: **`http://34.116.80.78:8765`**.
  - Endpoints: `/api/attempt`, `/api/practice`, `/api/practice/check`, `/api/complete`.
  - Telemetria POST: `sequence=%d&ticks=%d&final=%d&score=%d&flaps=...` e `round=%d&wait_ms=%d&ticks=%d&score=%d&flaps=...`.
  - Validação server-side: `Invalid server state.`, `Game/server versions differ.`, `The server deadline has passed.`, `token`, `flag`.
  - Restrição de URL: só HTTPS, o servidor do evento, ou localhost com porta explícita.

## Análise
- O jogo é **GUI (X11)** e a validação é **server-side**: o servidor dita os pipes/flap-keys e verifica a sequência de flaps enviada. A flag vem de `/api/complete` após 3 setores válidos dentro do prazo.
- Dois caminhos possíveis:
  1. **Jogar** o jogo (inviável headless/automatizado por ser GUI + timing + flap-key mutável).
  2. **Forjar o protocolo**: reverter o fluxo `/api/attempt` → rounds → `/api/complete`, reproduzindo as respostas esperadas pelo servidor (sequência de flaps correta por round, dentro dos ticks/deadline, com o token de sessão e a "versão" corretas).

## Bloqueio / estado
- Forjar requer entender exatamente: formato do token de sessão, como o servidor define os pipes (seed?), o cálculo esperado de `flaps/ticks/score` por round, e a checagem de versão. Isso é uma engenharia reversa extensa do loop de jogo + protocolo (não concluída).
- Não foi encontrada flag em texto plano nem atalho (ex.: `/api/practice/check` não obviamente vaza a flag).

## Próximos passos sugeridos
- Reverter em detalhe as funções que montam os POST (`sequence=`, `round=`) e o parser das respostas do servidor.
- Reproduzir uma sessão: `POST /api/attempt` → obter parâmetros do round (pipes/flap-key) → calcular a sequência de flaps que passa pelos pipes → `POST` cada round → `POST /api/complete` → ler a flag.
