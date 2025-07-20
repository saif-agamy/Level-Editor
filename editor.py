import pygame
import sys
import os
import json
import time
import math
from text import Text
from Settings import *
from utils import load_assets


class Editor:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("SA level editor")
        pygame.display.set_icon(pygame.image.load('Logo_icon.ico'))
        
        # Initialize display and surfaces
        self.init_main_screen()
        self.init_editor_surfaces()
        self.init_tilemap_window()
        self.init_tile_info_window()
        self.init_assets_window()
        self.init_settings_window()
        
        # Game state
        self.tile_size = TILE_SIZE
        self.tile_map = {}  # key: "x;y", value: {pos, type, rotate, size, selected}
        self.offgrid = {}  # key: "asset_num;layer" value: {pos, layer, type, rotate, size, selected}
        self.offgrid_rects = {}  # key "asset_num;layer" value: rect
        self.window_offgrid_rects = {}
        
        # Assets
        self.game_assets = load_assets()
        if len(self.game_assets) > 0 :
            self.default_asset_key = [list(self.game_assets.keys())[0], False]
        else :
            self.default_asset_key = [None, False]
        # Camera and input
        self.camera_scroll = [0, 0]
        self.shifting = False
        self.left_clicking = False
        
        # Show loading screen
        self.show_loading_screen()

    def init_main_screen(self):
        """Initialize the main display window."""
        self.screen_width, self.screen_height = 1280, 720
        self.main_screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
    def init_editor_surfaces(self):
        """Initialize editor surfaces and rectangles."""
        # Main editor area
        self.editor_width = int(self.screen_width * 0.735)
        self.editor_height = int(self.screen_height * 0.57)
        self.editor_surface = pygame.Surface((self.editor_width, self.editor_height))
        self.editor_rect = pygame.Rect(10, 10, self.editor_width, self.editor_height)
        
        # Scaled surface for zoomed-in view
        self.scaled_width = self.editor_width // 2
        self.scaled_height = self.editor_height // 2
        self.scaled_surface = pygame.Surface((self.scaled_width, self.scaled_height))
    
    def init_tilemap_window(self):
        """Initialize the tilemap selection window."""
        self.tilemap_window_width = self.screen_width * 0.24
        self.tilemap_window_height = self.editor_height * 0.6
        self.tilemap_window_resolution = (self.tilemap_window_width, self.tilemap_window_height)
        self.tilemap_window_surf = pygame.Surface(self.tilemap_window_resolution)
        self.tile_window_font = pygame.font.Font(FONT_PATH, 16)
        self.tilemap_window_rect = pygame.Rect(
            self.editor_width + 20, 10, 
            self.tilemap_window_width, self.tilemap_window_height
        )
        self.tiles_rects = {}
        self.tilemap_window_scroll = 0
    
    def init_tile_info_window(self):
        """Initialize the tile information window."""
        self.tile_info_width = self.tilemap_window_width
        self.tile_info_height = self.editor_height * 0.385
        self.tile_info_resolution = (self.tile_info_width, self.tile_info_height)
        self.tile_info_window = pygame.Surface(self.tile_info_resolution)
        self.tile_info_font = pygame.font.Font(FONT_PATH, 16)
        self.tile_info_rect = pygame.Rect(
            self.editor_width + 20, 
            self.tilemap_window_height + (self.editor_height * 0.02) + 10,
            self.tile_info_width, self.tile_info_height
        )
        
        # Tile options
        self.tiles_options = ["layer txt",'size txt']
        self.tiles_options_rects = {}
        start_y = 80
        padding = 10
        txt_bar_size = (100, 30)
        option_button_size = (40, 20)
        
        for option in self.tiles_options:
            if option.endswith("txt"):
                self.tiles_options_rects[option] = Text(
                    (self.tile_info_width - 120, start_y, txt_bar_size[0]),
                    txt_bar_size[0], txt_bar_size[1], self.tile_info_font
                )
            else:
                self.tiles_options_rects[option] = [
                    pygame.Rect(self.tile_info_width - 63, start_y, option_button_size[0], option_button_size[1]),
                    True
                ]
            start_y += 25 + padding
    
    def init_assets_window(self):
        """Initialize the assets selection window."""
        self.assets_width = self.editor_width
        self.assets_height = self.screen_height * 0.4
        self.assets_resolution = (self.editor_width, self.assets_height)
        self.assets_window = pygame.Surface(self.assets_resolution)
        self.assets_font = pygame.font.Font(FONT_PATH, 16)
        self.assets_info = {}
        self.assets_window_rect = pygame.Rect(
            10, self.editor_height + 20, 
            self.assets_width, self.assets_height
        )
        self.assets_window_scroll = 0
    
    def init_settings_window(self):
        """Initialize the settings window."""
        self.settings_width = self.tile_info_width
        self.settings_height = self.assets_height
        self.settings_resolution = (self.settings_width, self.settings_height)
        self.settings_window = pygame.Surface(self.settings_resolution)
        self.settings_font = pygame.font.Font(FONT_PATH, 16)
        self.settings_buttons = {}
        
        self.buttons_names = ["Show Grid", "map name txt", "save", "load", "On grid"]
        self.settings_window_rect = pygame.Rect(
            self.assets_width + 20,
            self.tilemap_window_height + self.tile_info_height + 27,
            self.settings_width, self.settings_height
        )
        
        self.text_bar_x = 190
        self.text_bar_y = 42
        start_y = 10
        button_size = (40, 20)
        increasing_rate = button_size[1] + 20
        
        for button in self.buttons_names:
            if button.endswith("txt"):
                self.settings_buttons[button] = Text(
                    (self.text_bar_x, self.text_bar_y),
                    100, 30, self.settings_font
                )
            else:
                self.settings_buttons[button] = [
                    pygame.Rect(self.settings_width - 20 - button_size[0], start_y, button_size[0], button_size[1]),
                    False
                ]
            start_y += increasing_rate
    
    def show_loading_screen(self):
        """Display the initial loading screen."""
        self.main_screen.fill(SCREEN_COLOR)
        
        loading_screen_font_1 = pygame.font.Font(FONT_PATH, 120)
        loading_screen_font_2 = pygame.font.Font(FONT_PATH, 30)
        
        logo_text = loading_screen_font_1.render("Saif Agamy", True, (255, 255, 255))
        editor_text = loading_screen_font_2.render("Level Editor made with python and pygame", True, (255, 255, 0))
        version_text = loading_screen_font_2.render(str(VERSION), True, (255, 255, 0))
        
        # Center the logo and editor text
        self.main_screen.blit(
            logo_text,
            (self.screen_width/2 - logo_text.get_width()/2,
            self.screen_height/2 - logo_text.get_height()/2 - editor_text.get_height()/2)
        )
        self.main_screen.blit(
            editor_text,
            (self.screen_width/2 - editor_text.get_width()/2,
            self.screen_height/2 - editor_text.get_height()/2 + editor_text.get_height() + 30)
        )
        self.main_screen.blit(version_text, (10, self.screen_height - 30))
        
        pygame.display.flip()
        time.sleep(3)  # This seems unnecessary, consider removing

    def run(self):
        """Main game loop."""
        while True:
            self.handle_events()
            self.change_offgrid_location()
            self.render()
            pygame.display.flip()
            self.update_buttons()
    
    def update_buttons(self):
        """Update button states and handle button actions."""
        for button_name, button in self.settings_buttons.items():
            if button_name == "save" and button[1]:
                self.save_map()
                button[1] = False
            elif button_name == "load" and button[1]:
                self.load_map()
                button[1] = False
            elif button_name.endswith('txt'):
                button.update()
            elif button_name == "On grid" :
                self.default_asset_key[1] = button[1]
        
        for option_name, option in self.tiles_options_rects.items():
            if option_name.endswith('txt'):
                option.update()
            else:
                pass

    def handle_events(self):
        """Process all user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            self.handle_mouse_events(event)
            self.handle_keyboard_events(event)
    
    def handle_mouse_events(self, event):
        """Handle mouse-related events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_button_map = {
                1: self.handle_left_click,
                2: self.handle_middle_click,
                3: self.handle_right_click,
                4: self.handle_scroll_up,
                5: self.handle_scroll_down
            }
            
            if event.button in mouse_button_map:
                mouse_button_map[event.button]()

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 :
                self.left_clicking = False
    
    def handle_left_click(self):
        """Handle left mouse button clicks."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if self.editor_rect.collidepoint(mouse_x, mouse_y):
            self.handle_editor_click(mouse_x, mouse_y)
        elif self.assets_window_rect.collidepoint(mouse_x, mouse_y):
            self.handle_assets_click(mouse_x, mouse_y)
        elif self.tilemap_window_rect.collidepoint(mouse_x, mouse_y):
            self.handle_tilemap_click(mouse_x, mouse_y)
        elif self.tile_info_rect.collidepoint(mouse_x, mouse_y):
            self.handle_tile_info_click(mouse_x, mouse_y)
        elif self.settings_window_rect.collidepoint(mouse_x, mouse_y):
            self.handle_settings_click(mouse_x, mouse_y)

        self.left_clicking = True
    
    def handle_editor_click(self, mouse_x, mouse_y):
        """Handle clicks in the editor area."""
        scaled_x, scaled_y = self.get_scaled_coords(mouse_x, mouse_y)
        tile_x = int(scaled_x / self.tile_size)
        tile_y = int(scaled_y / self.tile_size)
        pos_tiles = (tile_x, tile_y)
        tile_key = f"{pos_tiles[0]};{pos_tiles[1]}"

        if self.default_asset_key[1]:
            if tile_key in self.tile_map:
                self.select_tile(tile_key)
            else:
                self.add_tile(pos_tiles, tile_key)
        else :
            if self.default_asset_key[0] == None :
                for rect_key in self.offgrid_rects :
                    rect = self.offgrid_rects[rect_key]
                    if rect.collidepoint(scaled_x,scaled_y) :
                        self.select_offgrid(rect_key)
            else :
                self.add_offgrid((scaled_x,scaled_y))
    
    def handle_assets_click(self, mouse_x, mouse_y):
        """Handle clicks in the assets window."""
        local_x = mouse_x - self.assets_window_rect.x
        local_y = mouse_y - self.assets_window_rect.y
        
        for key, rect in self.assets_info.items():
            if rect.collidepoint(local_x, local_y):
                if key == self.default_asset_key[0]:
                    self.default_asset_key[0] = None
                else:
                    self.default_asset_key[0] = key
    
    def handle_tilemap_click(self, mouse_x, mouse_y):
        """Handle clicks in the tilemap window."""
        local_x = mouse_x - self.tilemap_window_rect.x
        local_y = mouse_y - self.tilemap_window_rect.y
        
        for key, rect in self.tiles_rects.items():
            if rect.collidepoint(local_x, local_y):
                self.select_tile(key)
        
        for key, rect in self.window_offgrid_rects.items():
            if rect.collidepoint(local_x, local_y):
                self.select_offgrid(key)
    
    def handle_tile_info_click(self, mouse_x, mouse_y):
        """Handle clicks in the tile info window."""
        local_x = mouse_x - self.tile_info_rect.x
        local_y = mouse_y - self.tile_info_rect.y
        
        for option_key, option in self.tiles_options_rects.items():
            if option_key.endswith("txt"):
                if option.rect.collidepoint(local_x, local_y):
                    option.stats = not option.stats
            else:
                if option[0].collidepoint(local_x, local_y):
                    option[1] = not option[1]
    
    def handle_settings_click(self, mouse_x, mouse_y):
        """Handle clicks in the settings window."""
        local_x = mouse_x - self.settings_window_rect.x
        local_y = mouse_y - self.settings_window_rect.y
        
        for button_name, button in self.settings_buttons.items():
            if button_name.endswith('txt'):
                if button.rect.collidepoint(local_x, local_y):
                    button.stats = not button.stats
            else:
                if button[0].collidepoint(local_x, local_y):
                    button[1] = not button[1]
    
    def handle_middle_click(self):
        """Handle middle mouse button clicks."""
        pass  # Currently unused
    
    def handle_right_click(self):
        """Handle right mouse button clicks."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if self.editor_rect.collidepoint(mouse_x, mouse_y):
            scaled_x, scaled_y = self.get_scaled_coords(mouse_x, mouse_y)
            tile_x = int(scaled_x / self.tile_size)
            tile_y = int(scaled_y / self.tile_size)
            tile_key = f"{tile_x};{tile_y}"
            
            if tile_key in self.tile_map:
                del self.tile_map[tile_key]

            # Create a list of keys to delete to avoid modifying dict during iteration
            keys_to_delete = []
            for rect_key, rect in self.offgrid_rects.items():
                if rect.collidepoint(scaled_x, scaled_y):
                    keys_to_delete.append(rect_key)
            
            # Delete the found keys
            for key in keys_to_delete:
                if key in self.offgrid:
                    del self.offgrid[key]
                if key in self.offgrid_rects:
                    del self.offgrid_rects[key]

        if self.assets_window_rect.collidepoint(mouse_x, mouse_y):
            self.default_asset_key[0] = None

        if self.editor_rect.collidepoint(mouse_x, mouse_y):
            self.deselect_all()
    
    def handle_scroll_up(self):
        """Handle mouse scroll up events."""
        self.handle_scroll(4)
    
    def handle_scroll_down(self):
        """Handle mouse scroll down events."""
        self.handle_scroll(5)
    
    def handle_scroll(self, direction):
        """Handle scroll events for scrollable windows."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if self.tilemap_window_rect.collidepoint(mouse_x, mouse_y):
            tilemap_height = 40 * len(self.tile_map) + 10
            offgrid_height = 40 * len(self.offgrid) + 10
            content_height = tilemap_height + offgrid_height
            visible_height = self.tilemap_window_resolution[1]
            min_scroll = 0
            max_scroll = min(0, visible_height - content_height)
            
            if direction == 4:  # Scroll up
                self.tilemap_window_scroll = min(min_scroll, self.tilemap_window_scroll + 5)
            elif direction == 5:  # Scroll down
                self.tilemap_window_scroll = max(max_scroll, self.tilemap_window_scroll - 5)
        
        elif self.assets_window_rect.collidepoint(mouse_x, mouse_y):
            rows = math.ceil(len(self.game_assets) / ASSETS_PER_ROW)
            content_height = 50 * rows + 40
            visible_height = self.assets_height
            min_scroll = 0
            max_scroll = min(0, visible_height - content_height)
            
            if direction == 4:  # Scroll up
                self.assets_window_scroll = min(min_scroll, self.assets_window_scroll + 5)
            elif direction == 5:  # Scroll down
                self.assets_window_scroll = max(max_scroll, self.assets_window_scroll - 5)
    
    def handle_keyboard_events(self, event):
        """Handle keyboard input events."""
        if event.type == pygame.KEYDOWN:
            self.handle_key_presses(event)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                self.shifting = False
    
    def handle_key_presses(self, event):
        """Handle key press events."""
        # Handle text input for text boxes
        for button in self.settings_buttons:
            if button.endswith("txt"):
                button_obj = self.settings_buttons[button]
                if button_obj.stats:
                    button_obj.type_txt(event, "str")
        
        for option in self.tiles_options_rects:
            if option.endswith("txt"):
                option_obj = self.tiles_options_rects[option]
                if option_obj.stats:
                    option_obj.type_txt(event, "int")
        
        # Handle editor navigation
        if self.editor_rect.collidepoint(*pygame.mouse.get_pos()):
            if event.key == pygame.K_w:
                self.camera_scroll[1] += self.tile_size * int(TILE_MAP_SCROLL_SPEED)
            elif event.key == pygame.K_s:
                self.camera_scroll[1] -= self.tile_size * int(TILE_MAP_SCROLL_SPEED)
            elif event.key == pygame.K_a:
                self.camera_scroll[0] += self.tile_size * int(TILE_MAP_SCROLL_SPEED)
            elif event.key == pygame.K_d:
                self.camera_scroll[0] -= self.tile_size * int(TILE_MAP_SCROLL_SPEED)
            elif event.key == pygame.K_r:
                self.rotate_selected_tiles()
        
        # Handle special keys
        if event.key == pygame.K_LSHIFT:
            self.shifting = True
        elif event.key == pygame.K_t:
            self.save_map()
        elif event.key == pygame.K_y:
            self.load_map()
        elif event.key == pygame.K_l:
            offgrid_keys = list(self.offgrid.keys())
            for offgrid_key in offgrid_keys:
                offgrid = self.offgrid[offgrid_key]
                if offgrid['selected'] :
                    for option in self.tiles_options_rects :
                        if option.endswith("txt") and option[:-4] == "layer" :
                            text_bar = self.tiles_options_rects[option]
                            self.change_layer(offgrid_key,int(text_bar.text))
        elif event.key == pygame.K_f:
            offgrid_keys = list(self.offgrid.keys())
            for offgrid_key in offgrid_keys:
                offgrid = self.offgrid[offgrid_key]
                if offgrid['selected'] :
                    for option in self.tiles_options_rects :
                        if option.endswith("txt") and option[:-4] == "size" :
                            text_bar = self.tiles_options_rects[option]
                            self.change_size(float(text_bar.text))
    
    def rotate_selected_tiles(self):
        """Rotate all selected tiles."""
        for tile in self.tile_map.values():
            if tile['selected']:
                tile['rotate'] += 1

        for offgrid in self.offgrid.values():
            if offgrid['selected']:
                offgrid['rotate'] += 1

    def change_offgrid_location(self):
        if self.left_clicking :
            for key in self.offgrid :
                offgrid = self.offgrid[key]
                rect = self.offgrid_rects[key]
                
                mouse_x = pygame.mouse.get_pos()[0]
                mouse_y = pygame.mouse.get_pos()[1]
                
                scaled_x = (self.scaled_width / self.editor_width) * mouse_x
                scaled_y = (self.scaled_height / self.editor_height) * mouse_y
                if offgrid['selected']:
                    img_size = (self.game_assets[offgrid['type']].get_width(),self.game_assets[offgrid['type']].get_height())
                    offgrid['pos'] = (scaled_x - img_size[0] + 2,scaled_y - img_size[1] + 1)
                    rect.topleft = (scaled_x - img_size[0] + 2,scaled_y - img_size[1] + 1)
    
    def get_scaled_coords(self, mouse_x, mouse_y):
        """Convert screen coordinates to scaled editor coordinates."""
        scaled_x = ((mouse_x - 10) * self.scaled_width / self.editor_width) - self.camera_scroll[0]
        scaled_y = ((mouse_y - 10) * self.scaled_height / self.editor_height) - self.camera_scroll[1]
        return scaled_x, scaled_y
    
    def add_tile(self, tile_pos, tile_key):
        """Add a new tile at the given position."""
        self.deselect_all()
        
        if self.default_asset_key[0] is not None:
            self.tile_map[tile_key] = {
                "pos": tile_pos,
                "type": self.default_asset_key[0],
                "rotate": 0,
                'selected': True
            }
    
    def add_offgrid(self, offgrid_tile_pos):
        """Add a new off-grid tile at the given position."""
        self.deselect_all()
        
        asset_num = len(self.offgrid)
        if self.default_asset_key[0] is not None:
            offgrid_key = f"{asset_num};0"
            
            if offgrid_key in self.offgrid:
                self.select_offgrid(offgrid_key)
            else:
                self.offgrid[offgrid_key] = {
                    'pos': (offgrid_tile_pos[0] - 6, offgrid_tile_pos[1] - 8),
                    'layer': 0,
                    'type': self.default_asset_key[0],
                    'rotate': 0,
                    'size': 1,
                    'selected': True
                }
                
                self.offgrid_rects[offgrid_key] = pygame.Rect(
                    offgrid_tile_pos[0] - 6, offgrid_tile_pos[1] - 8,
                    self.game_assets[self.default_asset_key[0]].get_width(),
                    self.game_assets[self.default_asset_key[0]].get_height()
                )
    
    def deselect_all(self):
        """Deselect all tiles and off-grid objects."""
        for tile in self.tile_map.values():
            tile["selected"] = False
        
        for offgrid in self.offgrid.values():
            offgrid["selected"] = False
    
    def select_tile(self, tile_key):
        """Select or deselect a tile."""
        if not self.shifting:
            self.deselect_all()
            
        if tile_key in self.tile_map:
            self.tile_map[tile_key]["selected"] = not self.tile_map[tile_key]["selected"]
    
    def select_offgrid(self, offgrid_key):
        """Select or deselect an off-grid object."""
        if not self.shifting:
            self.deselect_all()
            
        self.offgrid[offgrid_key]["selected"] = not self.offgrid[offgrid_key]["selected"]

    def change_layer(self,offgrid_key,new_layer_num) :
        # 1. Get the original offgrid object
        offgrid = self.offgrid[offgrid_key]
        
        # 2. Create new key with the new layer number
        asset_num = offgrid_key.split(';')[0]  # Get the part before ;
        new_key = f"{asset_num};{new_layer_num}"
        
        # 3. Create the updated offgrid object with new layer
        updated_offgrid = {
            'pos': offgrid['pos'],
            'layer': new_layer_num,
            'type': offgrid['type'],
            'rotate': offgrid['rotate'],
            'size': offgrid['size'],
            'selected': offgrid['selected']
        }
        
        # 4. Remove the old entry and add the new one
        del self.offgrid[offgrid_key]
        self.offgrid[new_key] = updated_offgrid
        
        # 5. Also update the offgrid_rects dictionary if it exists
        if offgrid_key in self.offgrid_rects:
            self.offgrid_rects[new_key] = self.offgrid_rects[offgrid_key]
            del self.offgrid_rects[offgrid_key]
        
        # 6. Reorder all offgrid objects by layer (optional)
        max_layer = max((grid['layer'] for grid in self.offgrid.values()), default=0)
        
        new_arranged_offgrid = {}
        for layer_num in range(0, max_layer + 1):
            for grid_key, grid_obj in self.offgrid.items():
                if grid_obj["layer"] == layer_num:
                    new_arranged_offgrid[grid_key] = grid_obj
        
        # 7. Update the offgrid dictionary (note: using = not ==)
        self.offgrid = new_arranged_offgrid

    def change_size(self,new_size) : 
        for offgrid_key in self.offgrid :
            offgrid = self.offgrid[offgrid_key]
            if offgrid['selected'] :
                offgrid['size'] = new_size

                if offgrid_key in self.offgrid_rects:
                    asset_img = self.game_assets[offgrid['type']]
                    self.offgrid_rects[offgrid_key] = pygame.Rect(
                        offgrid['pos'][0],
                        offgrid['pos'][1],
                        asset_img.get_width() * new_size,
                        asset_img.get_height() * new_size
                    )

    def render(self):
        """Render all editor components."""
        self.render_tiles()
        self.render_tilemap_assets()
        self.render_tiles_data()
        self.render_assets()
        self.render_settings()
        
        # Blit all surfaces to the main screen
        self.main_screen.fill(SCREEN_COLOR)
        self.main_screen.blit(self.editor_surface, self.editor_rect.topleft)
        self.main_screen.blit(self.tilemap_window_surf, self.tilemap_window_rect.topleft)
        self.main_screen.blit(self.tile_info_window, self.tile_info_rect.topleft)
        self.main_screen.blit(self.assets_window, self.assets_window_rect.topleft)
        self.main_screen.blit(self.settings_window, self.settings_window_rect.topleft)
    
    def render_tiles(self):
        """Render the tilemap to the editor surface."""
        self.scaled_surface.fill(EDITOR_BACKGROUND_COLOR)
        
        # Render all tiles
        for tile_data in self.tile_map.values():
            self.render_tile(tile_data)
        
        # Render all off-grid objects
        for offgrid_data in self.offgrid.values():
            self.render_offgrid(offgrid_data)
        
        # Draw grid if enabled
        if self.settings_buttons["Show Grid"][1]:
            self.draw_grid()
        
        # Show preview of selected asset
        self.render_asset_preview()
        
        # Scale up and blit to editor surface
        scaled = pygame.transform.scale(self.scaled_surface, (self.editor_width, self.editor_height))
        self.editor_surface.blit(scaled, (0, 0))
    
    def render_tile(self, tile_data):
        """Render a single tile."""
        x = tile_data["pos"][0] * self.tile_size
        y = tile_data["pos"][1] * self.tile_size
        tile_image = self.game_assets[tile_data["type"]]
        
        # Draw the tile
        self.scaled_surface.blit(
            pygame.transform.rotate(tile_image, tile_data['rotate'] * 90),
            (x + self.camera_scroll[0], y + self.camera_scroll[1])
        )
        
        # Highlight selected tiles
        if tile_data['selected']:
            rect_pos_x = tile_data['pos'][0] * self.tile_size
            rect_pos_y = tile_data['pos'][1] * self.tile_size
            rect = pygame.Rect(
                rect_pos_x + self.camera_scroll[0],
                rect_pos_y + self.camera_scroll[1],
                self.tile_size, self.tile_size
            )
            pygame.draw.rect(self.scaled_surface, SELECT_COLOR, rect, width=1)
    
    def render_offgrid(self, offgrid_data):
        """Render a single off-grid object."""
        offgrid_image = self.game_assets[offgrid_data["type"]]
        self.scaled_surface.blit(
            pygame.transform.scale(pygame.transform.rotate(offgrid_image, offgrid_data['rotate'] * 90),(offgrid_image.get_width()*offgrid_data['size'],offgrid_image.get_height()*offgrid_data['size'])),
            (offgrid_data['pos'][0] + self.camera_scroll[0],
            offgrid_data['pos'][1] + self.camera_scroll[1]))
        
        # Highlight selected off-grid objects
        if offgrid_data['selected']:
            rect_pos_x = offgrid_data['pos'][0]
            rect_pos_y = offgrid_data['pos'][1]
            rect = pygame.Rect(
                rect_pos_x + self.camera_scroll[0],
                rect_pos_y + self.camera_scroll[1],
                self.game_assets[offgrid_data['type']].get_width() * offgrid_data['size'], self.game_assets[offgrid_data['type']].get_height() * offgrid_data['size']
            )
            pygame.draw.rect(self.scaled_surface, SELECT_COLOR, rect, width=1)
    
    def draw_grid(self):
        """Draw grid lines on the editor surface."""
        grid_color = GRID_LINES_COLOR
        
        # Vertical lines
        for x in range(0, self.scaled_width, self.tile_size):
            pygame.draw.line(self.scaled_surface, grid_color, (x, 0), (x, self.scaled_height))
        
        # Horizontal lines
        for y in range(0, self.scaled_height, self.tile_size):
            pygame.draw.line(self.scaled_surface, grid_color, (0, y), (self.scaled_width, y))
    
    def render_asset_preview(self):
        """Show a preview of the currently selected asset under the mouse."""
        if self.default_asset_key[0] is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            if self.editor_rect.collidepoint(mouse_x, mouse_y):
                asset_img = self.game_assets[self.default_asset_key[0]].copy()
                asset_img.set_alpha(128)
                
                if self.default_asset_key[1]:  # On grid
                    scaled_x = ((mouse_x - 10) * self.scaled_width / self.editor_width)
                    scaled_y = ((mouse_y - 10) * self.scaled_height / self.editor_height)
                    
                    tile_x = int(scaled_x / self.tile_size)
                    tile_y = int(scaled_y / self.tile_size)
                    
                    self.scaled_surface.blit(
                        asset_img,
                        (tile_x * self.tile_size, tile_y * self.tile_size)
                    )
                else:  # Off grid
                    scaled_x = ((mouse_x - 25) * self.scaled_width / self.editor_width)
                    scaled_y = ((mouse_y - 30) * self.scaled_height / self.editor_height)
                    
                    self.scaled_surface.blit(asset_img, (scaled_x, scaled_y))
    
    def render_tilemap_assets(self):
        """Render the list of placed tiles in the tilemap window."""
        tile_display_size = 25
        padding = 15
        increasing_rate = tile_display_size + padding
        
        self.tilemap_window_surf.fill(WINDOWS_COLOR)
        
        # Combine tiles and off-grid objects for display
        tiles = self.tile_map.values()
        offgrids = self.offgrid
        
        if len(self.tile_map) == 0 and len(self.offgrid) == 0:
            empty_text = self.tile_window_font.render(
                "There is no tile to be shown", True, FONT_COLOR_LIGHT
            )
            self.tilemap_window_surf.blit(
                empty_text,
                (self.tilemap_window_width/4 - 30, self.tilemap_window_height/2 - 10)
            )
            return
        
        # Render each tile in the list
        start_pos_y = 10 + self.tilemap_window_scroll
        self.tiles_rects = {}
        self.window_offgrid_rects = {}
        
        for i, tile in enumerate(tiles):
            # Create background rectangle for the tile entry
            tile_rect = pygame.Rect(
                4, start_pos_y - 6,
                self.tilemap_window_resolution[0] - 10,
                tile_display_size + 12
            )
            
            # Draw the background (highlighted if selected)
            pygame.draw.rect(
                self.tilemap_window_surf,
                SELECT_COLOR if tile['selected'] else SCREEN_COLOR,
                tile_rect
            )
            
            # Draw the tile preview
            self.tilemap_window_surf.blit(
                pygame.transform.scale(self.game_assets[tile['type']], (25, 25)),
                (10, start_pos_y)
            )
            
            # Draw the tile name
            tile_name = self.tile_window_font.render(
                tile['type'],
                True,
                FONT_COLOR_DARK if tile['selected'] else FONT_COLOR_LIGHT
            )
            self.tilemap_window_surf.blit(tile_name, (40, start_pos_y + 2.5))
            
            # Store the rectangle for click detection
            if i < len(self.tile_map):
                self.tiles_rects[f"{tile['pos'][0]};{tile['pos'][1]}"] = tile_rect
            
            start_pos_y += increasing_rate

        for offgrid_key in offgrids:
            offgrid = offgrids[offgrid_key]
            # Create background rectangle for the tile entry
            tile_rect = pygame.Rect(
                4, start_pos_y - 6,
                self.tilemap_window_resolution[0] - 10,
                tile_display_size + 12
            )
            
            # Draw the background (highlighted if selected)
            pygame.draw.rect(
                self.tilemap_window_surf,
                SELECT_COLOR if offgrid['selected'] else SCREEN_COLOR,
                tile_rect
            )
            
            # Draw the tile preview
            self.tilemap_window_surf.blit(
                pygame.transform.scale(self.game_assets[offgrid['type']], (25, 25)),
                (10, start_pos_y)
            )
            
            # Draw the tile name
            tile_name = self.tile_window_font.render(
                offgrid['type'],
                True,
                FONT_COLOR_DARK if offgrid['selected'] else FONT_COLOR_LIGHT
            )
            self.tilemap_window_surf.blit(tile_name, (40, start_pos_y + 2.5))
            
            # Store the rectangle for click detection
            self.window_offgrid_rects[offgrid_key] = tile_rect
            
            start_pos_y += increasing_rate
    
    def render_tiles_data(self):
        """Render information about the selected tile in the info window."""
        self.tile_info_window.fill(WINDOWS_COLOR)
        tile_is_selected = False
        offgrid_is_selected = False
        
        # Check for selected tiles first
        for tile in self.tile_map.values():
            if tile['selected']:
                tile_is_selected = True
                self.render_tile_info(tile)
                break
        for offgrid in self.offgrid.values() :
            if offgrid['selected'] :
                self.render_offgrid_info(offgrid)
                offgrid_is_selected = True

        # If no tile is selected, show a message
        if not tile_is_selected and not offgrid_is_selected:
            empty_text = self.tile_info_font.render(
                "there is no tile selected", False, FONT_COLOR_LIGHT
            )
            self.tile_info_window.blit(
                empty_text,
                (self.tile_info_width/4 - 15, self.tile_info_height/2 - 10)
            )

        if offgrid_is_selected :
            # Render tile options
            for option_name, option in self.tiles_options_rects.items():
                if option_name.endswith("txt"):
                    # Text input option
                    option.render(self.tile_info_window)
                    for offgrid in self.offgrid.values() :
                        if offgrid['selected'] :
                            if not option.stats :
                                if option_name[:-4] == 'layer' :
                                    option.text = str(offgrid['layer'])
                                elif option_name[:-4] == 'size' :
                                    option.text = str(offgrid['size'])
                    
                    option_label = self.tile_info_font.render(
                        "- " + option_name[:-4] + " " + (f"[F]" if option_name[:-4] == 'size' else "[" + option_name[0].upper() + "]") , True, (255, 255, 255)
                    )
                    self.tile_info_window.blit(
                        option_label,
                        (option.rect.left - 170, option.rect.top + 2)
                    )
                else:
                    # Toggle button option
                    pygame.draw.rect(
                        self.tile_info_window,
                        (0, 255, 0) if option[1] else (255, 0, 0),
                        option[0]
                    )
                    
                    button_state = self.tile_info_font.render(
                        "ON" if option[1] else "OFF", True, (255, 255, 255))
                    self.tile_info_window.blit(
                        button_state,
                        (option[0].left + 5, option[0].top + 2))
                    
                    option_label = self.tile_info_font.render(
                        "- " + option_name, True, (255, 255, 255))
                    self.tile_info_window.blit(
                        option_label,
                        (option[0].left - 230, option[0].top + 2))
    
    def render_tile_info(self, tile):
        """Render detailed information about a specific tile."""
        # Display basic tile info
        tile_pos = self.tile_info_font.render(
            " - Tile position : " + str(tile['pos']), False, FONT_COLOR_LIGHT
        )
        tile_type = self.tile_info_font.render(
            " - Tile type : " + str(tile['type']), False, FONT_COLOR_LIGHT
        )
        tile_rotation = self.tile_info_font.render(
            " - Tile rotation : " + str((tile['rotate'] * 90) % 360), False, FONT_COLOR_LIGHT
        )
        
        self.tile_info_window.blit(tile_pos, (10, 10))
        self.tile_info_window.blit(tile_type, (10, 35))
        self.tile_info_window.blit(tile_rotation, (10, 60))
    
    def render_offgrid_info(self,offgrid):
        """Render detailed information about a specific tile."""
        # Display basic tile info
        offgrid_pos = self.tile_info_font.render(
            " - Tile position : " + str(offgrid['pos']), False, FONT_COLOR_LIGHT
        )
        offgrid_type = self.tile_info_font.render(
            " - Tile type : " + str(offgrid['type']), False, FONT_COLOR_LIGHT
        )
        offgrid_rotation = self.tile_info_font.render(
            " - Tile rotation : " + str((offgrid['rotate'] * 90) % 360), False, FONT_COLOR_LIGHT
        )
        
        self.tile_info_window.blit(offgrid_pos, (10, 10))
        self.tile_info_window.blit(offgrid_type, (10, 35))
        self.tile_info_window.blit(offgrid_rotation, (10, 60))

    def render_assets(self):
        """Render the assets selection window."""
        self.assets_window.fill(WINDOWS_COLOR)
        
        start_x = 25
        start_y = 20 + self.assets_window_scroll * ASSETS_SCROLL_SPEED
        padding_x = 20
        padding_y = 40
        tile_size = 50
        assets_per_row = ASSETS_PER_ROW
        
        self.assets_info = {}
        
        for index, (key, img) in enumerate(self.game_assets.items()):
            col = index % assets_per_row
            row = index // assets_per_row
            
            x = start_x + col * (tile_size + padding_x)
            y = start_y + row * (tile_size + padding_y)
            
            # Create rectangle for the asset
            rect = pygame.Rect(x - 5, y - 5, tile_size + 10, tile_size + 33)
            self.assets_info[key] = rect
            
            # Draw the asset background (highlighted if selected)
            pygame.draw.rect(
                self.assets_window,
                SELECT_COLOR if self.default_asset_key[0] == key else SCREEN_COLOR,
                rect
            )
            
            # Draw the asset image
            scaled_img = pygame.transform.scale(img, (tile_size, tile_size))
            self.assets_window.blit(scaled_img, (x, y))
            
            # Draw the asset name (truncated if too long)
            display_name = key if len(key) < 5 else f"{key[:6]}.."
            tile_name = self.assets_font.render(
                display_name, False,
                FONT_COLOR_DARK if self.default_asset_key[0] == key else FONT_COLOR_LIGHT
            )
            self.assets_window.blit(tile_name, (x, y + tile_size + 10))
    
    def render_settings(self):
        """Render the settings window."""
        self.settings_window.fill(WINDOWS_COLOR)
        
        # Render all buttons
        for button_name, button in self.settings_buttons.items():
            if button_name.endswith("txt"):
                # Text input button
                button.render(self.settings_window)
                
                # Draw the label
                label = self.settings_font.render(
                    button_name[:-4], True, (255, 255, 255))
                self.settings_window.blit(
                    label,
                    (button.rect.topleft[0] - 175, button.rect.topleft[1] + 10))
            else:
                # Regular button
                if button_name in ["save", "load"]:
                    button_color = FONT_COLOR_LIGHT if button[1] else SELECT_COLOR
                else:
                    button_color = BUTTONS_ON_OFF_COLORS[button[1]]
                
                pygame.draw.rect(self.settings_window, button_color, button[0])
                
                # Draw the button state/text
                if button_name in ["save", "load"]:
                    button_text = ""
                else:
                    button_text = "ON" if button[1] else "OFF"
                
                text_surface = self.settings_font.render(button_text, True, (255, 255, 255))
                self.settings_window.blit(
                    text_surface,
                    (button[0].topleft[0] + 4, button[0].topleft[1] + 3))
                
                # Draw the button label
                label = self.settings_font.render(button_name, True, (255, 255, 255))
                self.settings_window.blit(
                    label,
                    (button[0].topleft[0] - 230, button[0].topleft[1] + 10))
    
    def save_map(self):
        """Save the current tilemap to a file."""
        for button_name, button in self.settings_buttons.items():
            if button_name == "map name txt":
                try :
                    file_path = os.path.join("Maps", f"{button.text}.json")
                    with open(file_path, 'w') as file:
                        json.dump({ 
                            'tile_map' : self.tile_map,
                            'offgrid' : self.offgrid,
                            'tile_size' : self.tile_size,
                            },
                            file
                            )
                    break
                except :
                    pass
    
    def load_map(self):
        """Load a tilemap from a file."""
        for button_name, button in self.settings_buttons.items():
            if button_name == "map name txt":
                try :
                    file_path = os.path.join("Maps", f"{button.text}.json")
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as file:
                            data = json.load(file)
                            self.offgrid = data['offgrid']
                            self.offgrid_rects = {}
                            for offgrid_key in self.offgrid :
                                offgrid = self.offgrid[offgrid_key]
                                self.offgrid_rects[offgrid_key] = pygame.Rect(
                                    offgrid['pos'][0], offgrid['pos'][1],
                                    self.game_assets[offgrid['type']].get_width(),
                                    self.game_assets[offgrid['type']].get_height()
                                )
                            self.tile_map = data['tile_map']
                            self.tile_size = data['tile_size']
                    break
                except :
                    pass


if __name__ == "__main__":
    editor = Editor()
    editor.run()