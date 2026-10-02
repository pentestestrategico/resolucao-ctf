# CTF PMERJ: descoberta da palavra com SecLists e Python

Este tutorial demonstra um ataque de dicionário: testar palavras de uma lista até encontrar uma chave que decifre o criptograma. É uma busca limitada às candidatas, não uma busca por todas as chaves AES.

No desafio original, a pista já fornece as letras CAVEIRA. Aqui ignoramos essa informação para demonstrar como encontrar a palavra usando SecLists.

## 1. O que sabemos

- Algoritmo: AES-128, modo CBC, preenchimento PKCS#7.
- Criptograma: 80 bytes, representados por 160 caracteres hexadecimais.
- Trecho conhecido: `PMERJ (190) ----`, com 16 bytes.
- Código secreto: IV de 16 caracteres ASCII numéricos.

Assumimos que o trecho conhecido inicia a mensagem. O relatório diz que ele está contido na mensagem; sua posição inicial é uma hipótese.

Também testamos uma derivação específica: os primeiros 16 bytes de SHA-1 da palavra. Ela funcionou neste criptograma. As pistas PRNG e SHA1, sozinhas, não especificam essa fórmula nem a tornam equivalente ao SHA1PRNG do Java.

## 2. Arquivos da PoC

- Programa comentado: `/home/kali/Desktop/ctf/jhon.py`.
- Lista: `/home/kali/SecLists/Miscellaneous/lang-portuguese.txt`.
- Dependência Python: `cryptography`, já disponível no ambiente testado.

O programa não chama o John the Ripper. Apesar do nome do arquivo, ele implementa a busca em Python. A palavra correta não está fixada no código.

## 3. Executar a busca

```bash
python3 /home/kali/Desktop/ctf/jhon.py /home/kali/SecLists/Miscellaneous/lang-portuguese.txt
```

O script lê cada linha e testa a palavra original, em minúsculas, com a primeira letra maiúscula e em maiúsculas. Variações idênticas da mesma linha são descartadas.

Quando lê `caveira`, por exemplo, testa:

```text
caveira
Caveira
CAVEIRA
```

Essa regra é aplicada a todas as palavras, sem saber antecipadamente qual funciona.

## 4. Transformar cada candidata em chave

O trecho central do programa é:

```python
chave = hashlib.sha1(candidata.encode("utf-8")).digest()[:16]
```

`encode` transforma o texto em bytes. SHA-1 calcula um resultado de 20 bytes. `[:16]` seleciona os primeiros 16 bytes, formando a chave de 128 bits exigida pelo AES-128.

Uma palavra diferente ou outra capitalização produz outra chave.

## 5. Testar a chave sem conhecer o IV

Chamamos os blocos cifrados de C1, C2, C3 e assim por diante. No CBC:

```text
P1 = AES_decifrar(chave, C1) XOR IV
P2 = AES_decifrar(chave, C2) XOR C1
P3 = AES_decifrar(chave, C3) XOR C2
```

Só o primeiro bloco depende do IV original. Para testar a candidata, o programa decifra a partir de C2 usando C1 como IV:

```python
dec = Cipher(algorithms.AES(chave), modes.CBC(CRIPTOGRAMA[:16])).decryptor()
restante = dec.update(CRIPTOGRAMA[16:]) + dec.finalize()
```

Depois verifica o padding PKCS#7, a decodificação UTF-8 e se os caracteres são imprimíveis. Padding válido sozinho pode aparecer por acaso e não confirma a chave.

## 6. Recuperar e conferir o código secreto

Para uma candidata que passa nos filtros, o programa usa o prefixo conhecido:

```text
IV = AES_decifrar(chave, C1) XOR b"PMERJ (190) ----"
```

Ele confere se todos os 16 bytes do IV são dígitos ASCII de 0 a 9.

Nesta PoC, a busca por tentativas ocorre nas palavras que geram a chave. O IV é calculado diretamente, não enumerado por força bruta. O prefixo é uma entrada conhecida; não é descoberto pelo script.

## 7. Resultado reproduzido

Na execução local de validação, o programa retornou:

```text
Palavra encontrada: Caveira
Chave AES (hex): 35759ba0f40cb1dbc3cfb93dbbbf86c6
Código secreto (IV ASCII): 0000000007233652
Mensagem: PMERJ (190) ---- Na duvida, a seguranca da equipe sempre vem em primeiro lugar.
Tentativas: 31239
```

A quantidade de tentativas depende da versão e da ordem da lista. O tempo depende da máquina.

O programa também recifra a mensagem e compara os bytes com o criptograma original. Isso verifica a consistência das operações; não é autenticação nem prova isolada de que a chave está correta. O texto coerente, o padding e o IV numérico sustentam a solução em conjunto.

## 8. Usar candidatas previamente geradas pelo John

Se você já tem `candidatas.txt`, execute:

```bash
python3 /home/kali/Desktop/ctf/jhon.py candidatas.txt --sem-variacoes
```

O caminho relativo é interpretado a partir do diretório atual. A opção evita gerar novas variações sobre aquelas já presentes no arquivo.

Para conferir se o arquivo contém a candidata exata:

```bash
rg -n -x 'Caveira' candidatas.txt
```

## 9. Limites do exemplo

A PoC é específica deste criptograma, dessa hipótese de derivação e do prefixo conhecido. Se a palavra ou sua capitalização não estiverem entre as candidatas, ela não será encontrada. Uma senha aleatória longa pode tornar essa abordagem inviável.

O script recebe uma wordlist; ele não implementa a interface de três argumentos (semente, texto parcial e criptograma) pedida na missão original. Também não demonstra força bruta sobre os IVs numéricos. Ele demonstra a recuperação por dicionário solicitada neste tutorial.
