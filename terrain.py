import consts
import libtcodpy as libtcod

class TileData:

    def __init__(self, blocks, blocks_sight, name, char,
                 foreground_color, background_color, description='unremarkable terrain', stamina_cost=0, jumpable=True):
        self.blocks = blocks
        self.blocks_sight = blocks_sight
        self.name = name
        self.char = char
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.description = description
        self.stamina_cost = stamina_cost
        self.jumpable = jumpable

data = {
    'stone floor': TileData(False, False, 'stone floor', '.', (128, 96, 0), (64, 48, 0),
                             'the cold, cobblestone dungeon floor'),
    'stone wall': TileData(True, True, 'stone wall', '#', (255, 191, 0), (191, 143, 0),
                             'the sturdy masonry of the dungeon walls'),
    'shallow water': TileData(False, False, 'shallow water', '~', (0, 95, 191), (0, 64, 128),
                             'a shallow pool of grimy water', consts.SHALLOW_WATER_COST),
    'deep water': TileData(False, False, 'deep water', '~', (0, 64, 128), (0, 32, 64),
                             'a deep pool of grimy water', consts.DEEP_WATER_COST, False),
    'chasm': TileData(True, False, 'chasm', libtcod.CHAR_BLOCK1, (16, 16, 32), (0, 0, 16),
                             'a pit descending into darkness')
}
