import game as main
import libtcodpy as libtcod
import math
import consts
import fov
import effects
import combat
import dungeon
import spells
import syntax
import pathfinding
import ui

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
    def max_memory(self):
        return 3 + int(math.floor(self.wiz / 4))

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
            #'charm_magic_weapon',
            'weapon_halberd',
            'weapon_longsword',
            'equipment_leather_armor',
            'equipment_iron_helm'
        ],
        'description' : "Balanced melee fighter. Starts with good weapon and armor. Charm channels essence to imbue "
                        "temporary weapon effects."
    },
    'rogue' : {
        'str':10,
        'agi':14,
        'int':8,
        'spr':9,
        'con':8,
        'inventory':[
            #'charm_curse',
            'weapon_dagger',
            'equipment_leather_armor'
        ],
        'description' : "Nimble melee fighter. Starts with excellent agility. "
                        "Charm channels essence to curse enemies with negative effects."
    },
    'wanderer' : {
        'str':10,
        'agi':10,
        'int':10,
        'spr':14,
        'con':10,
        'inventory':[
            'charm_blessing',
            'potion_lesser_fire',
            'potion_lesser_earth',
            'potion_lesser_life',
            'potion_lesser_air',
            'potion_lesser_water'
        ],
        'description' : "Generalist class with great stats, especially spirit. Starts with no gear. "
                        "Charm channels essence to bless self with beneficial effects."
    },
    'fanatic' : {
        'str':13,
        'agi':9,
        'int':8,
        'spr':12,
        'con':8,
        'inventory':[
            'charm_resistance',
            'weapon_coal_mace'
        ],
        'description' : "Offensive melee fighter. Starts with no armor and a mace. "
                        "Charm channels essence to bless self with elemental resistance."
    },
    'wizard' : {
        'str':6,
        'agi':8,
        'int':12,
        'spr':10,
        'con':8,
        'inventory':[
            'charm_summoning',
            'book_lesser_fire',
            'gem_lesser_fire'
        ],
        'description' : "Fragile in melee, but have access to powerful offensive magic. "
                        "Starts with a tome. Charm channels essence to summon elementals"
    },
}

instance = None

def create(loadout):
    global instance

    loadout = loadouts[loadout]
    fighter_component = combat.Fighter(hp=100, xp=0, stamina=100, death_function=on_death, team='ally')
    instance = main.GameObject(25, 23, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component,
                        player_stats=PlayerStats(int(loadout['int']),int(loadout['spr']),int(loadout['str']),
                        int(loadout['agi']),int(loadout['con'])), description='An exile, banished to this forsaken '
                        'island for your crimes. This place will surely be your grave.',
                        movement_type=pathfinding.NORMAL)
    instance.level = 1
    instance.essence = []
    instance.known_spells = []
    instance.action_queue = []
    instance.skill_points = 0

    for item in loadout['inventory']:
        i = None

        if 'weapon' in item:
            i = main.create_item(item, material='iron', quality='')
        else:
            i = main.create_item(item)

        instance.fighter.inventory.append(i)
        if i.equipment is not None:
            i.equipment.equip()

    if consts.DEBUG_STARTING_ITEM is not None:
        test = main.create_item(consts.DEBUG_STARTING_ITEM)
        instance.fighter.inventory.append(test)

def handle_keys():

    game_state = main.game_state
    key = main.key
    mouse = main.mouse

    ui.mouse_select_monster()

    key_char = chr(key.c)

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key_char == 'q' and key.shift:
        return 'exit'  #exit game

    if game_state == 'playing':

        if instance.fighter and instance.fighter.has_status('stunned'):
            return 'stunned'

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
                    chosen_item.drop()
                    return 'dropped-item'
            if key_char == ',' and key.shift:
                #if stairs.x == instance.x and stairs.y == instance.y:
                    main.next_level()
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
                return meditate()
            if key_char == 'a':
                if key.shift:
                    ui.show_action_panel = not ui.show_action_panel
                    return 'didnt-take-turn'
                else:
                    return ui.show_ability_screen()
            if key_char == 'p': # TEMPORARY
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

    if action == 'finish-meditate':
        instance.fighter.adjust_stamina(consts.STAMINA_REGEN_WAIT)
        book = main.get_equipped_in_slot(instance.fighter.inventory, 'left hand')
        if book is not None and hasattr(book, 'spell_list'):
            book.refill_spell_charges()
            ui.message('Your spells have recharged.', libtcod.dark_cyan)
        return

    elif action == 'channel-meditate':
        instance.fighter.adjust_stamina(consts.STAMINA_REGEN_WAIT)
    elif action == 'channel-cast':
        instance.fighter.adjust_stamina(consts.STAMINA_REGEN_CHANNEL)
    elif callable(action):
        action()

def cast_spell():
    left_hand = main.get_equipped_in_slot(instance.fighter.inventory,'left hand')
    if not hasattr(left_hand, 'spell_list') or len(left_hand.spell_list) <= 0:
        ui.message("You have no spells available", libtcod.light_blue)
        return 'didnt-take-turn'
    else:
        letter_index = ord('a')
        ops = {}
        sp = {}
        for spell,level in left_hand.get_active_spells().items():
            spell_data = spells.library[spell]
            ops[chr(letter_index)] = [
                {
                    'category' : 'spell',
                    'text' : spell_data.name.title()
                },
                {
                    'category': 'stamina',
                    'text': '[%d]' % spell_data.levels[level-1]['stamina_cost'],
                    'color': libtcod.dark_green
                },
                {
                    'category': 'charges',
                    'text': '%d/%d' % (left_hand.spell_charges[spell], spell_data.levels[level-1]['charges']),
                    'color': libtcod.yellow
                }
            ]
            sp[chr(letter_index)] = spell
            letter_index += 1
        selection = ui.menu_ex('Cast which spell?', ops, 50, return_as_char=True)
        #names = []
        #ops = []
        #for spell,level in left_hand.get_active_spells().items():
        #    spell_data = spells.library[spell]
        #    stamina_cost = spell_data.levels[level-1]['stamina_cost']
        #    spell_charges = left_hand.spell_charges[spell]
        #    max_spell_charges = spell_data.levels[level-1]['charges']
        #    names.append(spell_data.name.title() + '[' + str(stamina_cost) + ']' + " " + str(spell_charges) + "/" + str(max_spell_charges))
        #    ops.append(spell)
        #selection = ui.menu('Cast which spell?', names, 30)
        if selection is not None:
            s = sp[selection]
            if left_hand.can_cast(s,instance):
                if spells.library[s].function() == 'success':
                    left_hand.spell_charges[s] -= 1
                    level = left_hand.spell_list[s]
                    instance.fighter.adjust_stamina(-spells.library[s].levels[level-1]['stamina_cost'])
                    return 'cast-spell'
                else:
                    return 'didnt-take-turn'
            else:
                return 'didnt-take-turn'
    return 'didnt-take-turn'

def pick_up_essence(essence, obj):
    if obj is instance and len(instance.essence) < instance.player_stats.max_essence:
        if isinstance(essence ,main.GameObject):
            instance.essence.append(essence.essence_type)
            ui.message('You are infused with magical power.', essence.color)
            essence.destroy()
        else:
            instance.essence.append(essence)
            ui.message('You are infused with magical power.', spells.essence_colors[essence])


def pick_up_xp(xp, obj):
    if obj is instance:
        instance.fighter.xp += consts.XP_ORB_AMOUNT_MIN + \
                             libtcod.random_get_int(0, 0, consts.XP_ORB_AMOUNT_MAX - consts.XP_ORB_AMOUNT_MIN)
        check_level_up()
        xp.destroy()

def check_level_up():
    next = consts.LEVEL_UP_BASE + instance.level * consts.LEVEL_UP_FACTOR
    if instance.fighter.xp >= next:
        level_up()
        instance.fighter.xp = instance.fighter.xp - next

def level_up():

    instance.level += 1
    instance.skill_points += instance.player_stats.wiz
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
        instance.fighter.max_hp += 20
        instance.fighter.hp += 20
    elif choice == 1:
        instance.player_stats.str += 1
    elif choice == 2:
        instance.player_stats.agi += 1
    elif choice == 3:
        instance.player_stats.int += 1
    elif choice == 4:
        instance.player_stats.wiz += 1

    purchase_skill()

    instance.fighter.heal(instance.fighter.max_hp / 2)

def purchase_skill():
    learned_skills = main.learned_skills

    skill = ui.skill_menu()
    if skill is not None and skill not in learned_skills:
        if skill.sp_cost > instance.skill_points:
            ui.message("You don't have enough skill points.", libtcod.light_blue)
        else:
            learned_skills.append(skill)
            instance.skill_points -= skill.sp_cost
            ui.message("Learned skill {}".format(skill.name.title()),libtcod.white)

def on_death(instance):
    ui.message("You're dead, sucka.", libtcod.grey)
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
            if target.fighter.team == 'ally':
                value = instance.swap_positions(target)
                return value
            else:
                success = instance.fighter.attack(target) != 'failed'
                if success and target.fighter:
                    ui.select_monster(target)
        else:
            value = instance.move(dx, dy)
            return value

    return success

def reach_attack(dx, dy):

    target_space = instance.x + 2 * dx, instance.y + 2 * dy
    target = main.get_monster_at_tile(target_space[0], target_space[1])
    if target is not None:
        result = combat.attack_ex(instance.fighter, target, instance.fighter.calculate_attack_stamina_cost(), instance.fighter.accuracy,
                             instance.fighter.attack_damage, 1.5, None, ('reach-attack', 'reach-attacks'),
                             instance.fighter.attack_shred, instance.fighter.attack_guaranteed_shred, instance.fighter.attack_pierce)
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
                combat.attack_ex(instance.fighter, target, 0, instance.fighter.accuracy, instance.fighter.attack_damage,
                                 None, None, ('cleave', 'cleaves'), instance.fighter.attack_shred,
                                 instance.fighter.attack_guaranteed_shred + 1, instance.fighter.attack_pierce)
        return 'cleaved'
    else:
        value = instance.move(dx, dy)
        if value:
            return 'moved'
    return 'failed'


def bash_attack(dx, dy):
    target = main.get_monster_at_tile(instance.x + dx, instance.y + dy)
    if target is not None:
        result = combat.attack_ex(instance.fighter, target, consts.BASH_STAMINA_COST, instance.fighter.accuracy * consts.BASH_ACC_MOD,
                                 instance.fighter.attack_damage, consts.BASH_DMG_MOD,
                                 None, ('bash', 'bashes'), instance.fighter.attack_shred + 1, instance.fighter.attack_guaranteed_shred,
                                 instance.fighter.attack_pierce)
        if result == 'hit' and target.fighter:
            ui.select_monster(target)
            # knock the target back one space. Stun it if it cannot move.
            direction = target.x - instance.x, target.y - instance.y  # assumes the instance is adjacent
            stun = False
            against = ''
            against_tile = main.current_map.tiles[target.x + direction[0]][target.y + direction[1]]
            if against_tile.blocks:
                stun = True
                against = main.current_map.tiles[target.x + direction[0]][target.y + direction[1]].name
            elif against_tile.elevation != target.elevation and against_tile.tile_type != 'ramp' and main.current_map.tiles[target.x][target.y] != 'ramp':
                stun = True
                against = 'cliff'
            else:
                for obj in main.current_map.objects:
                    if obj.x == target.x + direction[0] and obj.y == target.y + direction[1] and obj.blocks:
                        stun = True
                        against = obj.name
                        break


            if stun:
                #  stun the target
                if target.fighter.apply_status_effect(effects.StatusEffect('stunned', time_limit=2, color=libtcod.light_yellow)):
                    ui.message('%s %s with the %s, stunning %s!' % (
                                    syntax.name(target.name).capitalize(),
                                    syntax.conjugate(target is instance, ('collide', 'collides')),
                                    against,
                                    syntax.pronoun(target.name, objective=True)), libtcod.gold)
            else:
                ui.message('%s %s knocked backwards.' % (
                                    syntax.name(target.name).capitalize(),
                                    syntax.conjugate(target is instance, ('are', 'is'))), libtcod.gray)
                target.set_position(target.x + direction[0], target.y + direction[1])
                main.render_map()
                libtcod.console_flush()

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
            items_here[0].item.pick_up()
            return 'picked-up-item'
        options = []
        options.append('All')
        for item in items_here:
            options.append(item.name)

        selection = ui.menu('Pick up which item?', options, 30)
        if selection is not None:
            if selection == 0:
                for i in items_here:
                    i.item.pick_up()
            else:
                items_here[selection - 1].item.pick_up()
            return 'picked-up-item'
    else:
        essence_here = main.get_objects(instance.x, instance.y, condition=lambda o: hasattr(o, 'essence_type'))
        if len(essence_here) > 0:
            replace_essence(essence_here[0])
            return 'replaced-essence'
        else:
            interactable_here = main.get_objects(instance.x, instance.y, condition=lambda o:o.interact, distance=1) #get stuff that's adjacent too
            if len(interactable_here) > 0:
                result = interactable_here[0].interact(interactable_here[0])
                if result is None:
                    result = 'interacted'
                return result
    return 'didnt-take-turn'


def replace_essence(essence):
    instance.essence[ui.menu('Replace what essence with %s essence?\n' % essence.essence_type, instance.essence, 50)] = essence.essence_type
    essence.destroy()


def meditate():
    book = main.get_equipped_in_slot(instance.fighter.inventory, 'left hand')
    if book is None or not hasattr(book, 'spell_list'):
        ui.message('Without access to magic, you have no need of meditation.', libtcod.dark_cyan)
        return 'didnt-take-turn'
    ui.message('You tap into the magic of the world around you...', libtcod.dark_cyan)
    for i in range(consts.MEDITATE_CHANNEL_TIME - 1):
        instance.action_queue.append('channel-meditate')
    instance.action_queue.append('finish-meditate')
    return 'start-meditate'

def delay(duration,action,delay_action='delay'):
    for i in range(duration):
        instance.action_queue.append(delay_action)
    instance.action_queue.append(action)

def jump(actor=None):
    if not main.current_map.tiles[instance.x][instance.y].jumpable:
        ui.message('You cannot jump from this terrain!', libtcod.light_yellow)
        return 'didnt-take-turn'

    web = main.object_at_tile(instance.x, instance.y, 'spiderweb')
    if web is not None:
        ui.message('You struggle against the web.')
        web.destroy()
        return 'webbed'

    if instance.fighter.stamina < consts.JUMP_STAMINA_COST:
        ui.message("You don't have the stamina to jump!", libtcod.light_yellow)
        return 'didnt-take-turn'

    ui.message('Jump to where?', libtcod.white)

    ui.render_message_panel()
    libtcod.console_flush()
    (x, y) = ui.target_tile(consts.BASE_JUMP_RANGE, 'pick', consts.JUMP_ATTACK_ACC_MOD)
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
                    instance.fighter.adjust_stamina(-consts.JUMP_STAMINA_COST)

                    combat.attack_ex(instance.fighter, jump_attack_target, 0, instance.fighter.accuracy * consts.JUMP_ATTACK_ACC_MOD,
                                             instance.fighter.attack_damage,
                                             consts.JUMP_ATTACK_DMG_MOD, instance.fighter.on_hit, ('jump-attack','jump-attacks'),
                                             instance.fighter.attack_shred, instance.fighter.attack_guaranteed_shred,
                                             instance.fighter.attack_pierce)

                    return 'jump-attacked'
                else:
                    ui.message('There is something in the way.', libtcod.white)
                    return 'didnt-take-turn'
            else:
                # jump to open space
                instance.set_position(x, y)
                instance.fighter.adjust_stamina(-consts.JUMP_STAMINA_COST)
                return 'jumped'


    ui.message('Out of range.', libtcod.white)
    return 'didnt-take-turn'
