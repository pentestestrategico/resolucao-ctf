#!/usr/bin/env python3
import argparse,json,urllib.request,urllib.parse,urllib.error,time
from pathlib import Path
OUT=Path(__file__).resolve().parent

def rng(x):
    x^=(x<<13)&0xffffffff;x^=x>>17;x^=(x<<5)&0xffffffff
    return x&0xffffffff

class Flight:
    def __init__(self,seed):
        self.y=240*256;self.v=0;self.ticks=0;self.score=0;self.dead=False;self.seed=seed or 1
        self.pipes=[[(1040+270*i)*256,self.gap(),False] for i in range(5)]
    def gap(self):
        self.seed=rng(self.seed);return 125+self.seed%231
    def step(self,flap):
        if self.dead or self.ticks>=36000:self.dead=True;return
        if flap:self.v=-1724
        self.v=min(self.v+67,2048);self.y+=self.v;self.ticks+=1
        for p in self.pipes:p[0]-=717
        if self.y<=3072 or self.y>119807:self.dead=True
        for p in self.pipes:
            x,g,passed=p
            if 30720<x<=54271:
                if self.y-3071<=(g-87)*256 or self.y+3071>=(g+87)*256:self.dead=True
            if not passed and x<=30719:
                p[2]=True
                if not self.dead:self.score+=1
        for p in self.pipes:
            if p[0]<-17408:
                p[:]=[max(q[0] for q in self.pipes)+69120,self.gap(),False]

def plan(seed,target):
    # Retry locally with several tracking thresholds. Nothing is sent until valid.
    for bias in (0,10,-10,20,-20,30,-30):
        f=Flight(seed);flaps=[]
        while not f.dead and f.score<target:
            pipe=min((p for p in f.pipes if p[0]>30720),key=lambda p:p[0])
            goal=pipe[1]*256
            flap=f.y>goal+bias*256 and f.v>=-100
            if flap:flaps.append(f.ticks)
            f.step(flap)
        if not f.dead and f.score==target:
            # Replay all ticks independently to verify timing and score.
            check=Flight(seed);events=set(flaps)
            for t in range(f.ticks):check.step(t in events)
            assert check.score==target and not check.dead
            return {'ticks':f.ticks,'score':f.score,'flaps':flaps,'seed':seed}
    raise RuntimeError('No valid flight found by local controller')

def parse_response(raw):
    return {k:v[0] for k,v in urllib.parse.parse_qs(raw,keep_blank_values=True).items()}


def server_from_binary():
    import os,re
    configured=os.environ.get('FLAPPY_SERVER')
    if configured:return configured.rstrip('/')
    data=(OUT/'flappy_board').read_bytes()
    urls=re.findall(rb'http://(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]+',data)
    if not urls:raise RuntimeError('No event server in ELF; specify --server')
    return urls[0].decode()


def solve(server):
    # Use only the event API configured in the challenge ELF or supplied by user.
    token=None
    def request(endpoint,payload,filename):
        body=urllib.parse.urlencode(payload).encode()
        headers={'Content-Type':'application/x-www-form-urlencoded'}
        if token:headers['Authorization']='Bearer '+token
        req=urllib.request.Request(server+endpoint,data=body,headers=headers,method='POST')
        try:
            with urllib.request.urlopen(req,timeout=15) as response:
                raw=response.read().decode();status=response.status
        except urllib.error.HTTPError as error:
            raw=error.read().decode()
            (OUT/filename).write_text(raw)
            raise RuntimeError('HTTP '+str(error.code)+': '+raw) from error
        (OUT/filename).write_text(raw)
        if endpoint=='/api/attempt':(OUT/filename).chmod(0o600)
        parsed=parse_response(raw)
        if 'error' in parsed:raise RuntimeError(parsed['error'])
        assert status==200
        return parsed
    state=request('/api/attempt',{},'attempt.txt');token=state['token']
    while int(state['round'])<=3:
        number=int(state['round']);target=int(state['target'])
        replay=plan(int(state['seed']),target)
        replay.update(round=number,wait_ms=int(state['wait_seconds'])*1000)
        (OUT/f'round-{number}-replay.json').write_text(json.dumps(replay,indent=2)+'\n')
        payload={k:(','.join(map(str,value)) if k=='flaps' else value)
                 for k,value in replay.items() if k!='seed'}
        state=request('/api/complete',payload,f'round-{number}-response.txt')
        print(f'Round {number}: {target} points; {replay["ticks"]} ticks; accepted',flush=True)
        if 'flag' in state:
            (OUT/'flag.txt').write_text(state['flag']+'\n');print(state['flag']);return
    raise RuntimeError('Server did not return a flag')


def verify_saved():
    import hashlib
    evidence={'binary_sha256':hashlib.sha256((OUT/'flappy_board').read_bytes()).hexdigest(),'rounds':[]}
    for number in range(1,4):
        r=json.loads((OUT/f'round-{number}-replay.json').read_text());f=Flight(r['seed'])
        assert r['flaps']==sorted(set(r['flaps']))
        events=set(r['flaps']);assert all(0<=t<r['ticks'] for t in events)
        for tick in range(r['ticks']):
            f.step(tick in events);assert not f.dead,f'Collision at tick {tick}'
        assert f.score==r['score']==number*10
        response=parse_response((OUT/f'round-{number}-response.txt').read_text())
        assert int(response['round'])==number+1
        evidence['rounds'].append({'round':number,'score':f.score,'ticks':f.ticks,'flaps':len(events),
                                  'wait_ms':r['wait_ms'],'local_replay_valid':True,
                                  'server_next_round':int(response['round'])})
        print(f'Round {number}: replay valid; score={f.score}; server advanced to {number+1}')
    assert response['flag'].startswith('CSSCTF{') and response['flag'].endswith('}')
    evidence['flag']=response['flag'];evidence['server_completed']=True
    (OUT/'validation.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (OUT/'flag.txt').write_text(response['flag']+'\n');print(response['flag'])


def main():
    ap=argparse.ArgumentParser(description='Solve FLAPPY BOARD or verify saved replays offline')
    ap.add_argument('--solve',action='store_true',help='Open a fresh 20-minute session and solve all rounds')
    ap.add_argument('--server',help='Override event server from the ELF')
    ap.add_argument('--selftest',action='store_true',help='Test 100 local seeds; no network requests')
    args=ap.parse_args()
    if args.solve:solve(args.server.rstrip('/') if args.server else server_from_binary())
    elif args.selftest:
        for seed in range(1,101):plan(seed,30)
        print('100 local seeds validated, 30 points each')
    else:verify_saved()

if __name__=='__main__':main()
