#!/usr/bin/env python
from flask import Flask,session,jsonify,redirect,render_template
#from flup.server.fcgi import WSGIServer
from redis import StrictRedis as Redis
from meta3t import game
from random import choice as c
from time import sleep

app = Flask(__name__)
app.secret_key = "JU(P-IG9*G/()dbhj_2knHU(+?Rhuwj/90"
redis = Redis('localhost',6379,4)

alphabet = "abcdefghijklmnopqrstuxwvyz01234566789"
id = lambda: c(alphabet)+c(alphabet)+c(alphabet)+c(alphabet)

@app.route("/")
def init():
  if 'gid' not in session:
    gid = id()
    g = game()
    redis.set('game.%s'%gid,g.save(),300)
    session['gid'] = gid
    session['sym'] = 'x'
    first = True
  else:
    gid = session['gid']
    data = redis.get('game.%s'%gid)
    if not data: 
      session.pop('gid')
      return init()
    g = game.load(data)
    first = False
  return render_template('game.html',data=g.data,next=g.next,turn=g.turn,state=g.state,left=redis.ttl('game.%s'%gid),gid=gid,first=first,sym=session['sym'])

@app.route("/join/<gid>/")
def join(gid):
    data = redis.get('game.%s'%gid)
    if not data: 
      return redirect('/')
      #return render_template('404.html'), 404
    g = game.load(data)
    if 'gid' in session and session['gid'] == gid:
      return redirect('/')
    session['gid'] = gid
    if g.state==0:
      g.state = 1

      session['sym'] = 'o'
      redis.set('updated.%s.x'%gid,'true')
      redis.set('game.%s'%gid,g.save(),60)
    return render_template('game.html',data=g.data,next=g.next,turn=g.turn,state=g.state,left=redis.ttl('game.%s'%gid),gid=gid,sym=session['sym'],second='true')

@app.route("/status/")
def status():
  gid  = session['gid']
  data = redis.get('game.%s'%gid)
  if data:
    g = game.load(data)
    return jsonify(error=False,data=g.data,next=g.next,turn=g.turn,state=g.state,left=redis.ttl('game.%s'%gid),gid=gid,sym=session['sym'])
  return '{"error":true}'
  
@app.route("/<int:b>/<int:m>/")
def move(b,m): 
  gid = session['gid']
  data = redis.get('game.%s'%gid)
  if not data:
    return redirect('/')
    #return jsonify(status=404)
  g = game.load(data)
  gstate = g.play(m-1,b-1,session['sym'])
  if gstate==0:
    redis.set('game.%s'%gid,g.save(),60)
    #redis.publish('events','game.%s'%gid)
    redis.set('updated.%s.o'%gid,'true')
    redis.set('updated.%s.x'%gid,'true')
    return jsonify(data=g.data,status=200 if not gstate else 204)
    #return render_template('game.html',data=g.data,next=g.next,turn=g.turn,left=redis.ttl('game.%s'%gid),gid=gid,sym=session['sym'])
  else: return redirect('/')

def event_stream():
  pubsub = redis.pubsub()
  pubsub.subscribe('events')
  for message in pubsub.listen():
    print message
    yield "event: %s\r\n"%message['data']

@app.route('/stream')
def stream():
  return 3#Response(event_stream(), mimetype="text/event-stream")

@app.route('/poll')
def poll():
  for e in xrange(100):
    p = redis.get('updated.%s.%s'%(session['gid'],session['sym']))
    if p: 
      redis.delete('updated.%s.%s'%(session['gid'],session['sym']))
      return "1"
    sleep(0.1)
  return "0"

def main():
  redis.flushdb()
  app.run('0.0.0.0',80,debug=True)

if __name__ == '__main__': main()
