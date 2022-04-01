from operator import iconcat
import sys
from tabnanny import check
from time import sleep, localtime
# from PodSixNet.Server import Server
# from PodSixNet.Channel import Channel
from random import randint
import copy

##### cst

WIDTH = 6


##### cls


class Player:
    def __init__(self,liste_cases) -> None:
        self.liste_cases = liste_cases
        self.silo = 0


    def set_silo(self,new_value):
        self.silo = new_value


    def get_silo(self):
        return self.silo




class Case:
    def __init__(self, x):
        self.nb_de_graine = 6
        self.x = x


    def set_nb_de_graine(self,new_value):
        self.nb_de_graine = new_value


    def get_nb_de_graine(self):
        return self.nb_de_graine




class Grid:
    def __init__(self, server, width, height):
        self.server = server
        self.width = width
        self.height = height
        self.case = [Case(x) for x in range(2*(self.width))]
        self.needs_feeding = False #Variable qui permet de savoir s'il faut appliquer la règle nourrir,
                                   #modifiée par la fonction feed_rule



    def semage(self, indice_de_la_case):
        #effectue la plantation des graine de la case donnée en paramètre
        i = 0
        nb_graines_a_semer = self.case[indice_de_la_case].get_nb_de_graine()
        self.case[indice_de_la_case].set_nb_de_graine(self,0)
        while i < nb_graines_a_semer:
            indice_case_a_semer = indice_de_la_case + i +1
            if indice_case_a_semer >= 12: #Système pour recommencer à semer du départ si on a atteint la fin de la liste 
                indice_case_a_semer = indice_case_a_semer - 12      
            current_nb_graines = self.case[indice_case_a_semer].get_nb_de_graine()
            self.case[indice_case_a_semer].set_nb_de_graine(self, current_nb_graines + 1)
            if indice_de_la_case + i +1 + 1 >= 12: #On regarde ce qui se passera au tour d'après si on fait i+=1
                if indice_case_a_semer +1 - 12 !=  indice_de_la_case:
                    i+=1
                else: #Si i+=1 nous fait tomber sur la case de départ, on fait i+=2
                    i=+2                
            else:
                i+=1
        
    

    def camp_vide(self, Player):
        #Fonction à executer à chaque début de tour d'un joueur
        #Sert à définir s'il faut appliquer la règle de nourrir son adversaire
        s = 0
        for e in Player.liste_cases:
            s += self.case[e].get_nb_de_graine()
        if s == 0:
            return True
        else:
           False



    def feed_rule(self,Player):
        if self.camp_vide(self, Player):
            self.needs_feeding = True
        else:
            self.needs_feeding = False 



    def harvest_possible(self, indice_de_la_case):
        #Check si la récolte est possible dans une case dont l'indice est donné en paramètre, renvoie True ou False
        if self.case[indice_de_la_case].get_nb_de_graine()>0 and self.case[indice_de_la_case].get_nb_de_graine() < 4:
            return True
        return False 



    def previsualization(self, indice_de_la_case): 
        #renvoie l'indice de la case dans laquelle sera posée la dernière graine
        #si on choisi de semer à partir de la case qu'on a donnée en paramètre

        #pb si plus de 24 graines dans une case ?
        nb_graines_a_semer = self.case[indice_de_la_case].get_nb_de_graine()
        if indice_de_la_case + nb_graines_a_semer >= 12:
            return (indice_de_la_case + nb_graines_a_semer -12)
        return (indice_de_la_case + nb_graines_a_semer)




    def full_harvest(self, Player, indice_de_la_case_de_départ):
        #Effectue la récolte si possible, renvoie False si la récolte est impossible car le camp de l'adversaire serait vide
        valeur_silo = Player.get_silo
        testcopy = copy.deepcopy(self.case)
        indice_dernier_semis = self.previsualization(self, indice_de_la_case_de_départ)
        while Player.liste_cases.count(indice_dernier_semis) == 0 and indice_dernier_semis >= 0 and self.harvest_possible(self,indice_dernier_semis):
            x = testcopy[indice_dernier_semis].get_nb_de_graine
            testcopy[indice_dernier_semis] = 0
            valeur_silo +=x
            indice_dernier_semis -= 1

        for e in Game.players:   #Game.players == la liste des objets de la classe joueurs ?
            if Player != e:
                otherPlayer = e

        if not self.camp_vide(self, otherPlayer): #y a t il une liste des joueurs qq part?
            self.case = copy.deepcopy(testcopy)
            Player.set_silo(valeur_silo)

        else:
            return False



    def fin_du_game(self, Player): # Check si le joueur donné en entrée peut jouer un coup qui ne laissera pas vide le camp de son adversaire
        s = 0
        for e in Player.liste_cases:
            if self.full_harvest(self, Player, e) == False: #Est-ce-que la fonction full_harvest est exécutée ? 
                s += 1                                      #Si oui il faudra faire une fonction séparée pour check si un coup est jouable
            if s == 6:
                self.termination



    def termination (self):
        #Quand le jeu est terminé (voir la méthode fin_du_game), cette méthode rempli les silos des joueurs avec 
        #les graines restantes dans leurs camps respectifs
        s = 0
        for player in Game.players:  #Game.players == la liste des objets de la classe joueurs ?
            for e in player.liste_cases:
                s += self.case[e].get_nb_de_graine()
            valeur_silo = player.get_silo
            player.set_silo(valeur_silo + s)
            s = 0
