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
