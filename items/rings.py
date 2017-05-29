import libtcodpy

table = {
    'equipment_ring_of_stamina': {
        'name'          : 'Ring of Stamina',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : "A jade ring with the image of an oxen carved around it."
                          "Slowly regenerates its wearer's stamina over time",
        'stamina_regen' : 2
    },
    'equipment_ring_of_waterbreathing': {
        'name'          : 'Ring of Waterbreathing',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : 'A pink coral ring. Grants its wearer immunity to drowning.',
    },
    'equipment_ring_of_evasion': {
        'name'          : 'Ring of Evasion',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : "A thin band of silver set with an engraving of a cat."
                          "Enhances its wearer's dodging ability.",
        "evasion_bonus" : 4,
    },
    'equipment_ring_of_accuracy': {
        'name'          : 'Ring of Accuracy',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : "A copper ring set with a glass eye. Enhances its wearer's ability to hit targets.",
        'accuracy'      : 20,
    },
    'equipment_ring_of_mending': {
        'name'          : 'Ring of Mending',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : 'A ring composed of two halves joined together: one polished wood, the other hammered iron. '
                          'Reduces the amount of time it takes to repair shredded armor.',
    },
    'equipment_ring_of_vampirism': {
        'name'          : 'Ring of Vampirism',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : 'A bone ring lined with needles that dig into your flesh, drawing blood. Killing living '
                          'creatures while wearing it will heal you slightly.',
    },
    'equipment_ring_of_tenacity': {
        'name'          : 'Ring of Tenacity',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : "A simple brass ring that glows red when its wearer is near death. "
                          "Heals you over time as long as your health is low.",
    },
    'equipment_ring_of_fortitude': {
        'name'          : 'Ring of Fortitude',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : 'A stone ring carved with images of walls and castles. '
                          'Reduces the duration of hostile status effects.',
    },
    'equipment_ring_of_rage': {
        'name'          : 'Ring of Rage',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : 'A ring of braided hairs and strung with teeth. Taking damage while wearing this ring '
                          'will sometimes cause its wearer to enter a berserk rage.',
    },
    'equipment_ring_of_vengeance': {
        'name'          : 'Ring of Vengeance',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : 'A golden ring set with a skull cast in silver. '
                          'Enemies that damage the wearer of this ring will be cursed, reducing their defenses.',
    },
    'equipment_ring_of_burdens': {
        'name'          : 'Ring of Burdens',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : 'A thick pewter ring stamped with the likeness of a mule. Increases your equip load.',
        'weight'        : -10,
    },
    'equipment_ring_of_alchemy': {
        'name'          : 'Ring of Alchemy',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : 'A dull lead ring that transforms to a lustrous gold when slipped onto a finger. '
                          'While equipped, gems will give their opposite essence, if possible.',
    },
    'equipment_ring_of_poison_immunity': {
        'name'          : 'Ring of Poison Immunity',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : 'A silver ring in the shape of a serpent eating its own tail. '
                          'Protects is wearer from the effects of poison.',
        'immunities'    : ['poisoned']
    },
    'equipment_ring_of_freedom': {
        'name'          : 'Ring of Freedom',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : 'An alabaster ring set with a silver image of a bird in flight. '
                          'Grants immunity to movement-impairing effects.',
        'immunities'    : ['immobilized', 'displacement']
    },
    'equipment_ring_of_salvation': {
        'name'          : 'Ring of Salvation',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : 'A golden ring said to have been made by the Martyr herself. '
                          'This ring has the power to protect its wearer from death, but only once.',
    },
    'equipment_ring_of_blessings': {
        'name'          : 'Ring of Blessings',
        'category'      : 'accessory',
        'char'          : chr(147),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'ring',
        'description'   : 'A simple silver band set with a holy symbol. '
                          'Protects its wearer from curses, judgement, and doom.',
        'immunities'    : ['cursed', 'doom', 'judgement']
    },
}
