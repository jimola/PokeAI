import websocket
import requests
import json

class BattleState:
    def __init__(self, opponent):
        self.opponent = opponent
        self.cnt = 2
unwanted_chars = '\n\t >'
class SimpleAI:
    def __init__(self, username, password, team):
        self.username = username
        self.password = password
        self.ws = websocket.WebSocket()
        self.ws.connect('ws://localhost:8000/showdown/websocket')
        self.active_battles = dict()
        self.team = team
    def recv(self):
        w = self.ws.recv()
        print('RECEIVING: ' + w)
        return w
    def send(self, msg):
        print('SENDING: ' + msg)
        self.ws.send(msg)

    def run(self):
        self.login()
        while(True):
            msg = self.recv()
            tokens = [x.strip(unwanted_chars) for x in msg.split('|')]
            room = tokens[0]
            cmd = tokens[1]
            if room == '':
                #Global command
                if cmd == 'updatechallenges':
                    challenge_info = json.loads(tokens[2])
                    battle_info = challenge_info['challengesFrom']
                    if len(battle_info) > 0:
                        from_user, battle_format = next(iter(battle_info.items()))
                        if from_user:
                            if battle_format == 'gen7ou':
                                self.send('|/utm ' + self.team)
                                self.send('|/accept ' + from_user)
                            elif battle_format == 'gen7randombattle':
                                self.send('|/accept ' + from_user)
                if cmd == 'b':
                    B = tokens[2].strip(unwanted_chars)
                    U1 = tokens[3].strip(unwanted_chars)
                    U2 = tokens[4].strip(unwanted_chars)
                    if U1 == username:
                        self.active_battles[B] = BattleState(U2)
                    if U2 == username:
                        self.active_battles[B] = BattleState(U1)
            elif room in self.active_battles:
                B = self.active_battles[room]
                if cmd == 'player':
                    pass
                elif cmd == 'request' and tokens[2]:
                    request_info = json.loads(tokens[2])
                    if 'forceSwitch' in request_info:
                        self.send(room + '|/switch ' + str(B.cnt))
                        B.cnt += 1
                        continue
                    if 'wait' in request_info:
                        continue
                    if 'teamPreview' in request_info:
                        self.send(room + '|/team 123456')
                        continue
                    #Otherwise we assume its a move
                    self.send(room + '|/move 1')
                elif cmd == '':
                    #sub commands
                    self.parse_scmd(msg, room)

    def parse_scmd(self, msg, room):
        cmds = msg.split('\n|')
        for c in cmds[1:]:
            tokens = c.split('|')
            cmd = tokens[0]
            if cmd == 'move':
                pass
            if cmd == 'win':
                self.active_battles.pop(room)
            if cmd == 'poke':
                pass

    def login(self):
        self.send('|/autojoin')
        msg = self.recv()
        while(True):
            tk = msg.split('|')
            if(tk[1] == 'challstr'):
                login_token = msg[10:]
                break
            msg = self.recv()
        print('LOGIN: ' + login_token)
        #Need to remove |challstr| from the beginning"
        r = requests.post('http://localhost.psim.us/action.php', 
                            data={'act':'login',
                                'name': self.username,
                                'pass': self.password,
                                'challstr':login_token})
        #For some reason there is a leading ']' that needs to be removed
        login_info = json.loads(r.content[1:])
        assertion = login_info['assertion']
        self.send('|/trn ' + self.username + ',0,'+assertion)

    def logout(self):
        self.ws.send('|/logout')
try:
    f = open('../secret.txt').read()
    username, password = f.split('\n')[0:2]
except FileNotFoundError:
    print('File containing username and password not found')

teams = []
with open('teams.txt') as T:
    for line in T:
        teams.append(line[:-1])

#s = SimpleAI()
#asyncio.ensure_future(s.login(username, password))
#asyncio.ensure_future(s.challenge('GucciMoney', 'ou', teams[0]))
