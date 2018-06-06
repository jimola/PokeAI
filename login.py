import websocket
import requests
import json
import asyncio

class SimpleAI:
    def __init__(self):
        self.ws = websocket.WebSocket()
        self.ws.connect('ws://localhost:8000/showdown/websocket')
    async def recv(self):
        w = self.ws.recv()
        print('RECEIVING: ' + w)
        return w
    async def send(self, msg):
        print('SENDING: ' + msg)
        self.ws.send(msg)
    async def login(self, username, password):
        await self.send('|/autojoin')
        await self.recv()
        login_token = await self.recv()
        print('LOGIN: ' + login_token)
        #Need to remove |challstr| from the beginning"
        login_token = login_token[10:]
        r = requests.post('http://localhost.psim.us/action.php', 
                            data={'act':'login',
                                'name':username,
                                'pass':password,
                                'challstr':login_token})
        #For some reason there is a leading ']' that needs to be removed
        login_info = json.loads(r.content[1:])
        assertion = login_info['assertion']
        await self.send('|/trn jimola,0,'+assertion)
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

    async def challenge(self, username):
        await self.send('|/challenge ' + username + ', gen7randombattle')
        incoming = ''
        while True:
            incoming = await self.recv()
            cmd_type = incoming.split('|')[1]
            if(cmd_type == 'b'):
                break
            else:
                print('Last message ignored')
        #battle name and players
        self.battle_name = incoming.split('|')[2]
        self.cnt = 2
        await self.battle()

    async def battle(self):

        while(True):
            msg = []
            while True:
                msg = await self.recv()
                msg = msg.split('|')
                if msg[1] == 'request' and msg[2]:
                    content = json.loads(msg[2])
                    if 'forceSwitch' in content:
                        await self.send(self.battle_name + '|/switch ' +
                                str(self.cnt))
                        self.cnt += 1
                        break
                    if 'wait' in content:
                        break

                    await self.send(self.battle_name + '|/move 1')

try:
    f = open('../secret.txt').read()
    username, password = f.split('\n')[0:2]
except FileNotFoundError:
    print('File containing username and password not found')

loop = asyncio.get_event_loop()
s = SimpleAI()
asyncio.ensure_future(s.login(username, password))
asyncio.ensure_future(s.challenge('GucciMoney'))
loop.run_forever()
