import libtcodpy as libtcod
import game as main
import ui
import collections
import types

class NPC:
    def __init__(self, dialog, dialog_root, location):
        self.dialog = dialog
        self.dialog_root = dialog_root
        self.location = location

def start_conversation(target, actor):
    if target.npc is None:
        raise Exception('Tried to talk to non npc')

    npc = target.npc
    state = npc.dialog[npc.dialog_root]
    if state.get('event') is not None and callable(state['event']):
        state['event']()

    while state != 'end_conversation' and state is not None:
        if callable(state):
            state = state()
        if isinstance(state,types.StringTypes):
            if state in npc.dialog:
                state = npc.dialog[state]
            else:
                break
        if isinstance(state,list) or isinstance(state,tuple):
            state = main.random_entry(state)
        else:
            keys = state['options'].keys()
            selection = ui.menu(target.name + '\n\n' + state['text'],keys, width=45)
            if selection is not None:
                state = state['options'][ keys[selection] ]
            else:
                break

    return 'success'

def end_conversation():
    return 'end_conversation'

def change_root(npc, new_root):
    if npc in npcs.keys() and hasattr(npcs[npc], 'npc'):
        npcs[npc].npc.dialog_root = new_root

def change_location(npc, new_location):
    if npc in npcs.keys() and hasattr(npcs[npc], 'npc'):
        npcs[npc].npc.location = new_location

def event_leave_grotto():
    change_root('npc_herman', 'greeting_2')
    change_root('npc_greta', 'meeting_2_1')
    change_location('npc_greta', 'crossing')
    return 'one-off'

npcs = {}

data = {
    'npc_herman': {
        'name' : 'Herman of Yorn',
        'char' : '@',
        'color': libtcod.light_sepia,
        'root': 'meeting_1',
        'description': 'A sagely old man with a long gray beard. He wears the faded robes of a Yornish noble.',
        'location' : 'grotto',
        'dialog': {
            'meeting_1':{
                'event': lambda: change_root('npc_herman', 'greeting_1'),
                'text':"\"I say, I must admit I was not expecting visitors here. I sealed this cavern seeking refuge "
                       "from the mad beasts and monsters of the island, and for three years that seal has held. Who are"
                       " you, that enters this sanctuary? Some foul demon from the pits?\"",
                'options':{
                    'Continue':'meeting_2'
                }
            },
            'meeting_2':{
                'text':"\"Ah, no, I do not see that fury in your eyes. This isle has yet to take its hold of you. If "
                       "you come in peace, you are welcome here. Friends are rare in this cursed place. I am called "
                       "Herman. Yonder is my daughter Greta. We are at your service.\"",
                'options':{
                    "I've come to trade":'shop_1',
                    "I should be going (leave)": 'leave_1',
                    "I'd like to ask you something...": 'talk_hub'
                }
            },
            'greeting_1':{
                'text':"\"How can I assist you, friend?\"",
                'options':{
                    "I've come to trade":'shop_1',
                    "I should be going (leave)": 'leave_1',
                    "I'd like to ask you something...": 'talk_hub'
                }
            },
            'greeting_2':{
                'event': lambda: change_root('npc_herman', 'greeting_1'),
                'text':"\"Welcome back, my friend. I am glad to see you still alive.\"",
                'options':{
                    "I've come to trade":'shop_1',
                    "I should be going (leave)": 'leave_1',
                    "I'd like to ask you something...": 'talk_hub_2'
                }
            },
            'greeting_3':{
                'text':"\"Is there something else that interests you?\"",
                'options':{
                    "I've come to trade":'shop_1',
                    "I should be going (leave)": 'leave_1',
                    "I'd like to ask you something...": 'talk_hub'
                }
            },
            'talk_hub':{
                'text':"\"Of course. What would you like to know?\"",
                'options' : {
                    'What is this place?':'talk_1_1',
                    'What fate brings you here?':'talk_2_1'
                }
            },
            'talk_hub_2':{
                'text':"\"Of course. What would you like to know?\"",
                'options' : {
                    'What is this place?':'talk_1_1',
                    'What fate brings you here?':'talk_2_1',
                    'Where is Greta?':'talk_3_1'
                }
            },
            'talk_1_1':{
                'text':"\"This island? You know it as the Isle of Dread, but it was not always such. The curse on this"
                       " island was placed by the Gods themselves as punishment for wicked deeds.\"",
                'options' : {
                    'Continue':'talk_1_2'
                }
            },
            'talk_1_2':{
                'text':"\"In ancient times there was an empire that spanned globe. It's capital was here, on this "
                       "island. The ruins of that evil city lie North of here.\"",
                'options' : {
                    'Continue':'greeting_3'
                }
            },
            'talk_2_1':{
                'text':"\"Me? Ah, my story is a sad one. You see me now at my lowest point, after my fall from the "
                       "graces of the Queen. I was accused of treason, and banished to the Isle of Dread.\"",
                'options' : {
                    'Continue':'talk_2_2'
                }
            },
            'talk_2_2':{
                'text':"\"This alone I could have endured, but the Gods saw fit to test me further. My daughter "
                       "Greta, upon hearing my fate, took to arms against the Queen's men to save me from it.\"",
                'options' : {
                    'Continue':'talk_2_3'
                }
            },
            'talk_2_3':{
                'text':"\"But as skilled a warrior as she is, she was overcome. Now she, too, is banished here. Alas! "
                       "I would have gladly walked to the gallows if it meant my Greta could be free!\"",
                'options' : {
                    'Continue':'greeting_3'
                }
            },
            'talk_3_1':{
                'text':"\"Greta, that willful girl, has gone from here. She said she left for the river in search of"
                       " medicine. Gods, protect her when I cannot!\"",
                'options' : {
                    'Continue':'greeting_3'
                }
            },
            'shop_1':{
                'text':"\"I don't have much, I'm afraid. Does anything catch your eye?\"",
                'options': {
                    'Holy Symbol':lambda: ui.buy('charm_holy_symbol','treasure','success_1','greeting_1'),
                    'Prayer Beads':lambda: ui.buy('charm_prayer_beads','treasure','success_1','greeting_1'),
                    'Elixir of Life':lambda: ui.buy('elixir_life','treasure','success_1','greeting_1'),
                    'Back':'greeting_3'
                }
            },
            'success_1':{
                'text':"\"A fair trade. May it serve you better than it has served me.\"",
                'options' : {
                    'Continue':'greeting_3'
                }
            },
            'leave_1':{
                'text':"\"Safe travels, friend. May we meet again.\"",
                'options' : {
                    'Continue':end_conversation
                }
            }
        }
    },
    'npc_greta': {
        'name' : 'Greta',
        'char' : '@',
        'color' : libtcod.turquoise,
        'root' : 'meeting_1_1',
        'description' : 'A fierce young woman clad in chainmail with a rapier sheathed at her waist.',
        'location' : 'grotto',
        'dialog' : {
            'meeting_1_1':{
                'event': lambda: change_root('npc_greta', 'greeting_1'),
                'text':"\"Who goes there? You look to be a fellow exile. Fell foul of the tyrant Queen, did you? Well, "
                       "you're in good company!\"",
                'options':{
                    'Continue':'meeting_1_2',
                }
            },
            'meeting_1_2':{
                'text':"\"It's been so long since I've seen another face (save my father's). How did you find your way "
                       "here?\"",
                'options':{
                    'Continue':'meeting_1_3',
                }
            },
            'meeting_1_3':{
                'text':"\"Ah, no matter. What matters is that the seal has been broken. I must leave here, there is "
                       "much to do!\"",
                'options':{
                    'May I ask you something?':'talk_hub',
                    'Farewell' : 'leave_1'
                }
            },
            'meeting_2_1':{
                'event': lambda: change_root('npc_greta', 'greeting_1'),
                'text':"\"Hail, exile! I am glad to see your face again.\"",
                'options':{
                    'Continue':'greeting_1',
                }
            },
            'greeting_1':{
                'text':"\"How do you fare?\"",
                'options':{
                    'May I ask you something?':'talk_hub',
                    'Farewell.' : 'leave_1'
                }
            },
            'greeting_2':{
                'text':"\"Something else?\"",
                'options':{
                    'May I ask you something?':'talk_hub',
                    'Farewell.' : 'leave_1'
                }
            },
            'talk_hub':{
                'text': '\"Indeed! Ask me what?\"',
                'options': {
                    'Who are you?': 'talk_1_1',
                    'Where are you off to?': 'talk_2_1'
                }
            },
            'talk_1_1':{
                'text':"\"Ah yes, how rude of me. I am Greta, daughter of Herman. Pleased to make your acquaintance, "
                       "exile. I was banished here with my father three years ago.\"",
                'options': {
                    'Continue': 'greeting_2',
                }
            },
            'talk_2_1':{
                'text':"\"My father is falling ill. He would never admit it, but I always notice these things. I've "
                       "been staying here to care for him, but I can help him no further without proper medicine.\"",
                'options': {
                    'Continue': 'talk_2_2',
                }
            },
            'talk_2_2':{
                'text':"\"Now that you've broken the seal, I am free to leave here. I think I heard a river north of "
                       "here - that will be a good place to start. Maybe I'll see you there, exile.\"",
                'options': {
                    'Continue': 'greeting_2',
                }
            },
            'leave_1':{
                'text': "\"And to you, exile! Our paths will cross again.\"",
                'options' : {
                    'Continue':end_conversation
                }
            },
        }
    }
}