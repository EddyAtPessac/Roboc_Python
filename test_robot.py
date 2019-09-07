# -*-coding:Utf-8 -*
from robot import *
import unittest

class TestRobot(unittest.TestCase):

  def setUp(self):
    self.j1= Robot(None,'Joueur 1')
    pass
    
  def test_move_deny(self):
    """ Deplacement 'e2' (2 cases vers droite), mais refusée par le labyrinthe.
        le robot demande le deplacement, mais la commande est annulée suite au refus
    """
    # Init d'une position raw, col et d'une commande
    self.j1.pos=1,1
    self.j1.cmd='e2'
    #test du deplacement 1/2 on attends _pos= 1,2 et action=g
    #print (self.j1); print ("Apres tryCmd\n")      #
    r,c,a= self.j1.tryCmd()    # Demande au robot l'execution de la commande
    self.assertEqual(r,1)
    self.assertEqual(c,2)
    self.assertEqual(a,'g')
    # Refus du deplacement 
    #print (self.j1); print ("Refus deplacement\n")      #
    self.j1.acceptCmd(False)   # On refuse le deplacement
    self.assertEqual(self.j1.cmd,'') # Puisque refusée, la commande restante est effacée 
    #print (self.j1)      #
    
  def test_move_accept_2(self):
    """ Deplacement 2 cases vers le sud 's2', et acceptée. On laisse les 2 deplacements
        se faire, et la commande restante passer de 's2' a 's1' puis ''
    """
    # Init d'une position raw, col et d'une commande
    self.j1.pos=2,3
    self.j1.cmd='s2'
    #test du deplacement 1/2 on attends _pos= 3,3 et action=g
    #print (self.j1); print ("Apres tryCmd\n")      #
    r,c,a= self.j1.tryCmd()    # Demande au robot l'execution de la commande
    self.assertEqual(r,3)
    self.assertEqual(c,3)
    self.assertEqual(a,'g')
    # Accepte le deplacement 1
    #print (self.j1); print ("Deplacement 1 accepté\n")      #
    self.j1.acceptCmd(True)   # On accepte le deplacement
    self.assertEqual(self.j1.cmd,'s1') # la commande restante
    #test du deplacement 2/2 on attends _pos= 4,3 et action=g
    r,c,a= self.j1.tryCmd()    # Demande au robot l'execution de la commande
    self.assertEqual(r,4)
    self.assertEqual(c,3)
    self.assertEqual(a,'g')
    # Accepte le deplacement 2
    #print (self.j1); print ("Deplacement 2 accepté\n")      #
    self.j1.acceptCmd(True)   # On accepte le deplacement
    self.assertEqual(self.j1.cmd,'') # la commande restante
    
  def test_door_2_wall(self):
    """ Test murer une porte
    """
    self.j1.pos=2,3
    self.j1.cmd='nm'
    #test du murage d'une porte au nord du robot attends _pos= 1,3 et action=m
    #Si on accepte ou pas, la commande resultante doit etre vide
    r,c,a= self.j1.tryCmd()    # Demande au robot l'execution de la commande
    self.assertEqual(r,1)
    self.assertEqual(c,3)
    self.assertEqual(a,'m')
    # Accepte la commande 
    self.j1.acceptCmd(True)   # On accepte 
    self.assertEqual(self.j1.cmd,'') # la commande restante
    
  def test_wall_2_door(self):
    """ Test percer une porte
    """
    self.j1.pos=1,2
    self.j1.cmd='op'
    #test du perçage d'un mur a l'ouest du robot attends _pos= 1,1 et action=p
    #Si on accepte ou pas, la commande resultante doit etre vide
    r,c,a= self.j1.tryCmd()    # Demande au robot l'execution de la commande
    self.assertEqual(r,1)
    self.assertEqual(c,1)
    self.assertEqual(a,'p')
    # Accepte la commande 
    self.j1.acceptCmd(True)   # On accepte 
    self.assertEqual(self.j1.cmd,'') # la commande restante

    
if __name__ == '__main__':
  unittest.main()
  
   

