#!/usr/bin/env python3
Execute: python3 decifrar.py
Dependência: cryptography (python3 -m pip install cryptography).

A derivação confirmada neste desafio usa os primeiros 16 bytes do SHA-1
de "Caveira". Não é necessário implementar um PRNG para este criptograma.
"""

import hashlib

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


CRIPTOGRAMA_HEX = """
3194b86ab8edd5783e2f7ca1c75bf676904a1fbdbd2b5c248afaeeec4fca08150c2111
57efd08d464e77aa2b334dca2607dc098cc21121c2c3395a8b322cbd66d270d26ffdab
3020fdcfe7fbdcf8e08f
"""


def main() -> None:
    # fromhex ignora os espaços e as quebras de linha da transcrição.
    criptograma = bytes.fromhex(CRIPTOGRAMA_HEX)
    tamanho_bloco = 16  # AES sempre opera sobre blocos de 128 bits.
    if not criptograma or len(criptograma) % tamanho_bloco:
        raise ValueError("O criptograma precisa conter blocos completos de 16 bytes.")

    # A capitalização faz diferença: "Caveira" não equivale a "CAVEIRA".
    # digest() retorna bytes; hexdigest() retornaria texto hexadecimal.
    seed = b"Caveira"
    chave = hashlib.sha1(seed).digest()[:tamanho_bloco]

    # O enunciado fornece este trecho conhecido. A hipótese de que ele
    # inicia a mensagem foi confirmada pelo texto recuperado e pelo IV numérico.
    primeiro_bloco_conhecido = b"PMERJ (190) ----"
    if len(primeiro_bloco_conhecido) != tamanho_bloco:
        raise ValueError("O texto conhecido deve ocupar exatamente um bloco.")

    # No CBC: P1 = D_chave(C1) XOR IV.
    # Portanto: IV = D_chave(C1) XOR P1.
    # ECB é usado somente para calcular D_chave(C1), sem aplicar um IV.
    decifrador_bloco = Cipher(algorithms.AES(chave), modes.ECB()).decryptor()
    bloco_decifrado = (
        decifrador_bloco.update(criptograma[:tamanho_bloco])
        + decifrador_bloco.finalize()
    )
    iv = bytes(a ^ b for a, b in zip(bloco_decifrado, primeiro_bloco_conhecido))

    # O relatório afirma que o código secreto é o IV em caracteres ASCII
    # de 0 a 9. Mantemos uma string para preservar todos os zeros iniciais.
    if not all(ord("0") <= valor <= ord("9") for valor in iv):
        raise ValueError("O IV recuperado não contém somente dígitos ASCII.")
    codigo_secreto = iv.decode("ascii")

    # Agora podemos decifrar todos os blocos usando AES-128-CBC.
    decifrador = Cipher(algorithms.AES(chave), modes.CBC(iv)).decryptor()
    mensagem_com_padding = decifrador.update(criptograma) + decifrador.finalize()

    # PKCS#7 completa o último bloco. A biblioteca valida os bytes antes
    # de removê-los. O argumento 128 é o tamanho do bloco em BITS.
    removedor = padding.PKCS7(128).unpadder()
    mensagem = removedor.update(mensagem_com_padding) + removedor.finalize()
    texto = mensagem.decode("utf-8")

    # Verificação de consistência: aplicar novamente padding e cifrar deve
    # reproduzir cada byte do criptograma recebido. Isso não é autenticação;
    # o texto legível e o IV numérico também sustentam a solução encontrada.
    adicionador = padding.PKCS7(128).padder()
    mensagem_recomposta = adicionador.update(mensagem) + adicionador.finalize()
    cifrador = Cipher(algorithms.AES(chave), modes.CBC(iv)).encryptor()
    recifrado = cifrador.update(mensagem_recomposta) + cifrador.finalize()
    if recifrado != criptograma:
        raise ValueError("A recifragem não reproduziu o criptograma original.")

    print(f"Chave AES (hex): {chave.hex()}")
    print(f"IV (hex): {iv.hex()}")
    print(f"Código secreto (IV ASCII): {codigo_secreto}")
    print(f"Mensagem: {texto}")
    print("Validação: recifragem idêntica ao criptograma original.")


if __name__ == "__main__":
    main()
