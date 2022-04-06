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

CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 600
CIRCLE = 120
INTERVAL = 30
GAP_X = (CANVAS_WIDTH-(6*CIRCLE+5*INTERVAL))//2
GAP_Y = 20

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
        print("> Server disconnected")
        exit()

    def Network_connectError(self, data):
        self.window.connectErrorLabel.pack()

    def Network_leaderboard(self, data):
        self.window.set_leaderboard(data["states"], data["scores"])
    
    def Network_askChallenge(self, data):
        self.window.set_challengelist(data["player"], data["score"], data["hour"])

    def Network_startGame(self, data):
        pass

    def Network_endGame(self, data):
        self.window.grid.refresh([0 for i in range(12)])

    def Network_refresh(self, data):
        self.window.grid.refresh(data["cases"])
        nickname = data["turn"]
        if nickname == self.window.nickname.get(): self.window.turnLabel.config(text="C'est ton tour !")
        else: self.window.turnLabel.config(text=f"C'est au tour {nickname}")
        print(f"> Refresh {data}")
    
    def Network_preview(self, data):
        self.window.grid.set_borders("black")
        self.window.grid.set_border(data["case"], "red")


class ClientWindow(Tk):
    def __init__(self, host, port):
        Tk.__init__(self)
        self.title("Awélé")
        self.resizable(False, False)
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

        self.ruleLabel = Label(self.rulesFrame, text="Règles du jeu :").pack(pady=20)

        self.rulesLabel = Label(self.rulesFrame, text="").pack(pady=10)

        self.rulesFrame.pack()

                ### rulesFrame />

        self.menuNotebook.add(self.leaderboardFrame, text ="Liste des joueurs")
        self.menuNotebook.add(self.challengelistFrame, text="Défis en attente")
        self.menuNotebook.add(self.rulesFrame, text ="Règles du jeu")
        self.menuNotebook.pack(expand=1, fill="both")

            ### menuNotebook />

            ### < menuGame

        self.menuGameFrame = Frame(self)

        self.canvas = Canvas(self.menuGameFrame, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, bd="1", bg="#F0F0F0")
        self.canvas.pack()
        self.grid = Grid(self, self.canvas)

        self.turnLabel = Label(self.menuGameFrame, text="Vous pouvez lancer une partie !", font=("Arial", 25))
        self.turnLabel.pack()

            ### menuGame />

        ### generalFrame />

    ###

    def send_nickname(self, nickname):
        self.client.Send({"action":"setNickname", "nickname":nickname})

    ###

    def confirm_nickname(self):
        self.geometry("1480x720")
        self.connectionFrame.pack_forget()
        self.menuGameFrame.pack(padx=(0,40), pady=30, side=RIGHT, anchor="c")
        self.generalFrame.pack(padx=20, pady=30, anchor="c")

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
            self.challengeLabel.config(justify="center", text="Vous ne pouez pas jouer contre vous-même !\n(Faut pas abuser...)")
        elif self.leaderboardTreeview.item(self.leaderboardTreeview.focus())["values"][1] != "Connecté":
            self.challengeLabel.config(justify="center", text="Ce joueur n'est pas disponible pour un défi !\n(On veut bien mais bonjour l'ambiance...)")
        else:
            self.challengeLabel.config(text="")
            self.client.Send({"action":"askChallenge", "nickname":nickname})
        self.leaderboardTreeview.item(self.leaderboardTreeview.focus())["values"][1]

    def acceptChallenge(self):
        nickname = self.challengelistTreeview.item(self.challengelistTreeview.focus())["text"]
        self.client.Send({"action":"acceptChallenge", "nickname":nickname})

    ###

    def MainLoop(self):
        while self.client.state != DEAD:
            self.update()
            self.client.Loop()
            sleep(0.001)
        exit()


class Grid:
    def __init__(self, window, canvas):
        self.window = window
        self.canvas = canvas
        self.grid_img = PhotoImage(file="src/back.png")
        self.canvas.create_image(1, 1, image=self.grid_img, anchor="nw")
        self.cases = [Case(self.window, self.canvas, i) for i in range(12)]

    def set_border(self, nb, color):
        self.cases[nb].set_color(color)

    def set_borders(self, color):
        for i in range(12): self.set_border(i, color)

    def refresh(self, numbers):
        for i in range(12):
            self.cases[i].refresh(numbers[i])


class Case:
    def __init__(self, window, canvas, nb):
        self.window = window
        self.canvas = canvas
        self.nb = nb
        self.x, self.y = GAP_X+(CIRCLE+INTERVAL)*(lambda x: x if x<6 else 5-(x-6))(self.nb), (CANVAS_HEIGHT//2)+(lambda x: GAP_Y+CIRCLE if x<6 else -GAP_Y)(self.nb)
        self.dx, self.dy = GAP_X+CIRCLE+(CIRCLE+INTERVAL)*(lambda x: x if x<6 else 5-(x-6))(self.nb), (CANVAS_HEIGHT//2)+(lambda x: GAP_Y if x<6 else -GAP_Y-CIRCLE)(self.nb)
        self.refresh(0)

    def set_color(self, color):
        self.circle = self.canvas.create_oval(self.x, self.y, self.dx, self.dy, width=3, outline=color)

    def refresh(self, nb):
        if nb>20: nb = 20
        self.current_img = PhotoImage(file=f"src/case{nb}.png")
        self.case_img = self.canvas.create_image(self.x, self.y, image=self.current_img, anchor="sw")
        self.circle = self.canvas.create_oval(self.x, self.y, self.dx, self.dy, width=3)
        self.canvas.tag_bind(self.case_img, "<Button-1>", lambda e: self.window.client.Send({"action":"preview", "case_nb":self.nb}))
        self.canvas.tag_bind(self.case_img, "<Button-3>", lambda e: self.window.client.Send({"action":"confirmation", "case_nb":self.nb}))

##### start

if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    host, port = "localhost", "1234"
else:
    host, port = sys.argv[1].split(":")
client_window = ClientWindow(host, port)
client_window.MainLoop()
