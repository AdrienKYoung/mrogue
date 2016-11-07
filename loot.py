import libtcodpy
import spells

table = {
    'default': ['spell_lightning',None]
}

proto = {
    'spell_lightning': {
        'name': 'Lightning Bolt',
        'char': '/',
        'on_use': spells.cast_lightning,
        'color': libtcodpy.yellow,
        'type': 'spell'
    }
}