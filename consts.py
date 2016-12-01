# GAME
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 50
MAP_HEIGHT = 50
LIMIT_FPS = 20
FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
MAX_ROOM_MONSTERS = 6
MAX_ROOM_ITEMS = 2

# GUI panel constants
BAR_WIDTH = 20
INVENTORY_WIDTH = 50
SIDE_PANEL_WIDTH = 24
SIDE_PANEL_HEIGHT = 50
SIDE_PANEL_X = 0
SIDE_PANEL_Y = 0
PANEL_HEIGHT = 8
PANEL_WIDTH = SCREEN_WIDTH - SIDE_PANEL_WIDTH
PANEL_Y = 0
PANEL_X = SIDE_PANEL_WIDTH
MAP_VIEWPORT_WIDTH = SCREEN_WIDTH - SIDE_PANEL_WIDTH
MAP_VIEWPORT_HEIGHT = SCREEN_HEIGHT - PANEL_HEIGHT
MAP_VIEWPORT_X = SIDE_PANEL_WIDTH
MAP_VIEWPORT_Y = PANEL_HEIGHT

# message log constants
MSG_X = 2
MSG_WIDTH = PANEL_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 2
LEVEL_SCREEN_WIDTH = 40
CHARACTER_SCREEN_WIDTH = 30

# SPELLS
HEAL_AMOUNT = 50
LIGHTNING_RANGE = 4
LIGHTNING_DAMAGE = 30
CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8
FIREBALL_RANGE = 6
FIREBALL_DAMAGE = 24
FIREBALL_RADIUS = 2

# COMBAT STATS
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150
EVADE_FACTOR = 50.0
ARMOR_FACTOR = 50.0
BASE_JUMP_RANGE = 2
JUMP_STAMINA_COST = 50
UNARMED_STAMINA_COST = 5
JUMP_ATTACK_ACC_MOD = 0.5
JUMP_ATTACK_DMG_MOD = 2.0
BASH_STAMINA_COST = 20
BASH_ACC_MOD = 1.0
BASH_DMG_MOD = 0.25

# TERRAIN FACTORS
SHALLOW_WATER_COST = 5
DEEP_WATER_COST = 15
STAMINA_REGEN_MOVE = 5
STAMINA_REGEN_WAIT = 25

# MONSTERS
TUNNEL_SPIDER_MAX_WEB_DIST = 8
REEKER_PUFF_MAX = 4
REEKER_PUFF_RADIUS = 3
REEKER_PUFF_DURATION = 6
REEKER_PUFF_DAMAGE = 3
FROG_TONGUE_ACC = 0.75
FROG_TONGUE_DMG = 10
FROG_TONGUE_RANGE = 4
FROG_TONGUE_COOLDOWN = 6
CENTIPEDE_STING_DURATION = 3
CENTIPEDE_STING_AMPLIFICATION = 1.5
BLASTCAP_STUN_DURATION = 4

# MAPGEN
MG_ROOM_MAX_SIZE = 12
MG_ROOM_MIN_SIZE = 6
MG_MAX_ROOMS = 30
MG_CIRCLE_ROOM_MIN_RADIUS = 3
MG_CIRCLE_ROOM_MAX_RADIUS = 6
