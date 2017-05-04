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
                'text':"Greeting 1",
                'options':{
                    'Shop':'shop_1',
                    'Talk':'talk_1',
                    'Leave':'leave_1'
                }
            },
            'talk_1':{
                'text':"Talk 1",
                'options' : {
                    'Continue':'greeting_1'
                }
            },
            'shop_1':{
                'text':"Shop 1",
                'options': {
                    'holy symbol':lambda: ui.buy('charm_holy_symbol','treasure','leave_1','leave_1')
                }
            },
            'success_1':{
                'text':"Talk 1",
                'options' : {
                    'Continue':'greeting_1'
                }
            },
            'leave_1':{
                'text':"Leave 1",
                'options' : {
                    'Continue':end_conversation
                }
            }
        }
    }
}