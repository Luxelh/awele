#!/usr/bin/env python3
#coding:utf-8

import sys
from tabnanny import check
from time import sleep, localtime
from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from random import randint
from datetime import datetime

##### cst

WIDTH = 9
HEIGHT = 7

ONLINE = 1
ONGAME = 2
OFFLINE = 0

##### cls

class ClientChannel(Channel):
    nickname = "anonymous"
    color = "red"
    state = False

    def Close(self):
        self._server.Del_Player(self)

    def get_nickname(self):
        return self.nickname

    def get_color(self):
        return self.color

    def set_state(self, state):
        self.state = state

    def Network_setNickname(self, data):
        self.nickname = data["nickname"]
        if self.nickname in self._server.get_states().keys() and self._server.get_states()[self.nickname]: self.Send({"action":"connectError"})
        else:
            self._server.set_state(self)
            self._server.set_score(self)
            print(f"> Adding player : {self._server.get_states()}")
            self.Send({"action":"start"})
            self._server.send_leaderboard_to_all()
    
    def Network_askChallenge(self, data):
        self._server.send_to(data["nickname"], {"action":"askChallenge", "player":self.nickname, "score":self._server.get_score(self.nickname) , "hour":datetime.now().strftime("%H:%M")})

    def Network_acceptChallenge(self, data):
        self._server.new_game(self, self._server.get_player(data["player"]))

class TheServer(Server):
    channelClass = ClientChannel
    def __init__(self, localaddr):
        Server.__init__(self, localaddr=localaddr)
        print("> Server launched")
        self.players, self.states, self.scores, self.games = {}, {}, {}, []

    def Connected(self, channel, addr):
        self.Add_Player(channel)

    def Add_Player(self, player):
        self.players[player] = True

    def Del_Player(self, player):
        self.states[player.nickname] = OFFLINE
        del self.players[player]
        print(f"> Deleting player : {self.get_states()}")
        self.send_leaderboard_to_all()

    ### setter

    def set_state(self, p):
        self.states[p.nickname] = ONLINE

    def set_score(self, p):
        if p.nickname not in self.scores.keys(): self.scores[p.nickname] = 0

    ### getter

    def get_player(self, nickname):
        for p in self.players:
            if p.nickname == nickname: return p

    def get_players_nicknames(self):
        return [p.nickname for p in self.players]

    def get_states(self):
        return self.states

    def get_scores(self):
        return self.scores

    def get_score(self, nickname):
        return self.scores[nickname]

    ### game fct

    def new_game(self, player1, player2):
        self.games.append(Game(self, player1, player2))

    ### send fct

    def send_to(self, nickname, data):
        [p.Send(data) for p in self.players if p.nickname is nickname]

    def send_to_all(self, data):
        [p.Send(data) for p in self.players]

    def send_leaderboard_to_all(self):
        self.send_to_all({"action":"leaderboard", "states":self.states, "scores":self.scores})

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.001)


class Game:
    def __init__(self, server, player1, player2):
        self.server = server
        self.players = [player1, player2]
        for p in self.players:
            self.server.states[p.nickname] = ONGAME
            p.Send({"action":"startGame"})
        self.server.send_leaderboard_to_all()
        print(f"> Game created : {self.players[0].nickname} vs {self.players[1].nickname}")
        self.end_Game(self.players[0])

    def end_Game(self, winner):
        for p in self.players:
            self.server.states[p.nickname] = ONLINE
            p.Send({"action":"endGame", "winner":winner.nickname})
        self.server.scores[winner.nickname] += 1
        self.server.send_leaderboard_to_all()
        print(f"> Game deleted : {winner.nickname} wins")


##### start

if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    host, port = "localhost", "1234"
else:
    host, port = sys.argv[1].split(":")
s = TheServer((host, int(port)))
s.Launch()
