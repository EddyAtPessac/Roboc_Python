# -*-coding:Utf-8 -*

"""Ce fichier contient le code principal du jeu.

Exécutez-le avec Python pour lancer le jeu.

"""

import os
import labyrinthe
import socket
import select 
import time
import re
#from labyrinthe import Labyrinthe,bloqueException,sortieException


def myInt(_str):
  """ Permet la conversion string vers int sans gerer l'exception """
  try:
    val= int(_str)
  except ValueError:
    val=0
  return val

#Creation labyrinthe
lab= labyrinthe.Labyrinthe()
ipServ,port="",12800
mySock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lst_cnx=list()      # Liste des connexions acceptées
PlayWithWait=True

def main(card_num):
  global lst_cnx      # Liste des connexions acceptées
  global mySock
  global PlayWithWait
  # Pour etre sur du chemin, demande notre chemin absolut
  curPath= os.path.dirname(os.path.realpath(__file__))
  print("Bonjour. Bienvenue dans le serveur du jeu Roboc\n")
  #print ("Nous sommes là: {}".format(curPath))
  cartesPath = curPath+"/cartes/"      #Chemin des cartes
  cartesFiles=list()      # Nom des fichier des cartes et des parties en cours
  key=1               # cle des fichiers
  keyMax=1

  # On affiche les cartes existantes
  print ("Cartes disponibles:")
  for nom_fichier in os.listdir(cartesPath):
    if nom_fichier.endswith(".txt"):
      cartesFiles.append(nom_fichier)   
      strAff1="{}..........................................".format(nom_fichier[:-3])
      strAff2="{}".format(key)
      strAff=strAff1[:30]+strAff2
      print(strAff)
      key+=1;
      keyMax=key
  choix=0     #Demande le choix jusqu'a ce qu'une cle>0  soit donnée
  if card_num >=0:    # Si deja une carte choisie en argument, on saute la question
    choix=card_num
    
  while choix <1 or choix >=keyMax:
      choix= myInt(input("Votre choix: "))
      
  carte=cartesPath+cartesFiles[choix-1]
  print ("On charge {}\n".format(carte))

  r=input( "Faite <Enter> pour le jeu normal (demandé pour le TP), en s'attendant, ou <R> pour jeu en temps Réel, \npour que le plus rapide gagne (tapez R pour Rapide)>")
  PlayWithWait= (r!='r' and r!='R')
  if (not PlayWithWait):
    print ('Mode rapide, on ne s\'attend pas')
  else:
    print ('Mode classique, du TP, on attend le coup du prochain joueur')
  
  lab.createFromFile(carte)
  print(lab)
  
  #Mise en place serveur
  mySock.bind((ipServ,port))
  mySock.listen(5)
  lst_clients=list()  # Liste des sockets demande de connexion
  
  ###################### Boucle principale du jeu ######################
  acceptNew=True    # Vrai tant que l'on peut accepter de nouveau joueurs
  servLoop= True  
  nbClient=0
  cps=1
  print ("Attente des joueurs...\r")

  while servLoop:
    # Phase 1: on attend le debut de partie en attendant tous les clients avant la touche 'd'
    while acceptNew:
      # choppe tous les client qui se sont declarés
      lst_clients,wlst,xlst= select.select([mySock],[],[],0.1)  
      for client in lst_clients:
        nbClient+=1
        cnx,infoCnx= client.accept()
        cnx.send(str(nbClient).encode())    # Donne un numero de connexion au client, pour pouvoir le reconnaitre quand il répond
        lab.appendRobot(cnx)   # Ajoute notre connexion client dans la liste des robots
        lst_cnx.append(cnx)    # Ajoute à la liste des connexions acceptées 
        print(lab.buildViewMap(0))    # Affiche vue du jeu sur le serveur
        print ('{} Joueurs \r'.format(nbClient))
        try:
          cnx.send(lab.buildView(nbClient,"Faire 'c' pour commencer la partie").encode()) # Envoie sa carte à ce client
        except:
          pass
      dicCmd= checkClientReception()    # Reçoie toutes les commandes client
      if 'c' in dicCmd.values():  # Si on a reçu un 'c' dans les commandes, on passe à la  2ieme phase
        acceptNew = False
        print ('Ordre de commencer la partie...\r')
        lab.sendAllViews("\nDébut de partie")    # Debut de partie: envoie une carte a chaque robot
        
    # Phase 2: on joue
    while servLoop:
      print ('\ncoup {} -'.format(cps), end=''); cps+=1
      if (not PlayWithWait):
        time.sleep(0.5)   # Ralenti un peu l'affichage, les joueurs ne sont pas si rapide que ça
      # Gestion des commandes reçues
      applyClientReception()        # Prend en compte les reception client et met a jour les commandes
      #Gestion des actions
      stop, robName = boucleRobots() 
      # Gestion fin de partie 
      if stop==True: 
        print("Le joueur {} a atteind la sortie ".format(robName)) 
        msg1='********************************************\n'
        msg2= '***  Fin de partie, le joueur {} a gagné  ***\n'.format(robName)
        msg= msg1+msg2+msg1
        for cnx in lst_cnx:
          cnx.send(msg.encode())
        servLoop= False
  print ("Fin de jeu.")
  os.system("pause")

def ejectClient( indx):
  """ Supprime un client de la liste des connexions et son robot du labyrinthe.
      Pour le moment cette option n'est pas active.
  """
  global lst_cnx
  global lab
  del lst_cnx[indx]   #Supprime la connexion de la liste
  msg = "Le joueur {} a quitté la partie".format(lab.lstRob[indx].name)
  del lab.lstRob[indx]  # Supprime le joueur du labyrinthe
  lab.sendAllViews(msg)  # Maj des vues avec message
  
def boucleRobots():
  """ Boucle sur chaque robot du labyrinthe. 
      Si le jeu est en mode classique, on attend d'avoir une commande valide avant de lui faire executer par lab.actionUnRobot(rob). 
      Sinon, on attend pas, on passe au suivant, et tant pis si leur joueur n'est pas assez rapide.
      Si le labyrinthe est  modifié ou si la commande est modifiée, on renvoie la nouvelle carte au joueur.
  """
  global lab
  does,stop=False,False
  robName=''
  msg=''
  for rbIndx in range(len( lab.lstRob)):  # Boucle sur les robots
    labCmd=''
    rob=  lab.lstRob[rbIndx]  # Reference sur le robot actuel
    robName=rob.name  # Note nom du robot que l'on fait jouer
    print ('Robot {} -'.format(rbIndx+1,),end='')
    while (PlayWithWait and rob.cmd==''):    # Si on joue en s'attendant: attend que la commande ne soit pas vide 
      applyClientReception()
    else:
      does,stop= lab.actionUnRobot(rob)   # does vaut True si une commande a été interpretée et executée
    if stop:    # Le joueur a atteind la sortie
      msg='Le joueur {} a gagné.'.format(robName)
    if does:    #Si une commande a été interpretée, la carte a bougée, ou la commande a changée
      lab.sendAllViews(msg)     # Renvoie une vue 
      print(lab.buildViewMap(0))    # Affiche vue du jeu sur le serveur
    if stop:
      break #Inutile de continuer dans ce cas
  return stop, robName    # Renvoie stop et le nom du robot qui a joué pour faire ça



def checkClientReception():  
  """ Ecoute tous les clients donc la connexion a été acceptée.
      Retourne une liste de dico avec {id, msg} 
  """
  global lst_cnx
  cliSended=list()
  cmd_dic=dict()       #Liste des messages reçus
  try:
    cliSended,w,x =select.select(lst_cnx,[],[],0.1) # Check les clients qui ont un truc a dire
  except select.error:
    pass
  else:
    if cliSended == None:
      cliSended=[]
  for cli in cliSended:
    try:
      msg= cli.recv(256).decode()
      cli_no= int(msg[:2])     # Numero de client en prefixe du message
      cmd_dic[cli_no]=msg[2:]   # Ajoute message avec son identifiant
    except:
      pass  # Dans l'etat, on ne sait pas gerer une deconnexion du client... 
            # On bloquera ici dans l'attente d'un commande qui ne viendra pas.
      print ('Problème reception client. Serveur planté en attente du client qui a disparu ...')
      time.sleep(1)
  return cmd_dic

def applyClientReception():
  """ Ecoute tous les clients et envoie les commandes reçues aux robots.
      C'est a robot de decider s'il la prend, la bufférise, ou la jette
  """
  debug=0
  cmdes= checkClientReception()
  if debug and len(cmdes)>0:
    print ('Rx: {}\r'.format(cmdes))
  for j,cmd in cmdes.items():
    rob=lab.lstRob[j-1]         # Pour le robot concerné
    rob.addCmd(cmd)             # Ajoute la commande (direct ou dans buffer)

  
if __name__ == '__main__':
  main(0)

  
