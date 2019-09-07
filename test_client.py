# -*-coding:Utf-8 -*
from client import *
import unittest

class TestClient(unittest.TestCase):

  def setUp(self):
    #self.j1= Robot(None,'Joueur 1')
    pass
    
  def test_o32(self):
    vc= validCmde('o32')
    self.assertEqual(vc,'o32')
  def test_s(self):
    vc= validCmde('s')
    self.assertEqual(vc,'s1')
  def test_n(self):
    vc= validCmde('n')
    self.assertEqual(vc,'n1')
  def test_e55(self):
    vc= validCmde('e55')
    self.assertEqual(vc,'e55')
  def test_pn(self):
    vc= validCmde('pn')
    self.assertEqual(vc,'np')
  def test_ms(self):
    vc= validCmde('ms')
    self.assertEqual(vc,'sm')
  def test_None(self):
    vc= validCmde('x5')
    self.assertEqual(vc,None)
  def test_C(self):
    vc= validCmde('C')
    self.assertEqual(vc,'c')

if __name__ == '__main__':
  unittest.main()
  
