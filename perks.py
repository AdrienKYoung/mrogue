import player

class Perk:
    def __init__(self, name, description, category=None, on_tick=None, requirements_fnc=None, requirements_str='No Requirements', sp_cost=20):
        self.name = name
        self.description = description
        self.category = category
        self.on_tick = on_tick
        self.requirements_fnc = requirements_fnc
        self.requirements_str = requirements_str
        self.sp_cost = sp_cost

    def on_tick(self):
        if self.on_tick:
            self.on_tick()

    def meets_requirements(self):
        if player.instance.skill_points < self.sp_cost:
            return False #Not enough SP
        if self.requirements_fnc:
            return self.requirements_fnc
        else:
            return True  # Default to True if no requirements

list = [
    Perk('Iron Skin', 'You gain 3 armor while not wearing armor', category='unarmed', requirements_str='Level 2'),
    #Perk('Test0', 'Test0 Description', category='unarmed'),
    #Perk('Test1', 'Test1 Description', category='unarmed'),
    #Perk('Test2', 'Test2 Description', category='unarmed'),
    #Perk('Test3', 'Test3 Description', category='unarmed'),
    #Perk('Test4', 'Test4 Description', category='unarmed'),
    #Perk('Test5', 'Test5 Description', category='unarmed'),
    #Perk('Test6', 'Test6 Description', category='unarmed'),
    #Perk('Test7', 'Test7 Description', category='unarmed'),
    #Perk('Test8', 'Test8 Description', category='unarmed'),
    #Perk('Test9', 'Test9 Description', category='unarmed'),
    Perk('Armored Champion', 'Gain armor for every adjacent enemy if you are wearing armor.', category='armor'),
    Perk('Shield Bash', 'Blocking attacks with a shield has a chance to stun the attacker.', category='shields'),
    Perk('Heavy Blows', 'Your attacks with maces have a chance to shred (doubled for jump attacks)', category='maces'),
    Perk('Pommel Strike', 'Deal reduced damage, but shred armor.', category='swords'),
    Perk("Duelist's Stance", 'Gain increased evasion against enemies you have recently damaged with a sword.', category='swords'),
    Perk('Sweep', 'Attack all enemies around you to a range of 2. Uses a great deal of stamina', category='polearms'),
    Perk('Vitality', 'Healing is 25% more effective.', category='life magic'),
    Perk('Resurrection', 'Upon dying, revive with full health (ONCE).', category='life magic'),
    Perk('Absorb', 'Heal 1-6 HP whenever you gain Life essence.', category='life magic'),
    Perk('Fire Affinity', '5%% chance to conserve fire essence when spending fire essence.', category='fire magic'),
    Perk('Inner Flame', 'Exhaust yourself. Gain 2-4 fire essence.', category='fire magic'),
    Perk('Pyromaniac', 'Gain immunity to burning. Leave a fire trail behind you when you move.', category='fire magic'),
    Perk('Tailwind', 'After you cast an air magic spell, if your next action is a move, it does not cost an action.', category='air magic'),
    Perk('Waterlung', 'Meditating in deep water refills your breath', category='water magic'),
    Perk('Grip of the Depths','Chance to gain water essence whenever an enemy drowns.', category='water magic'),
    Perk('Lichform', 'Sacrifice 50%% of your max HP. Gain immunity to status effects, resistance to all elements, and immunity to dark magic.', category='dark magic'),
    Perk('Judgemental', 'Enemies that cast non-radiant spells within 2 spaces of you take heavy radiant damage.', category='radiant magic'),
    #Perk('Endtest1', 'Endtest1 Description', category='radiant magic'),
    #Perk('Endtest2', 'Endtest2 Description', category='radiant magic'),
    #Perk('Endtest3', 'Endtest3 Description', category='radiant magic'),
]