import libtcodpy as libtcod
import game as main
import ui
import collections
import types

class NPC:
    def __init__(self, dialog, dialog_root):
        self.dialog = dialog
        self.dialog_root = dialog_root

def start_conversation(target, actor):
    if target.npc is None:
        raise Exception('Tried to talk to non npc')

    npc = target.npc
    state = npc.dialog[npc.dialog_root]

    while state != 'end_conversation' and state is not None:
        print state
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
            selection = ui.menu(state['text'],keys)
            if selection is not None:
                state = state['options'][ keys[selection] ]
            else:
                break

    return 'success'

def end_conversation():
    return 'end_conversation'

data = {
    'npc_hermit': {
        'name' : 'Shrine Hermit',
        'char' : 'H',
        'color': libtcod.light_sepia,
        'root': 'greeting_1',
        'description': 'A hunched figure hidden under ragged robes',
        'dialog': {
            'greeting_1':{
                'text':"Come to bring me something nice?",
                'options':{
                    'Shop':'shop_1',
                    'Talk':'talk_1',
                    'Leave':'leave_1'
                }
            },
            'talk_1':{
                'text':"Much time has passed since another's footsteps echoed on these stones.",
                'options' : {
                    'Continue':'talk_2'
                }
            },
            'talk_2':{
                'text':"Such silence is sacred in this forsaken land.",
                'options' : {
                    'Continue':'greeting_1'
                }
            },
            'shop_1':{
                'text':"I'll give you one of these for something nice.",
                'options': {
                    'holy symbol':lambda: ui.buy('charm_holy_symbol','treasure','success_1','greeting_1'),
                    'Back':'greeting_1'
                }
            },
            'success_1':{
                'text':"Yes, perfect! Enjoy your trinket.",
                'options' : {
                    'Continue':'greeting_1'
                }
            },
            'leave_1':{
                'text':"Fare thee well then.",
                'options' : {
                    'Continue':end_conversation
                }
            }
        }
    }
}