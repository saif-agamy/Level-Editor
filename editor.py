import pygame 
import sys

class editor :
  def __init__(self) :
    #main setup
    pygame.init()
    self.resolution = (1280,720)
    self.main_screen = pygame.display.set_mode(self.resolution)

    #editor screen
    self.editor_resolution = [0,0]
    self.editor_resolution[0] = 0.75 * self.resolution[0]
    self.editor_resolution[1] = 0.60 * self.resolution[1]
    self.editor_screen = pygame.Surface(self.editor_resolution)

    #editor settings
    self.tile_size = 16
    self.tile_map = {
      #tile pos : {pos : () , type : "" , rotate : (1 -> 4) , size_in_tiles : int }
    }

    #setup assets
    self.editor_assets = {}
    self.game_assets = {
      "top-left" : pygame.image.load(r"assets\test tiles\tile_0000.png"),
      "top" : pygame.image.load(r"assets\test tiles\tile_0001.png"),
      "top-right" : pygame.image.load(r"assets\test tiles\tile_0002.png"),
      "left" : pygame.image.load(r"assets\test tiles\tile_0027.png"),
      "center" : pygame.image.load(r"assets\test tiles\tile_0028.png"),
      "right" : pygame.image.load(r"assets\test tiles\tile_0029.png"),
      "bottom-left" : pygame.image.load(r"assets\test tiles\tile_0054.png"),
      "bottom" : pygame.image.load(r"assets\test tiles\tile_0055.png"),
      "bottom-right" : pygame.image.load(r"assets\test tiles\tile_0056.png"),
    }

    self.default_asset_key = list(self.game_assets.keys())[0]
    self.default_asset = self.game_assets[self.default_asset_key]
    self.selected_tile = None 

  def run(self) :
    while True :
      #events code 
      for event in pygame.event.get() :
        #exit 
        if event.type == pygame.QUIT :
          pygame.quit()
          sys.exit()
        
        #mouse events 
        if event.type == pygame.MOUSEBUTTONDOWN :
          mouse_pos = pygame.mouse.get_pos()
          mouse_pos_tile = (int(mouse_pos[0] / self.tile_size), int(mouse_pos[1] / self.tile_size))
          self.add_tile(mouse_pos_tile)
        
        if event.type == pygame.MOUSEBUTTONUP :
          pass

        #keyboard events
        if event.type == pygame.KEYDOWN :
          pass
        
        if event.type == pygame.KEYUP :
          pass
        
      for key in self.tile_map :
        tile = self.tile_map[key]
        print(tile['pos'])

      #main screen code
      self.main_render()
      pygame.display.flip()

  def main_render(self) :
    self.render_tilemap()
    self.main_screen .fill((114, 112, 110))
    self.main_screen.blit(self.editor_screen,(0,0))
    
  def render_tilemap(self) :
    self.editor_screen.fill((135, 206, 235))
    for key in self.tile_map :
        tile = self.tile_map[key]
        x = int(tile['pos'][0] * self.tile_size)
        y = int(tile['pos'][1] * self.tile_size)
        self.editor_screen.blit(self.game_assets[tile["type"]], (x, y))
    

  def add_tile(self,pos_tiles) :
    pos_tiles_format = str(pos_tiles[0]) + ';' + str(pos_tiles[1])
    if pos_tiles_format not in self.tile_map :
      self.tile_map[pos_tiles_format] = {
        "pos" : pos_tiles,
        "type" : self.default_asset_key,
        "rotate" : 1,
        "size_in_tiles" : 1,
        }
    else:
      self.select(pos_tiles)

  def select(self,pos_tiles) :
    self.selected_tile = self.tile_map[str(pos_tiles[0]) + ';' + str(pos_tiles[1])]

program = editor()
program.run()