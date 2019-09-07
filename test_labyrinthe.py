# -*-coding:Utf-8 -*
from labyrinthe import *
import unittest

class TestLabyrinthe(unittest.TestCase):
  """   Test des interractions Robots / Labyrinthe 
        Note: les tests dans les differentes directions sont faite par test_robot
        ici on se contente de tester les refus du labyrinthe, et ses modifications
  """
  
  def setUp(self):
    """ On cree un labyrinthe avec deux robots dedans """
    self.lab = Labyrinthe()
    self.lab.createFromFile('cartes/facile.txt')
    self.rob1= self.lab.appendRobot(None)
    self.rob2= self.lab.appendRobot(None)
    # Posit des robots la ou ca nous arrange
    self.rob1.pos=5,8
    self.rob2.pos=7,8
    pass
    
  def test_move_ok(self):
    """ Test d'un deplacement classique""" 
    self.rob1.cmd='o4'
    does,stop= self.lab.actionUnRobot(self.rob1)
    #print (self.lab.buildView(1))   # Vue pour le joueur 1
    self.assertEqual(does,True)
    self.assertEqual(self.rob1.pos,(5,7))
    does,stop= self.lab.actionUnRobot(self.rob1)
    self.assertEqual(self.rob1.pos,(5,6))
    does,stop= self.lab.actionUnRobot(self.rob1)
    self.assertEqual(self.rob1.pos,(5,5))
    #print (self.lab.buildView(1))   # Vue pour le joueur 1
    
  def test_move_in_wall(self):
    """ On bute sur un mur: la commande est razée, l'execution rejetée"""  
    self.rob1.pos=5,5    # On est en butée 
    self.rob1.cmd='o2'
    does,stop= self.lab.actionUnRobot(self.rob1)
    #print (self.lab.buildView(1))   # Vue pour le joueur 1
    self.assertEqual(self.rob1.pos,(5,5)) # Robot pas bougé
    
  def test_wall_2_door(self):
    """ Verifie que l'on transforme un mur en porte"""
    dbg=False
    if dbg:
      print("test_wall_2_door")
    row,col=5,4
    self.rob1.pos=5,5    # On est en butée 
    self.rob1.cmd='op'    # Note: c'est dans cet ordre que l'on note la commande 
    if dbg:
      print (self.lab.buildView(1))  
    self.assertEqual(self.lab._grid[row][col],'O')  # C'est un mur
    does,stop= self.lab.actionUnRobot(self.rob1)
    if dbg:
      print (self.lab.buildView(1))  
    self.assertEqual(does,True)     # Action ok
    self.assertEqual(self.lab._grid[row][col],'.')  # C'est une porte 


  def test_ext_wall_2_door(self):
    """ Verifie que l'on ne peut pas transformer un mur exterieur en porte"""
    dbg=False
    if dbg:
      print("test_ext_wall_2_door")
    row,col=7,9
    self.rob1.pos=7,8    # On est en butée 
    self.rob1.cmd='ep'    # Note: c'est dans cet ordre que l'on note la commande 
    if dbg:
      print (self.lab.buildView(1))  
    self.assertEqual(self.lab._grid[row][col],'O')  # C'est un mur
    does,stop= self.lab.actionUnRobot(self.rob1)
    if dbg:
      print (self.lab.buildView(1))  
    self.assertEqual(does,True)     # Action ok
    self.assertEqual(self.lab._grid[row][col],'O')  # C'est toujours un mur

  def test_door_2_wall(self):
    """ Verifie que l'on transforme une porte en mur 
        on change aussi de robot 
    """
    #print("test_door_2_wall")
    row,col=6,8
    self.rob2.pos=7,8    
    self.rob2.cmd='nm'    # Note: c'est dans cet ordre que l'on note la commande 
    #print (self.lab.buildView(2))  
    self.assertEqual(self.lab._grid[row][col],'.')  # C'est une porte 
    does,stop= self.lab.actionUnRobot(self.rob2)
    #print (self.lab.buildView(2)) 
    self.assertEqual(does,True)     # Action ok
    self.assertEqual(self.lab._grid[row][col],'O')  # C'est un mur
    
  def test_wall_2_wall(self):
    """ Verifie que l'on ne peut pas modifier un mur en mur """
    dbg=False
    if dbg:
      print("test_wall_2_wall")
    row,col=5,4
    self.rob1.pos=5,5   
    self.rob1.cmd='om'    # Note: c'est dans cet ordre que l'on note la commande 
    if dbg:
      print (self.lab.buildView(1))  
    self.assertEqual(self.lab._grid[row][col],'O')  # C'est un mur
    does,stop= self.lab.actionUnRobot(self.rob1)
    if dbg:
      print (self.lab.buildView(1))  
    self.assertEqual(does,True)     # Action interpretée    
    self.assertEqual(self.lab._grid[row][col],'O')  # C'est tjs un mur

    
if __name__ == '__main__':
  unittest.main()
