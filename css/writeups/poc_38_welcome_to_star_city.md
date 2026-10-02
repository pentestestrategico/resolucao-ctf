# PoC — Welcome to Star City (Web, 15 pts) — #38

**Flag:** `CSSCTF{we_BU1LT_this_city_from_r0ck_and_R011}`  ✅

## Enunciado
Alvo `http://34.116.80.78:9981/`. Dica: *"is there more to be seen than meets the eye?"*

## Passos
1. HTML da página é mínimo e só referencia `style.css`.
2. Na **última linha** do CSS há um comentário:
   ```css
   /*Q1NTQ1RGJTdCd2VfQlUxTFRfdGhpc19jaXR5X2Zyb21fcjBja19hbmRfUjAxMSU3RA*/
   ```
3. Começa com `Q1NTQ1RG` = Base64 de "CSSCTF". Decodificar Base64 → URL-decode:
   ```bash
   echo 'Q1NTQ1RGJTdCd2VfQlUxTFRfdGhpc19jaXR5X2Zyb21fcjBja19hbmRfUjAxMSU3RA' \
     | base64 -d | python3 -c "import sys,urllib.parse;print(urllib.parse.unquote(sys.stdin.read()))"
   # CSSCTF{we_BU1LT_this_city_from_r0ck_and_R011}
   ```

## Lição
Esconder segredo em comentário de CSS codificado (Base64+URL-encode) é ofuscação, não segurança — o cliente recebe tudo.
