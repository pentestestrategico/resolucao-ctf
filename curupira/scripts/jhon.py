#!/usr/bin/env python3
"""Ataque de dicionário ao criptograma do CTF, sem conhecer a palavra.

Dependência: cryptography.
Uso: python3 jhon.py [wordlist]
Para candidatas já geradas pelo John: python3 jhon.py candidatas.txt --sem-variacoes
Não chama o John: implementa a geração de variações e a verificação em Python.
"""

import argparse
import hashlib
from pathlib import Path
import sys
import time

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


CRIPTOGRAMA = bytes.fromhex(
    "3194b86ab8edd5783e2f7ca1c75bf676904a1fbdbd2b5c248afaeeec4fca08150c2111"
    "57efd08d464e77aa2b334dca2607dc098cc21121c2c3395a8b322cbd66d270d26ffdab"
    "3020fdcfe7fbdcf8e08f"
)
# Pista do enunciado, não a mensagem completa nem a senha procurada.
PREFIXO = b"PMERJ (190) ----"
LISTA_PADRAO = Path("/home/kali/SecLists/Miscellaneous/lang-portuguese.txt")


def testar(candidata):
    """Retorna chave, IV e mensagem se todas as verificações passarem."""
    # Hipótese de derivação do desafio: SHA-1 truncado em 16 bytes.
    chave = hashlib.sha1(candidata.encode("utf-8")).digest()[:16]

    # C1 serve como IV para decifrar a partir de C2, sem o IV original.
    dec = Cipher(algorithms.AES(chave), modes.CBC(CRIPTOGRAMA[:16])).decryptor()
    restante = dec.update(CRIPTOGRAMA[16:]) + dec.finalize()
    try:
        unpad = padding.PKCS7(128).unpadder()
        restante = unpad.update(restante) + unpad.finalize()
        texto = restante.decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None
    # Padding válido sozinho pode ocorrer por acaso. Exigimos texto plausível.
    if not texto or not all(c.isprintable() or c in "\r\n\t" for c in texto):
        return None

    # P1 = D(K, C1) XOR IV; portanto IV = D(K, C1) XOR P1.
    dec = Cipher(algorithms.AES(chave), modes.ECB()).decryptor()
    bloco = dec.update(CRIPTOGRAMA[:16]) + dec.finalize()
    iv = bytes(a ^ b for a, b in zip(bloco, PREFIXO))
    if not all(48 <= b <= 57 for b in iv):
        return None

    mensagem = PREFIXO + restante
    # Verificação de consistência; não é autenticação criptográfica.
    pad = padding.PKCS7(128).padder()
    padded = pad.update(mensagem) + pad.finalize()
    enc = Cipher(algorithms.AES(chave), modes.CBC(iv)).encryptor()
    if enc.update(padded) + enc.finalize() != CRIPTOGRAMA:
        return None
    return chave, iv, mensagem.decode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wordlist", nargs="?", type=Path, default=LISTA_PADRAO)
    parser.add_argument("--sem-variacoes", action="store_true",
                        help="Testar cada linha exatamente como fornecida")
    args = parser.parse_args()
    inicio = time.monotonic()
    tentativas = 0
    print(f"Lista: {args.wordlist}", flush=True)
    try:
        # UTF-8 estrito evita alterar silenciosamente palavras da lista.
        with args.wordlist.open(encoding="utf-8-sig") as arquivo:
            for linha in arquivo:
                palavra = linha.rstrip("\r\n")
                if not palavra:
                    continue
                variantes = [palavra] if args.sem_variacoes else [
                    palavra, palavra.lower(), palavra.capitalize(), palavra.upper()
                ]
                # Preserva a ordem e elimina repetições dentro desta linha.
                for candidata in dict.fromkeys(variantes):
                    tentativas += 1
                    resultado = testar(candidata)
                    if resultado:
                        chave, iv, mensagem = resultado
                        print(f"Palavra encontrada: {candidata}")
                        print(f"Chave AES (hex): {chave.hex()}")
                        print(f"Código secreto (IV ASCII): {iv.decode('ascii')}")
                        print(f"Mensagem: {mensagem}")
                        print(f"Tentativas: {tentativas}")
                        print(f"Tempo: {time.monotonic() - inicio:.2f} s")
                        print("Validação: texto, padding, IV numérico e recifragem consistentes.")
                        return 0
                    if tentativas % 10000 == 0:
                        print(f"Testadas {tentativas} candidatas...", file=sys.stderr)
    except (OSError, UnicodeError) as erro:
        print(f"Erro ao ler a lista: {erro}", file=sys.stderr)
        return 2
    print(f"Nenhuma candidata passou nas verificações ({tentativas} tentativas).")
    print("Isso não esgota outras palavras, variações ou derivações de chave.")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nBusca interrompida.", file=sys.stderr)
        sys.exit(130)
