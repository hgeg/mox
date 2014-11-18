#!/usr/bin/env python
import json
uni = lambda _: _[1:]==_[:-1] and not all(map(lambda e: e==' ',_))
ful = lambda _: all(map(lambda e: e!=' ',_))

class game:
  def __init__(self):
   self.data = [[' ']*10 for e in range(9)]
   self.turn = 0
   self.next = -1
   # states:
   # 0. waiting for "O-player"
   # 1. playable state
   # 2. game finished. "X" wins
   # 3. game finished. "O" wins
   self.state = 0 

  def play(self,m,b=-1,sym=' '):
    if self.state!=1: return
    if self.turn%2 and sym=='x': return -55
    if not self.turn%2 and sym=='o': return -61
    mov = (self.next if b==-1 else b,m)
    if mov[0]>-1 and self.finished(mov[0]): return -22
    if not mov[0]==self.next and self.next>0: return -27
    if not -1<mov[1]<9: return -72
    p = self.data[mov[0]][mov[1]]
    if p==" ":
      self.data[mov[0]][mov[1]] = 'o' if self.turn%2 else 'x'
      if self.check(mov[0]):
        self.data[mov[0]][9] = 'o' if self.turn%2 else 'x'
      elif ful(self.data[mov[0]][:9]):
        self.data[mov[0]][9] = 'n'
      self.checkall()
      self.next = -1 if self.finished(mov[1]) else mov[1]
      self.turn += 1
      return 0
    else: return -36

  def finished(self,p):
    return not self.data[p][9] == ' '
    
  def check(self,p):
    d = self.data[p]
    return (uni(d[:3]) | uni(d[3:6]) | uni(d[6:9]) | uni(d[:9:3]) | uni(d[1::3]) | uni(d[2::3]) | uni(d[::4]) | uni(d[2:7:2]))

  def checkall(self):
    md = [r[9] for r in self.data]
    if (uni(md[:3]) | uni(md[3:6]) | uni(md[6:9]) | uni(md[:9:3]) | uni(md[1::3]) | uni(md[2::3]) | uni(md[::4]) | uni(md[2:7:2])):
      self.state = 3 if self.turn%2 else 2

  def board(self,p): 
    return self.data[p]

  def save(self): return json.dumps({'data':self.data,'next':self.next,'turn':self.turn,'state':self.state})

  @staticmethod
  def load(s): 
    g = game()
    data = json.loads(s)
    g.data = data['data']
    g.turn = data['turn']
    g.next = data['next']
    g.state = data['state']
    return g
