import game as main
import libtcodpy as libtcod
import math
import consts
import ui
import fov
import effects

class PlayerStats:

    def __init__(self, int=10, wiz=10, str=10, agi=10):
        self.base_int = int
        self.base_wiz = wiz
        self.base_str = str
        self.base_agi = agi

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
    def max_mana(self):
        return 1 + int(math.floor(self.wiz / 4))

instance = None

def create():
    global instance

    fighter_component = main.Fighter(hp=100, xp=0, stamina=100, death_function=on_death)
    instance = main.GameObject(25, 23, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component,
                        player_stats=PlayerStats(), description='You, the fearless adventurer!')
    instance.level = 1
    instance.mana = []
    instance.known_spells = []
    instance.action_queue = []

    leather_armor = main.create_item('equipment_leather_armor')
    instance.fighter.inventory.append(leather_armor)
    leather_armor.equipment.equip()
    dagger = main.create_item('equipment_dagger', material='iron', quality='')
    instance.fighter.inventory.append(dagger)
    dagger.equipment.equip()

    if consts.DEBUG_STARTING_ITEM is not None:
        test = main.create_item(consts.DEBUG_STARTING_ITEM)
        instance.fighter.inventory.append(test)

def handle_keys():

    game_state = main.game_state
    key = main.key
    mouse = main.mouse

    ui.mouse_select_monster()

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game

    if game_state == 'playing':

        if instance.fighter and instance.fighter.has_status('stunned'):
            return 'stunned'

        if instance.action_queue is not None and len(instance.action_queue) > 0:
            action = instance.action_queue[0]
            instance.action_queue.remove(action)
            do_queued_action(action)
            return action

        key_char = chr(key.c)
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
        elif key.vk == libtcod.KEY_KP7:
            moved = move_or_attack(-1, -1, ctrl)
        elif key.vk == libtcod.KEY_KP9:
            moved = move_or_attack(1, -1, ctrl)
        elif key.vk == libtcod.KEY_KP1:
            moved = move_or_attack(-1, 1, ctrl)
        elif key.vk == libtcod.KEY_KP3:
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
            if key_char == 'u':
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
            if key_char == 'j':
                return jump()
            if key_char == 'e':
                ui.examine()
            if key.vk == libtcod.KEY_TAB:
                ui.target_next_monster()
            if key_char == 'm':
                return meditate()
            if key_char == 'a':
                return ui.show_ability_screen()
            if key_char == 'l': # TEMPORARY
                ui.skill_menu()
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
        manatype = 'normal'

        if len(instance.mana) < instance.player_stats.max_mana:
            instance.mana.append(manatype)
            ui.message('You have finished meditating. You are infused with magical power.', libtcod.dark_cyan)
            return
        elif manatype != 'normal':
            for i in range(len(instance.mana)):
                if instance.mana[i] == 'normal':
                    instance.mana[i] = manatype
                    ui.message('You have finished meditating. You are infused with magical power.', libtcod.dark_cyan)
                    return
        ui.message('You have finished meditating. You were unable to gain any more power than you already have.', libtcod.dark_cyan)
        return

def cast_spell():
    if len(instance.known_spells) <= 0:
        ui.message("You don't know any spells.", libtcod.light_blue)
        return 'didnt-take-turn'
    else:
        names = []
        for s in instance.known_spells:
            names.append(s.name + ' ' + s.cost_string)
        selection = ui.menu('Cast which spell?', names, 30)
        if selection is not None:
            if instance.known_spells[selection].check_mana():
                if instance.known_spells[selection].cast():
                    return 'cast-spell'
                else:
                    return 'didnt-take-turn'
            else:
                ui.message("You don't have enough mana to cast that spell.", libtcod.light_blue)
                return 'didnt-take-turn'
    return 'didnt-take-turn'

def pick_up_mana(mana, obj):
    if obj is instance and len(instance.mana) < instance.player_stats.max_mana:
        instance.mana.append(mana.mana_type)
        ui.message('You are infused with magical power.', mana.color)
        mana.destroy()


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
    learned_skills = main.learned_skills

    instance.level += 1
    ui.message('You grow stronger! You have reached level ' + str(instance.level) + '!', libtcod.green)
    choice = None
    while choice == None:
        choice = ui.menu('Level up! Choose a stat to raise:\n',
        ['Constitution (+20 HP, from ' + str(instance.fighter.base_max_hp) + ')',
            'Strength (+1 attack, from ' + str(instance.fighter.base_power) + ')',
            'Agility (+1 defense, from ' + str(instance.fighter.base_defense) + ')',
            'Intelligence (increases spell damage)',
            'Wisdom (increases spell slots, spell utility)'
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

    if instance.level % 3 == 0:
        skill = ui.skill_menu(add_skill=True)
        if skill is not None and skill not in learned_skills:
            learned_skills.append(skill)

def on_death(instance):
    ui.message('You\'re dead, sucka.', libtcod.grey)
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
            success = instance.fighter.attack(target) != 'failed'
            if success and target.fighter:
                ui.select_monster(target)
        else:
            value = instance.move(dx, dy)
            return value

    return success


def dig(dx, dy):
    changed_tiles = main.changed_tiles

    dig_x = instance.x + dx
    dig_y = instance.y + dy
    if main.current_cell.map[dig_x][dig_y].diggable:
        main.current_cell.map[dig_x][dig_y].tile_type = 'stone floor'
        changed_tiles.append((dig_x, dig_y))
        if main.pathfinding.map:
            main.pathfinding.map.mark_passable((dig_x, dig_y))
        fov.set_fov_properties(dig_x, dig_y, False, main.current_cell.map[dig_x][dig_y].elevation)
        main.check_breakage(main.get_equipped_in_slot(instance.fighter.inventory, 'right hand'))
        return 'success'
    else:
        ui.message('You cannot dig there.', libtcod.lightest_gray)
        return 'failed'


def reach_attack(dx, dy):

    target_space = instance.x + 2 * dx, instance.y + 2 * dy
    target = main.get_monster_at_tile(target_space[0], target_space[1])
    if target is not None:
        result = instance.fighter.attack_ex(target, instance.fighter.calculate_attack_stamina_cost(), instance.fighter.accuracy,
                             instance.fighter.attack_damage * 1.5, instance.fighter.damage_variance, None, 'reach-attacks',
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
                instance.fighter.attack_ex(target, 0, instance.fighter.accuracy, instance.fighter.attack_damage,
                                 instance.fighter.damage_variance, None, 'cleaves', instance.fighter.attack_shred,
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
        result = instance.fighter.attack_ex(target, consts.BASH_STAMINA_COST, instance.fighter.accuracy * consts.BASH_ACC_MOD,
                                 instance.fighter.attack_damage * consts.BASH_DMG_MOD, instance.fighter.damage_variance,
                                 None, 'bashes', instance.fighter.attack_shred + 1, instance.fighter.attack_guaranteed_shred,
                                 instance.fighter.attack_pierce)
        if result == 'hit' and target.fighter:
            ui.select_monster(target)
            # knock the target back one space. Stun it if it cannot move.
            direction = target.x - instance.x, target.y - instance.y  # assumes the instance is adjacent
            stun = False
            against = ''
            against_tile = main.current_cell.map[target.x + direction[0]][target.y + direction[1]]
            if against_tile.blocks:
                stun = True
                against = main.current_cell.map[target.x + direction[0]][target.y + direction[1]].name
            elif against_tile.elevation != target.elevation and against_tile.tile_type != 'ramp' and main.current_cell.map[target.x][target.y] != 'ramp':
                stun = True
                against = 'cliff'
            else:
                for obj in main.current_cell.objects:
                    if obj.x == target.x + direction[0] and obj.y == target.y + direction[1] and obj.blocks:
                        stun = True
                        against = obj.name
                        break

            if stun:
                #  stun the target
                if target.fighter.apply_status_effect(effects.StatusEffect('stunned', time_limit=2, color=libtcod.light_yellow)):
                    ui.message('The ' + target.name + ' collides with the ' + against + ', stunning it!', libtcod.gold)
            else:
                ui.message('The ' + target.name + ' is knocked backwards.', libtcod.gray)
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
        interactable_here = main.get_objects(instance.x, instance.y, condition=lambda o:o.interact, distance=1) #get stuff that's adjacent too
        if len(interactable_here) > 0:
            interactable_here[0].interact(interactable_here[0])
            return 'interacted'
    return 'didnt-take-turn'

def meditate():
    ui.message('You tap into the magic of the world around you...', libtcod.dark_cyan)
    for i in range(consts.MEDITATE_CHANNEL_TIME - 1):
        instance.action_queue.append('channel-meditate')
    instance.action_queue.append('finish-meditate')
    return 'start-meditate'

def jump(actor=None):
    if not main.current_cell.map[instance.x][instance.y].jumpable:
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
        if main.current_cell.map[x][y].blocks:
            ui.message('There is something in the way.', libtcod.light_yellow)
            return 'didnt-take-turn'
        elif main.is_blocked(x, y, instance.elevation) and main.current_cell.map[x][y].elevation > instance.elevation:
            ui.message("You can't jump that high!", libtcod.light_yellow)
            return 'didnt-take-turn'
        else:
            jump_attack_target = None
            for obj in main.current_cell.objects:
                if obj.x == x and obj.y == y and obj.blocks:
                    jump_attack_target = obj
                    break
            if jump_attack_target is not None:
                # Jump attack
                land = main.land_next_to_target(jump_attack_target.x, jump_attack_target.y, instance.x, instance.y)
                if land is not None:
                    instance.set_position(land[0], land[1])
                    instance.fighter.adjust_stamina(-consts.JUMP_STAMINA_COST)

                    instance.fighter.attack_ex(jump_attack_target, 0, instance.fighter.accuracy * consts.JUMP_ATTACK_ACC_MOD,
                                             instance.fighter.attack_damage * consts.JUMP_ATTACK_DMG_MOD,
                                             instance.fighter.damage_variance, instance.fighter.on_hit, 'jump-attacks',
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