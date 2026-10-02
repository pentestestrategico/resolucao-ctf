# Progresso — Severed Symmetry (Cryptography, 200 pts) — #28  [NÃO CONCLUÍDO]

## Enunciado
Criptosistema multivariado (MQ) sobre GF(17). Dados: `source.py` (keygen/encrypt) + `out.txt` (chave pública + ciphertext). Recuperar a FLAG. Sem a chave privada.

## Análise do esquema (source.py)
- Parâmetros: `p=17, n=32, m=34, t=16, s=4`.
- Estrutura em camadas (estilo UOV/Rainbow/HFEv-):
  - `z = A2·x + b2` (afim, linear).
  - **Camada w** (t=16): `w_i = z_i − q_i(z[t:])` → **quadrática** em x.
  - **Camada U** (m−t=18): `U_j = umap_j(w, z[t:])`, quadrática em (w, z) → **quártica** em x (termos `w_a·w_b`).
  - Público: `P = A1·central + b1` → 34 polinômios **quárticos** em 32 variáveis (~55k monômios cada; `out.txt` = 31 MB).
- Ciphertext: 3 blocos de 34 valores (flag ~44 bytes, frame = len(4B) + flag, dígitos base-17 width 2).

## Ataque "Severed Symmetry" (degree-falling) — parcial
A parte de grau 4 dos 34 polinômios tem posto ≤ 18 (vem só da camada U, `w_a·w_b`). Logo o **left-kernel** da parte de grau 4 tem dimensão ≥ 34−18 = **16** → 16 combinações lineares dos polinômios públicos cuja parte quártica (e, empiricamente, cúbica) se anula → **16 equações puramente quadráticas**.

Confirmado experimentalmente:
```
deg-4 left-kernel dim = 16  -> 16 equações de grau <= 2
(partes quadráticas dessas 16 são independentes: posto 16)
```
Essas 16 quadráticas **isolam a camada w** (a "simetria cortada"). Com elas recuperam-se os valores `w(x)=W`.

## O que falta (caminho identificado, não implementado)
1. Ajustar a parte de grau 4 de cada equação U (as 18 complementares) como forma quadrática nos 16 polinômios w (resolver `beta_ab` tal que deg4(U)=Σ beta_ab·w_a·w_b).
2. Substituir `w_a·w_b → W_a·W_b` (válido no conjunto solução) → colapsar cada quártica U para **quadrática em z[16:]** (16 variáveis).
3. Resolver o sistema quadrático sobredeterminado em 16 variáveis (relinearização/XL — viável nesse tamanho) + enumerar os s=4 "vinegar" (17⁴≈83k) como na decrypt.
4. Recuperar `z` → `x = A2⁻¹(z−b2)` por bloco → `decode_frame` → flag.

## Status
Estrutura do ataque validada (degree-falling funciona e isola a camada quadrática). A implementação completa da inversão é extensa e sem CAS (sage/magma indisponíveis) tem risco alto; **ficou pendente**.
