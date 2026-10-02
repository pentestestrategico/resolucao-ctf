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
