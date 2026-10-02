# CTF Write-up — Welcome to Star City

- **Evento:** CSS CTF Semester 2 2026 (Cybersecurity Society Sydney)
- **Plataforma:** https://ctf.cybersecurity.sydney/
- **Desafio:** Welcome to Star City
- **Categoria:** Web
- **Pontos:** 15 (Beginner)
- **Autor:** Michael Dalton
- **Alvo:** http://34.116.80.78:9981/
- **Data de resolução:** 2026-09-30
- **Status:** ✅ Resolvido (submissão retornou "Correct")

---

## Flag

```
CSSCTF{we_BU1LT_this_city_from_r0ck_and_R011}
```

---

## Enunciado

> Welcome to Star City. Home of stars galore. But is there more to be seen than meets the eye?
>
> Flag Format: CSSCTF{...}

A frase-chave *"is there more to be seen than meets the eye?"* ("há mais do que se vê à primeira vista?")
aponta claramente para **conteúdo escondido** na página — um clássico de desafios Web para iniciantes.

---

## Reconhecimento

Ao abrir `http://34.116.80.78:9981/`, a página exibe apenas um letreiro neon
"Welcome to Star City" sobre um skyline animado. Nenhuma flag visível.

O HTML servido é minúsculo (309 bytes) e não contém comentários nem a flag:

```html
<!DOCTYPE html><html><head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>STAR1001</title>
  <link rel="stylesheet" href="style.css">
</head><body>
  <div class="skyline" aria-hidden="true"></div>
  <main><h1 data-text="Welcome to Star City">Welcome to Star City</h1></main>
</body></html>
```

O único recurso externo referenciado é **`style.css`**. Como o desafio é da categoria Web
e a dica fala em "algo além do que se vê", o próximo passo natural é inspecionar o CSS.

## Exploração

Baixando e analisando o `style.css` (13.619 bytes), quase todo o arquivo é decoração
(gradientes, estrelas, animações `@keyframes`). O achado está **na última linha do arquivo**,
num comentário CSS facilmente ignorado:

```css
@keyframes shimmer { to { background-position: -300% 0; } }
/*Q1NTQ1RGJTdCd2VfQlUxTFRfdGhpc19jaXR5X2Zyb21fcjBja19hbmRfUjAxMSU3RA*/
```

A string começa com `Q1NTQ1RG`, que em Base64 decodifica para `CSSCTF` — sinal claro
de que é a flag codificada.

### Decodificação (duas camadas)

1. **Base64 → texto:**

   ```
   Q1NTQ1RGJTdCd2VfQlUxTFRfdGhpc19jaXR5X2Zyb21fcjBja19hbmRfUjAxMSU3RA
   → CSSCTF%7Bwe_BU1LT_this_city_from_r0ck_and_R011%7D
   ```

2. **URL-decode** (`%7B` = `{`, `%7D` = `}`):

   ```
   CSSCTF{we_BU1LT_this_city_from_r0ck_and_R011}
   ```

### Comandos usados

```bash
# 1. Baixar o CSS e caçar comentários / conteúdo suspeito
curl -s http://34.116.80.78:9981/style.css -o star.css
grep -aoE '/\*.*\*/' star.css
# -> /*Q1NTQ1RGJTdCd2VfQlUxTFRfdGhpc19jaXR5X2Zyb21fcjBja19hbmRfUjAxMSU3RA*/

# 2. Decodificar: Base64 seguido de URL-decode
s='Q1NTQ1RGJTdCd2VfQlUxTFRfdGhpc19jaXR5X2Zyb21fcjBja19hbmRfUjAxMSU3RA'
echo "$s" | base64 -d | python3 -c "import sys,urllib.parse;print(urllib.parse.unquote(sys.stdin.read()))"
# -> CSSCTF{we_BU1LT_this_city_from_r0ck_and_R011}
```

## Submissão

A flag foi inserida no campo "Bandeira" do desafio na plataforma e a resposta foi **"Correct"**.

---

## Causa raiz / Lição

O desafio ilustra um princípio básico de segurança web: **o cliente recebe tudo** — HTML, CSS
e JS ficam totalmente acessíveis ao usuário. "Esconder" um segredo num comentário de CSS
(ainda que codificado em Base64) **não é segurança** — é apenas ofuscação trivial.

**Recomendações defensivas:**
- Nunca armazenar segredos em arquivos estáticos entregues ao cliente (HTML/CSS/JS).
- Codificação (Base64, URL-encode) **não é criptografia**; não oferece confidencialidade.
- Segredos devem residir no servidor, protegidos por autenticação/autorização.

## Metodologia (checklist para desafios Web de "conteúdo escondido")

1. Ver o código-fonte da página (`view-source:` / DevTools).
2. Procurar comentários HTML e elementos ocultos (`display:none`, `hidden`, off-screen).
3. Enumerar e baixar **todos** os recursos referenciados (CSS, JS, imagens, SVGs, fontes).
4. Procurar comentários e strings suspeitas nesses arquivos (`grep` por padrão da flag e por Base64).
5. Checar arquivos comuns: `robots.txt`, `sitemap.xml`, `.git/`, headers HTTP de resposta.
6. Decodificar/normalizar qualquer string codificada (Base64, hex, URL-encode).
