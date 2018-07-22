import websocket
import requests
import json

class BattleAI:
    def __init__(self, opponent):
        self.opponent = opponent
        self.cnt = 1
        self.requests = None
    def team_preview(self):
        return '123456'
    def switch(self):
        self.cnt += 1
        return str(self.cnt)
    def move(self):
        return '1'
    def update(self, msg):
        print('Battle Update')
        print(msg)

unwanted_chars = '\n\t >'
class AutoBattler:
    def __init__(self, username, password, team, address):
        self.username = username
        self.password = password
        self.ws = websocket.WebSocket()
        self.ws.connect(address)
        self.battle_ais = dict()
        self.team = team
    def recv(self):
        w = self.ws.recv()
        #print('RECEIVING: ' + w)
        return w
    def send(self, msg):
        #print('SENDING: ' + msg)
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
                        self.battle_ais[B] = BattleAI(U2)
                    if U2 == username:
                        self.battle_ais[B] = BattleAI(U1)
            elif room in self.battle_ais:
                B = self.battle_ais[room]
                if cmd == 'request' and tokens[2]:
                    request_info = json.loads(tokens[2])
                    B.requests = request_info
                elif cmd == '' or cmd == 'player':
                    if B.requests:
                        #Checks if this command came after a request
                        B.update(msg)
                        if 'forceSwitch' in request_info:
                            self.send(room + '|/switch ' + B.switch())
                        elif 'wait' in request_info:
                            pass
                        elif 'teamPreview' in request_info:
                            self.send(room + '|/team ' + B.team_preview())
                        else:
                            #Otherwise it's a move request
                            self.send(room + '|/move ' + B.move())
                    else:
                        self.parse_scmd(msg, room)

    def parse_scmd(self, msg, room):
        cmds = msg.split('\n|')
        for c in cmds[1:]:
            tokens = c.split('|')
            cmd = tokens[0]
            if cmd == 'move':
                pass
            if cmd == 'win' or cmd == 'tie':
                self.battle_ais.pop(room)
                self.requests.pop(room)
                self.send('|/leave ' + room)
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
    username = input("Enter Showdown Username: ")
    password = input("Enter Showdown Password: ")

teams = []
with open('teams.txt') as T:
    for line in T:
        teams.append(line[:-1])
address = 'ws://localhost:8000/showdown/websocket' #if you start on port 8000
s = AutoBattler(username, password, teams[0], address)
s.run()
#asyncio.ensure_future(s.login(username, password))
#asyncio.ensure_future(s.challenge('GucciMoney', 'ou', teams[0]))
