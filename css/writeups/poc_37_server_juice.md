# PoC — Server Juice (OSINT, 15 pts) — #37  [RESOLVIDO]

**Flag:** `CSSCTF{premiumreserve}`  ✅

## Enunciado
Categoria OSINT. *"If you want to appease the algorithm (and maybe get a head start on future hints), consider keeping us on your radar by following."* Flag format: CSSCTF{...}.

## Solução
Desafio de "siga nossas redes sociais" — a flag estava publicada na conta oficial dos
organizadores no Instagram (**@cybersecuritysydney**, renomeada de `usyd_cybersoc`;
CSS = Cybersecurity Society Sydney, dona de `cybersecurity.sydney`).

A flag **não** estava na bio nem no corpo dos posts, e sim **nos comentários** de um post
da conta — daí o enunciado pedir para "seguir / ficar no radar". Visualizando os comentários
(logado no Instagram) aparece:

```
CSSCTF{premiumreserve}
```

## Contas oficiais localizadas (recon)
- Instagram: **@cybersecuritysydney**  ← flag nos comentários
- Linktree `linktr.ee/usyd_cybersoc`; LinkedIn `usyd-csec`; Facebook; Discord `discord.gg/vRFEPEHy8Z`; site `usydcyber.com`

## Lição
Em OSINT de redes sociais, não parar na bio/posts: **comentários, respostas e stories**
também carregam o conteúdo. O acesso exige estar logado na plataforma.
