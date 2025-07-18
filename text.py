import pygame

class Text :
  def __init__(self,pos,width,height,font,text=""):
    self.rect = pygame.Rect(pos[0],pos[1],width,height)
    self.width = width
    self.font = font
    self.text = text 
    self.active_color = (255,255,255)
    self.inactive_color = (28, 28, 27)
    self.text_active_color = (0,0,0)
    self.text_inactive_color = (255,255,255)
    self.text_color = self.text_inactive_color
    self.color = self.inactive_color
    self.stats = False
    self.text_surface = self.font.render(self.text,True,self.color)

  def type_txt(self,key,type = "str") :
    if type == 'str' :
      if key.unicode in ["q","w","e","r","t","y","u","i","o","p","a","s","d","f","g","h","j","k","l","z","x","c","v","b","n","m"," ","1","2","3","4","5","6","7","8","9","0","-","_"] :
        self.text += key.unicode
        self.text_surface = self.font.render(self.text,True,self.text_color)
    elif type == 'int' :
      if key.unicode in ['1','2','3','4','5','6','7','8','9','0'] :
        self.text += key.unicode
        self.text_surface = self.font.render(self.text,True,self.text_color)

    if key.key == pygame.K_BACKSPACE :
      self.text = self.text[:-1]
      self.text_surface = self.font.render(self.text,True,(0,0,0))
      

  def update(self):
    if self.stats :
      self.color = self.active_color
      self.text_color = self.text_active_color
      self.text_surface = self.font.render(self.text,True,self.text_color)
    else :
      self.color = self.inactive_color
      self.text_color = self.text_inactive_color
      self.text_surface = self.font.render(self.text,True,self.text_color)

    if self.width < self.text_surface.get_width() + 10 :
      self.text = self.text[:-1]
      self.text_surface = self.font.render(self.text,True,self.text_color)

  def render(self,surf):
    pygame.draw.rect(surf, self.color, self.rect)
    surf.blit(self.text_surface, (self.rect.x + 5, self.rect.y + 5))
