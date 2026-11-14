from midiutil import MIDIFile
from pathlib import Path
import math, wave, json
import numpy as np
from music21 import stream, note, chord, meter, key, tempo, instrument, metadata

OUT = Path(r'C:\Users\xiajt\Documents\Codex\2026-10-31\diao-ya\outputs')
OUT.mkdir(parents=True, exist_ok=True)
BPM=112
PPQ=480
BAR=3.0  # quarter-note beats in 6/8
BARS=32
DUR=BAR*BARS
SR=44100

# pitch helper: C4=60
def midi(p): return p

def add_event(events, track, start, dur, pitch, vel=80, role=None):
    events.setdefault(track, []).append((float(start), float(dur), int(pitch), int(vel), role))

events={}
tracks=[
 ('Flute',73,0),('Solo Violin',40,1),('Oboe',68,2),('Harp',46,3),
 ('Celesta',8,4),('Strings',48,5),('Cello/Bass',32,6),('Percussion',0,9)
]
# D minor / modal color chord voicings
chords=[
    [50,57,60,64], [46,53,57,62], [41,48,53,57], [48,55,60,64],
    [43,50,53,58], [50,57,60,65], [51,58,62,65], [45,52,57,61],
]
# Main melody, 8-bar seed, then transformed repetitions
melody=[
 [62,65,69,67,65], [64,65,69,72,69], [69,67,65,64,62], [72,69,67,65,64],
 [65,69,72,74,72], [69,67,65,62,65], [67,65,64,62,60], [61,64,69,67,65],
]
mel_durs=[[.5,.5,1,.5,.5],[.5,.5,.5,1,.5],[.5,.5,.5,.5,1],[.5,.5,1,.5,.5],
 [.5,.5,.5,.5,.5, .5],[.5,.5,.5,.5,1],[.5,.5,.5,.5,1],[.5,.5,.5,.5,1]]
for b in range(BARS):
    sec=b//8; local=b%8; start=b*BAR
    trans=0
    if sec==1: trans=12
    elif sec==2: trans=7
    elif sec==3: trans=0
    notes=melody[local]
    ds=mel_durs[local]
    t=start
    for i,(p,d) in enumerate(zip(notes,ds)):
        # final section has a few descending answers
        pp=p+trans
        if sec==3 and local in (0,4) and i==0: pp-=12
        vel=88 + (8 if sec==2 else 0)
        add_event(events,'Flute',t,d,pp,vel,'melody')
        # violin answers every other bar, offset by a half beat
        if b>=8 and (b%2==1):
            add_event(events,'Solo Violin',t+0.25,d*0.9,pp-12,vel-12,'answer')
        t += d
    # Oboe countermelody on long tones in A sections
    if b<8 or b>=24:
        root=chords[b%8][0]
        add_event(events,'Oboe',start+0.0,1.0,root+12,68,'counter')
        add_event(events,'Oboe',start+1.0,0.5,root+14,64,'counter')
        add_event(events,'Oboe',start+1.5,1.5,root+12,65,'counter')
    else:
        # B/C oboe punctuates offbeats
        add_event(events,'Oboe',start+0.5,0.5,62+(b%3)*2,68,'counter')
        add_event(events,'Oboe',start+2.0,0.5,65+(b%2)*2,72,'counter')

# harmonic bed and harp patterns
for b in range(BARS):
    start=b*BAR; c=chords[b%8]
    # string pad with inner motion in C section
    add_event(events,'Strings',start,2.5,c[0],52,'pad')
    add_event(events,'Strings',start,2.5,c[1],45,'pad')
    add_event(events,'Strings',start,2.5,c[2],47,'pad')
    add_event(events,'Strings',start,2.5,c[3],43,'pad')
    if b>=16 and b<24:
        add_event(events,'Strings',start+1.5,1.5,c[0]+12,55,'lift')
    # harp rolling 6/8 arpeggio, with occasional reverse turn
    arp=[c[0],c[2],c[1]+12,c[3],c[2],c[1]]
    if b%4==3: arp=list(reversed(arp))
    for j,p in enumerate(arp):
        add_event(events,'Harp',start+j*.5,.45,p,54+8*(b%4==0),'arp')
    # celesta glitter on offbeats
    for j,p in enumerate([c[2]+12,c[3]+12,c[2]+12]):
        add_event(events,'Celesta',start+0.25+j*1.0,.28,p,40+(j==1)*12,'sparkle')
    if b%4==2:
        add_event(events,'Celesta',start+2.5,.25,c[1]+24,62,'sparkle')
    # bass / cello ostinato
    bass=c[0]-12
    pattern=[(0,.75,bass),(0.75,.75,c[2]-12),(1.5,.75,bass+7),(2.25,.75,c[1]-12)]
    if b>=16 and b<24:
        pattern=[(0,.5,bass),(0.5,.5,bass+7),(1,.5,c[1]-12),(1.5,.5,bass),(2,.5,c[2]-12),(2.5,.5,bass+7)]
    for off,d,p in pattern:
        add_event(events,'Cello/Bass',start+off,d,p,62 if b%2 else 69,'ostinato')

# Percussion: low frame drum, hand drum, shaker and chime hits
for b in range(BARS):
    s=b*BAR
    # frame drum pulse (C2 in our synth mapping)
    for off in (0,1.5): add_event(events,'Percussion',s+off,.16,36,66,'frame')
    if b%2==1: add_event(events,'Percussion',s+2.5,.12,38,58,'tap')
    # shaker eighths, accent the 2nd and 6th eighth
    for j in range(6): add_event(events,'Percussion',s+j*.5,.08,82,38+(j in (1,4))*12,'shaker')
    # temple / chime at phrase ends
    if b in (7,15,23,31): add_event(events,'Percussion',s+2.5,.5,76,70,'chime')

# MIDI export
mf=MIDIFile(len(tracks), adjust_origin=True)
for i,(name,prog,chan) in enumerate(tracks):
    mf.addTrackName(i,0,name)
    mf.addTempo(i,0,BPM)
    if chan!=9: mf.addProgramChange(i,chan,0,prog)
for i,(name,prog,chan) in enumerate(tracks):
    for st,d,p,v,role in events.get(name,[]):
        if chan==9:
            mf.addNote(i,chan,p,st,d,v)
        else:
            mf.addNote(i,chan,p,st,d,v)
mid_path=OUT/'biyi_cheng_original.mid'
with open(mid_path,'wb') as f: mf.writeFile(f)

# MusicXML export for editing in MuseScore / music21
score=stream.Score(); score.metadata=metadata.Metadata(); score.metadata.title='比翼城夜行曲（原创草稿）'; score.metadata.composer='Codex 原创编曲尝试'
score.insert(0, tempo.MetronomeMark(number=BPM)); score.insert(0, meter.TimeSignature('6/8')); score.insert(0,key.Key('d','minor'))
inst_classes={'Flute':instrument.Flute,'Solo Violin':instrument.Violin,'Oboe':instrument.Oboe,'Harp':instrument.Harp,'Celesta':instrument.Celesta,'Strings':instrument.StringInstrument,'Cello/Bass':instrument.Violoncello,'Percussion':instrument.Percussion}
for name,_,_ in tracks:
    part=stream.Part(); part.id=name; part.partName=name; part.insert(0,inst_classes[name]())
    part.insert(0, meter.TimeSignature('6/8')); part.insert(0, key.Key('d','minor'))
    # insert events; chord-like simultaneous notes are separate notes in parts
    for st,d,p,v,role in sorted(events.get(name,[]), key=lambda x:(x[0],x[2])):
        if name=='Percussion':
            n=note.Unpitched(); n.duration.quarterLength=d; n.offset=st; n.volume.velocity=v
        else:
            n=note.Note(p); n.duration.quarterLength=d; n.offset=st; n.volume.velocity=v
        part.insert(st,n)
    score.insert(0,part)
xml_path=OUT/'biyi_cheng_original.musicxml'; score.write('musicxml',fp=str(xml_path))

# Simple synthesizer for a listenable WAV (no external soundfont required)
seconds=DUR*60/BPM
N=int(seconds*SR)+1
t=np.arange(N)/SR
mix=np.zeros((N,2),dtype=np.float64)
# stable per-track sound recipes
def synth_note(st,dur,pitch,vel,track):
    start=int(st*60/BPM*SR); length=max(1,int(dur*60/BPM*SR)); end=min(N,start+length)
    if end<=start: return
    tt=np.arange(end-start)/SR
    f=440*2**((pitch-69)/12)
    # attack/release in seconds, percussion gets shorter
    atk=min(0.03, max(0.005,dur*60/BPM*0.12)); rel=min(0.25, max(0.04,dur*60/BPM*0.35))
    env=np.ones_like(tt)
    a=int(atk*SR); r=int(rel*SR)
    if a>0: env[:a]=np.linspace(0,1,a)
    if r>0: env[-r:]*=np.linspace(1,0,r)
    if track=='Flute':
        sig=np.sin(2*np.pi*f*tt)+0.22*np.sin(4*np.pi*f*tt)+0.08*np.sin(6*np.pi*f*tt)
    elif track=='Solo Violin':
        sig=np.sin(2*np.pi*f*tt)+0.45*np.sin(4*np.pi*f*tt)+0.23*np.sin(6*np.pi*f*tt)+0.12*np.sin(8*np.pi*f*tt)
        env*=0.86+0.14*np.sin(2*np.pi*5*tt)
    elif track=='Oboe':
        sig=np.sin(2*np.pi*f*tt)+0.55*np.sin(3*np.pi*f*tt)+0.30*np.sin(4*np.pi*f*tt)
    elif track=='Harp':
        env=np.exp(-tt*5.5)*np.minimum(1,tt*SR/8)
        sig=np.sin(2*np.pi*f*tt)+0.28*np.sin(4*np.pi*f*tt)+0.12*np.sin(6*np.pi*f*tt)
    elif track=='Celesta':
        env=np.exp(-tt*4.0)*np.minimum(1,tt*SR/6)
        sig=np.sin(2*np.pi*f*tt)+0.6*np.sin(4*np.pi*f*tt)+0.25*np.sin(8*np.pi*f*tt)
    elif track=='Strings':
        sig=np.sin(2*np.pi*f*tt)+0.35*np.sin(4*np.pi*f*tt)+0.15*np.sin(6*np.pi*f*tt)
        env*=0.55+0.45*np.minimum(1,tt/(0.3))
    elif track=='Cello/Bass':
        sig=np.sin(2*np.pi*f*tt)+0.50*np.sin(4*np.pi*f*tt)+0.18*np.sin(6*np.pi*f*tt)
    else:
        # pitched percussion and shaker
        if pitch==82:
            sig=np.random.default_rng(start+pitch).normal(0,1,len(tt))*np.exp(-tt*40)
        elif pitch==76:
            sig=np.sin(2*np.pi*f*tt)+.25*np.sin(2*np.pi*2.4*f*tt)
            env*=np.exp(-tt*5)
        else:
            sig=np.sin(2*np.pi*f*tt)*np.exp(-tt*22)
    amp=(vel/127)*0.12
    pan={'Flute':.62,'Solo Violin':.40,'Oboe':.55,'Harp':.28,'Celesta':.72,'Strings':.48,'Cello/Bass':.50,'Percussion':.56}[track]
    left=math.cos(pan*math.pi/2); right=math.sin(pan*math.pi/2)
    y=amp*sig*env
    mix[start:end,0]+=y*left; mix[start:end,1]+=y*right

for name,_,_ in tracks:
    for st,d,p,v,role in events.get(name,[]): synth_note(st,d,p,v,name)
# light stereo delay/reverb
for delay,decay in [(0.18,.18),(0.36,.10)]:
    k=int(delay*SR); mix[k:,0]+=mix[:-k,1]*decay; mix[k:,1]+=mix[:-k,0]*decay
mx=np.max(np.abs(mix)); mix=np.clip(mix/(mx+1e-9)*0.92,-1,1)
frames=(mix*32767).astype(np.int16)
wav_path=OUT/'biyi_cheng_original.wav'
with wave.open(str(wav_path),'wb') as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(frames.tobytes())

# Compact machine-readable metadata
meta={'title':'比翼城夜行曲（原创草稿）','duration_seconds':round(seconds,2),'tempo_bpm':BPM,'meter':'6/8','key':'D minor / modal','tracks':[x[0] for x in tracks], 'note_count':sum(len(v) for v in events.values()), 'copyright_note':'原创旋律与编曲；仅参考“轻快、流动、浪漫的幻想城市场景”氛围，不复制原曲旋律。'}
(OUT/'biyi_cheng_original.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(meta,ensure_ascii=False))
