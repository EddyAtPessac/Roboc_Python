# -*-coding:Utf-8 -*
import os
import time
import random
import select
#import fcntl, termios

#Nos modules 
from robot import *
# Module de la classe Labyrinthe


  

class Labyrinthe:
  """ Classe labyrinthe: contient une représentation de la carte (murs, espaces et portes) 
      et la liste des robots qui sont dedans 
  """
  def __init__(self):
    self._grid=[]           # Ca c'est la liste des lignes qui contiennent chacune une liste de colones
    self._couloirs=list()   # Liste des cases disponibles pour la circulation (A l'init)
    self.lstRob=list()     # Liste des Robots dans notre labyrinthe
    self.curPlayer=''
  
  def createFromFile(self, fname):
    """ Remplissage de la grille a partir du fichier passé. 
        Au passage, on fait la liste des couloir (cases disponibles pour poser des robots)
    """
    row,col=0,0
    with open(fname, "r") as fData:
      mapData=fData.readlines()  #Lit toutes les lignes du  fichier
    for fileRowData in mapData:      #info sur la ligne: chaque caratere represente une case du labyrinthe
      if fileRowData[0]=='\n' or fileRowData[0]=='\r':    # Le read/write du fichier rajoute des sauts de ligne
        continue                                          # ... si trouvé en début de ligne, on ignore cette ligne
      self._grid.append([])         # Ajoute la ligne sur la grille de jeu
      for car in fileRowData:       # chaque caractere represente une colone 
        self._grid[row].append([' '])   # Ajoute la colone
        self._grid[row][col]= car       # Place l'objet decrit dans cette cellule
        if car=='.' or car==' ':        # Si on est dans un couloir, 
          self._couloirs.append((row,col))    #  on ajoute cette case à la liste des couloirs
        col+=1
      row+=1  # ligne fichier suivante
      col=0


  def buildViewMap( self, robDisplay):
    """ Represente le labyrinthe avec ses robots. l'index en parametre est le numero
        du robot [1 a n]  pour laquelle la vue est construite. C'est a dire pour
        laquelle le robot est représenté par 'X' au lieu de 'x'. Si l'index est 
        à 0, c'est une vue générique où tous les robots sont représentés par leur numero 
    """
    # Pour une raison que j'ignore, si on place un \r ca marche, mais ca peut ecraser les autres chaines de caractere 
    # a la concatenation. Mais si on met des \n ça saute 2 lignes ...
    strLabView='\n'
    nbRow=0
    nbCol=0
    maxRaw=len(self._grid)
    for row in range (maxRaw):     # boucle sur les lignes
      maxCol= len(self._grid[row])
      for col in range (maxCol):    # pour chaque colone
        car = self._grid[row][col]                # recupere le decor
        for robIndx in range (len(self.lstRob)):        # liste des robots
          if (row,col)==self.lstRob[robIndx].pos:      # Si ce robot est dans cette case
            car='x'                                # on rajoute le robot ici
            if robDisplay == 1+robIndx:            # Si c'est le robot pour lequel on fait cette vue, c'est un grand X
              car='X'
            if robDisplay==0:
              car=self.lstRob[robIndx].name[0]     # Carte generale: affiche les robots avec leur numeros 
          #print("'{}'".format(car),end='')
        strLabView+= car
      #strLabView= strLabView +'\r'   # Affichage ligne suivante
    #strLabView+=('Lab: maxRaw:{} maxCol:{}\n'.format(maxRaw,maxCol))
    return strLabView

  def buildView(self, robDisplay, msg=''):
    """ Construit vue du labyrinthe avec les commandes et les messages eventuels"""
    # Constrution vue globale
    status=str()
    #msgEntet= '== Joueur{} ==\n'.format(robDisplay)
    msgEntet=' '
    strLabView= self.buildViewMap(robDisplay)

    # Si pas de message, et vue pour un joueur et que au moins un joueur, rappel du nom du joueur
    if msg=='' and  robDisplay>0 and len(self.lstRob)>0:   
      msg='*Joueur {}*'.format(self.lstRob[robDisplay-1].name)
    if len(msg)>1 and msg[-1]!='\n':
      msg+='\n'
    # Affichage 'commande en cour' ou   'a vous:'
    if robDisplay>0:     # Si c'est un joueur specifique
      robDisplay-=1       #Index de la liste commence a 0
      cmd= self.lstRob[robDisplay].cmd    # Commande en cour d'execution
      if cmd=='':
         status='Entrez commande:'
      else:
         status= "Commande en cours:'{}'".format(cmd)
    strView="\n%s%s%s%s" % (msgEntet,strLabView,msg,status)
    return strView

  def sendView(self,robNo,msg=''):
    """ Envoie la representation de la carte et le statut au client """
    strView= self.buildView(robNo,msg)
    bufTx= strView.encode()
    try:
      self.lstRob[robNo-1].cnx.send(bufTx)
    except:
      print ("Probleme envoie carte robot n°{}".format(robNo))

  def sendAllViews (self, msg=''):
    """ Envoie la vue du labyrinthe a tous les robots sur leur socket """ 
    robNo= 1  # Pour buildview, le numero commence à 1
    for rob in self.lstRob:       #Boucle sur tous nos robots enregistrés
      self.sendView(robNo,msg)
      robNo+=1
  def __repr__(self):
    """ Representation affichable du labyrinthe et des robots qui sont dedans
    """
    return self.buildView(0)

  def __str__(self):
    return repr(self)

  def actionUnRobot(self, rob):
    """ Demande au robot l'action a faire, verifie si faisable ou pas, 
        l'execute si ok et rend compte au robot si ok 
    """
    self.curPlayer= rob.name          # Note joueur en cour
    row,col,action= rob.tryCmd()      # Demande action et ligne, colone au robot
    if len(rob.cmd)>0:
      pass
    ok= None
    stop=False
    if action=='g':                   # Deplacement
      ok = self._grid[row][col]!='O'    # Accepté si la case demandée est differente d'un mur
      stop= self._grid[row][col]=='U'   # Controle supplementaire: Est-ce la fin de jeu 
    elif action =='p':                # perce une porte dans un mur
      ok = self._grid[row][col]=='O'    # Accepté si la case demandée est un mur
      # Verification supplémentaire: interdit de percer les bords du labyrinthe
      maxRaw= len(self._grid)
      maxCol= len(self._grid[0])    # On considere que toutes les lignes ont la même largeure
      #print ('Perce {},{} maxRaw={}  maxCol= {} '.format(row,col,maxRaw, maxCol))
      if row==0 or row>=maxRaw-1:  # Tentative de percer sur bord du labyrinthe: on refuse
        ok= False
      if col==0 or col>=maxCol-2:   # -2 car la fin de ligne contient un\r
        ok=False
      if ok:
        self._grid[row][col]='.'          # Transforme le mur en porte
    elif action =='m':                # mure une porte 
      ok = self._grid[row][col]=='.'    # Accepté si la case demandée est une porte
      self._grid[row][col]='O'          # Tranforme la porte en mur 
    if ok is not None:                # Si action prise en compte 
      rob.acceptCmd(ok)               #    Deplacement ok ou pas
    return (ok!=None, stop)            # Renvoie True si une action a été interpretée. False sinon

  def appendRobot(self, cnx):
    """ Ajout d'un robot au hasard dans une case de type 'couloir'  dans le labyrinthe
    """
    nbJoueur= len(self.lstRob)
    #name = 'Joueur ' + str(nbJoueur+1)
    name = str(nbJoueur+1)
    newRob= Robot( cnx, name)
    pos = random.choice(self._couloirs)   # Trouve une position au hasard dans les cases de type couloirs
    self._couloirs.remove(pos)    # Enleve cette case des cases possibles pour les robots
    newRob.pos= pos
    robInList = self.lstRob.append(newRob) # Ajoute le robot dans le labyrinthe
    robInList = self.lstRob[len(self.lstRob)-1]   #Reference sur le robot créé
    return robInList    # A toute fin utile reference du robot créé dans la liste
 
