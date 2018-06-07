import websocket
import requests
import json
import asyncio

class SimpleAI:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.ws = websocket.WebSocket()
        self.ws.connect('ws://localhost:8000/showdown/websocket')
        self.active_battles = dict()
    async def recv(self):
        w = self.ws.recv()
        print('RECEIVING: ' + w)
        return w
    async def send(self, msg):
        print('SENDING: ' + msg)
        self.ws.send(msg)

    async def run(self):
        await self.login()
        while(True):
            msg = await self.recv()
            tokens = msg.split('|')
            room = tokens[0]
            cmd = tokens[1]
            if(room == ''):
                if cmd == 'updatechallenges':
                    challenge_info = json.loads(tokens[2])
                    battle_info = challenge_info['challengesFrom']
                    from_user = next(iter(battle_info.keys()))
                    if(from_user):
                        await self.send('|/accept ' + from_user)
                #Global command
                pass
            else:
                #Battle command
                pass
    async def login(self):
        await self.send('|/autojoin')
        msg = await self.recv()
        while(True):
            tk = msg.split('|')
            if(tk[1] == 'challstr'):
                login_token = msg[10:]
                break
            msg = await self.recv()
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
        await self.send('|/trn ' + self.username + ',0,'+assertion)
        #Seems to tell us about server history
        await self.recv()

        #'|updatesearch|{"searching":[],"games":null}'
        await self.recv()

        #'|updateuser|jimola|1|102'
        await self.recv()

        #'|j| jimola\n'
        await self.recv()

    def logout(self):
        self.ws.send('|/logout')
        self.ws.close()
        s.ws = None

    async def challenge(self, username, battle_type='random', team=None):
        if(battle_type == 'random'):
            await self.send('|/challenge ' + username + ', gen7randombattle')
        else:
            await self.send('|/utm\n'+team)
            await self.send('|/challenge ' + username + ', gen7ou')
        incoming = ''
        while True:
            incoming = await self.recv()
            cmd_type = incoming.split('|')[1]
            if(cmd_type == 'b'):
                break
        #battle name and players
        self.battle_name = incoming.split('|')[2]
        self.cnt = 2
        await self.battle()

    async def battle(self):
        battle_on = True
        while battle_on:
            msg = await self.recv()
            split_msg = msg.split('|')
            if split_msg[1] == 'request' and split_msg[2]:
                content = json.loads(split_msg[2])
                if 'forceSwitch' in content:
                    await self.send(self.battle_name + '|/switch ' +
                            str(self.cnt))
                    self.cnt += 1
                    continue
                if 'wait' in content:
                    continue

                await self.send(self.battle_name + '|/move 1')
            elif split_msg[1] == '\n' and (split_msg[2] == 'move' 
                    or split_msg[2] == 'switch'):
                sub_commands = msg.split('\n|')
                print('SCMD: ')
                for scmd in sub_commands:
                    s_cmd = scmd.split('|')
                    cmd_type = s_cmd[0]
                    print(cmd_type)
                    if(cmd_type == 'win'):
                        battle_on = False
                        break

try:
    f = open('../secret.txt').read()
    username, password = f.split('\n')[0:2]
except FileNotFoundError:
    print('File containing username and password not found')

teams = []
with open('teams.txt') as T:
    for line in T:
        teams.append(line[:-1])

loop = asyncio.get_event_loop()
s = SimpleAI()
#asyncio.ensure_future(s.login(username, password))
#asyncio.ensure_future(s.challenge('GucciMoney', 'ou', teams[0]))
loop.run_forever()
