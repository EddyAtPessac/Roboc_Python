# -*-coding:Utf-8 -*
import os
import socket
import time
#from threading import Thread, RLock
import threading
import re
import sys 
lock= threading.RLock()


strCommandes=  "\n   Bienvenu dans le jeu roboc\n"
strCommandes+= "   Les commandes possibles sont les suivantes:    \n"
strCommandes+= "      c ........... commencer le jeu (attendez les autres petits camarades avant de faire ça)\n"
strCommandes+= "      pD .......... transformer le mur en porte dans la direction D\n"
strCommandes+= "      mD .......... transformer la porte en mur dans la direction D\n"
strCommandes+= "      Les directions sont:  n,s,e,o (voir déplacements ci dessous)\n"
strCommandes+= "    Déplacements: \n"
strCommandes+= "      n .......... aller vers le nord\n"
strCommandes+= "      s .......... aller vers le sud\n"
strCommandes+= "      e .......... aller vers l'est\n"
strCommandes+= "      o .......... aller vers l'ouest\n"
strCommandes+= "   Vous pouvez preciser le nombre de fois à la suite:\n"
strCommandes+= "   exemple:   o5    ira 5 fois vers l'ouest "
strCommandes+= "   ou jusqu'à la rencontre d'un mur\n"
strCommandes+= "   Pour ces deplacements multiples, chaque joueur avance d'un coup a tour de rôle\n"
strCommandes+= "   s'il bute sur un mur, la commande s'arrete et vous reprenez la main pour donner une nouvelle instruction \n\n"





def validCmde(cmde):
  """ Verifie la syntaxe de la commande passée, et revoie la commande correspondante formatée pour le serveur """
  retCmd=None
  nb=1
  motif1=re.compile(r'^(?P<dir1>[eons]{1})(?P<Nb>\d{1,2})?$|^(?P<action>[mp]{1})(?P<dir2>[eons]{1})|^(?P<start>)[cC]{1}|^(?P<quit>)[qQ]{1}')
  find= motif1.search(cmde)
  #print(find.groupdict())
  if find is not None:
    # Deplacement dans une direction, avec ou sans nombre de coups
    if find.group('dir1') is not None:
      if find.group('Nb') is not None:
        nb=int(find.group('Nb'))
      retCmd=find.group('dir1')+str(nb)  #Deplacement nb fois dans une direction
    # Action de Perçage ou murage avec une direction
    if find.group('action') is not None and find.group('dir2') is not None:
      retCmd=find.group('dir2')+find.group('action')  # murage ou perçage d'une porte
    # Debut de partie par 'c'
    if find.group('start')is not None:
      retCmd='c'
    # Gestion quit supprimée, car trop penible a gerer...  
    #if find.group('quit')is not None:
    #  retCmd='q'
  with lock:
    if retCmd is None:
      print("Commande incorrecte\n")
    else:
      print ("                 \n")
  return retCmd
      
      
    
def playerClientReceiverThread():
  """ Tread de reception des cartes. Se contente d'afficher tout ce que l'on reçoi du serveur
  """
  global mySock     # On utilise la variable mySock globale
  bufSz=1024
  mapView=''
  """ Montre la carte reçue du serveur Si disponible """
  myTread= threading.currentThread()
  mt= myTread  # Raccourci
  cont= getattr(myTread, "do_run", True)   # cont prend la valeur de do_run (ou True si pas accessible)
  while mySock != None:    #Tant que le socket est actif
    try:
      client_map = mySock.recv(bufSz)
      mapView=client_map.decode()
      with lock:
        print (mapView)
        if re.search('Fin',mapView)!=None:
          mySock=None
    except:
      with lock:
        print ('Erreur reception\r')
      time.sleep(1)
      pass

def playerClientTransmiter():
  """ Tread d'emission des commandes. Attend les saisies clavier, les vérifies, 
      et les transmet au serveur, en les préfixant avec notre Identifiant.
  """
  global mySock   # On utilise la variable mySock globale que l'on va modifier
  cmdOk=None
  """ Attend les commande du joueur, et les transmet si elle sont valides """
  while mySock != None:    #Tant que le socket est actif
    cmde= input ()
    if mySock==None:  # Verif si la socket est toujours la...
      break
    cmdOk= validCmde(cmde)
    cmdOk= '{0:02d}{1}'.format(clientId, cmdOk)   #On prefixe notre commande avec notre numero de client sur 2 chiffres
    if cmdOk!=None:
      with lock:
        pass
        #print ('Commande: {}\r'.format(cmdOk))
      try:
        cmdTx=cmdOk.encode()
        mySock.send(cmdTx)
      except:
         print ('Erreur emission\n')
         break
      if cmdOk[2]=='q': 
        mySock.close() 
        mySock= None   # Coupe la socket
        with lock:
          print ('Vous quittez la partie\r')    # Le serveur a été averti, on averti le joueur


ipServ,port="localhost",12800
mySock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientId=0  

    
# Le main du client 
def main():
  global clientId
  global ipServ
  # ~ #print("argc:{}, cmde:{}".format(len(sys.argv),sys.argv[0]))
  if len(sys.argv)>1:   # Si adresse du serveur passé en argument, on la prend
    ipServ= sys.argv[1]
  print ('Connexion à {}'.format(ipServ))
  attCnx=True
  # Boucle attente connexion et reception de notre Identifiant
  while attCnx:
    try:
      mySock.connect((ipServ, port))
      strId=mySock.recv(256).decode()   # Attend l'Id du serveur
      attCnx=False
    except:
      pass
      
  clientId= int(strId)
  print (strCommandes)
  print ('Connecté à {} avec l\'id {} \r'.format(ipServ, clientId) )
  #La connexion est ok, on demarre le jeu 
  # En lançant les 2 thread d'emission et de reception  
  kbdScan = threading.Thread(target= playerClientReceiverThread)
  displayer= threading.Thread(target= playerClientTransmiter) 
  displayer.start()
  kbdScan.start()
  kbdScan.join()
  displayer.join()
  os.system("pause")

      
if __name__ == '__main__':
  main()
