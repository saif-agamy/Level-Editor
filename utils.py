import pygame 
import os
from Settings import ASSETS_FOLDER_PATH

def load_assets():
    Assets = {}
    #Load and return all tile assets. 
    for file in os.listdir(ASSETS_FOLDER_PATH) :
        if file.endswith(".png"):
            key = os.path.splitext(file)[0]
            img_path = os.path.join(ASSETS_FOLDER_PATH,file)
            Assets[key] = pygame.image.load(img_path).convert()

    return Assets