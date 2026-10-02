# Severed Symmetry — explicação e PoC

## Resultado

```text
CSSCTF{P35T0_5CH3M3_4TT4CK2026}
```

O ataque usa somente `source.py` e `out.txt`. Não precisa da chave privada, de serviços externos ou de adivinhar o conteúdo da flag. A implementação reproduzível está em `solve.py`; uma cópia completa está no final deste documento.

## Como executar

Requisitos: Python 3 e NumPy. Com NumPy disponível, execute:

```bash
cd /home/kali/Desktop/ctf/css
OPENBLAS_NUM_THREADS=1 python3 solve.py
```

O solver lê os arquivos na própria pasta, imprime a flag e salva `flag.txt`. Ele importa as funções de `source.py`, sem executar seu `main`. Não execute `source.py` diretamente: seu `main` gera uma nova instância e sobrescreve `out.txt`.

## 1. Entender a construção

Todas as operações são em F₁₇, isto é, módulo 17. Os parâmetros são:

- 32 variáveis de entrada e 34 equações públicas;
- 16 coordenadas na primeira camada;
- 4 variáveis vinegar e 12 variáveis oil na camada restante.

O programa aplica uma transformação afim secreta à entrada:

```text
z = A2 · entrada + b2
w_i = z_i − q_i(z_16, …, z_31),   i = 0, …, 15
central = (w, U(w, z_16, …, z_31))
P(entrada) = A1 · central + b1
```

Cada `q_i` é quadrático. Cada `U_i` também é quadrático, mas não contém produtos entre duas variáveis oil. Substituir `w` em `U` produz os termos de grau até 4 vistos na chave pública.

A fraqueza é que as transformações afins não escondem certos subespaços recuperáveis por álgebra linear.

## 2. Cancelar os termos de grau 3 e 4

Monte uma matriz `C` com uma linha por polinômio público e uma coluna por monômio. Separe as colunas de grau maior que 2 em `C_high`.

Uma combinação de equações com coeficientes `k` é quadrática quando:

```text
C_highᵀ · k = 0
```

O núcleo dessa matriz tem dimensão 16. Colocando uma base nas colunas de `K`, recuperamos:

```text
W(entrada) = Kᵀ · P(entrada)
```

Essas 16 equações são combinações invertíveis das coordenadas `w`, acrescidas de constantes. O solver calcula o núcleo usando 400 colunas para economizar trabalho e, em seguida, verifica que a combinação cancela TODAS as colunas de grau 3 e 4. Essa verificação é uma asserção no código.

## 3. Recuperar as direções da primeira camada

Calcule a matriz Hessiana de cada equação em `W`. Para um termo `a·x_i²`, a diagonal recebe `2a`; para `a·x_i·x_j`, as posições `(i,j)` e `(j,i)` recebem `a`.

As partes quadráticas dependem somente das últimas 16 coordenadas secretas. Portanto, a interseção dos núcleos das Hessianas revela as 16 direções nas quais `W` varia apenas linearmente:

```text
X = núcleo da matriz formada empilhando as Hessianas
```

Complete `X` com um complemento `Y`, de modo que qualquer entrada tenha a forma:

```text
entrada = X·a + Y·y
```

Se `L` contém os coeficientes lineares de `W`, então, para um bloco cifrado `c`:

```text
W(X·a + Y·y) = (L·X)·a + W(Y·y)
a = (L·X)⁻¹ · (Kᵀ·c − W(Y·y))
```

A função `lift(y)` implementa essa fórmula. Ela transforma uma escolha de 16 coordenadas `y` em uma entrada de 32 coordenadas que já satisfaz as 16 equações recuperadas.

## 4. Reduzir a camada restante a equações quadráticas

Defina, para cada bloco:

```text
R(y) = P(lift(y)) − c
```

Embora `P` tenha grau 4, `R` tem grau no máximo 2: na construção secreta, as coordenadas `w` já foram fixadas pelo ciphertext. Restam as equações `U` nas últimas 16 coordenadas.

Reconstruímos as constantes, os coeficientes lineares e as Hessianas de `R` avaliando-o em 153 pontos:

```text
0; e_i; 2·e_i; e_i + e_j para i < j
```

Aqui `e_i` é um vetor da base canônica. A interpolação usa o inverso de 2 em F₁₇, que é 9.

## 5. Recuperar o subespaço oil

Na base secreta, cada Hessiana residual tem a estrutura:

```text
       vinegar  oil
H = [    A       B  ]
    [    Bᵀ      0  ]
```

Como há somente 4 coordenadas vinegar, quando `B` tem posto 4, os vetores do núcleo de `H` têm componente vinegar nula. Seus componentes oil satisfazem `B·oil = 0`.

Nesta instância, juntar os núcleos das Hessianas e tomar seu espaço gerado recupera um subespaço de dimensão 12. O solver completa essa base com 4 direções vinegar e verifica explicitamente que todos os blocos oil–oil das Hessianas são zero.

Esse passo é uma propriedade verificada desta instância; a dimensão e a verificação do bloco zero aparecem durante a execução e no código.

## 6. Enumerar vinegar e resolver oil por álgebra linear

Escreva `y = O·o + V·v`, com 12 coordenadas oil `o` e 4 vinegar `v`. Na nova base, cada equação residual é:

```text
R_k(o,v) = d_k + l_o,k·o + l_v,k·v
           + oᵀ·H_ov,k·v + (1/2)·vᵀ·H_vv,k·v
```

Fixar `v` deixa um sistema linear em `o`:

```text
(l_o,k + H_ov,k·v) · o
    = −d_k − l_v,k·v − (1/2)·vᵀ·H_vv,k·v
```

Enumeramos no máximo `17⁴ = 83.521` valores de `v` por bloco. Para cada um, usamos eliminação de Gauss módulo 17 para resolver o sistema de 34 equações em 12 incógnitas. Sistemas inconsistentes são descartados.

Para cada solução candidata, o solver reconstrói a entrada com `lift` e exige que sua avaliação nas 34 equações públicas seja EXATAMENTE igual ao bloco cifrado.

## 7. Decodificar e validar

A execução que resolveu o desafio produziu:

```text
Quadratic combinations: 16
Common radical: 16
Block 0 oil dimension 12
Recovered block 0 after 24390 candidates
Block 1 oil dimension 12
Recovered block 1 after 23903 candidates
Block 2 oil dimension 12
Recovered block 2 after 80652 candidates
CSSCTF{P35T0_5CH3M3_4TT4CK2026}
```

Os três vetores recuperados são concatenados e passados a `source.decode_frame`. Cada byte foi codificado com dois dígitos em base 17. O frame contém quatro bytes de comprimento, o texto e padding zero.

A validação final combina dois critérios: reprodução de cada bloco cifrado pelas equações públicas e aceitação do comprimento, dos bytes e do padding pelo decodificador original.

## PoC completa — solve.py

```python
import json,itertools,time
from pathlib import Path
import numpy as np
import source
P=17
D=Path(__file__).resolve().parent

def rr(a):
 a=np.array(a,dtype=np.int64).copy()%P; k=0; piv=[]
 for j in range(a.shape[1]):
  ids=np.flatnonzero(a[k:,j])
  if not len(ids):continue
  i=k+ids[0]; a[[i,k]]=a[[k,i]]; a[k]=a[k]*pow(int(a[k,j]),-1,P)%P
  f=a[:,j].copy(); f[k]=0; a=(a-f[:,None]*a[k])%P
  piv.append(j); k+=1
  if k==len(a):break
 return a,piv

def ker(a):
 r,p=rr(a); free=[i for i in range(r.shape[1]) if i not in p]; b=np.zeros((r.shape[1],len(free)),dtype=np.int64)
 for k,j in enumerate(free):
  b[j,k]=1
  for i,c in enumerate(p):b[c,k]=-r[i,j]%P
 return b

def inv(a):return np.array(source.invert(a.tolist(),P),dtype=np.int64)
def complete(cols,n):
 b=cols.copy()
 for e in np.eye(n,dtype=np.int64):
  trial=np.column_stack((b,e))
  if len(rr(trial.T)[1])>b.shape[1]:b=trial
  if b.shape[1]==n:return b

print('Loading',flush=True)
d=json.loads((D/'out.txt').read_text()); polys=source.unpack(d['public_key']['polynomials'])
mons=sorted(set().union(*polys)); lookup={m:i for i,m in enumerate(mons)}
C=np.zeros((34,len(mons)),dtype=np.int64)
for i,f in enumerate(polys):
 for m,c in f.items():C[i,lookup[m]]=c
high=[i for i,m in enumerate(mons) if len(m)>2]
# A small subset finds the kernel; verify against every high-degree coefficient.
K=ker(C[:,high[:400]].T); assert np.all(K.T@C[:,high]%P==0)
print('Quadratic combinations:',K.shape[1],flush=True)
W=K.T@C%P
Hs=[]
for row in W:
 h=np.zeros((32,32),dtype=np.int64)
 for m,c in zip(mons,row):
  if len(m)==2:
   i,j=m; h[i,j]+=c; h[j,i]+=c
 Hs.append(h%P)
X=ker(np.vstack(Hs)); print('Common radical:',X.shape[1],flush=True)
T=complete(X,32); X=T[:,:16]; Y=T[:,16:]
L=np.array([[row[lookup[(i,)]] for i in range(32)] for row in W]); LX=L@X%P; LXinv=inv(LX)
low=[i for i,m in enumerate(mons) if len(m)<=2]; lm=[mons[i] for i in low]; WC=W[:,low]
mi=np.full((len(mons),4),32,dtype=np.int64)
for i,m in enumerate(mons):mi[i,:len(m)]=m

def ev(points):
 points=np.atleast_2d(points); out=[]
 for pts in np.array_split(points,max(1,(len(points)+15)//16)):
  pts=np.column_stack((pts,np.ones(len(pts),dtype=np.int64)))
  vals=np.prod(pts[:,mi],axis=2)%P; out.extend(vals@C.T%P)
 return np.array(out)
def wev(points):
 points=np.atleast_2d(points); vals=np.ones((len(points),len(lm)),dtype=np.int64)
 for j,m in enumerate(lm):
  for i in m:vals[:,j]=vals[:,j]*points[:,i]%P
 return vals@WC.T%P

samples=[np.zeros(16,dtype=np.int64)]
for i in range(16):
 e=np.eye(16,dtype=np.int64)[i]; samples.extend([e,2*e])
for i in range(16):
 for j in range(i+1,16):samples.append(np.eye(16,dtype=np.int64)[i]+np.eye(16,dtype=np.int64)[j])
samples=np.array(samples)

def fit(vals):
 const=vals[0]; linear=[]; H=np.zeros((len(const),16,16),dtype=np.int64)
 for i in range(16):
  a,b=vals[1+2*i]-const,vals[2+2*i]-const
  q=(b-2*a)*9%P; linear.append((a-q)%P); H[:,i,i]=2*q%P
 k=33
 for i in range(16):
  for j in range(i+1,16):
   h=(vals[k]-vals[1+2*i]-vals[1+2*j]+const)%P; H[:,i,j]=H[:,j,i]=h; k+=1
 return const,np.array(linear).T,H

answers=[]
for bi,c in enumerate(d['ciphertext']['blocks']):
 c=np.array(c); target=K.T@c%P
 def lift(y):
  y=np.atleast_2d(y); yp=y@Y.T%P; x=(target-wev(yp))@LXinv.T%P
  return (yp+x@X.T)%P
 vals=(ev(lift(samples))-c)%P
 const,lin,H=fit(vals)
 oil_candidates=np.concatenate([ker(h) for h in H],axis=1)
 oil=rr(oil_candidates.T)[0]; oil=oil[np.any(oil,axis=1)].T
 print('Block',bi,'oil dimension',oil.shape[1],flush=True)
 B=complete(oil,16); O=B[:,:12]; V=B[:,12:]
 h=np.einsum('ai,kab,bj->kij',B,H,B)%P; l=lin@B%P
 assert not np.any(h[:,:12,:12])
 found=None
 for count,v in enumerate(itertools.product(range(P),repeat=4)):
  v=np.array(v); mat=(l[:,:12]+np.einsum('kij,j->ki',h[:,:12,12:],v))%P
  rhs=-(const+l[:,12:]@v+9*np.einsum('i,kij,j->k',v,h[:,12:,12:],v))%P
  # solve 34 equations in 12 oil coordinates
  r,piv=rr(np.column_stack((mat,rhs)))
  if 12 in piv:continue
  if len(piv)!=12:continue
  o=r[:12,12]; y=O@o+V@v; x=lift(y%P)[0]
  if np.array_equal(ev(x)[0],c):found=x;break
 assert found is not None
 answers.extend(found.tolist()); print('Recovered block',bi,'after',count+1,'candidates',flush=True)
flag=source.decode_frame(answers,17,32)
(D/'flag.txt').write_bytes(flag+b'\n'); print(flag.decode())

```
