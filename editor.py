import pygame
import sys


class Editor:
    def __init__(self):
        pygame.init()

        # Main screen setup
        self.screen_width, self.screen_height = 1280, 720
        self.main_screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        # Editor screen setup
        self.editor_width = int(self.screen_width * 0.75)
        self.editor_height = int(self.screen_height * 0.60)
        self.editor_surface = pygame.Surface((self.editor_width, self.editor_height))

        self.scaled_width = self.editor_width // 2
        self.scaled_height = self.editor_height // 2
        self.scaled_surface = pygame.Surface((self.scaled_width, self.scaled_height))

        # Tile settings
        self.tile_size = 16
        self.tile_map = {}  # key: "x;y", value: {pos, type, rotate, size}

        # Assets
        self.game_assets = self.load_assets()
        self.default_asset_key = list(self.game_assets.keys())[0]
        self.selected_tile = None

    def load_assets(self):
        #Load and return all tile assets.
        base_path = r"assets\test tiles"
        return {
            "top-left": pygame.image.load(f"{base_path}\\tile_0000.png"),
            "top": pygame.image.load(f"{base_path}\\tile_0001.png"),
            "top-right": pygame.image.load(f"{base_path}\\tile_0002.png"),
            "left": pygame.image.load(f"{base_path}\\tile_0027.png"),
            "center": pygame.image.load(f"{base_path}\\tile_0028.png"),
            "right": pygame.image.load(f"{base_path}\\tile_0029.png"),
            "bottom-left": pygame.image.load(f"{base_path}\\tile_0054.png"),
            "bottom": pygame.image.load(f"{base_path}\\tile_0055.png"),
            "bottom-right": pygame.image.load(f"{base_path}\\tile_0056.png"),
        }

    def run(self):
        #Main game loop.
        while True:
            self.handle_events()
            self.render()
            pygame.display.flip()

    def handle_events(self):
        #Process all user input.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click()

    def handle_mouse_click(self):
        #Handle clicking on the tilemap.
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Convert to scaled surface coordinates
        scaled_x = mouse_x * self.scaled_width / self.editor_width
        scaled_y = mouse_y * self.scaled_height / self.editor_height

        tile_x = int(scaled_x / self.tile_size)
        tile_y = int(scaled_y / self.tile_size)

        self.add_tile((tile_x, tile_y))

    def add_tile(self, tile_pos):
        #Place or select a tile at the given tile position.
        key = f"{tile_pos[0]};{tile_pos[1]}"
        if key not in self.tile_map:
            self.tile_map[key] = {
                "pos": tile_pos,
                "type": self.default_asset_key,
                "rotate": 1,
                "size_in_tiles": 1,
            }
        else:
            self.selected_tile = self.tile_map[key]

    def render(self):
        #Render everything on screen.
        self.render_tiles()

        self.main_screen.fill((114, 112, 110))
        self.main_screen.blit(self.editor_surface, (0, 0))

    def render_tiles(self):
        #Render the tilemap to the editor surface.
        self.scaled_surface.fill((135, 206, 235))  # Sky blue background

        for tile_data in self.tile_map.values():
            x = tile_data["pos"][0] * self.tile_size
            y = tile_data["pos"][1] * self.tile_size
            tile_image = self.game_assets[tile_data["type"]]
            self.scaled_surface.blit(tile_image, (x, y))

        # Scale up and blit to editor surface
        scaled = pygame.transform.scale(self.scaled_surface, (self.editor_width, self.editor_height))
        self.editor_surface.blit(scaled, (0, 0))


if __name__ == "__main__":
    editor = Editor()
    editor.run()