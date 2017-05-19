#part of mrogue, an interactive adventure game
#Copyright (C) 2017 Adrien Young and Tyler Soberanis
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import log
import collections
import string

class PlayerStats:

    def __init__(self, int=10, wiz=10, str=10, agi=10, con=10):
        self.base_int = int
        self.base_wiz = wiz
        self.base_str = str
        self.base_agi = agi
        self.base_con = con

    @property
    def int(self):
        return self.base_int

    @property
    def wiz(self):
        return self.base_wiz

    @property
    def str(self):
        return self.base_str

    @property
    def agi(self):
        return self.base_agi

    @property
    def con(self):
        return self.base_con

    @property
    def max_essence(self):
        return 1 + int(math.floor(self.wiz / 4))

loadouts = {
    'warrior' : {
        'str':12,
        'agi':10,
        'int':6,
        'spr':10,
        'con':12,
        'inventory':[
            ['weapon_longsword','weapon_hatchet','weapon_mace'],
            'charm_raw',
            'shield_wooden_buckler',
            'equipment_leather_armor',
            'equipment_iron_helm'
        ],
        'description' : "Balanced melee fighter. Starts with good weapon and armor."
    },
    'rogue' : {
        'str':10,
        'agi':14,
        'int':8,
        'spr':9,
        'con':8,
        'inventory':[
            'charm_raw',
            'weapon_dagger',
            'equipment_leather_armor',
            'glass_key',
            'weapon_crossbow'
        ],
        'description' : "Nimble melee fighter. Starts with excellent agility."
    },
    'wanderer' : {
        'str':12,
        'agi':12,
        'int':10,
        'spr':14,
        'con':12,
        'inventory':[
            'charm_raw',
        ],
        'description' : "Generalist class with great stats, especially spirit. Starts with no gear."
    },
    'fanatic' : {
        'str':13,
        'agi':9,
        'int':10,
        'spr':10,
        'con':9,
        'inventory':[
            ['book_lesser_death'],
            'charm_raw',
            'weapon_coal_mace'
        ],
        'description' : "Melee magic caster. Starts with a tome, no armor and a mace."
    },
    'wizard' : {
        'str':6,
        'agi':8,
        'int':12,
        'spr':10,
        'con':8,
        'inventory':[
            ['book_lesser_cold', 'book_lesser_fire', 'book_lesser_life'],
            'charm_raw',
            #'charm_farmers_talisman',
            #'charm_holy_symbol',
            #'charm_shard_of_creation',
            #'charm_volatile_orb',
            #'charm_elementalists_lens',
            #'charm_primal_totem',
            #'charm_prayer_beads',
            'equipment_cloth_robes',
            'gem_lesser_fire',
            'gem_lesser_water',
            'gem_lesser_earth',
            'gem_lesser_air',
            'gem_lesser_cold',
            'gem_lesser_life',
            'gem_lesser_arcane',
            'gem_lesser_radiance',
            'gem_lesser_death'
        ],
        'description' : "Fragile in melee, but have access to powerful offensive magic. "
                        "Starts with a tome."
    },
}

instance = None
is_meditating = False

def create(loadout):
    global instance

    loadout = loadouts[loadout]
    fighter_component = combat.Fighter(hp=100, stamina=100, death_function=on_death, on_get_hit=on_get_hit,
                                       on_get_kill=on_get_kill, team='ally', evasion=5)
    instance = main.GameObject(25, 23, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component,
                        player_stats=PlayerStats(int(loadout['int']),int(loadout['spr']),int(loadout['str']),
                        int(loadout['agi']),int(loadout['con'])), description='An exile, banished to this forsaken '
                        'island for your crimes. This place will surely be your grave.',
                        movement_type=pathfinding.NORMAL, on_tick=on_tick)
    instance.level = 1
    instance.essence = []
    instance.known_spells = []
    instance.action_queue = []
    instance.skill_points = 20
    instance.skill_point_progress = 0
    instance.fighter.xp = 0
    instance.perk_abilities = []
    if consts.DEBUG_INVINCIBLE:
        instance.fighter.apply_status_effect(effects.invulnerable(duration=None))

    for item in loadout['inventory']:
        i = None
        prototype = item
        if not isinstance(item,basestring):
            idx = ui.menu("Choose a starting item",[string.capwords(items.table()[a]['name']) for a in item],30,x_center=consts.SCREEN_WIDTH / 2)
            if idx is None:
                return 'cancelled'
            prototype = item[idx]

        if 'weapon' in prototype:
            i = main.create_item(prototype, material='iron', quality='')
        elif 'equipment' in prototype or 'shield' in prototype:
            i = main.create_item(prototype, material='', quality='')
        else:
            i = main.create_item(prototype)

        instance.fighter.inventory.append(i)
        i.item.holder = instance
        if i.equipment is not None:
            i.equipment.equip(no_message=True)

    if consts.DEBUG_STARTING_ITEM is not None:
        test = main.create_item(consts.DEBUG_STARTING_ITEM)
        instance.fighter.inventory.append(test)
    return 'success'

def handle_keys():

    game_state = main.game_state
    key = main.key
    mouse = main.mouse

    ui.mouse_select_monster()

    if key.vk == libtcod.KEY_CHAR:
        key_char = chr(key.c)
    else:
        key_char = None

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key_char == 'q' and key.shift:
        return 'exit'  #exit game

    log.info("INPUT","Key input: {}",[key_char])

    if game_state == 'playing':

        if instance.fighter:
            if instance.fighter.has_status('stunned'):
                return 'stunned'
            if instance.fighter.has_status('frozen'):
                return 'frozen'

        if instance.action_queue is not None and len(instance.action_queue) > 0:
            action = instance.action_queue[0]
            instance.action_queue.remove(action)
            do_queued_action(action)
            return action

        moved = False
        ctrl = key.lctrl or key.rctrl
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            moved = move_or_attack(0, -1, ctrl)
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            moved = move_or_attack(0, 1, ctrl)
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            moved = move_or_attack(-1, 0, ctrl)
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            moved = move_or_attack(1, 0, ctrl)
        elif key.vk == libtcod.KEY_KP7 or key_char == 'y':
            moved = move_or_attack(-1, -1, ctrl)
        elif key.vk == libtcod.KEY_KP9 or key_char == 'u':
            moved = move_or_attack(1, -1, ctrl)
        elif key.vk == libtcod.KEY_KP1 or key_char == 'h':
            moved = move_or_attack(-1, 1, ctrl)
        elif key.vk == libtcod.KEY_KP3 or key_char == 'j':
            moved = move_or_attack(1, 1, ctrl)
        elif key.vk == libtcod.KEY_KP5 or key_char == 's':
            instance.fighter.adjust_stamina(consts.STAMINA_REGEN_WAIT) # gain stamina for standing still
            moved = True  # so that this counts as a turn passing
            pass
        else:
            if key.vk == libtcod.KEY_PAGEUP:
                ui.scroll_message(1)
            if key.vk == libtcod.KEY_PAGEDOWN:
                ui.scroll_message(-1)
            if key_char == 'g':
                return pick_up_item()
            if key_char == 'i':
                return ui.inspect_inventory()
            if key_char == 'e':
                chosen_item = ui.inventory_menu('Use which item?')
                if chosen_item is not None:
                    use_result = chosen_item.use()
                    if use_result == 'cancelled':
                       return 'didnt-take-turn'
                    else:
                       return 'used-item'
            if key_char == 'd':
                chosen_item = ui.inventory_menu('Drop which item?')
                if chosen_item is not None:
                    if chosen_item.drop() == 'cancelled':
                        return 'didnt-take-turn'
                    else:
                        return 'dropped-item'
            if key_char == 'c':
                ui.msgbox('Character Information\n\nLevel: ' + str(instance.level) + '\n\nMaximum HP: ' +
                       str(instance.fighter.max_hp),
                       consts.CHARACTER_SCREEN_WIDTH)
            if key_char == 'z':
                return cast_spell()
            if key_char == 'v':
                return jump()
            if key_char == 'x':
                ui.examine()
            if key.vk == libtcod.KEY_TAB:
                ui.target_next_monster()
            if key_char == 'm':
                if key.shift:
                    ui.show_map_screen()
                    return 'didnt-take-turn'
                else:
                    return meditate()
            if key_char == 'a':
                if key.shift:
                    ui.show_action_panel = not ui.show_action_panel
                    return 'didnt-take-turn'
                else:
                    return ui.show_ability_screen()
            if key_char == 'p': #and key.shift:
                purchase_skill()
                return 'didnt-take-turn'
            if mouse.rbutton_pressed:
                offsetx, offsety = instance.x - consts.MAP_VIEWPORT_WIDTH / 2, instance.y - consts.MAP_VIEWPORT_HEIGHT / 2
                mouse_pos = mouse.cx + offsetx - consts.MAP_VIEWPORT_X, mouse.cy + offsety - consts.MAP_VIEWPORT_Y
                if main.in_bounds(mouse_pos[0], mouse_pos[1]):
                    ui.examine(mouse_pos[0], mouse_pos[1])
            return 'didnt-take-turn'
        if not moved:
            return 'didnt-take-turn'

def do_queued_action(action):
    if action == 'wait' or action is None:
        instance.fighter.adjust_stamina(consts.STAMINA_REGEN_WAIT)
    elif action == 'channel-cast':
        instance.fighter.adjust_stamina(consts.STAMINA_REGEN_CHANNEL)
    elif callable(action):
        action()

def cast_spell():
    if instance.fighter.has_status('silence'):
        ui.message('You are silenced!',libtcod.yellow)
        return 'didnt-take-turn'
    result = _cast_spell()
    if result == 'cast-spell':
        if main.has_skill('stonecloak'):
            instance.fighter.apply_status_effect(effects.stoneskin(5),True)
        if main.has_skill('tailwind'):
            instance.fighter.apply_status_effect(effects.free_move(),True)
    return result

def _cast_spell():
    # Complicated because spell mastery

    #tuple - name, level, charges
    m_spells = [(s[0],s[1],instance.memory.spell_charges[s[0]]) for s in instance.memory.spell_list.items()]
    left_hand = main.get_equipped_in_slot(instance.fighter.inventory, 'left hand')

    if hasattr(left_hand, 'spell_list') and len(left_hand.spell_list) > 0:
        for s in left_hand.flat_spell_list:
            if left_hand.spell_list[s] > 0:
                m_spells.append((s, left_hand.spell_list[s], left_hand.spell_charges[s]))
        #m_spells += [(s[0],s[1],left_hand.spell_charges[s[0]]) for s in left_hand.spell_list.items() if s[1] > 0]

    if len(m_spells) < 1:
        ui.message("You have no spells available", libtcod.light_blue)
        return 'didnt-take-turn'
    else:
        letter_index = ord('a')
        ops = collections.OrderedDict()
        sp = {}
        for spell,level,charges in m_spells:
            spell_data = spells.library[spell]

            name_color = libtcod.white
            stamina_cost = spell_data.levels[level-1]['stamina_cost']
            if stamina_cost > instance.fighter.stamina:
                stamina_color = libtcod.dark_red
                name_color = libtcod.dark_gray
            else:
                stamina_color = libtcod.dark_green

            miscast = get_miscast_chance(spells.library[spell])
            miscast_color = libtcod.color_lerp(libtcod.blue, libtcod.red, float(miscast) / 100.0)
            if miscast >= 100:
                name_color = libtcod.dark_gray

            if charges <= 0:
                charges_color = libtcod.dark_red
                name_color = libtcod.dark_gray
            else:
                charges_color = libtcod.yellow

            d = collections.OrderedDict()
            d['spell'] = {
                    'text' : spell_data.name.title(),
                    'color' : name_color
                }
            d['stamina'] = {
                    'text': '[%d]' % stamina_cost,
                    'color': stamina_color
                }
            d['charges'] = {
                    'text': '%d/%d' % (charges, spell_data.max_spell_charges(level)),
                    'color': charges_color
                }
            d['miscast'] = {
                    'text': str(miscast) + '%%',
                    'color': miscast_color
                }
            d['description'] = string.capwords(spell_data.name) + '\n\n' + spell_data.description

            ops[chr(letter_index)] = d
            sp[chr(letter_index)] = spell
            letter_index += 1

        selection = ui.menu_ex('Cast which spell?', ops, 50, return_as_char=True)
        if selection is not None:
            s = sp[selection]
            if left_hand is not None:
                level = left_hand.spell_list[s]
                cost = spells.library[s].levels[level-1]['stamina_cost']
                cast_check = left_hand.can_cast(s,instance)
                if cast_check == 'miscast':
                    instance.fighter.adjust_stamina(-2 * cost)
                    return 'miscast'
                elif cast_check:
                    if spells.library[s].function() == 'success':
                        left_hand.spell_charges[s] -= 1
                        if main.has_skill('blood_magic') and instance.fighter.stamina < cost:
                            instance.fighter.hp -= cost - instance.fighter.stamina
                            instance.fighter.stamina = 0
                        else:
                            instance.fighter.adjust_stamina(-cost)
                        instance.fighter.apply_status_effect(effects.StatusEffect('meditate', time_limit=None,
                                          color=libtcod.yellow, description='Meditating will renew your missing spells.'))
                        return 'cast-spell'
                    else:
                        return 'didnt-take-turn'
                else:
                    return 'didnt-take-turn'
            if s in instance.memory.spell_list and instance.memory.can_cast(s, instance):
                cast_check = instance.memory.can_cast(s, instance)
                level = instance.memory.spell_list[s]
                cost = spells.library[s].levels[level - 1]['stamina_cost']
                if cast_check == 'miscast':
                    instance.fighter.adjust_stamina(-2 * cost)
                    return 'miscast'
                elif cast_check:
                    if spells.library[s].function() == 'success':
                        instance.memory.spell_charges[s] -= 1
                        if main.has_skill('blood_magic') and instance.fighter.stamina < cost:
                            instance.fighter.hp -= cost - instance.fighter.stamina
                            instance.fighter.stamina = 0
                        else:
                            instance.fighter.adjust_stamina(-cost)
                        instance.fighter.apply_status_effect(effects.StatusEffect('meditate', time_limit=None,
                                          color=libtcod.yellow, description='Meditating will renew your missing spells.'))
                        return 'cast-spell'
                    else:
                        return 'didnt-take-turn'
                else:
                    return 'didnt-take-turn'
            else:
                return 'didnt-take-turn'
    return 'didnt-take-turn'

def get_miscast_chance(spell):
    requirement = spell.int_requirement - main.skill_value('scholar')
    if instance.player_stats.int > requirement:
        return 0
    else:
        diff = requirement - instance.player_stats.int
        return min(100, diff * int(requirement / 2))

def pick_up_essence(essence, obj):
    if obj is not instance:
        return 'failure'
    if len(instance.essence) < instance.player_stats.max_essence:
        if isinstance(essence ,main.GameObject):
            instance.essence.append(essence.essence_type)
            ui.message('You are infused with the essence of %s.' % essence.essence_type, essence.color)
            essence.destroy()
            return 'success'
        else:
            instance.essence.append(essence)
            ui.message('You are infused with the essence of %s.' % essence, spells.essence_colors[essence])
            return 'success'
    else:
        return replace_essence(essence)


def pick_up_xp(xp, obj):
    if obj is instance:
        instance.fighter.xp += consts.XP_ORB_AMOUNT_MIN + \
                             libtcod.random_get_int(0, 0, consts.XP_ORB_AMOUNT_MAX - consts.XP_ORB_AMOUNT_MIN)
        check_level_up()

        instance.skill_point_progress += instance.player_stats.wiz
        if instance.skill_point_progress >= 100:
            ui.message('Your skills have increased.', libtcod.green)
            instance.skill_points += 10
            instance.skill_point_progress -= 100
            purchase_skill()

        xp.destroy()

def check_level_up():
    next = consts.LEVEL_UP_BASE + instance.level * consts.LEVEL_UP_FACTOR
    if instance.fighter.xp >= next:
        level_up()
        instance.fighter.xp = instance.fighter.xp - next

def level_up():

    instance.level += 1
    ui.message('You grow stronger! You have reached level ' + str(instance.level) + '!', libtcod.green)
    choice = None
    while choice is None:
        choice = ui.menu('Level up! Choose a stat to raise:\n', [
            'Constitution',
            'Strength',
            'Agility',
            'Intelligence',
            'Wisdom'
         ], consts.LEVEL_SCREEN_WIDTH)

    if choice == 0:
        instance.player_stats.con += 1
    elif choice == 1:
        instance.player_stats.str += 1
    elif choice == 2:
        instance.player_stats.agi += 1
    elif choice == 3:
        instance.player_stats.int += 1
    elif choice == 4:
        instance.player_stats.wiz += 1

    hp_growth = instance.player_stats.con / 2
    if instance.player_stats.con % 2 == 1:
        hp_growth += instance.level % 2

    instance.fighter.max_hp += hp_growth
    instance.fighter.hp += hp_growth

    instance.fighter.heal(int(instance.fighter.max_hp * consts.LEVEL_UP_HEAL))

def purchase_skill():
    learned_skills = main.learned_skills

    skill = ui.skill_menu()
    if skill is not None:
        cost = perks.perk_list[skill]['sp_cost']
        if cost > instance.skill_points:
            ui.message("You don't have enough skill points.", libtcod.light_blue)
        else:
            success = True
            if perks.perk_list[skill].get('on_acquire') is not None:
                success = perks.perk_list[skill].get('on_acquire')()
            if success == 'failed':
                ui.message("Canceled", libtcod.red)
                return
            if skill in learned_skills.keys():
                learned_skills[skill] += 1
            else:
                learned_skills[skill] = 1
            if not consts.DEBUG_FREE_PERKS:
                instance.skill_points -= cost
            ui.message("Learned skill {}".format(perks.perk_list[skill]['name'].title()),libtcod.white)

def on_death(instance):
    if instance.fighter.has_status('auto-res'):
        instance.fighter.remove_status('auto-res')
        instance.fighter.heal(instance.fighter.max_hp)
        ui.message("Not today, death.", libtcod.green)
    else:
        ui.message("You're dead, sucka.", libtcod.dark_red)
        main.game_state = 'dead'
        instance.char = '%'
        instance.color = libtcod.darker_red

def move_or_attack(dx, dy, ctrl=False):

    if ctrl:
        weapon = main.get_equipped_in_slot(instance.fighter.inventory, 'right hand')
        if weapon and weapon.ctrl_attack:
            if weapon.quality != 'broken':
                success = weapon.ctrl_attack(dx, dy) != 'failed'
            else:
                ui.message('Your ' + weapon.owner.name + ' cannot do that in its current state!')
                return False
        else:
            success = bash_attack(dx, dy) != 'failed'
    else:
        target = main.get_monster_at_tile(instance.x + dx, instance.y + dy)
        if target is not None:
            import monsters
            if target.fighter.team == 'ally':
                if target.fighter.has_flag(monsters.IMMOBILE):
                    ui.message('%s cannot swap places with you.' % syntax.name(target).capitalize())
                    return False
                else:
                    value = instance.swap_positions(target)
                    return value
            else:
                success = instance.fighter.attack(target) != 'failed'
                if success and target.fighter:
                    ui.select_monster(target)
        else:
            value = instance.move(dx, dy)
            if value and instance.fighter.has_status('free move'):
                instance.fighter.remove_status('free move')
                return False
            return value

    return success

def reach_attack(dx, dy):

    target_space = instance.x + 2 * dx, instance.y + 2 * dy
    target = main.get_monster_at_tile(target_space[0], target_space[1])
    if target is not None:
        result = combat.attack_ex(instance.fighter, target, instance.fighter.calculate_attack_stamina_cost(), verb=('reach-attack', 'reach-attacks'))
        if result != 'failed' and target.fighter:
            ui.select_monster(target)
        return result
    else:
        target = main.get_monster_at_tile(instance.x + dx, instance.y + dy)
        if target is not None:
            result = instance.fighter.attack(target)
            if result != 'failed' and target.fighter:
                ui.select_monster(target)
        else:
            value = instance.move(dx, dy)
            if value:
                return 'moved'
    return 'failed'


def cleave_attack(dx, dy):
    # attack all adjacent creatures
    adjacent = main.adjacent_tiles_diagonal(instance.x, instance.y)
    if adjacent and len(adjacent) > 0:
        stamina_cost = instance.fighter.calculate_attack_stamina_cost() * 2
        if instance.fighter.stamina < stamina_cost:
            ui.message("You don't have the stamina to perform a cleave attack!", libtcod.light_yellow)
            return 'failed'
        instance.fighter.adjust_stamina(-stamina_cost)
        for tile in adjacent:
            target = main.get_monster_at_tile(tile[0], tile[1])
            if target and target.fighter:
                combat.attack_ex(instance.fighter, target, 0, verb=('cleave', 'cleaves'))
        return 'cleaved'
    else:
        value = instance.move(dx, dy)
        if value:
            return 'moved'
    return 'failed'


def bash_attack(dx, dy):
    target = main.get_monster_at_tile(instance.x + dx, instance.y + dy)
    if target is not None:
        result = combat.attack_ex(instance.fighter, target, consts.BASH_STAMINA_COST,
                                  damage_multiplier=consts.BASH_DMG_MOD, verb=('bash', 'bashes'))
        if result == 'hit' and target.fighter:
            ui.select_monster(target)
            actions.knock_back(instance,target)

        return result
    else:
        value = instance.move(dx, dy)
        if value:
            return 'moved'
    return 'failed'

def pick_up_item():
    items_here = main.get_objects(instance.x, instance.y, condition=lambda o: o.item)
    if len(items_here) > 0:
        if len(items_here) == 1:
            items_here[0].item.pick_up(instance)
            return 'picked-up-item'
        options = []
        options.append('All')
        for item in items_here:
            options.append(item.name)

        selection = ui.menu('Pick up which item?', options, 30)
        if selection is not None:
            if selection == 0:
                for i in items_here:
                    i.item.pick_up(instance)
            else:
                items_here[selection - 1].item.pick_up(instance)
            return 'picked-up-item'
    else:
        essence_here = main.get_objects(instance.x, instance.y, condition=lambda o: hasattr(o, 'essence_type'))
        if len(essence_here) > 0:
            if replace_essence(essence_here[0]) == 'success':
                return 'replaced-essence'
            else:
                return 'didnt-take-turn'
        else:
            interactable_here = main.get_objects(instance.x, instance.y, condition=lambda o:o.interact)  # prioritize this space
            if len(interactable_here) == 0:
                interactable_here = main.get_objects(instance.x, instance.y, condition=lambda o:o.interact, distance=1) #get stuff that's adjacent too
            if len(interactable_here) > 0:
                result = interactable_here[0].interact(interactable_here[0], instance)
                if result is None:
                    result = 'interacted'
                return result
    return 'didnt-take-turn'


def replace_essence(essence):
    if isinstance(essence, main.GameObject):
        essence_type = essence.essence_type
    else:
        essence_type = essence
    index = ui.menu('Replace what essence with %s essence?\n' % essence_type, instance.essence, 50)
    if index is None:
        return 'cancelled'
    instance.essence[index] = essence_type
    if isinstance(essence, main.GameObject):
        essence.destroy()
    return 'success'


def get_key(name='Glass Key'):
    for item in instance.fighter.inventory:
        if item.name == name:
            return item
    return None


def meditate():
    book = main.get_equipped_in_slot(instance.fighter.inventory, 'left hand')
    if (book is None or not hasattr(book, 'spell_list')) and len(instance.memory.spell_list) == 0:
        ui.message('Without access to magic, you have no need of meditation.', libtcod.dark_cyan)
        return 'didnt-take-turn'
    ui.message('You tap into the magic of the world around you...', libtcod.dark_cyan)

    if main.has_skill('solace'):
        instance.fighter.apply_status_effect(effects.solace(),True)

    for i in range(consts.MEDITATE_CHANNEL_TIME - 1):
        instance.action_queue.append('wait')
    instance.action_queue.append(_do_meditate)
    return 'start-meditate'

def _do_meditate():
    instance.fighter.adjust_stamina(consts.STAMINA_REGEN_WAIT)
    book = main.get_equipped_in_slot(instance.fighter.inventory, 'left hand')
    if book is not None and hasattr(book, 'spell_list'):
        book.refill_spell_charges()
        instance.memory.refill_spell_charges()
        ui.message('Your spells have recharged.', libtcod.dark_cyan)
    instance.fighter.remove_status('meditate')
    instance.fighter.remove_status('solace')

def delay(duration,action,delay_action='delay'):
    for i in range(duration):
        instance.action_queue.append(delay_action)
    instance.action_queue.append(action)

def jump(actor=None, range=None, stamina_cost=None):
    if range is None:
        range = consts.BASE_JUMP_RANGE
    if stamina_cost is None:
        stamina_cost = consts.JUMP_STAMINA_COST
    if not main.current_map.tiles[instance.x][instance.y].jumpable:
        ui.message('You cannot jump from this terrain!', libtcod.light_yellow)
        return 'didnt-take-turn'

    web = main.object_at_tile(instance.x, instance.y, 'spiderweb')
    if web is not None:
        ui.message('You struggle against the web.')
        web.destroy()
        return 'webbed'

    if instance.fighter.stamina < stamina_cost:
        ui.message("You don't have the stamina to jump!", libtcod.light_yellow)
        return 'didnt-take-turn'

    ui.message('Jump to where?', libtcod.white)

    ui.render_message_panel()
    libtcod.console_flush()
    (x, y) = ui.target_tile(range, 'pick', consts.JUMP_ATTACK_ACC_MOD)
    if x is not None and y is not None:
        if main.current_map.tiles[x][y].blocks:
            ui.message('There is something in the way.', libtcod.light_yellow)
            return 'didnt-take-turn'
        elif main.current_map.tiles[x][y].is_pit:
            ui.message("You really don't want to jump into this bottomless pit.", libtcod.light_yellow)
            return 'didnt-take-turn'
        elif main.is_blocked(x, y, from_coord=(instance.x, instance.y), movement_type=instance.movement_type) and main.current_map.tiles[x][y].elevation > instance.elevation:
            ui.message("You can't jump that high!", libtcod.light_yellow)
            return 'didnt-take-turn'
        else:
            jump_attack_target = None
            for obj in main.current_map.objects:
                if obj.x == x and obj.y == y and obj.blocks:
                    jump_attack_target = obj
                    break
            if jump_attack_target is not None and not jump_attack_target.fighter:
                ui.message('There is something in the way.', libtcod.light_yellow)
                return 'didnt-take-turn'
            elif jump_attack_target is not None and jump_attack_target is not instance:
                # Jump attack
                land = main.land_next_to_target(jump_attack_target.x, jump_attack_target.y, instance.x, instance.y)
                if land is not None:
                    instance.set_position(land[0], land[1])
                    instance.fighter.adjust_stamina(-stamina_cost)

                    accuracy_mod = consts.JUMP_ATTACK_ACC_MOD
                    damage_multiplier = consts.JUMP_ATTACK_DMG_MOD

                    if main.has_skill('death_from_above'):
                        accuracy_mod = 1
                        damage_multiplier *= 1.5

                    if main.has_skill('flying_knee_smash') and \
                        main.get_equipped_in_slot(instance.fighter.inventory,'right hand') is None:
                        damage_multiplier *= 2

                    combat.attack_ex(instance.fighter, jump_attack_target, 0, accuracy_modifier=accuracy_mod,
                                             damage_multiplier=damage_multiplier,verb=('jump-attack','jump-attacks'))

                    return 'jump-attacked'
                else:
                    ui.message('There is something in the way.', libtcod.white)
                    return 'didnt-take-turn'
            else:
                # jump to open space
                instance.set_position(x, y)
                instance.fighter.adjust_stamina(-stamina_cost)
                return 'jumped'


    ui.message('Cancelled.', libtcod.white)
    return 'didnt-take-turn'

def level_spell_mastery():
    tomes = [t.equipment.get_active_spells().items() for t in instance.fighter.inventory if hasattr(t.equipment,'spell_list') and len(t.equipment.spell_list) > 0]
    spell_list = list(set([spell for tome in tomes for spell in tome if spells.is_max_level(spell[0],spell[1]) ] ))
    choice = ui.menu("Select a spell to memorize",[spells.library[s[0]].name.title() for s in spell_list],40)
    if choice is not None:
        instance.memory.add_spell(spell_list[choice][0],spell_list[choice][1])
    else:
        return 'failed'

def learn_ability(name):
    return lambda: _learn_ability(name)

def _learn_ability(name):
    import abilities
    for a in instance.perk_abilities:
        if a.name == abilities.data[name]['name']:
            return
    ability = abilities.data[name]
    instance.perk_abilities.append(abilities.Ability(ability['name'],ability['description'],
                                                                  ability['function'],ability['cooldown']))

def on_tick(this):
    if main.has_skill('pyromaniac'):
        main.create_fire(this.x,this.y,10)
    if main.has_skill('frostbite'):
        for enemy in main.get_visible_units_ex(lambda f: f.fighter.team != 'ally'):
            if enemy.fighter.hp < enemy.fighter.max_hp / 2:
                enemy.fighter.apply_status_effect(effects.slowed(2),True)
    if main.has_skill('heir_to_the_heavens'):
        if hasattr(instance,'heir_to_the_heavens_cd'):
            instance.heir_to_the_heavens_cd -= 1
    if main.has_skill('rising_storm'):
        if hasattr(instance,'rising_storm_last_attack'):
            instance.rising_storm_last_attack += 1
        else:
            instance.rising_storm_last_attack = 0
    if instance.fighter.stamina_regen > 0:
        instance.fighter.adjust_stamina(instance.fighter.stamina_regen)

    for ability in abilities.default_abilities.values():
        ability.on_tick()

    if instance.fighter.hp < 25:
        instance.fighter.heal(instance.fighter.item_equipped_count('equipment_ring_of_tenacity'))

def on_get_hit(this,other,damage):
    if main.has_skill('heir_to_the_heavens'):
        if not hasattr(instance,'heir_to_the_heavens_cd'):
            instance.heir_to_the_heavens_cd = 0
        if (this.fighter.hp <= (damage * 2) or this.fighter.hp < (this.fighter.max_hp * 0.2)) and instance.heir_to_the_heavens_cd < 1:
            if actions.summon_guardian_angel() != 'failed':
                instance.heir_to_the_heavens_cd = 70
                instance.fighter.apply_status_effect(effects.invulnerable(1),True)

    if main.has_skill('adrenaline'):
        health_percentage = float(instance.fighter.hp) / float(instance.fighter.max_hp)
        adrenaline_chance = (1.0 - health_percentage) * 0.75
        if libtcod.random_get_float(0, 0.0, 1.0) < adrenaline_chance:
            instance.fighter.adjust_stamina(10)
            ui.message('You feel a surge of adrenaline!', libtcod.light_yellow)

    if main.roll_dice('1d20' <= instance.fighter.item_equipped_count('equipment_ring_of_rage')):
        instance.fighter.apply_status_effect(effects.berserk())

    if main.roll_dice('1d20' <= instance.fighter.item_equipped_count('equipment_ring_of_vengeance')):
        other.fighter.apply_status_effect(effects.cursed())

def on_get_kill(this,other,damage):
    this.fighter.heal(this.fighter.item_equipped_count('equipment_ring_of_vampirism') * 2)

def get_abilities():
    import abilities

    # Always available
    opts = [abilities.default_abilities['attack'], abilities.default_abilities['jump']]

    # Weapon ability, or bash if none
    weapon = main.get_equipped_in_slot(instance.fighter.inventory, 'right hand')
    if weapon is not None and weapon.owner.item.ability is not None:
        opts.append(weapon.owner.item.ability)
    else:
        opts.append(abilities.default_abilities['bash'])

    # Activatable items other than weapon
    for i in main.get_all_equipped(instance.fighter.inventory):
        if i is not weapon and i.owner.item.ability is not None:
            opts.append(i.owner.item.ability)

    # Perk abilities
    for p in instance.perk_abilities:
        opts.append(p)

    # Raise shield
    sh = instance.fighter.get_equipped_shield()
    if sh is not None and not sh.raised:
        opts.append(abilities.default_abilities['raise shield'])

    return opts

import game as main
import libtcodpy as libtcod
import math
import consts
import effects
import combat
import spells
import syntax
import pathfinding
import ui
import perks
import actions
import abilities
import items
