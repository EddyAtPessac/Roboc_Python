# -*-coding:Utf-8 -*
# Module de la classe Robot

class Robot:
  """ Classe Robot 
      gere la position et le deplacement du robot
      l'attribut cmd contient la commande a executer, qui a ete mise en forme et qui 
      est re-actualisée a chaque tour ('s3' devient 's2' au tour d'apres)
  """
  
  def __init__(self, cnx, name):
    """ Creation d'un robot avec sa socket et son nom et les autres attributs
    """
    self.name=name    # Nom du joueur
    self.cnx=cnx      # Connexion de ce robot pour envoie de la carte
    self.pos=tuple()  # Colone et Ligne ( col, row )
    self.cmd=''       # Commande en cour d'execution (direction + nbre 's3' ou direction+action 'sp' 'sg' )
    self.bufCmd=''    # Buffer reception. Stocke la commande reçue en attendant que la commande en cour devienne vide
    self._nextCmd=''  # Commande restante si commande en cour validée
    self._nextPos=tuple() # Nouvelle position si commande en cour validée
    self.ret=''       # Commande codée pour le labyrinthe (position, action) (Stockée ici car pratique pour debuguer)

  
  def newPos(self,direction=''):
    """ Retourne le tuple (row, col) de la nouvelle position en fonction 
        de la position actuelle et de la direction indiquée en parametre 
    """
    direction=direction.upper()
    row,col= self.pos
    if direction=='N' :
      row-=1
    elif direction=='S':
      row+=1
    elif direction=='E':
      col+=1
    elif direction=='O':
      col-=1
    # print( "Direction: {} row:{}  col:{}\n".format(direction,row,col))
    return row,col
  
  def tryCmd(self):
    """ Prepare l'execution de la commande _cmd en cours. 
        Retourne le resultat sous la forme d'un tuple (row,col,action) l'action est 'p','m', ou 'g' pour Go (deplacement) a faire.
        Si l'action est possible, l'appel a  acceptCmd(True/Fals) la validera ou pas
        Les prochaines positions et commande sont stockées dans les variables nextXxxx
    """
    self._ret= (0,0,'n')    # Pas d'action serveur par defaut
    if len(self.cmd)<1:
      return self._ret
    direction= self.cmd[0]     # Note direction
    r,c= self.newPos(direction)      # Calcule cellule concernée par l'action ou le deplagement
    
    # ---------- Si c'est une modification du labyrinthe  -----
    if self.cmd[1]=='p' or self.cmd[1]=='m':  
      # On prepare le nouvel etat en cas de succes
      self._nextCmd=''        # Une fois cette commande executée, il ne reste plus rien a faire
      self._nextPos=self.pos # Notre position ne changera pas
      self._ret = (r,c,self.cmd[1])   # Demande au serveur cette action sur cette case
    
    # --------- Dans les autres cas, c'est un deplacement, on decompte le nombre de deplacements ---------
    else:
      nb=1
      if self.cmd[1:]!='':      # Nb dep avec cmd[1:] est validé
        # print ('Nb dep:"{}"'.format(self.cmd[1:]))
        try:
          nb=int (self.cmd[1:])     #Nbre de deplacements restants dans la commande
        except:
          print ('PB avec int({})\r'.format( self.cmd[1:]))
      nb-=1
      #print(" r{} c{} nb{} \n".format(r,c,nb))
      if nb==0:           # Si plus de deplacement, il n'y aura plus rien a executer
        self._nextCmd='' 
      else:
        self._nextCmd= direction+str(nb)    # Sinon, direction + nbre de deplacement restants
      self._nextPos=r,c     # On se retrouvera sur cette case
      self._ret= (r,c,'g')      # Go r,c
    return self._ret
    
  def addCmd(self, cmd):
    """ Ajoute commande reçue au robot.
        Si aucune commande n'est en cour, on le met dans la commande, sinon, dans un buffer
        qui sera pris en compte lorsque qu'il n'y aura plus de commande à executer.
    """
    if self.cmd=='':
      self.cmd=cmd
    else:
      if ( self.bufCmd==''):
        self.bufCmd=cmd
  
  def acceptCmd(self,ok):
    """ Validation ou pas de la commande passee au labyrinthe par tryCmd(). 
        Si la commande est acceptee, le nouvel etat devient l'etat courant.
        Sinon, la position ne change pas et la commande est videe.
    """
    if ok:    # Le mouvement ou la modification de la porte est acceptée
      self.cmd = self._nextCmd
      self.pos= self._nextPos
    else:     # Pas de bol, c'est pas possible. On ne touche pas à la position
      self.cmd= ''   # Pas utile de continuer avec cette commande

    if self.cmd=='':          #Si plus de commande a executer, on prend ce qu'il reste dans le buffer clavier
      self.cmd=self.bufCmd
      self.bufCmd=''
      
    
  def __repr__(self):
    """ Representation des caracteristiques du robot
    """
    reprStr = "\nJoueur: '{0}'  \n".format(self.name)
    r,c= self.pos
    reprStr+= "Position (ligne,col): {0},{1}\n".format(r,c)
    reprStr+= "Commande:{0}\n".format(self.cmd)
    #reprStr+= "Len _nextPos {0}\n".format(len(self._nextPos))
    #reprStr+= "Len _nextCmd {0}\n".format(len(self._nextCmd))
    if len(self._ret) >0:
      reprStr+= "Action serveur: {}\n".format(self._ret)
    if len(self._nextPos) >0:    # Uniquement si on a initialisé les éléments nextXxxx()
      r,c= self._nextPos
      reprStr+= "Nvelle posit: {0},{1}\n".format(r,c)
      reprStr+= "Nvelle cmd:{0}".format( self._nextCmd)
    return reprStr
    
  def __str__(self):
    return repr(self)
  
if __name__ == '__main__':
  help ( Robot)
       
      
    
  
