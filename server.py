#!/usr/bin/env python3
#coding:utf-8

import sys
import copy
from tabnanny import check
from time import sleep, localtime
from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from random import randint
from datetime import datetime


##### cst

WIDTH = 12

ONLINE = 1
ONGAME = 2
OFFLINE = 0

##### cls

class ClientChannel(Channel):
    nickname = "anonymous"
    color = "red"
    state = False
    game = None
    silo = None
    liste_cases = []

    def Close(self):
        self._server.Del_Player(self)

    def get_nickname(self):
        return self.nickname

    def get_color(self):
        return self.color

    def get_game(self):
        return self.game

    def get_silo(self):
        return self.silo

    def get_liste_cases(self):
        return self.liste_cases

    def set_state(self, state):
        self.state = state

    def set_game(self, game):
        self.game = game

    def set_silo(self, nb):
        self.silo = nb

    def set_liste_cases(self, l):
        self.liste_cases = l

    def add_to_silo(self, nb):
        self.silo += nb

    def in_game(self):
        return self.game != None

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
        try:
            if self.game == None and self._server.get_states()[data["nickname"]] == ONLINE:
                self._server.send_to(data["nickname"], {"action":"askChallenge", "player":self.nickname, "score":self._server.get_score(self.nickname) , "hour":datetime.now().strftime("%H:%M")})
        except: pass

    def Network_acceptChallenge(self, data):
        try:
            if self.game == None and self._server.get_states()[data["nickname"]] == ONLINE:
                self._server.new_game(self, self._server.get_player(data["nickname"]))
        except: pass

    def Network_preview(self, data):
        if self.in_game(): self.game.previsualization(self, data["case_nb"])

    def Network_confirmation(self, data):
        if self.in_game(): self.game.confirmation(self, data["case_nb"])


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
        if player.in_game(): player.get_game().player_quit(player)
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
        [p.Send(data) for p in self.players if nickname == p.get_nickname()]

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
            p.set_game(self)
            p.Send({"action":"startGame"})
        self.server.send_leaderboard_to_all()
        self.active_player = self.players[0]

        self.grid = Grid(self)
        for i in range(2):
            self.players[i].set_silo(0)
            self.players[i].set_liste_cases(list(range(6*i,6+6*i)))

        self.refresh()
        print(f"> Game created : {self.players[0].nickname} vs {self.players[1].nickname}")

    def get_players(self):
        return self.players

    def switch_nb(self, nb):
        if nb<6: return nb+6
        return nb-6

    def confirmation(self, player, nb):
        if player == self.active_player and nb<6:
            if player == self.players[1]:
                nb = self.switch_nb(nb)
            if self.grid.get_cases(0)[nb].get_nb_de_graine():
                derniere_case = self.grid.previsualization(nb)
                if not self.grid.full_harvest(player, nb, derniere_case, True):
                    player.Send({"action":"impossible"})
                else:
                    self.grid.semage(nb)
                    self.grid.full_harvest(player, nb, derniere_case, False)
                    self.switch_player()
                    if player.get_game(): self.refresh()

    def previsualization(self, player, nb):
        if player == self.active_player and nb<6:
            if player == self.players[1]: nb = self.switch_nb(nb)
            if self.grid.get_cases(0)[nb].get_nb_de_graine():
                result = self.grid.previsualization(nb)
                if player == self.players[1]: result = self.switch_nb(result)
                player.Send({"action":"preview", "case":result})

    def switch_player(self):
        if self.active_player == self.players[0]: self.active_player = self.players[1]
        else: self.active_player = self.players[0]
        if self.grid.fin_du_game(self.active_player): self.grid.termination()

    def refresh(self):
        for p in range(2):
            self.players[p].Send({"action":"refresh", "cases":[c.get_nb_de_graine() for c in self.grid.get_cases(p)], "turn":self.active_player.nickname, "silos":self.grid.get_silos(self.players[p])})

    def player_quit(self, player):
        if self.players[0] == player: del self.players[0]
        else: del self.players[1]
        self.end_game(self.players[0])

    def end_game(self, winner):
        for p in self.players:
            self.server.states[p.nickname] = ONLINE
            p.set_game(None)
            p.Send({"action":"endGame", "winner":winner.nickname})
        self.server.scores[winner.nickname] += 1
        self.server.send_leaderboard_to_all()
        print(f"> Game deleted : {winner.nickname} wins")


class Grid:
    def __init__(self, game):
        self.game = game
        self.cases = [Case() for i in range(WIDTH)]

    def get_cases(self, p):
        if not p: return self.cases
        return self.cases[6:]+self.cases[:6]

    def get_silos(self, p):
        if p == self.game.players[0]: return [self.game.players[0].get_silo(), self.game.players[1].get_silo()]
        return [self.game.players[1].get_silo(), self.game.players[0].get_silo()]

    def semage(self, indice_de_la_case):
        #effectue la plantation des graine de la case donnée en paramètre
        i = 0
        nb_graines_a_semer = self.cases[indice_de_la_case].get_nb_de_graine()
        self.cases[indice_de_la_case].set_nb_de_graine(0)
        while i < nb_graines_a_semer:
            indice_case_a_semer = indice_de_la_case + i + 1
            while indice_case_a_semer >= 12: #Système pour recommencer à semer du départ si on a atteint la fin de la liste 
                indice_case_a_semer -= 12 
            current_nb_graines = self.cases[indice_case_a_semer].get_nb_de_graine()
            self.cases[indice_case_a_semer].set_nb_de_graine(current_nb_graines + 1)
            prochain_indice_case_a_semer = indice_case_a_semer + 1
            while prochain_indice_case_a_semer >=12: prochain_indice_case_a_semer -= 12
            if prochain_indice_case_a_semer == indice_de_la_case: i += 2
            else: i+= 1
        

    def previsualization(self, indice_de_la_case):
        nb = indice_de_la_case + self.cases[indice_de_la_case].get_nb_de_graine()
        while nb >= 12: nb -= 12
        return nb

    def camp_vide(self, player): #Le "Player" donné en entrée est l'adversaire
        #Fonction à executer à chaque début de tour d'un joueur
        #Sert à définir s'il faut appliquer la règle de nourrir son adversaire
        return sum([self.cases[i].get_nb_de_graine() for i in player.get_liste_cases()]) == 0

    def full_harvest(self, player, premiere_case, derniere_case, test):
        #Effectue la récolte si possible, renvoie False si la récolte est impossible car le camp de l'adversaire serait vide
        silo = player.get_silo()
        testcopy = copy.deepcopy(self.cases)
        while derniere_case not in player.get_liste_cases() and derniere_case >= 0 and self.harvest_possible(derniere_case):
            silo += testcopy[derniere_case].get_nb_de_graine()
            testcopy[derniere_case].set_nb_de_graine(0)
            derniere_case -= 1

        for e in self.game.get_players(): #Game.players == la liste des objets de la classe joueurs ?
            if player != e:
                otherPlayer = e

        if not self.camp_vide(otherPlayer) and not test:
            self.cases = copy.deepcopy(testcopy)
            player.set_silo(silo)
        elif not sum([testcopy[i].get_nb_de_graine() for i in player.get_liste_cases()]) == 0 and test:
            return True
        elif sum([testcopy[i].get_nb_de_graine() for i in player.get_liste_cases()]) == 0 and test:
            return False

    def harvest_possible(self, indice_de_la_case):
        #Check si la récolte est possible dans une case dont l'indice est donné en paramètre, renvoie True ou False
        return self.cases[indice_de_la_case].get_nb_de_graine()>1 and self.cases[indice_de_la_case].get_nb_de_graine()<4

    def fin_du_game(self, player): #Fonction à lancer à chaque début de tour d'un joueur
                                   # Check si le joueur donné en entrée peut jouer un coup qui ne laissera pas vide le camp de son adversaire
                                   # Return False si un tel coup est possible, et sinon, termine le jeu en remplissant les silos et return True
        if self.camp_vide(player): return True
        for i in player.get_liste_cases():
            if self.full_harvest(player, i, self.previsualization(i), True): return False
        return True

    def termination(self):
        #Quand le jeu est terminé (voir la méthode fin_du_game), cette méthode rempli les silos des joueurs avec 
        #les graines restantes dans leurs camps respectifs
        s = 0
        for player in self.game.get_players():
            for e in player.get_liste_cases():
                s += self.cases[e].get_nb_de_graine()
            valeur_silo = player.get_silo()
            player.set_silo(valeur_silo + s)
            s = 0
        
        if self.game.get_players()[0].get_silo() > self.game.get_players()[1].get_silo(): self.game.end_game(self.game.get_players()[0])
        else: self.game.end_game(self.game.get_players()[1])

    
class Case:
    def __init__(self):
        self.nb_de_graine = 2

    def get_nb_de_graine(self):
        return self.nb_de_graine

    def set_nb_de_graine(self, new_value):
        self.nb_de_graine = new_value


##### start

if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    host, port = "localhost", "1234"
else:
    host, port = sys.argv[1].split(":")
s = TheServer((host, int(port)))
s.Launch()
