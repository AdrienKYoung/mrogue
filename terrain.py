import consts
import libtcodpy as libtcod

class TileData:

    def __init__(self, blocks, blocks_sight, name, char,
                 foreground_color, background_color, description='unremarkable terrain', stamina_cost=0, jumpable=True,
                 burnTemp=0, flammable=False, diggable=False, isWall = False, isFloor = False, isWater = False,
                 isRamp=False, isPit=False):
        self.blocks = blocks
        self.blocks_sight = blocks_sight
        self.name = name
        self.char = char
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.description = description
        self.stamina_cost = stamina_cost
        self.jumpable = jumpable
        self.burnTemp = burnTemp
        self.flammable = flammable
        self.diggable = diggable
        self.isWall = isWall
        self.isFloor = isFloor
        self.isWater = isWater
        self.isRamp = isRamp
        self.isPit = isPit

data = {
    'stone floor': TileData(False, False, 'stone floor', '.', (128, 96, 0), (64, 48, 0),
                             'the cold, cobblestone dungeon floor', isFloor=True),
    'stone wall': TileData(True, True, 'stone wall', '#', (255, 191, 0), (191, 143, 0),
                             'the sturdy masonry of the dungeon walls', diggable=True, isWall=True),
    'damp soil': TileData(False, False, 'damp soil', '.', (128, 96, 0), (64, 48, 0),
                             'damp, loamy soil crawling with worms and insects', isFloor=True),
    'mossy stone wall': TileData(True, True, 'mossy stone wall', '#', (255, 191, 0), (191, 143, 0),
                             'a crumbling stone cliff overgrown with moss, ferns and vines', diggable=True, isWall=True),
    'shale': TileData(False, False, 'shale', '.', (48, 48, 48), (31, 31, 31),
                             'broken shingles of flat, smooth stone', isFloor=True),
    'dark shale wall': TileData(True, True, 'dark shale wall', '#', (96, 96, 96), (64, 64, 64),
                             'a sheer cliff of blackened stone', diggable=True, isWall=True),
    'wooden palisade': TileData(True, True, 'wooden palisade', '#', (94, 75, 47), (31, 24, 15),
                             'a barrier crafted from dry wooden posts lashed together with rope',
                             diggable=True, isWall=True, flammable=True),
    'gnarled tree': TileData(True, True, 'gnarled tree', chr(157), (94, 75, 47), (31, 31, 31),
                             'a twisted, leafless tree, worn down by the gritty winds of the badlands', flammable=True, isWall=True),
    'sand': TileData(False, False, 'sand', '.', (158, 134, 100), (127, 101, 63),
                             'fine, damp sand', isFloor=True),
    'sea cliff': TileData(True, True, 'sea cliff', '#', (63, 50, 31), (31, 24, 15),
                             'a jagged outcropping of briny rock', diggable=True, isWall=True),
    'shallow water': TileData(False, False, 'shallow water', 247, (0, 95, 191), (0, 64, 128),
                             'a shallow pool of grimy water', consts.SHALLOW_WATER_COST, isWater=True),
    'deep water': TileData(False, False, 'deep water', 247, (0, 64, 128), (0, 32, 64),
                             'a deep pool of grimy water', consts.DEEP_WATER_COST, jumpable=False, isWater=True),
    'shallow seawater': TileData(False, False, 'shallow water', 247, (0, 95, 191), (0, 64, 128),
                             'foamy saltwater, rolled ashore by the gentle waves', consts.SHALLOW_WATER_COST, isWater=True),
    'deep seawater': TileData(False, False, 'deep water', 247, (0, 64, 128), (0, 32, 64),
                             'vast depths of seawater, rolling with the tide', consts.DEEP_WATER_COST, jumpable=False, isWater=True),
    'mud': TileData(False, False, 'mud', 247, (94, 75, 47), (63, 50, 31),
                             'a thick puddle of mud that impedes movement - dodging attacks will be much more difficult here', consts.MUD_COST, isWater=True),
    'lava': TileData(False,False,'lava',247,libtcod.yellow,libtcod.dark_red,'Boiling molten stone',consts.DEEP_WATER_COST,jumpable=True),
    'chasm': TileData(False, False, 'chasm', libtcod.CHAR_BLOCK1, (16, 16, 32), (0, 0, 16),
                             'a pit descending into darkness', isPit=True),
    'grass floor': TileData(False, False, 'grass floor', ',', (4, 140, 13), (29, 71, 10),
                             'a grass consisting of strange mossy tufts. Though damp to the touch, this grass has been known to fuel wildfires with surprising vigor.', flammable=True, isFloor=True),
    'dry grass': TileData(False, False, 'dry grass', ',', (56, 49, 43), (38, 33, 29),
                             'dry stalks of grass that rustle in the wind. Might they burn?', flammable=True, isFloor=True),
    'scorched floor': TileData(False, False, 'scorched floor', '.', (94, 55, 55), (30, 30, 30),
                             'embers linger on this still-warm floor scorched by flame', isFloor=True),
    'stone ramp': TileData(False, False, 'ramp', '/', (128, 96, 0), (64, 48, 0),
                             'a ramp', isRamp=True),
    'shale slope': TileData(False, False, 'shale slope', '/', (48, 48, 48), (31, 31, 31),
                             'a smooth slope of shale', isRamp=True),
    'frozen soil': TileData(False, False,'frozen soil','.',(128, 96, 0), (20, 20, 20),'Soil packed hard by frost',
                            isFloor=True),
    'frozen slope': TileData(False, False,'frozen soil','/',(128, 96, 0), (20, 20, 20),'A slope of frosty earth',
                            isRamp=True),
    'snow drift': TileData(False, False, 'snow drift', '~', libtcod.white, libtcod.light_gray,
                             'pristine, waist deep powdered snow. It will be difficult to move through until it has been crushed down.',
                           consts.SNOW_COST, isFloor=True),
    'snowy ground': TileData(False, False, 'snow drift', '.', libtcod.white, libtcod.sepia,
                             'trampled snow, mixed with dirt', isFloor=True),
    'snowy slope': TileData(False, False, 'snowy slope', '/', libtcod.white, libtcod.sepia,
                             'a slope covered in snow', isRamp=True),
    'barren tree': TileData(True, True, 'barren tree', chr(157), libtcod.sepia,libtcod.white,
                             'a frozen, barren tree', flammable=True, isWall=True),
    'pine tree': TileData(True, True, 'pine tree', libtcod.CHAR_ARROW2_N, libtcod.darkest_green,libtcod.white,
                             'a pine tree, its needles ever green', flammable=True, isWall=True),
}

# flags
FLAG_NO_DIG = 1
