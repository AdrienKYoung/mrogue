

def channel(actor,delay,spell_name,delegate):
    is_player = actor is player.instance
    ui.message_flush(syntax.conjugate(is_player,['You begin',actor.name.capitalize() + ' begins']) + ' to cast ' + spell_name)
    if is_player:
        player.delay(delay,delegate,'channel-spell')
    else:
        actor.behavior.behavior.queue_action(delegate,delay)

def get_cast_time(actor,spell_name):
    base = abilities.data.get(spell_name).get('cast_time',0)
    if actor is None:
        actor = player.instance
        return main.clamp(base - int((actor.player_stats.int - 10) / 5) - main.has_skill('archmage'), 0, 5)
    else:
        return base

def attack(actor=None, target=None):
    x,y = ui.target_tile(max_range=1)
    target = None
    for object in main.current_map.fighters:
        if object.x == x and object.y == y:
            target = object
            break
    if target is not None and target is not player.instance:
        result = player.instance.fighter.attack(target)
        if result != 'failed':
            return result
    return 'didnt-take-turn'

def attack_reach(actor=None, target=None):
    x, y = ui.target_tile(max_range=1)
    target = None
    for object in main.current_map.fighters:
        if object.x == x and object.y == y:
            target = object
            break
    if target is not None and target is not player.instance:
        result = player.reach_attack(target.x - actor.x, target.y - actor.y)
        if result != 'failed':
            return result
    return 'didnt-take-turn'

def bash_attack(actor=None, target=None):
    x,y = ui.target_tile(max_range=1)
    target = None
    for object in main.current_map.fighters:
        if object.x == x and object.y == y:
            target = object
            break
    if target is not None and target is not player.instance:
        result = player.bash_attack(target.x - actor.x,target.y - actor.y)
        if result != 'failed':
            return result
    return 'didnt-take-turn'

def sweep_attack(actor=None, target=None):
    weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'right hand')
    ability_data = abilities.data['ability_sweep']

    if weapon is None or weapon.subtype != 'polearm':
        ui.message('You need a polearm to use this ability')
        return 'didnt-take-turn'

    targets = main.get_objects(actor.x,actor.y,distance=2, condition=lambda o: o.fighter is not None and o.fighter.team != 'ally')
    targets = [t for t in targets if (abs(t.x - actor.x) == 2 or abs(t.y - actor.y) == 2)]
    if len(targets) > 0:
        for enemy in targets:
            combat.attack_ex(actor.fighter,enemy,0, verb=('sweep','sweeps'))
        actor.fighter.adjust_stamina(-(weapon.stamina_cost * ability_data['stamina_multiplier']))
        return True
    else:
        ui.message('There are no targets in range')
        return 'didnt-take-turn'

#note: doesn't support unarmed attacks
def weapon_attack_ex(ability, actor, target):
    weapon = None
    ability_data = abilities.data[ability]

    if actor is None or actor is player.instance:
        actor = player.instance
        weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'right hand')

        require_weapon = ability_data.get('require_weapon')
        if require_weapon is not None and (weapon is None or weapon.subtype != require_weapon):
            ui.message('You need a {} to use that ability'.format(require_weapon), libtcod.yellow)
            return 'didnt-take-turn'

        x, y = ui.target_tile(max_range=ability_data.get('max_range',1))
        for object in main.current_map.fighters:
            if object.x == x and object.y == y:
                target = object
                break

        if target is None or target is player.instance:
            return 'didnt-take-turn'
    else:
        weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'right hand')

    if target is not None:

        on_hit = weapon.on_hit
        if ability_data.get('on_hit') is not None:
            on_hit.append(ability_data.get('on_hit'))

        damage_multiplier = ability_data.get('damage_multiplier',1)
        if callable(damage_multiplier):
            damage_multiplier = damage_multiplier(actor,target)

        result = combat.attack_ex(actor.fighter, target, int(weapon.stamina_cost * ability_data.get('stamina_multiplier',1)),
                                  accuracy_modifier=ability_data.get('accuracy_multiplier',1),
                                  damage_multiplier=damage_multiplier,
                                  guaranteed_shred_modifier=weapon.guaranteed_shred_bonus +
                                                            ability_data.get('guaranteed_shred_bonus',0),
                                  pierce_modifier=weapon.pierce_bonus + ability_data.get('pierce_bonus',0),
                                  shred_modifier=weapon.shred_bonus + ability_data.get('shred_bonus', 0),
                                  verb=ability_data.get('verb'), on_hit=on_hit)

        if result != 'failed' and result != 'didnt-take-turn':
            return result
    return 'didnt-take-turn'

#automates some nasty currying needed to pass ability into on_hit functions
def on_hit_tx(delegate,ability):
    return lambda a,b,c: delegate(ability,a,b,c)

def exhaust_self(ability,actor,*_):
    ability_data = abilities.data[ability]
    actor.fighter.apply_status_effect(effects.exhausted(ability_data['exhaustion_duration']))

def swap(actor,target,_):
    actor.swap_positions(target)

def berserk_self(actor=None, target=None):
    if actor is not None and actor.fighter is not None:
        if not actor.fighter.has_status('berserk') and not actor.fighter.has_status('exhausted'):
            actor.fighter.apply_status_effect(effects.berserk())
            if actor is not player.instance:
                ui.message('%s %s!' % (
                                syntax.name(actor.name).capitalize(),
                                syntax.conjugate(False, ('roar', 'roars'))), libtcod.red)
        else:
            if actor is player.instance:
                ui.message("You cannot go berserk right now.", libtcod.yellow)
            return 'didnt-take-turn'

def spawn_vermin(actor=None, target=None):
    #Filthy hackery to add some state
    if not hasattr(actor, 'summons'):
        actor.summons = []

    for s in actor.summons:  # clear dead things from summoned list
        if not s.fighter:
            actor.summons.remove(s)

    if len(actor.summons) < consts.VERMAN_MAX_SUMMONS:
        summon_choice = main.random_choice_index([e['weight'] for e in abilities.vermin_summons])
        summon_tiles = []
        for y in range(5):
            for x in range(5):
                pos = actor.x - 2 + x, actor.y - 2 + y
                if main.in_bounds(pos[0], pos[1]) and not main.is_blocked(pos[0], pos[1]):
                    summon_tiles.append(pos)
        for i in range(abilities.vermin_summons[summon_choice]['count']):
            if len(summon_tiles) > 0:
                pos = summon_tiles[libtcod.random_get_int(0, 0, len(summon_tiles) - 1)]
                spawn = main.spawn_monster(abilities.vermin_summons[summon_choice]['monster'], pos[0], pos[1])
                ui.message('A ' + spawn.name + " crawls from beneath the verman's cloak.", actor.color)
                spawn.fighter.loot_table = None
                actor.summons.append(spawn)
                summon_tiles.remove(pos)

def raise_zombie(actor=None, target=None):

    check_corpse = main.adjacent_tiles_diagonal(actor.x, actor.y)
    check_corpse.append((actor.x, actor.y))
    corpse = None
    for tile in check_corpse:
        corpses_here = main.get_objects(tile[0], tile[1], lambda o: o.name.startswith('remains of'))
        if len(corpses_here) > 0:
            corpse = corpses_here[0]
            break

    if corpse is not None:
        spawn_tile = main.find_closest_open_tile(corpse.x, corpse.y)
        ui.message('A dark aura emanates from the necroling... a corpse walks again.', libtcod.dark_violet)
        main.spawn_monster('monster_rotting_zombie', spawn_tile[0], spawn_tile[1])
        corpse.destroy()
        return 'rasied-zombie'
    else:
        return 'didnt-take-turn'


def fireball(actor=None, target=None):
    channel(actor, get_cast_time(actor,'ability_fireball'), 'fireball', lambda: _continuation_fireball(actor, target))

def _continuation_fireball(actor, target):
    x, y = 0, 0
    spell = abilities.data['ability_fireball']
    if actor is player.instance:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
    else:
        x = target.x
        y = target.y
    if x is None: return 'cancelled'
    ui.message('The fireball explodes!', libtcod.flame)
    for obj in main.current_map.fighters:
        if obj.distance(x, y) <= spell['radius']:
            combat.spell_attack(actor.fighter, obj, 'ability_fireball')
            obj.fighter.apply_status_effect(effects.burning())
    return 'success'

def arcane_arrow(actor=None, target=None):
    spell = abilities.data['ability_arcane_arrow']
    x, y = 0, 0
    if actor is None or actor is player.instance:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(spell['range'], 'beam_interrupt', default_target=default_target)
        actor = player.instance
    else:
        x = target.x
        y = target.y
    if x is None: return 'cancelled'
    line = main.beam(actor.x, actor.y, x, y)
    if line is None or len(line) < 1: return 'cancelled'

    ui.render_projectile((actor.x, actor.y), (x, y), libtcod.fuchsia, None)

    for l in line:
        for obj in main.current_map.fighters:
            if obj.x == l[0] and obj.y == l[1]:
                combat.spell_attack(actor.fighter, obj,'ability_arcane_arrow')
                return 'success'
    return 'failure'

def smite(actor=None, target=None):
    spell = abilities.data['ability_smite']
    x, y = 0, 0
    if actor is None or actor is player.instance:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        target = main.get_monster_at_tile(*ui.target_tile(spell['range'],'pick', default_target=default_target))
        actor = player.instance

    if target is None: return 'cancelled'

    combat.spell_attack(actor.fighter, target,'ability_smite')
    return 'success'

def heat_ray(actor=None, target=None):
    spell = abilities.data['ability_heat_ray']
    line = None
    if actor is None:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(spell['range'], 'beam_interrupt', default_target=default_target)
        actor = player.instance
    else:
        x = target.x
        y = target.y
    if x is None: return 'cancelled'
    line = main.beam(actor.x, actor.y, x, y)
    if line is None or len(line) < 1: return 'cancelled'

    for obj in main.current_map.fighters:
        for l in line:
            if obj.x == l[0] and obj.y == l[1]:
                combat.spell_attack(actor.fighter, obj,'ability_heat_ray')
    return 'success'


def flame_wall(actor=None, target=None):
    x, y = 0, 0
    if actor is None:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        (x, y) = ui.target_tile()
        if x is None:
            return 'cancelled'
        actor = player.instance
    else:
        x = target.x
        y = target.y
    if x is not None:
        main.create_fire(x, y, 10)
        return 'success'
    return 'failure'


def shatter_item(actor=None, target=None):
    x, y = 0, 0
    dc = 8
    if actor is None:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        (x, y) = ui.target_tile()
        if x is None:
            return 'cancelled'
        actor = player.instance
        choices = main.get_objects(x, y)
        if len(choices) > 1:
            target = choices[ui.menu('Which target?', [i.name for i in choices], 24)]
        elif len(choices) > 0:
            target = choices[0]
        else:
            return 'cancelled'
        dc += 4
    else:
        x, y = target.x, target.y

    if target is None:
        return 'cancelled'
    item = None
    inventory = None
    if target.fighter is not None:
        inventory = target.fighter.inventory
        if inventory is None or len(inventory) == 0:
            if actor == player.instance:
                ui.message('Target has no items', libtcod.light_blue)
            return 'cancelled'
        item = inventory[main.random_choice_index(inventory)]
        dc += 5
    elif target.item is not None:
        item = target

    if main.roll_dice('1d20') + main.roll_dice('1d{}'.format(actor.fighter.spell_power)) > dc:
        ui.message("{} shatters into pieces!".format(item.name), libtcod.flame)
        if inventory is not None:
            inventory.remove(item)
        item.destroy()
        for obj in main.current_map.fighters:
            if obj.distance(x, y) <= consts.FIREBALL_RADIUS:
                combat.spell_attack_ex(actor.fighter, obj, None, 'shrapnel', '4d4', 1, 'slashing', 0)
        return 'success'
    else:
        ui.message("Shatter failed to break {}!".format(item), libtcod.yellow)
        return 'success'


def magma_bolt(actor=None, target=None):
    spell = abilities.data['ability_magma_bolt']
    x, y = 0, 0
    if actor is None:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        (x, y) = ui.target_tile(max_range=spell['range'])
        actor = player.instance
        if x is None: return 'cancelled'
        target = main.get_monster_at_tile(x, y)
    else:
        x = target.x
        y = target.y
    if target is not None:
        combat.spell_attack(actor.fighter, target,'ability_magma_bolt')
    main.current_map.tiles[x][y].tile_type = 'lava'
    main.current_map.pathfinding.mark_blocked((x, y))
    main.changed_tiles.append((x, y))


def confuse():
    ui.message('Choose a target with left-click, or right-click to cancel.', libtcod.white)
    ui.render_message_panel()
    libtcod.console_flush()
    monster = main.target_monster(consts.CONFUSE_RANGE)
    if monster is None or monster.behavior is None:
        return 'cancelled'
    else:
        if monster.fighter.apply_status_effect(
                effects.StatusEffect('confusion', consts.CONFUSE_NUM_TURNS, color=libtcod.pink,
                                     on_apply=_set_confused_behavior)):
            ui.message('%s %s confused!' % (
                syntax.name(monster.name).capitalize(),
                syntax.conjugate(monster is player.instance, ('are', 'is'))), libtcod.light_blue)

def silence(actor=None,target=None):
    if actor is None:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        target = main.get_monster_at_tile(*ui.target_tile(abilities.data['ability_silence']['range'], 'pick', default_target=default_target))

    if target is None:
        return 'cancelled'
    elif target.fighter.apply_status_effect(effects.silence(),True):
        ui.message('%s %s silenced!' % (
            syntax.name(target.name).capitalize(),
            syntax.conjugate(target is player.instance, ('are', 'is'))), libtcod.light_blue)

def _set_confused_behavior(object):
    if object.behavior is not None:
        old_ai = object.behavior.behavior
        object.behavior.behavior = ai.ConfusedMonster(old_ai)
        object.behavior.behavior.owner = object

def heal():
    if player.instance.fighter.hp == player.instance.fighter.max_hp:
        ui.message('You are already at full health.', libtcod.white)
        return 'cancelled'

    ui.message('You feel better.', libtcod.white)
    player.instance.fighter.heal(consts.HEAL_AMOUNT)


def waterbreathing():
    player.instance.fighter.apply_status_effect(effects.StatusEffect('waterbreathing', 31, libtcod.light_azure))


def shielding():
    player.instance.fighter.shred = 0
    player.instance.fighter.apply_status_effect(effects.StatusEffect('shielded', 21, libtcod.dark_blue))


def frog_tongue(actor, target):
    if actor.distance_to(target) <= consts.FROG_TONGUE_RANGE and fov.monster_can_see_object(actor, target):
        if target.fighter.hp > 0 and main.beam_interrupt(actor.x, actor.y, target.x, target.y) == (target.x, target.y):
            ui.message("The frog's tongue lashes out at you!", libtcod.dark_green)
            result = combat.attack_ex(actor.fighter, target, 0, accuracy_modifier=1.5, damage_multiplier=1.5, verb=('pull', 'pulls'))
            if result == 'hit':
                beam = main.beam(actor.x, actor.y, target.x, target.y)
                pull_to = beam[max(len(beam) - 3, 0)]
                target.set_position(pull_to[0], pull_to[1])
            return 'success'
    return 'didnt-take-turn'

def ignite():
    target = ui.target_tile(consts.IGNITE_RANGE)
    if target[0] is not None and target[1] is not None:
        tile = main.current_map.tiles[target[0]][target[1]]
        if tile.blocks:
            ui.message('The ' + tile.name + ' is in the way.', libtcod.gray)
            return False
        elif tile.tile_type == 'shallow water' or tile.tile_type == 'deep water':
            ui.message('You cannot ignite water.', libtcod.gray)
            return False
        obj = main.get_objects(target[0], target[1], lambda o: o.blocks)
        if len(obj) > 0:
            ui.message('%s %s in the way' % (
                syntax.name(obj[0].name).capitalize(),
                syntax.conjugate(obj[0] is player.instance, ('are', 'is'))), libtcod.gray)
            return False
        ui.message('You conjure a spark of flame, igniting the ' + tile.name + '!', libtcod.flame)
        main.create_fire(target[0], target[1], 10)
        return True
    return False

def dig(dx, dy):
    import player, dungeon
    changed_tiles = main.changed_tiles

    dig_x = player.instance.x + dx
    dig_y = player.instance.y + dy
    change_type = dungeon.branches[main.current_map.branch]['default_floor']
    if main.current_map.tiles[dig_x][dig_y].elevation != main.current_map.tiles[player.instance.x][player.instance.y].elevation:
        change_type = dungeon.branches[main.current_map.branch]['default_ramp']
    if main.current_map.tiles[dig_x][dig_y].diggable:
        main.current_map.tiles[dig_x][dig_y].tile_type = change_type
        changed_tiles.append((dig_x, dig_y))
        if main.current_map.pathfinding:
            main.current_map.pathfinding.mark_unblocked((dig_x, dig_y))
        fov.set_fov_properties(dig_x, dig_y, False)
        fov.set_fov_recompute()
        main.check_breakage(main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand'))
        return 'success'
    else:
        ui.message('You cannot dig there.', libtcod.lightest_gray)
        return 'failed'

forge_targets = ['weapon','armor']

def forge():
    import loot
    choices = [i for i in player.instance.fighter.inventory if i.equipment is not None and i.equipment.category in forge_targets]

    if len(choices) < 1:
        ui.message('You have no items to forge.',libtcod.orange)
        return 'didnt-take-turn'

    index = ui.menu('Forge what?',[c.name for c in choices])
    if index is None:
        ui.message('Cancelled.',libtcod.orange)
        return 'didnt-take-turn'
    target = choices[index].equipment

    if target.quality == 'artifact':
        ui.message('Your ' + target.owner.name + ' shimmers briefly. It cannot be improved further by this magic.',
                   libtcod.orange)
    elif target.category == 'weapon' and target.material == '': #can't forge summoned weapons
        ui.message('The %s cannot be altered by this magic.' % target.owner.name, libtcod.orange)
    else:
        ui.message('Your ' + target.owner.name + ' glows bright orange!', libtcod.orange)

        index = loot.quality_progression.index(target.quality)
        new_quality = loot.quality_progression[index + 1]
        main.set_quality(target, new_quality)
        ui.message('It is now a ' + target.owner.name + '.', libtcod.orange)
    return True

def aquatic(target):
    import pathfinding
    target.movement_type = target.movement_type | pathfinding.AQUATIC

def flight(target):
    import pathfinding
    target.movement_type = target.movement_type | pathfinding.FLYING

def auto_res(target):
    target.fighter.apply_status_effect(effects.auto_res())

def lichform(target):
    target.fighter.max_hp = int(target.fighter.max_hp * 0.7)
    target.fighter.hp = min(target.fighter.hp,target.fighter.max_hp)
    target.fighter.apply_status_effect(effects.lichform())

def gaze_into_the_void(target):
    for i in range(3): player.pick_up_essence('void',player.instance)

def skullsplitter_calc_damage_bonus(actor,target):
    return 1.5 * ( 2 - target.fighter.hp / target.fighter.max_hp)

def summon_guardian_angel():
    adj = main.adjacent_tiles_diagonal(player.instance.x, player.instance.y)

    # Get viable summoning position. Return failure if no position is available
    summon_positions = []
    for tile in adj:
        if not main.is_blocked(tile[0], tile[1]):
            summon_positions.append(tile)
    if len(summon_positions) == 0:
        return 'failed'
    summon_pos = summon_positions[libtcod.random_get_int(0, 0, len(summon_positions) - 1)]

    # Select monster type - default to goblin
    summon_type = 'monster_guardian_angel'
    summon = main.spawn_monster(summon_type, summon_pos[0], summon_pos[1], team='ally')
    summon.behavior.follow_target = player.instance

    # Set summon duration
    summon.summon_time = 30 + libtcod.random_get_int(0, 0, 15)
    ui.message('Your prayers have been answered!',libtcod.light_blue)
    return 'success'

def summon_roaches(actor, attacker, damage):
    if not hasattr(actor, 'summon_limit') or not hasattr(actor, 'summons'):
        actor.summon_limit = 8
        actor.summons = []
    remove = []
    for s in actor.summons:
        if s.fighter is None or not s in main.current_map.fighters:
            remove.append(s)
    for s in remove:
        actor.summons.remove(s)

    if len(actor.summons) >= actor.summon_limit:
        return
    if fov.player_can_see(actor.x, actor.y):
        ui.message('Cockroaches crawl from %s wounds!' % syntax.name(actor.name, possesive=True), libtcod.dark_magenta)
    for adj in main.adjacent_tiles_diagonal(actor.x, actor.y):
        if len(actor.summons) >= actor.summon_limit:
            break
        if not main.is_blocked(adj[0], adj[1]) and libtcod.random_get_int(0, 1, 10) <= 5:
            actor.summons.append(main.spawn_monster('monster_cockroach', adj[0], adj[1]))

def potion_essence(essence):
    return lambda : player.pick_up_essence(essence,player.instance)

def charm_resist():
    if len(player.instance.essence) < 1:
        ui.message("You don't have any essence.", libtcod.light_blue)
        return 'didnt-take-turn'
    essence = ui.choose_essence_from_pool()
    if essence is None:
        return 'didnt-take-turn'
    player.instance.fighter.apply_status_effect(effects.resistant(element=essence))
    if essence in spells.charm_resist_extra_resists:
        for effect in spells.charm_resist_extra_resists[essence]:
            player.instance.fighter.apply_status_effect(effects.resistant(effect=effect,color=spells.essence_colors[essence]),supress_message=True)
    player.instance.essence.remove(essence)

def charm_summoning():
    if len(player.instance.essence) < 1:
        ui.message("You don't have any essence.", libtcod.light_blue)
        return 'didnt-take-turn'
    adj = main.adjacent_tiles_diagonal(player.instance.x, player.instance.y)

    # Get viable summoning position. Return failure if no position is available
    summon_positions = []
    for tile in adj:
        if not main.is_blocked(tile[0], tile[1]):
            summon_positions.append(tile)
    if len(summon_positions) == 0:
        ui.message('There is no room to summon an ally here.')
        return
    summon_pos = summon_positions[libtcod.random_get_int(0, 0, len(summon_positions) - 1)]

    # Select essence
    essence = ui.choose_essence_from_pool()
    if essence is None:
        return 'didnt-take-turn'
    player.instance.essence.remove(essence)

    # Select monster type - default to goblin
    summon_type = 'monster_goblin'
    import monsters
    if essence in spells.charm_summoning_summons.keys() and spells.charm_summoning_summons[essence]['summon'] in monsters.proto.keys():
        summon_type = spells.charm_summoning_summons[essence]['summon']
    summon = main.spawn_monster(summon_type, summon_pos[0], summon_pos[1], team='ally')
    summon.behavior.follow_target = player.instance

    # Set summon duration
    t = spells.charm_summoning_summons[essence]['duration']
    summon.summon_time = t + libtcod.random_get_int(0, 0, t)

def charm_blessing():
    if len(player.instance.essence) < 1:
        ui.message("You don't have any essence.", libtcod.light_blue)
        return 'didnt-take-turn'
    essence = ui.choose_essence_from_pool()
    if essence is None:
        return 'didnt-take-turn'
    player.instance.fighter.apply_status_effect(spells.charm_blessing_effects[essence]['buff']())
    player.instance.essence.remove(essence)

def charm_battle():
    if len(player.instance.essence) < 1:
        ui.message("You don't have any essence.", libtcod.light_blue)
        return 'didnt-take-turn'
    elif len(player.instance.fighter.inventory) >= 26:
        ui.message('You are carrying too many items to summon another.')
        return 'didnt-take-turn'
    essence = ui.choose_essence_from_pool()
    if essence is None:
        return 'didnt-take-turn'
    summoned_weapon = main.create_item(spells.charm_battle_effects[essence]['weapon'], material='', quality='')
    if summoned_weapon is None:
        return
    expire_ticker = type('', (), {})()  # Create an empty object for duck typing
    equipped_weapon = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
    expire_ticker.old_weapon = equipped_weapon
    if summoned_weapon.equipment.slot == 'both hands':
        expire_ticker.old_left = main.get_equipped_in_slot(player.instance.fighter.inventory, 'left hand')
    else:
        expire_ticker.old_left = None
    if equipped_weapon is not None:
        equipped_weapon.dequip()
    summoned_weapon.item.pick_up(player.instance)
    expire_ticker.weapon = summoned_weapon
    expire_ticker.max_ticks = 15
    effect = effects.StatusEffect('summoned weapon', expire_ticker.max_ticks + 1, summoned_weapon.color)
    player.instance.fighter.apply_status_effect(effect)
    expire_ticker.effect = effect
    expire_ticker.ticks = 0
    expire_ticker.on_tick = charm_battle_on_tick
    main.current_map.tickers.append(expire_ticker)
    player.instance.essence.remove(essence)

def charm_battle_on_tick(ticker):
    dead_flag = False
    dropped = False
    if not ticker.weapon.equipment.is_equipped:
        ui.message('The %s fades away as you release it from your grasp.' % ticker.weapon.name.title(), libtcod.light_blue)
        dead_flag = True
        dropped = True
    elif ticker.ticks > ticker.max_ticks:
        dead_flag = True
        ui.message("The %s fades away as it's essence depletes." % ticker.weapon.name.title(), libtcod.light_blue)
    if dead_flag:
        ticker.dead = True
        ticker.weapon.item.drop(no_message=True)
        ticker.weapon.destroy()
        player.instance.fighter.remove_status('summoned weapon')
        if not dropped:
            if ticker.old_weapon is not None:
                ticker.old_weapon.equip()
            if ticker.old_left is not None:
                ticker.old_left.equip()


import libtcodpy as libtcod
import game as main
import consts
import syntax
import fov
import abilities
import effects
import spells
import ui
import ai
import player
import combat
