# PoC — prince walk (Reverse Engineering, 50 pts) — #46

**Flag:** `CSSCTF{P12INC3_0R_P1NC3?}`  *(encontrada, não submetida)*

## Enunciado
Binário `prince_walk` (ncurses game). Avatar em (1,1), beacon em **(999999,999999)**. "Alcance o beacon." Pistas: *"You know PINCE is installed, right?"* e achievement *"Reject Debugger, Embrace Walking"*.

## Análise
- Jogo interativo; caminhar até (999999,999999) é inviável (mapa procedural, árvores bloqueiam).
- A intenção é usar um editor de memória/debugger (PINCE) para teleportar — ou reverter a geração da flag.
- Na função de vitória (offset `0x2c52`), quando `x==y==0xf423f` (999999), a flag é **computada deterministicamente** a partir das coordenadas via hashes (`lowbias32` em 0x2c18, `rotl32` em 0x2bf8) e uma tabela em `.rodata` (0x4a80). Não é armazenada em texto plano.

## Exploração (chamar a função via gdb, sem jogar)
A função `flag_gen(int x, int y, char* buf, size_t n)` só depende dos argumentos → basta chamá-la:
```bash
gdb -q -batch \
  -ex 'break isatty' -ex 'run < /dev/null' \
  -ex 'python
import gdb
base=[int(l.split()[0],16) for l in gdb.execute("info proc mappings",to_string=True).splitlines() if "prince_walk" in l][0]
buf=int(gdb.parse_and_eval("(long)malloc(256)"))
gdb.execute("call (int)((int(*)(int,int,char*,long))%d)(999999,999999,%d,256)"%(base+0x2c52,buf))
print(gdb.execute("x/s %d"%buf,to_string=True))
' ./prince_walk
```
(Quebra em `isatty` — chamado no check de terminal — garante libc carregada; depois chama a função diretamente.)

Saída:
```
Developer:
"No you didn't."

MISSION COMPLETE

CSSCTF{P12INC3_0R_P1NC3?}
```

## Lição
Reverter/chamar diretamente a rotina que gera o segredo evita "jogar" o desafio. O flag é um trocadilho: **PRINCE** (o jogo) vs **PINCE** (o debugger que o autor esperava que você usasse).
