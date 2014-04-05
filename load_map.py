import json

def load_map(map_filename): # Load a map from a map file

    #map_f = open(map_filename, 'r')
    data = json.load(open(map_filename))

    width = data['tileswide']
    height = data['tileshigh']

    
    #for i in range(0:width):
    #    for j in range(0:height):
    #        tilegrid[i,j] = data['tiles']['x']['y']['tile']

    
    
    tile_map = data['layers'][0]['tiles']

    grid = [[0 for i in range(width)] for j in range(height)]
        
    for tile in tile_map:
        x = tile['x']
        y = tile['y']
        grid[x][y] = tile['tile']

    #print grid

    return grid
