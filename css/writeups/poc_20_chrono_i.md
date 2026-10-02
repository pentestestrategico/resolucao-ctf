# PoC — Chrono I (Cryptography, 25 pts) — #20

**Flag:** `CSSCTF{every_second_hides_a_secret}`  ✅

## Enunciado
- Mensagem: `2026/09/21 14:35:07 - "As always, The time is always the key to unlock it"`
- Ciphertext: `ESUITO{gwfvb_xejqnf_nimgt_b_whhrlv}`

## Análise
`ESUITO` deve virar `CSSCTF`. Deslocamentos (cipher−plain): E−C=2, S−S=0, U−S=2, I−C=6, T−T=0, O−F=9 → **2,0,2,6,0,9** = os dígitos de **2026/09/21...** → **Vigenère com chave = dígitos do timestamp**.

## Solução
```python
ct="ESUITO{gwfvb_xejqnf_nimgt_b_whhrlv}"
key="20260921143507"; ki=0; out=[]
for ch in ct:
    if ch.isalpha():
        s=int(key[ki%len(key)]); ki+=1
        base=ord('A') if ch.isupper() else ord('a')
        out.append(chr((ord(ch)-base-s)%26+base))
    else: out.append(ch)
print("".join(out))   # CSSCTF{every_second_hides_a_secret}
```
