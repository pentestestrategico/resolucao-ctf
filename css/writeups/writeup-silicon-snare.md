---
title: "Silicon Snare"
ctf: "CSSCTF — Return of Nexus"
date: 2026-09-30
category: misc
flag_format: "CSSCTF{32 bits}"
---

# Silicon Snare — explicação e PoC

## Resultado

```text
CSSCTF{01010000010000010101001101010011}
```

O padrão acima ativa `Override` e é a única solução do circuito reconstruído. A ordem é `I00` a `I31`, começando às 12 horas e seguindo no sentido horário.

## Arquivos e reprodução

Os artefatos estão na subpasta `silicon-snare/`, preservando os arquivos do desafio anterior:

- `schematic.svg` e `schematic.png`: cópias dos arquivos fornecidos em Downloads;
- `solve_silicon.py`: PoC completa, do SVG à flag, usando somente a biblioteca padrão do Python;
- `netlist.json`: portas e conexões extraídas, incluindo IDs e coordenadas dos fios;
- `validation.json`: valores intermediários, prova de unicidade pelo solver e testes de inversão de bits;
- `flag.txt`: resultado.

Execute:

```bash
cd /home/kali/Desktop/ctf/css/silicon-snare
python3 solve_silicon.py
```

Também é possível fornecer outro caminho para o mesmo SVG:

```bash
python3 solve_silicon.py /home/kali/Downloads/schematic.svg
```

Não há dependências externas. O extrator usa os IDs de grupos desta renderização Matplotlib; um SVG reexportado com outros IDs exigiria adaptar a extração.

## 1. Seguir os fios e reconstruir as portas

A legenda fornecida define:

| Símbolo | Equação |
| --- | --- |
| Flow (`f`) | `Y = A AND B` |
| Merge (`m`) | `Y = A XOR B` |
| Negate (`n`) | `Y = NOT A` |
| Shift (`s`) | `Y0 = A OR B`; `Y1 = A AND NOT B` |

A porta Shift é assimétrica: trocar A e B muda Y1. Seu lado pontudo contém A e Y0; o lado plano contém B e Y1.

No SVG, os caminhos dos fios são `line2d_1` a `line2d_143`. Os terminais das portas estão nos pequenos segmentos pretos `line2d_269` a `line2d_497`. A PoC conecta a extremidade de cada fio ao terminal com as mesmas coordenadas, com tolerância de `0,00001` unidade SVG. Os rótulos são recuperados das referências aos glifos de texto.

Esta extração preserva os caminhos individuais. Interseções geométricas no meio de fios não geram novas conexões: segundo a legenda, somente um ponto preenchido indica ramificação. Fios que partem do mesmo terminal são tratados como cópias do mesmo sinal.

Resultado da extração: **74 portas e 143 fios**. Todos os terminais de entrada foram ligados uma única vez; as saídas usadas foram identificadas explicitamente como Y, Y0 ou Y1. O último fio conecta `f13` ao centro `Override`.

As 32 portas Merge externas formam um padrão simples, apesar do emaranhado visual:

```text
m[i] = I[(i + 7) mod 32] XOR I[i],   i = 0, …, 31
```

Os rótulos das portas usam hexadecimal: `m10` é a porta de índice 16; os rótulos de entrada usam decimal: `I10` é a entrada de índice 10.

## 2. Propagar a exigência Override = 1

As últimas portas são:

```text
Override = f13 = f12 AND f11
f12 = I03 AND I01
f11 = f08 AND f10
f10 = f0f AND f0c
```

Logo `I01 = I03 = 1`, e `f08`, `f0f` e `f0c` também precisam valer 1.

Três portas XOR internas parecem introduzir alternativas, mas há reconvergência de sinais. A identidade útil é:

```text
(a AND NOT b) XOR a = a AND b
```

Seguindo os fios:

```text
m20 = s02.Y1 XOR s01.Y1 = s01.Y1 AND f02
m21 = s03.Y1 XOR f04    = f04 AND f05
m22 = s0c.Y1 XOR n05    = n05 AND s0b.Y1
```

Outra identidade resolve o ramo com duas inversões:

```text
n02 = NOT(s06.Y0)
    = NOT(n00 OR n01)
    = f09 AND f0a
```

Agora basta propagar:

- Uma Flow com saída 1 exige A = B = 1.
- Uma Shift com Y1 = 1 exige A = 1 e B = 0.
- Uma Shift com Y0 = 0 exige A = B = 0.
- Uma Negate inverte o valor exigido.

A propagação completa chega a estas condições nas portas externas:

| Ramo exigido | Merge = 1 | Merge = 0 |
| --- | --- | --- |
| `f08` | `m02 m08 m0a m0c m10 m12 m14 m16 m18 m1a m1c m1e` | `m00 m04 m06 m0e` |
| `f0c` | `m01 m09 m11 m19` | `m05 m0d m15 m1d` |
| `f0f` | `m03 m13 m1b m1f` | `m07 m0b m0f m17` |

Portanto, as saídas de `m00` a `m1f` devem ser:

```text
01110000111010001111101011111011
```

## 3. Recuperar as entradas e verificar unicidade

Defina `d[i]` como o valor exigido de Merge. Então:

```text
I[(i + 7) mod 32] = I[i] XOR d[i]
```

Como `gcd(7,32) = 1`, saltar sete posições percorre todas as entradas. Escolher um valor para I00 determina os outros 31 bits. As equações Merge admitem dois padrões complementares; a condição final `I01 = I03 = 1` seleciona:

```text
I00–I07: 01010000
I08–I15: 01000001
I16–I23: 01010011
I24–I31: 01010011
```

Como conferência adicional, os bytes acima representam `PASS` em ASCII; a flag exige os bits, não essa palavra.

A PoC faz a resolução diretamente a partir do circuito extraído, sem embutir o padrão de Merge ou a flag. Cada porta é traduzida para cláusulas booleanas, e um solver DPLL completo encontra uma atribuição que satisfaz `Override = 1`.

São **119 variáveis booleanas e 291 cláusulas**, incluindo as duas saídas de cada Shift. Para comprovar unicidade, o script acrescenta uma cláusula que proíbe exatamente o padrão encontrado nas 32 entradas. O sistema passa a ser insatisfatível: não existe outra entrada que ative Override no circuito extraído.

Por fim, um simulador separado do solver avalia as portas usando AND, XOR, NOT e as duas regras Shift. Ele confirma a saída 1 para a flag e saída 0 após inverter individualmente cada um dos 32 bits.

Saída real da PoC:

```text
Gates: 74 Wires: 143
Override: 1 Unique solution: True
Single-bit flips rejected: 32
CSSCTF{01010000010000010101001101010011}
```

A verificação é local, sobre o esquema fornecido; não foi feita submissão à plataforma do CTF.

## Evidência de integridade

SHA-256 do SVG analisado:

```text
63a680d0f62a1375f796b316c595c54477eac84c5d7c435b49b4dbecb02e7a72
```

## Netlist resumida e valores recuperados

| Porta | Tipo | A | B | Saída |
| --- | --- | --- | --- | --- |
| `m00` | XOR | `I07` | `I00` | 0 |
| `m01` | XOR | `I08` | `I01` | 1 |
| `m02` | XOR | `I09` | `I02` | 1 |
| `m03` | XOR | `I10` | `I03` | 1 |
| `m04` | XOR | `I11` | `I04` | 0 |
| `m05` | XOR | `I12` | `I05` | 0 |
| `m06` | XOR | `I13` | `I06` | 0 |
| `m07` | XOR | `I14` | `I07` | 0 |
| `m08` | XOR | `I15` | `I08` | 1 |
| `m09` | XOR | `I16` | `I09` | 1 |
| `m0a` | XOR | `I17` | `I10` | 1 |
| `m0b` | XOR | `I18` | `I11` | 0 |
| `m0c` | XOR | `I19` | `I12` | 1 |
| `m0d` | XOR | `I20` | `I13` | 0 |
| `m0e` | XOR | `I21` | `I14` | 0 |
| `m0f` | XOR | `I22` | `I15` | 0 |
| `m10` | XOR | `I23` | `I16` | 1 |
| `m11` | XOR | `I24` | `I17` | 1 |
| `m12` | XOR | `I25` | `I18` | 1 |
| `m13` | XOR | `I26` | `I19` | 1 |
| `m14` | XOR | `I27` | `I20` | 1 |
| `m15` | XOR | `I28` | `I21` | 0 |
| `m16` | XOR | `I29` | `I22` | 1 |
| `m17` | XOR | `I30` | `I23` | 0 |
| `m18` | XOR | `I31` | `I24` | 1 |
| `m19` | XOR | `I00` | `I25` | 1 |
| `m1a` | XOR | `I01` | `I26` | 1 |
| `m1b` | XOR | `I02` | `I27` | 1 |
| `m1c` | XOR | `I03` | `I28` | 1 |
| `m1d` | XOR | `I04` | `I29` | 0 |
| `m1e` | XOR | `I05` | `I30` | 1 |
| `m1f` | XOR | `I06` | `I31` | 1 |
| `s00` | SHIFT | `m10` | `m00` | Y0=1; Y1=1 |
| `f00` | AND | `m18` | `m08` | 1 |
| `f01` | AND | `s00.Y1` | `f00` | 1 |
| `s01` | SHIFT | `m14` | `m04` | Y0=1; Y1=1 |
| `f02` | AND | `m1c` | `m0c` | 1 |
| `s02` | SHIFT | `s01.Y1` | `f02` | Y0=1; Y1=0 |
| `m20` | XOR | `s02.Y1` | `s01.Y1` | 1 |
| `f03` | AND | `f01` | `m20` | 1 |
| `f04` | AND | `m12` | `m02` | 1 |
| `f05` | AND | `m1a` | `m0a` | 1 |
| `s03` | SHIFT | `f04` | `f05` | Y0=1; Y1=0 |
| `m21` | XOR | `s03.Y1` | `f04` | 1 |
| `s04` | SHIFT | `m16` | `m06` | Y0=1; Y1=1 |
| `s05` | SHIFT | `m1e` | `m0e` | Y0=1; Y1=1 |
| `f06` | AND | `s05.Y1` | `s04.Y1` | 1 |
| `f07` | AND | `f06` | `m21` | 1 |
| `f08` | AND | `f03` | `f07` | 1 |
| `f09` | AND | `m11` | `m01` | 1 |
| `n00` | NOT | `f09` | — | 0 |
| `f0a` | AND | `m19` | `m09` | 1 |
| `n01` | NOT | `f0a` | — | 0 |
| `s06` | SHIFT | `n00` | `n01` | Y0=0; Y1=0 |
| `n02` | NOT | `s06.Y0` | — | 1 |
| `s07` | SHIFT | `m05` | `m15` | Y0=0; Y1=0 |
| `n03` | NOT | `s07.Y0` | — | 1 |
| `s08` | SHIFT | `m0d` | `m1d` | Y0=0; Y1=0 |
| `n04` | NOT | `s08.Y0` | — | 1 |
| `f0b` | AND | `n04` | `n03` | 1 |
| `f0c` | AND | `f0b` | `n02` | 1 |
| `f0d` | AND | `m13` | `m03` | 1 |
| `s09` | SHIFT | `m1b` | `m0b` | Y0=1; Y1=1 |
| `f0e` | AND | `s09.Y1` | `f0d` | 1 |
| `s0a` | SHIFT | `m07` | `m17` | Y0=0; Y1=0 |
| `n05` | NOT | `s0a.Y0` | — | 1 |
| `s0b` | SHIFT | `m1f` | `m0f` | Y0=1; Y1=1 |
| `s0c` | SHIFT | `n05` | `s0b.Y1` | Y0=1; Y1=0 |
| `m22` | XOR | `s0c.Y1` | `n05` | 1 |
| `f0f` | AND | `m22` | `f0e` | 1 |
| `f10` | AND | `f0f` | `f0c` | 1 |
| `f11` | AND | `f08` | `f10` | 1 |
| `f12` | AND | `I03` | `I01` | 1 |
| `f13` | AND | `f12` | `f11` | 1 |

## PoC completa

```python
#!/usr/bin/env python3
"""Extract exact SVG wire endpoints and reconstruct the logic circuit."""
import argparse,json,math,re,xml.etree.ElementTree as ET
from pathlib import Path
NS={'s':'http://www.w3.org/2000/svg'}
XL='{http://www.w3.org/1999/xlink}href'

def points(path):
    values=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',path.get('d',''))))
    return list(zip(values[::2],values[1::2]))

def extract(path):
    root=ET.parse(path).getroot()
    groups={g.get('id'):g for g in root.findall('.//s:g',NS)}
    labels=[]
    for i in range(62,136):
        g=groups[f'text_{i}']
        label=''.join(chr(int(u.get(XL).split('-')[-1],16)) for u in g.findall('.//s:use',NS))
        assert re.fullmatch('[mfsn][0-9a-f]{2}',label),label
        labels.append(label)
    terminals={}; gates={}; index=269
    for label in labels:
        typ=label[0]
        names={'m':['Y','A','B'],'f':['Y','A','B'],'n':['A','Y'],'s':['A','Y0','B','Y1']}[typ]
        gates[label]={'type':{'m':'XOR','f':'AND','n':'NOT','s':'SHIFT'}[typ],'inputs':{}}
        for name in names:
            p=groups[f'line2d_{index}'].find('s:path',NS)
            terminals[(label,name)]=points(p)[-1]; index+=1
    assert index==498
    def match(point):
        pairs=sorted((math.dist(point,pos),port) for port,pos in terminals.items())
        assert pairs[0][0]<0.00001,(point,pairs[:3])
        return pairs[0][1]
    wires=[]
    for i in range(1,144):
        p=groups[f'line2d_{i}'].find('s:path',NS); pts=points(p)
        if i<=64 or i in (139,140):
            angle=math.atan2(pts[0][0]-419.083408,390.891743-pts[0][1])%(2*math.pi)
            source=f'I{round(angle*32/(2*math.pi))%32:02d}'
        else:
            node,port=match(pts[0]); assert port.startswith('Y'),(i,node,port)
            source=node+(f'.{port}' if gates[node]['type']=='SHIFT' else '')
        if i==143:destination='Override'
        else:
            node,port=match(pts[-1]); assert port in ('A','B'),(i,node,port)
            assert port not in gates[node]['inputs']
            gates[node]['inputs'][port]=source; destination=f'{node}.{port}'
        wires.append({'svg_id':f'line2d_{i}','source':source,'destination':destination,'start':pts[0],'end':pts[-1]})
    for label,g in gates.items():assert set(g['inputs'])==({'A'} if g['type']=='NOT' else {'A','B'}),(label,g)
    return {'gates':gates,'wires':wires,'override':wires[-1]['source']}

def cnf(net):
    # Truth-table encoding: exclude exactly the rows violating each gate.
    names=[f'I{i:02d}' for i in range(32)]
    for name,g in net['gates'].items():
        names.extend([name+'.Y0',name+'.Y1'] if g['type']=='SHIFT' else [name])
    ids={name:i+1 for i,name in enumerate(names)}
    clauses=[]
    def relation(args,output,function):
        from itertools import product
        for values in product((0,1),repeat=len(args)):
            expected=int(function(*values))
            # If all inputs match this row, force its correct output.
            clauses.append([(-ids[a] if v else ids[a]) for a,v in zip(args,values)]
                           +[ids[output] if expected else -ids[output]])
    def conjunction(a,b,y):
        clauses.extend([[-y,a],[-y,b],[y,-a,-b]])
    def disjunction(a,b,y):
        clauses.extend([[y,-a],[y,-b],[-y,a,b]])
    for name,g in net['gates'].items():
        a=ids[g['inputs']['A']]
        b=ids[g['inputs']['B']] if 'B' in g['inputs'] else None
        typ=g['type']
        if typ=='SHIFT':
            disjunction(a,b,ids[name+'.Y0'])
            conjunction(a,-b,ids[name+'.Y1'])
        elif typ=='AND':conjunction(a,b,ids[name])
        elif typ=='NOT':clauses.extend([[ids[name],a],[-ids[name],-a]])
        elif typ=='XOR':relation(list(g['inputs'].values()),name,lambda a,b:a^b)
    clauses.append([ids[net['override']]])
    return ids,clauses


def sat(clauses,assignment=None):
    """Complete DPLL SAT solver, including both branches of each decision."""
    assignment={} if assignment is None else assignment.copy()
    while True:
        if any(not c for c in clauses):return None
        if not clauses:return assignment
        unit=next((c[0] for c in clauses if len(c)==1),None)
        if unit is None:break
        assignment[abs(unit)]=int(unit>0)
        clauses=[[x for x in c if x!=-unit] for c in clauses if unit not in c]
    from collections import Counter
    counts=Counter(abs(x) for c in clauses for x in c)
    variable=max(counts,key=counts.get)
    for literal in (variable,-variable):
        branch=[[x for x in c if x!=-literal] for c in clauses if literal not in c]
        trial=assignment.copy();trial[variable]=int(literal>0)
        result=sat(branch,trial)
        if result is not None:return result
    return None


def evaluate(net,bits):
    # Independently simulate the extracted circuit using ordinary Boolean logic.
    assert len(bits)==32 and set(bits)<=set('01')
    values={f'I{i:02d}':int(b) for i,b in enumerate(bits)}
    pending=dict(net['gates'])
    while pending:
        progress=False
        for name,g in list(pending.items()):
            if not all(v in values for v in g['inputs'].values()):continue
            a=values[g['inputs']['A']];b=values[g['inputs']['B']] if 'B' in g['inputs'] else None
            typ=g['type']
            if typ=='SHIFT':values[name+'.Y0']=int(a or b);values[name+'.Y1']=int(a and not b)
            elif typ=='AND':values[name]=a&b
            elif typ=='XOR':values[name]=a^b
            elif typ=='NOT':values[name]=1-a
            del pending[name];progress=True
        assert progress,'Circuit contains a cycle or unresolved input'
    return values[net['override']],values


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('svg',nargs='?',default=str(Path(__file__).parent/'schematic.svg'))
    args=ap.parse_args();out=Path(__file__).parent
    net=extract(args.svg);(out/'netlist.json').write_text(json.dumps(net,indent=2)+'\n')
    ids,clauses=cnf(net);model=sat(clauses);assert model is not None
    assert all(ids[f'I{i:02d}'] in model for i in range(32))
    bits=''.join(str(model[ids[f'I{i:02d}']]) for i in range(32))
    override,values=evaluate(net,bits);assert override==1
    blocking=[-ids[f'I{i:02d}'] if bits[i]=='1' else ids[f'I{i:02d}'] for i in range(32)]
    unique=sat(clauses+[blocking]) is None;assert unique
    flips=[]
    for i in range(32):
        changed=bits[:i]+str(1-int(bits[i]))+bits[i+1:]
        result,_=evaluate(net,changed);assert result==0
        flips.append({'input':f'I{i:02d}','override_after_flip':result})
    import hashlib
    evidence={'flag':'CSSCTF{'+bits+'}','bits':bits,'override':override,'unique':unique,
              'gates':len(net['gates']),'wires':len(net['wires']),'sat_variables':len(ids),
              'sat_clauses':len(clauses),'svg_sha256':hashlib.sha256(Path(args.svg).read_bytes()).hexdigest(),
              'gate_values':values,'single_bit_flip_checks':flips}
    (out/'validation.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (out/'flag.txt').write_text(evidence['flag']+'\n')
    print('Gates:',len(net['gates']),'Wires:',len(net['wires']))
    print('Override:',override,'Unique solution:',unique)
    print('Single-bit flips rejected:',len(flips))
    print(evidence['flag'])

if __name__=='__main__':main()

```
