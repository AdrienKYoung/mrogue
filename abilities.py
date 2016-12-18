import game as main
import consts
import libtcodpy as libtcod
import effects

class Ability:
    def __init__(self, name, description, function, cooldown, targeting = None, range = None, type = None):
        self.name = name
        self.function = function
        self.description = description
        self.cooldown = cooldown
        self.current_cd = 0
        self.targeting = targeting #self, single, burst
        self.range = range
        self.type = type #attack, support, summoning

    def use(self, actor = None):
        if self.current_cd < 1:
            result = self.function(actor)
            self.current_cd = self.cooldown
        else:
            if actor is main.player:
                main.message('{} is on cooldown'.format(self.name), libtcod.red)
            result = 'didnt-take-turn'
        return result

    def on_tick(self):
        if self.current_cd > 0:
            self.current_cd -= 1


class Perk:
    def __init__(self, name, description, requirement=None, category=None):
        self.name = name
        self.description = description
        self.requirement = requirement
        self.category = category


def ability_attack(actor = None):
    x,y = main.target_tile(max_range=1)
    target = None
    for object in main.objects:
        if object.x == x and object.y == y and object.fighter is not None:
            target = object
            break
    if target is not None and target is not main.player:
        result = main.player.fighter.attack(target)
        if result != 'failed':
            return result
    return 'didnt-take-turn'

def ability_attack_reach(actor = None):
    x, y = main.target_tile(max_range=2)
    target = None
    for object in main.objects:
        if object.x == x and object.y == y and object.fighter is not None:
            target = object
            break
    if target is not None and target is not main.player:
        result = main.player.fighter.attack(target)
        if result != 'failed':
            return result
    return 'didnt-take-turn'

def ability_bash_attack(actor = None):
    x,y = main.target_tile(max_range=1)
    target = None
    for object in main.objects:
        if object.x == x and object.y == y and object.fighter is not None:
            target = object
            break
    if target is not None and target is not main.player:
        result = main.player_bash_attack(target)
        if result != 'failed':
            return result
    return 'didnt-take-turn'

def ability_berserk_self(actor = None):
    if actor is not None and actor.fighter is not None:
        if not actor.fighter.has_status('berserk') and not actor.fighter.has_status('exhausted'):
            actor.fighter.apply_status_effect(effects.berserk())
            if actor is not main.player:
                main.message("{} roars!!".format(actor.name),libtcod.red)
        elif actor is main.player:
            main.message("You can't berserk right now.", libtcod.yellow)

data = {
    #item abilities
    'thrust': {
        'name': 'Thrust',
        'description': 'Thrust at an enemy up to 2 spaces away',
        'function': ability_attack_reach,
        'cooldown': 0
    },

    #monster abilities
    'berserk': {
        'name': 'Berserk',
        'function': ability_berserk_self,
        'cooldown': 30,
        'targeting': 'self',
        'type': 'support'
    },
}

default_abilities = [
    Ability('Attack','Attack an enemy',ability_attack,0),
    Ability('Bash','Knock an enemy back',ability_bash_attack,0),
    Ability('Jump','Jump to a tile',main.jump,0)
]

skill_list = [
    Perk('Iron Skin', 'You gain 3 armor while not wearing armor', category='unarmed'),
    Perk('Test0', 'Test0 Description', category='unarmed'),
    Perk('Test1', 'Test1 Description', category='unarmed'),
    Perk('Test2', 'Test2 Description', category='unarmed'),
    Perk('Test3', 'Test3 Description', category='unarmed'),
    Perk('Test4', 'Test4 Description', category='unarmed'),
    Perk('Test5', 'Test5 Description', category='unarmed'),
    Perk('Test6', 'Test6 Description', category='unarmed'),
    Perk('Test7', 'Test7 Description', category='unarmed'),
    Perk('Test8', 'Test8 Description', category='unarmed'),
    Perk('Test9', 'Test9 Description', category='unarmed'),
    Perk('Armored Champion', 'Gain armor for every adjacent enemy if you are wearing armor.', category='armor'),
    Perk('Shield Bash', 'Blocking attacks with a shield has a chance to stun the attacker.', category='shields'),
    Perk('Heavy Blows', 'Your attacks with maces have a chance to shred (doubled for jump attacks)', category='maces'),
    Perk('Pommel Strike', 'Deal reduced damage, but shred armor.', category='swords'),
    Perk("Duelist's Stance", 'Gain increased evasion against enemies you have recently damaged with a sword.', category='swords'),
    Perk('Sweep', 'Attack all enemies around you to a range of 2. Uses a great deal of stamina', category='polearms'),
    Perk('Vitality', 'Healing is 25% more effective.', category='life magic'),
    Perk('Resurrection', 'Upon dying, revive with full health (ONCE).', category='life magic'),
    Perk('Absorb', 'Heal 1-6 HP whenever you gain Life mana.', category='life magic'),
    Perk('Fire Affinity', '5%% chance to conserve fire mana when spending fire mana.', category='fire magic'),
    Perk('Inner Flame', 'Exhaust yourself. Gain 2-4 fire mana.', category='fire magic'),
    Perk('Pyromaniac', 'Gain immunity to burning. Leave a fire trail behind you when you move.', category='fire magic'),
    Perk('Tailwind', 'After you cast an air magic spell, if your next action is a move, it does not cost an action.', category='air magic'),
    Perk('Waterlung', 'Meditating in deep water refills your breath', category='water magic'),
    Perk('Grip of the Depths','Chance to gain water mana whenever an enemy drowns.', category='water magic'),
    Perk('Lichform', 'Sacrifice 50%% of your max HP. Gain immunity to status effects, resistance to all elements, and immunity to dark magic.', category='dark magic'),
    Perk('Judgemental', 'Enemies that cast non-radiant spells within 2 spaces of you take heavy radiant damage.', category='radiant magic'),
    Perk('Endtest1', 'Endtest1 Description', category='radiant magic'),
    Perk('Endtest2', 'Endtest2 Description', category='radiant magic'),
    Perk('Endtest3', 'Endtest3 Description', category='radiant magic'),
]