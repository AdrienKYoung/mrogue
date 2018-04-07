import libtcodpy as libtcod
import game as main
import ui
import collections
import types
import ai

class NPC:
    def __init__(self, npc_id, dialog_root='meeting_1'):
        self.npc_id = npc_id
        self.dialog_root = dialog_root
        self.active = True

    @property
    def dialog(self):
        return data[self.npc_id]['dialog']
    @property
    def location(self):
        return data[self.npc_id]['location']

    def deactivate(self):
        if hasattr(self, 'owner') and self.owner and self.owner.interact:
            self.owner.interact = None
        self.active = False

    def activate(self):
        if hasattr(self, 'owner'):
            self.owner.interact = start_conversation
        self.active = True

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

def event_recruit_npc(npc_id):
    import player
    if not npc_id in npcs.keys():
        raise Exception('NPC was not found')
    npc = npcs[npc_id]
    if not npc.fighter:
        raise Exception('NPC has no fighter component')
    npc.fighter.team = 'ally'
    npc.fighter.permanent_ally = True
    npc.behavior.follow_target = player.instance
    npc.npc.deactivate()
    npc.npc.location = None
    return 'success'

npcs = {}

data = {
    'npc_herman': {
        'name' : 'Herman of Yorn',
        'char' : '@',
        'color': libtcod.light_sepia,
        'root': 'meeting_1',
        'description': 'A sagely old man with a long gray beard. He wears the faded robes of a Yornish noble.',
        'location' : 'grotto',
        'gender' : 'male',
        'proper_noun' : True,
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
                    "I should be going": 'leave_1',
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
                    '(leave)':end_conversation
                }
            }
        }
    },
    'npc_greta': {
        'name' : 'Greta of Yorn',
        'char' : '@',
        'color' : libtcod.turquoise,
        'root' : 'meeting_1_1',
        'description' : 'A fierce young woman clad in chainmail with a rapier sheathed at her waist.',
        'location' : 'grotto',
        'gender' : 'female',
        'proper_noun' : True,
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
                'text':"\"Hail, exile! I hoped I would see your face again.\"",
                'options':{
                    'Continue':'meeting_2_2',
                }
            },
            'meeting_2_2':{
                'text':"\"I had hoped to cross the river here, but the bridge is out. Has been for about a thousand "
                       "years by the looks of it.\"",
                'options':{
                    'Continue':'meeting_2_3',
                }
            },
            'meeting_2_3':{
                'text':"\"The Gardens lie beyond. Some magic has protected them from the decay of time. It is there I "
                       "can find the herbs I require for my father, I am sure of it.\"",
                'options':{
                    'Continue':'meeting_2_4',
                }
            },
            'meeting_2_4':{
                'text':"\"I just need to find a way across...\"",
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
                    '(leave)':end_conversation
                }
            },
        }
    },
    'npc_rigel':{
        'name': 'Rigel of Astergard',
        'char': '@',
        'color': libtcod.amber,
        'root' : 'meeting_1_1',
        'description' : 'A grizzled mercenary in a worn suit of armor, leaning against a spear',
        'location' : 'crossing',
        'gender' : 'male',
        'proper_noun' : True,
        'dialog' : {
            'meeting_1_1':{
                'event': lambda: change_root('npc_rigel', 'greeting_1'),
                'text':"\"Ho now, what have we here? Some poor wretch washed ashore by the tides of fate?\"",
                'options' : {
                    'Continue' :'meeting_1_2'
                }
            },
            'meeting_1_2':{
                'text':"\"And just look at this one! Why, I'm surprised this island hasn't eaten you up already!\"",
                'options' : {
                    'Continue' : 'meeting_1_3'
                }
            },
            'meeting_1_3':{
                'text':"\"Come, sit, rest awhile. A small one like you will need all your strength if you are to "
                       "survive what is yet to come.\"",
                'options' : {
                    'Continue' : 'greeting_2'
                }
            },
            'greeting_1':{
                'text':"\"What else shall we discuss?\"",
                'options':{
                    'What is your story?' : 'talk_1_1',
                    'I need advice.': 'talk_2_1',
                    'Come fight with me!' : 'recruit_1',
                    'I must be going' : 'leave_1'
                }
            },
            'greeting_2':{
                'text':"\"Let us talk.\"",
                'options':{
                    'What is your story?' : 'talk_1_1',
                    'I need advice.': 'talk_2_1',
                    'Come fight with me!' : 'recruit_1',
                    'I must be going' : 'leave_1'
                }
            },
            'talk_1_1':{
                'text':"\"I am called Rigel. I am a mercenary by trade, and I have seen more battles than you have seen"
                       " summers.\"",
                'options' : {
                    'Continue' : 'talk_1_2'
                }
            },
            'talk_1_2':{
                'text':"\"I traveled far and wide in my campaigns. I have seen the peaks of the Arangs and the great "
                       "cities of Yorn. Yet in all my travels, only one place remained unconquered. \"",
                'options' : {
                    'Continue' : 'talk_1_3'
                }
            },
            'talk_1_3':{
                'text':"\"So here I came. Does that surprise you? Ha! How can I explain to one so young?\"",
                'options' : {
                    'Continue' : 'talk_1_4'
                }
            },
            'talk_1_4':{
                'text':"\"I have seen much in my years, not just nations and battlefields. I have seen men grow old and"
                       " frail. I watched my own father wither and die like a grape on the vine.\"",
                'options' : {
                    'Continue' : 'talk_1_5'
                }
            },
            'talk_1_5':{
                'text':"\"That is not the end I seek. I have spilled seas of blood to keep the reaper at bay. I will "
                       "not lay down my arms and surrender to him while time devours me.\"",
                'options' : {
                    'Continue' : 'talk_1_6'
                }
            },
            'talk_1_6':{
                'text':"\"My place is the battlefield. I was born for it. I will die on it. So lay on, Isle of Dread! "
                       "Give this old soldier the death he has so deserved!\"",
                'options' : {
                    'Continue' : 'greeting_1'
                }
            },
            'talk_2_1':{
                'text':"\"My advice? Well that depends on what you seek.\"",
                'options' : {
                    'Continue' : 'talk_2_2'
                }
            },
            'talk_2_2':{
                'text':"\"If you want to survive for a while? Well that can be done. Bury yourself in a hole somewhere "
                       "and wait to see if death comes first by hunger or by shame.\"",
                'options' : {
                    'Continue' : 'talk_2_3'
                }
            },
            'talk_2_3':{
                'text':"\"But you want more than that? Then the road ahead is not easy. Beneath this cursed ground "
                       "there lies great power. To seek it, you must find your way to the Citadel of the Ancients, "
                       "from whence all the world was once ruled.\"",
                'options' : {
                    'Continue' : 'talk_2_4'
                }
            },
            'talk_2_4':{
                'text':"\"But the citadel looms above the imperial city, beyond the gates. There the Blind Sentinel "
                       "keeps his post. Passage to the city will not be possible unless you can restore to him his "
                       "lost sight.\"",
                'options' : {
                    'Continue' : 'talk_2_5'
                }
            },
            'talk_2_5':{
                'text':"\"Or so I was told, many years ago. It is difficult to find knowledge about an island from "
                       "whence no one returns. We have only myths and legends to serve as guides. Heed them well.\"",
                'options' : {
                    'Continue' : 'greeting_1'
                }
            },
            'recruit_1':{
                'text':"\"For you? Ha! Charity is no virtue of the mercenary, small one. What have you for me in "
                       "exchange for my service?\"",
                'options': {
                    'Give treasure':lambda: ui.buy(lambda :event_recruit_npc('npc_rigel'),'treasure','success_1', 'greeting_1'),
                    'Never mind':'greeting_1'
                }
            },
            'success_1':{
                'text':"\"Superb! Yes, this will do nicely. You have my spear at your service, young one. "
                       "To battle!\"",
                'options' : {
                    'Leave' : end_conversation
                }
            },
            'leave_1':{
                'text':"\"Watch yourself out there, young one, or you won't last long! Ha!\"",
                'options' : {
                    'Leave' : end_conversation
                }
            }
        }
    }
}

fighters = {
    'npc_rigel': {
        'hp': 250,
        'strength_dice' : '2d24',
        'armor': 0,
        'evasion': 3,
        'will': 14,
        'fortitude': 18,
        'accuracy': 32,
        'move_speed': 1.0,
        'attack_speed': 0.95,
        'ai': ai.AI_Default,
        'description': 'A grizzled mercenary in a worn suit of armor, his spear held at the ready',
        'loot_level':2,
        'equipment': [
            {'weapon_spear':100},
            {'equipment_plate_armor':100},
            {'equipment_armet_helm':100},
            {'equipment_gauntlets': 100},
            {'equipment_greaves': 100}],
        'shred': 2,
        'subtype':'homunculus',
        'team' : 'neutral',
    },
}