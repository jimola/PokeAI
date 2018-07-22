
## A Pokemon AI

### Prerequisites

Clone the repository. The Pokemon-Showdown repository will be empty.  
Fill it by typing 'git submodule init' and 'git submodule update'.  

You will need websockets. Run 'pip install websocket-client'.

### Running

Pokemon-Showdown is my fork of the regular Pokemon Showdown repo.  
Start a server by running pokemon-showdown within that folder.

To start the current AI, type 'python main.py'. But three things are needed
before it can run.  
First, the server's websocket address. This will look like 
'ws://localhost:8000/showdown/websocket'. Second, a username and password for 
logging in. Third, a team which to use (there are some default teams in teams.txt).

The AI is contained in the BattleAI class. It sucks right now, 
and it sometimes fails to even make a move (like if
its pokemon is taunted and it tries an invalid move). Let's make it better!
