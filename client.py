#!/usr/bin/env python3
#coding:utf-8

import sys
from time import sleep
from sys import stdin, exit
from PodSixNet.Connection import connection, ConnectionListener
from tkinter import *
from tkinter.ttk import *


##### cst

INITIAL = 0
ACTIVE = 1
DEAD = -1

WIDTH = 300
HEIGHT = 300

##### class

class Client(ConnectionListener):
    def __init__(self, host, port, window):
        self.window = window
        self.Connect((host, port))
        self.state = ACTIVE
        print("Client started")

    def Network_connected(self, data):
        print("You are now connected to the server")

    def Loop(self):
        connection.Pump()
        self.Pump()

    def quit(self):
        self.window.destroy()
        self.state = DEAD

    def Network_start(self, data):
        self.window.confirm_nickname()

    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()

    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()

    def Network_connectError(self, data):
        self.window.connectErrorLabel.pack()

    def Network_leaderboard(self, data):
        self.window.set_leaderboard(data["states"], data["scores"])
    
    def Network_askChallenge(self, data):
        self.window.set_challengelist(data["player"], data["score"], data["hour"])

    def Network_startGame(self, data):
        self.window.menuNotebook.pack_forget()

    def Network_endGame(self, data):
        self.window.menuNotebook.pack(expand=1, fill="both")


class ClientWindow(Tk):
    def __init__(self, host, port):
        Tk.__init__(self)
        self.title("Awélé")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", lambda: self.client.quit())
        self.client = Client(host, int(port), self)
        self.playerState = False
        self.nickname = StringVar()

        ### < connectionFrame

        self.connectionFrame = Frame(self)
        connectLabel = Label(self.connectionFrame, text="Entrez votre pseudo :").pack()
        connectEntry = Entry(self.connectionFrame, width=20, textvariable=self.nickname).pack()
        connectButton = Button(self.connectionFrame, text="Se connecter", command=lambda: self.send_nickname(self.nickname.get()) if self.nickname.get() != "" else 0).pack(padx=10, pady=5)
        self.connectErrorLabel = Label(self.connectionFrame, text="Ce pseudo est déjà utilisé !")
        self.connectionFrame.pack(padx=20, pady=30)

        ### connectionFrame />
        
        ### < generalFrame

        self.generalFrame = Frame(self)

            ### < menuNotebook

        self.menuNotebook = Notebook(self.generalFrame, width=450, height=800)

                ### < leaderboardFrame

        self.leaderboardFrame = Frame(self.menuNotebook)

                    ### < optionsFrame

        optionsFrame = Frame(self.leaderboardFrame, height=200)
        self.challengeLabel = Label(optionsFrame, text="")
        self.challengeLabel.pack()
        askButton = Button(optionsFrame, text="Défier", command=self.askChallenge).pack(padx=10, pady=3)
        optionsFrame.pack(side=BOTTOM, pady=(0,20))

                    ### optionsFrame />

                    ### boardFrame

        self.boardFrame = Frame(self.leaderboardFrame)

        self.leaderboardTreeview = Treeview(self.boardFrame, columns=("score", "etat"))

        leaderboardScrollbar = Scrollbar(self.boardFrame, orient=VERTICAL)
        leaderboardScrollbar.pack(side=RIGHT, fill=Y)
        
        self.leaderboardTreeview.config(yscrollcommand=leaderboardScrollbar.set)
        leaderboardScrollbar.config(command=self.leaderboardTreeview.yview)

        self.leaderboardTreeview.column("#0", width=150, minwidth=100, stretch=False)
        self.leaderboardTreeview.column("score", width=60, minwidth=50, stretch=False)
        self.leaderboardTreeview.column("etat", width=100, minwidth=50, stretch=False)
        self.leaderboardTreeview.heading("#0" , text="Joueur")
        self.leaderboardTreeview.heading("score", text="Score")
        self.leaderboardTreeview.heading("etat", text="Etat")
        self.leaderboardTreeview.pack()

        self.boardFrame.pack(pady=20)

                    ### boardFrame />

        self.leaderboardFrame.pack(fill=None, expand=False)

                ### leaderboardFrame />

                ### < challengelistFrame

        self.challengelistFrame = Frame(self.menuNotebook)

                    ### < challengelistoptionsFrame

        challengelistoptionsFrame = Frame(self.challengelistFrame, height=200)
        acceptButton = Button(challengelistoptionsFrame, text="Accepter", command=self.acceptChallenge).pack(padx=10, pady=3)
        challengelistoptionsFrame.pack(side=BOTTOM, pady=(0,20))

                    ### challengelistoptionsFrame />

                    ### < challengelistboardFrame

        self.challengelistboardFrame = Frame(self.challengelistFrame)

        self.challengelistTreeview = Treeview(self.challengelistboardFrame, columns=("score", "heure"))

        challengelistScrollbar = Scrollbar(self.challengelistboardFrame, orient=VERTICAL)
        challengelistScrollbar.pack(side=RIGHT, fill=Y)
        
        self.challengelistTreeview.config(yscrollcommand=challengelistScrollbar.set)
        challengelistScrollbar.config(command=self.challengelistTreeview.yview)

        self.challengelistTreeview.column("#0", width=150, minwidth=100, stretch=False)
        self.challengelistTreeview.column("score", width=60, minwidth=50, stretch=False)
        self.challengelistTreeview.column("heure", width=60, minwidth=50, stretch=False)
        self.challengelistTreeview.heading("#0" , text="Joueur")
        self.challengelistTreeview.heading("score", text="Score")
        self.challengelistTreeview.heading("heure", text="Heure")
        self.challengelistTreeview.pack()

        self.challengelistboardFrame.pack(pady=20)

                    ### challengelistboardFrame />

        self.leaderboardFrame.pack(fill=None, expand=False)

                ### challengelistFrame />

                ### < rulesFrame

        self.rulesFrame = Frame(self.menuNotebook)

        self.rulesLabel = Label(self.rulesFrame, text="Règles du jeu :").pack(pady=20)

        self.rulesFrame.pack()

                ### rulesFrame />

        self.menuNotebook.add(self.leaderboardFrame, text ="Liste des joueurs")
        self.menuNotebook.add(self.challengelistFrame, text="Défis en attente")
        self.menuNotebook.add(self.rulesFrame, text ="Règles du jeu")
        self.menuNotebook.pack(expand=1, fill="both")

            ### menuNotebook />

        ### generalFrame />

    ###

    def send_nickname(self, nickname):
        self.client.Send({"action":"setNickname", "nickname":nickname})

    ###

    def confirm_nickname(self):
        self.geometry("600x720")
        self.connectionFrame.pack_forget()
        self.generalFrame.pack(padx=20, pady=30)

    def set_leaderboard(self, states, scores):
        for i in self.leaderboardTreeview.get_children(): self.leaderboardTreeview.delete(i)
        order = sorted(scores.items(), key=lambda x: x[1])
        self.leaderboardTreeview.configure(height=len(states))
        for i in range(len(order)): self.leaderboardTreeview.insert("", i, text=f"{order[i][0]}", values=(order[i][1], (lambda x: "Connecté" if x==1 else ("En jeu" if x==2 else "Hors ligne"))(states[order[i][0]])))

    def set_challengelist(self, player, score, hour):
        for i in self.challengelistTreeview.get_children():
            if self.challengelistTreeview.item(i)["text"] == player: self.challengelistTreeview.delete(i)
        self.challengelistTreeview.insert("", 0, text=player, values=(score, hour))

    ###

    def askChallenge(self):
        nickname = self.leaderboardTreeview.item(self.leaderboardTreeview.focus())["text"]
        if nickname == self.nickname.get(): 
            self.challengeLabel.config(justify="center", text="Vous ne pouez pas jouer contre vous-même ! (Faut pas abuser...)")
        elif self.leaderboardTreeview.item(self.leaderboardTreeview.focus())["values"][1] != "Connecté":
            self.challengeLabel.config(justify="center", text="Ce joueur n'est pas disponible pour un défi !\n(On veut bien mais bonjour l'ambiance...)")
        else:
            self.challengeLabel.config(text="")
            self.client.Send({"action":"askChallenge", "nickname":nickname})
        self.leaderboardTreeview.item(self.leaderboardTreeview.focus())["values"][1]

    def acceptChallenge(self):
        nickname = self.challengelistTreeview.item(self.challengelistTreeview.focus())["text"]
        self.client.Send({"action":"acceptChallenge", "player":nickname})

    ###

    def MainLoop(self):
        while self.client.state != DEAD:
            self.update()
            self.client.Loop()
            sleep(0.001)
        exit()


##### start

if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    host, port = "localhost", "1234"
else:
    host, port = sys.argv[1].split(":")
client_window = ClientWindow(host, port)
client_window.MainLoop()
