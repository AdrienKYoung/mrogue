#mrogue, an interactive adventure game
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

import consts

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

# todo: make more interesting
def essence_fist(actor=None, target=None):
    ability_data = abilities.data['ability_essence_fist']
    x,y = ui.target_tile(max_range=1)
    if x is None:
        return 'didnt-take-turn'

    ops = player.instance.essence
    choice = ui.menu('Which essence?',ops)
    if choice is not None:
        essence = ops[choice]
    else:
        return "didnt-take-turn"

    target = None
    for object in main.current_map.fighters:
        if object.x == x and object.y == y:
            target = object
            break
    if target is not None and target is not player.instance:
        result = combat.attack_ex(player.instance.fighter,target,ability_data['stamina_cost'],damage_multiplier=ability_data['damage_multiplier'])
        if result != 'failed':
            player.instance.essence.remove(essence)
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

        shred_bonus = ability_data.get('shred_bonus',0)
        if callable(shred_bonus):
            shred_bonus = shred_bonus(actor,target)

        result = combat.attack_ex(actor.fighter, target, int(weapon.stamina_cost * ability_data.get('stamina_multiplier',1)),
                                  accuracy_modifier=ability_data.get('accuracy_multiplier',1),
                                  damage_multiplier=damage_multiplier,
                                  guaranteed_shred_modifier=weapon.guaranteed_shred_bonus +
                                                            ability_data.get('guaranteed_shred_bonus',0),
                                  pierce_modifier=weapon.pierce_bonus + ability_data.get('pierce_bonus',0),
                                  shred_modifier=weapon.shred_bonus + shred_bonus,
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

def mace_stun(attacker, target, damage):
    scaling_factor = 1
    stun_duration = 2
    if target.fighter is None:
        return
    if(attacker is player.instance):
        scaling_factor = attacker.player_stats.str / 10
        if main.has_skill('ringing_blows'):
            scaling_factor *= 1.5
            stun_duration = 3
    if libtcod.random_get_float(0,0.0,1.0) * scaling_factor > 0.85:
        if attacker == player.instance:
            ui.message("Your " + main.get_equipped_in_slot(player.instance.fighter.inventory,'right hand').owner.name.title() + " rings out!",libtcod.blue)
        target.fighter.apply_status_effect(effects.stunned())

def berserk_self(actor=None, target=None):
    if actor is not None and actor.fighter is not None:
        if not actor.fighter.has_status('berserk') and not actor.fighter.has_status('exhausted'):
            actor.fighter.apply_status_effect(effects.berserk())
            if actor is not player.instance:
                ui.message('%s %s!' % (
                                syntax.name(actor).capitalize(),
                                syntax.conjugate(False, ('roar', 'roars'))), libtcod.red)
            return 'success'
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
    if actor is None:
        actor = player.instance
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
        ui.message('A dark aura emanates from %s... a corpse walks again.' % syntax.name(actor), libtcod.dark_violet)
        zombie = main.spawn_monster('monster_rotting_zombie', spawn_tile[0], spawn_tile[1])
        if actor is player.instance:
            zombie.fighter.team = 'ally'
            zombie.behavior.follow_target = player.instance
        corpse.destroy()
        return 'rasied-zombie'
    else:
        return 'didnt-take-turn'


def fireball(actor=None, target=None):
    if actor is None:
        actor = player.instance
    channel(actor, get_cast_time(actor,'ability_fireball'), 'fireball', lambda: _continuation_fireball(actor, target))
    return 'success'

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
            if obj.fighter is not None:
                obj.fighter.apply_status_effect(effects.burning())
    for _x in range(x - 1, x + 2):
        for _y in range(y - 1, y + 2):
            main.melt_ice(_x, _y)
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
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        target = main.get_monster_at_tile(*ui.target_tile(spell['range'],'pick', default_target=default_target))
        actor = player.instance

    if target is None: return 'cancelled'

    combat.spell_attack(actor.fighter, target,'ability_smite')
    return 'success'

def heat_ray(actor=None, target=None):
    spell = abilities.data['a' \
                           'bility_heat_ray']
    line = None
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        tiles = ui.target_tile(spell['range'], 'beam', default_target=default_target)
        actor = player.instance
    else:
        x = target.x
        y = target.y
        tiles = main.beam(actor.x, actor.y, x, y)
    if tiles is None or len(tiles) < 1 or tiles[0] is None or tiles[0][0] is None: return 'cancelled'
    end = (tiles[len(tiles) - 1][0], tiles[len(tiles) - 1][1])
    ui.render_projectile((actor.x, actor.y), end, libtcod.flame, libtcod.CHAR_BLOCK3)

    for obj in main.current_map.fighters:
        for l in tiles:
            if obj.x == l[0] and obj.y == l[1]:
                combat.spell_attack(actor.fighter, obj,'ability_heat_ray')

    main.melt_ice(end[0], end[1])

    return 'success'


def flame_wall(actor=None, target=None):
    x, y = 0, 0
    spell = abilities.data['ability_flame_wall']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
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
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
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
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
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
    return 'success'

def frozen_orb(actor=None, target=None):
    spell = abilities.data['ability_frozen_orb']
    x, y = 0, 0
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
        actor = player.instance
        if x is None: return 'cancelled'
        target = main.get_monster_at_tile(x, y)
    if target is not None:
        if combat.spell_attack(actor.fighter, target,'ability_frozen_orb') == 'hit' and target.fighter is not None:
            target.fighter.apply_status_effect(effects.slowed())

def flash_frost(actor=None, target=None):
    spell = abilities.data['ability_flash_frost']
    x, y = 0, 0
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
        actor = player.instance
        if x is None: return 'cancelled'
        target = main.get_monster_at_tile(x, y)
    if target is not None:
        target.fighter.apply_status_effect(effects.frozen(5))
        if actor is player.instance or fov.player_can_see(target.x, target.y):
            ui.message('%s %s frozen solid!' %
                       (syntax.name(target).capitalize(),
                        syntax.conjugate(target is player.instance, ('are', 'is'))),
                        spells.essence_colors['cold'])
        return 'success'
    else:
        if actor is player.instance:
            ui.message('There is no one to freeze here.', libtcod.gray)
        return 'didnt-take-turn'

def ice_shards(actor=None, target=None):
    x, y = 0, 0
    if actor is None:
        actor = player.instance
    spell = abilities.data['ability_ice_shards']
    if actor is player.instance:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        tiles = ui.target_tile(max_range=spell['range'], targeting_type='cone')
    else:
        tiles = [(target.x, target.y)]
        x = target.x
        y = target.y
    if tiles is None or len(tiles) == 0 or tiles[0] is None or tiles[1] is None: return 'cancelled'
    for tile in tiles:
        reed = main.object_at_tile(tile[0], tile[1], 'reeds')
        if reed is not None:
            reed.destroy()
        for obj in main.current_map.fighters:
            if obj.x == tile[0] and obj.y == tile[1]:
                combat.spell_attack(actor.fighter, obj, 'ability_ice_shards')
                if obj.fighter is not None:
                    obj.fighter.apply_status_effect(effects.slowed())
                    obj.fighter.apply_status_effect(effects.bleeding())
    return 'success'

def snowstorm(actor=None, target=None):
    x, y = 0, 0
    spell = abilities.data['ability_snowstorm']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
        if x is None:
            return 'cancelled'
        actor = player.instance
    else:
        x = target.x
        y = target.y
    if x is not None:
        zone = main.Zone(spell['radius'],_snowstorm_tick,_snowstorm_tick)
        storm = main.GameObject(x,y,'@','Snowstorm',libtcod.light_azure,zones=[zone],summon_time=10)
        storm.creator = actor
    return 'failure'

def _snowstorm_tick(actor,target):
    if main.roll_dice('1d10' > 7):
        combat.spell_attack(actor.owner.creator.fighter,target,'ability_snowstorm')
        target.fighter.apply_status_effect(effects.slowed())
        target.fighter.apply_status_effect(effects.blinded())
        fx = main.GameObject(target.x,target.y,'*','cloud of cold',libtcod.light_azure,summon_time=2)
        main.current_map.objects.append(fx)

def hex(actor=None,target=None):
    x, y = 0, 0
    spell = abilities.data['ability_hex']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(max_range=spell['range'], default_target=default_target)
        if x is None: return 'cancelled'
        actor = player.instance
        target = main.get_monster_at_tile(x, y)
    if target is not None:
        target.fighter.apply_status_effect(effects.cursed())
    return 'success'

def defile(actor=None,target=None):
    x, y = 0, 0
    spell = abilities.data['ability_defile']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(max_range=spell['range'], default_target=default_target)
        if x is None: return 'cancelled'
        actor = player.instance
        target = main.object_at_coords(x, y)
    if target is not None:
        if target.is_corpse:
            main.raise_dead(actor,target)
        elif target.fighter is not None and (target.fighter.subtype == 'undead' or target.fighter.subtype == 'fiend'):
            target.fighter.heal(int(target.fighter.max_hp / 3))
            ui.message("Dark magic strengthens {}!".format(target.name))
        elif target.fighter is not None:
            combat.spell_attack(actor.fighter, target, 'ability_defile')
    return 'success'

def shackles_of_the_dead(actor=None,target=None):
    x, y = 0, 0
    spell = abilities.data['ability_defile']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(max_range=spell['range'], default_target=default_target)
        if x is None: return 'cancelled'
        actor = player.instance
    else:
        x = target.x
        y = target.y

    for (_x,_y) in main.adjacent_tiles_diagonal(x,y):
        obj = main.get_monster_at_tile(_x,_y)
        if obj is not None:
            obj.fighter.apply_status_effect(effects.immobilized())
    return 'success'

def sacrifice(actor=None,target=None):
    if actor is None:
        actor = player.instance

    spell = abilities.data['ability_sacrifice']
    actor.fighter.take_damage(min(30,int(actor.fighter.hp / 2)))
    damage_mod = int((actor.fighter.max_hp - actor.fighter.hp )/ actor.fighter.max_hp)

    for (_x,_y) in main.adjacent_tiles_diagonal(actor.x,actor.y):
        obj = main.get_monster_at_tile(_x,_y)
        if obj is not None and obj.fighter.team == 'enemy':
            combat.spell_attack_ex(actor.fighter,obj,None,spell['base_damage'],0,'death',spell['pierce'],0,1 + damage_mod)
    return 'success'

def corpse_dance(actor=None,target=None):
    x, y = 0, 0
    spell = abilities.data['ability_corpse_dance']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
        if x is None: return 'cancelled'
        actor = player.instance
    else:
        x = target.x
        y = target.y

    for (_x, _y) in main.adjacent_tiles_diagonal(x, y):
        objects = main.get_objects(_x,_y,None,spell['radius'])
        for o in objects:
            if o is not None and o.is_corpse:
                main.raise_dead(actor,o)

        obj = main.get_monster_at_tile(_x, _y)
        if obj is not None and obj.fighter.team == 'ally' and obj.fighter.subtype == 'undead':
            obj.fighter.apply_status_effect(effects.swiftness(spell['buff_duration']))
            obj.fighter.apply_status_effect(effects.berserk(spell['buff_duration']))
    return 'success'

def battle_cry(actor=None,target=None):
    if actor is None:
        actor = player.instance

    for unit in main.current_map.fighters:
        if unit.fighter.team != actor.fighter.team:
            unit.fighter.apply_status_effect(effects.cursed(20))
            if unit.behavior is not None and hasattr(unit.behavior,'ai_state'):
                unit.behavior.ai_state = 'pursuing'
                unit.behavior.last_seen_position = player.instance.x, player.instance.y

    ui.message("{} {} out a battle cry!".format(
        syntax.conjugate(actor is player.instance,['You',actor.name]),
        syntax.conjugate(actor is player.instance,['let','lets'])
    ))

    return 'success'

def mass_heal(actor=None,target=None):
    if actor is None:
        actor = player.instance

    for unit in main.current_map.fighters:
        if unit.fighter.team == actor.fighter.team:
            unit.fighter.apply_status_effect(effects.regeneration())
            amount = int(round(0.25 * unit.fighter.max_hp))
            unit.fighter.heal(amount)
            ui.message("{} {} healed!".format(syntax.conjugate(unit is player.instance,['You',unit.name]),
                       syntax.conjugate(unit is player.instance,['were','was'])), libtcod.white)
    return 'success'

def mass_cleanse(actor=None,target=None):
    if actor is None:
        actor = player.instance

    for unit in main.current_map.fighters:
        if unit.fighter.team == actor.fighter.team:
            effects = list(player.instance.fighter.status_effects)
            for status in effects:
                if status.cleanseable:
                    player.instance.fighter.remove_status(status.name)
    return 'success'

def mass_reflect(actor=None,target=None):
    if actor is None:
        actor = player.instance

    for unit in main.current_map.fighters:
        if unit.fighter.team == actor.fighter.team:
            unit.fighter.apply_status_effect(effects.reflect_magic())
    return 'success'

def knock_back(actor,target):
    # knock the target back one space. Stun it if it cannot move.
    direction = target.x - actor.x, target.y - actor.y  # assumes the instance is adjacent
    stun = False
    against = ''
    against_tile = main.current_map.tiles[target.x + direction[0]][target.y + direction[1]]
    if against_tile.blocks:
        stun = True
        against = main.current_map.tiles[target.x + direction[0]][target.y + direction[1]].name
    elif against_tile.elevation != target.elevation and against_tile.tile_type != 'ramp' and \
                    main.current_map.tiles[target.x][target.y] != 'ramp':
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
        if target.fighter.apply_status_effect(
                effects.StatusEffect('stunned', time_limit=2, color=libtcod.light_yellow)):
            ui.message('%s %s with the %s, stunning %s!' % (
                syntax.name(target).capitalize(),
                syntax.conjugate(target is actor, ('collide', 'collides')),
                against,
                syntax.pronoun(target.name, objective=True)), libtcod.gold)
    else:
        ui.message('%s %s knocked backwards.' % (
            syntax.name(target).capitalize(),
            syntax.conjugate(target is actor, ('are', 'is'))), libtcod.gray)
        target.set_position(target.x + direction[0], target.y + direction[1])
        main.render_map()
        libtcod.console_flush()

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
                syntax.name(monster).capitalize(),
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
            syntax.name(target).capitalize(),
            syntax.conjugate(target is player.instance, ('are', 'is'))), libtcod.light_blue)

def check_doom(obj=None):
    fx = [f for f in obj.fighter.status_effects if f.name == 'doom']
    if len(fx) > 0 and fx[0].stacks >= 13:
        ui.message("Death comes for {}".format(obj.name),libtcod.dark_crimson)
        obj.fighter.take_damage(obj.fighter.max_hp)

def blade_dance(actor=None, target=None):
    if actor is None or actor is player.instance: # player is casting
        #check for equipped sword
        weapon = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
        if weapon is None or weapon.subtype != 'sword':
            ui.message('You cannot do that without a sword.', libtcod.white)
            return 'didnt-take-turn'

        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        target = main.get_monster_at_tile(
            *ui.target_tile(abilities.data['ability_blade_dance']['range'], 'pick', default_target=default_target))
    else:
        target = main.get_monster_at_tile(target[0], target[1])

    if target is None:
        return 'didnt-take-turn'
    else:
        actor.swap_positions(target)
        actor.fighter.attack(target)

def pommel_strike(actor=None, target=None):
    if actor is None or actor is player.instance: # player is casting
        #check for equipped sword
        weapon = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
        if weapon is None or weapon.subtype != 'sword':
            ui.message('You cannot do that without a sword.', libtcod.white)
            return 'didnt-take-turn'

        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        target = main.get_monster_at_tile(
            *ui.target_tile(abilities.data['ability_pommel_strike']['range'], 'pick', default_target=default_target))
    else:
        target = main.get_monster_at_tile(target[0], target[1])

    if target is None:
        return 'didnt-take-turn'
    else:
        combat.attack_ex(actor.fighter, target, int(actor.fighter.calculate_attack_stamina_cost() * 1.5),
                         verb=('pommel-strike', 'pommel-strikes'), shred_modifier=2)

def _set_confused_behavior(object):
    if object.behavior is not None:
        old_ai = object.behavior.behavior
        object.behavior.behavior = ai.ConfusedMonster(old_ai)
        object.behavior.behavior.owner = object

def heal(amount=consts.HEAL_AMOUNT, use_percentage=False):
    if use_percentage:
        amount = int(round(amount * player.instance.fighter.max_hp))
    if player.instance.fighter.hp == player.instance.fighter.max_hp:
        ui.message('You are already at full health.', libtcod.white)
        return 'cancelled'

    ui.message('You feel better.', libtcod.white)
    player.instance.fighter.heal(amount)


def waterbreathing():
    player.instance.fighter.apply_status_effect(effects.StatusEffect('waterbreathing', 31, libtcod.light_azure))


def hardness(actor=None):
    if actor is None:
        actor = player.instance
    if actor.fighter is None:
        return 'failure'
    actor.fighter.shred = 0
    actor.fighter.apply_status_effect(effects.stoneskin(21))
    if actor is player.instance or fov.player_can_see(actor.x, actor.y):
        ui.message('%s armor is repaired and %s skin becomes as hard as stone.' % (
            syntax.name(actor, possesive=True).capitalize(),
            syntax.pronoun(actor.name, possesive=True)),
            spells.essence_colors['earth'])
    return 'success'

def cleanse():
    effects = list(player.instance.fighter.status_effects)

    cleansed = False
    for status in effects:
        if status.cleanseable:
            cleansed = True
            player.instance.fighter.remove_status(status.name)
    if cleansed:
        ui.message("You feel refreshed.")
        return 'success'
    else:
        ui.message("You aren't afflicted with any harmful effects")
        return 'didnt-take-turn'


def invulnerable():
    player.instance.fighter.apply_status_effect(effects.invulnerable(10))
    return 'success'

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
                syntax.name(obj[0]).capitalize(),
                syntax.conjugate(obj[0] is player.instance, ('are', 'is'))), libtcod.gray)
            return False
        ui.message('You conjure a spark of flame, igniting the ' + tile.name + '!', libtcod.flame)
        main.create_fire(target[0], target[1], 10)
        return True
    return False


def on_hit_judgement(attacker, target, damage):
    if target.fighter is not None:
        target.fighter.apply_status_effect(effects.judgement(stacks=main.roll_dice('2d6')))

def pickaxe_dig(dx, dy):
    result = dig(player.instance.x + dx, player.instance.y + dy)
    if result == 'failed':
        ui.message('You cannot dig there.', libtcod.orange)
    else:
        item = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
        if item is not None:
            main.check_breakage(item)

def dig_line(x, y, dx, dy, length, actor=None):
    if actor is None: actor = player.instance
    result = 'failure'
    for i in range(length):
        d = dig(x + dx * i, y + dy * i)
        if result != 'success':
            result = d
    if result == 'success':
        if actor is player.instance or fov.player_can_see(actor.x, actor.y):
            ui.message('The earth parts before %s.' % syntax.name(actor), spells.essence_colors['earth'])
    else:
        if actor is player.instance:
            ui.message('There is nothing to dig in that direction.', libtcod.gray)
    return result

def dig(dig_x, dig_y):
    import player, dungeon
    if dig_x < 0 or dig_y < 0 or dig_x >= consts.MAP_WIDTH or dig_y >= consts.MAP_HEIGHT:
        return 'failed'

    change_type = dungeon.branches[main.current_map.branch]['default_floor']
    if main.current_map.tiles[dig_x][dig_y].elevation != main.current_map.tiles[player.instance.x][player.instance.y].elevation:
        change_type = dungeon.branches[main.current_map.branch]['default_ramp']
    if main.current_map.tiles[dig_x][dig_y].diggable:
        main.current_map.tiles[dig_x][dig_y].tile_type = change_type
        main.changed_tiles.append((dig_x, dig_y))
        if main.current_map.pathfinding:
            main.current_map.pathfinding.mark_unblocked((dig_x, dig_y))
        fov.set_fov_properties(dig_x, dig_y, False)
        fov.set_fov_recompute()
        return 'success'
    else:
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

def vanguard(target):
    player.instance.add_zone(main.Zone(1,on_enter=vanguard_attack))

def vanguard_attack(actor,target):
    weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'right hand')
    if weapon is not None and weapon.subtype == 'polearm':
        attack(actor,target)

def skullsplitter_calc_damage_bonus(actor,target):
    return 1.5 * ( 2 - target.fighter.hp / target.fighter.max_hp)

def crush_calc_damage_bonus(actor,target):
    return 1.5 + (target.fighter.armor+1 / 20) * 2.5

def crush_calc_shred_bonus(actor,target):
    return 1 + int(target.fighter.armor / 2)

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
        ui.message('Cockroaches crawl from %s wounds!' % syntax.name(actor, possesive=True), libtcod.dark_magenta)
    for adj in main.adjacent_tiles_diagonal(actor.x, actor.y):
        if len(actor.summons) >= actor.summon_limit:
            break
        if not main.is_blocked(adj[0], adj[1]) and libtcod.random_get_int(0, 1, 10) <= 5:
            actor.summons.append(main.spawn_monster('monster_cockroach', adj[0], adj[1]))

def poison_attack_1(actor,target,damage):
    if main.roll_dice('1d10') > target.fighter.armor:
        target.fighter.apply_status_effect(effects.poison())

def potion_essence(essence):
    return lambda : player.pick_up_essence(essence,player.instance)

def teleport(actor, x, y):
    if actor is None:
        actor = player.instance

    if actor is player.instance or fov.player_can_see(actor.x, actor.y):
        ui.message('%s %s in a crackle of magical energy!' %
                   (syntax.name(actor).capitalize(),
                    syntax.conjugate(actor is player.instance, ('vanish', 'vanishes'))),
                    spells.essence_colors['arcane'])
    actor.set_position(x, y)
    if actor is not player.instance and fov.player_can_see(actor.x, actor.y):
        ui.message('%s appears out of thin air!' % syntax.name(actor).capitalize(), spells.essence_colors['arcane'])
    return 'success'

def teleport_random(actor=None):
    destination = main.find_random_open_tile()
    return teleport(actor, destination[0], destination[1])

def teleportal_on_tick(teleportal):
    if not hasattr(teleportal, 'timer'):
        teleportal.timer = 3
        return
    else:
        teleportal.timer -= 1
    if teleportal.timer <= 0:
        destination = main.find_random_open_tile()
        for obj in main.get_objects(teleportal.x, teleportal.y):
            if obj is not teleportal:
                teleport(obj, destination[0], destination[1])
        teleportal.destroy()

def create_teleportal(x, y):
    portal = main.GameObject(x, y, 9, 'teleportal', spells.essence_colors['arcane'], on_tick=teleportal_on_tick)
    portal.timer = 4
    main.current_map.add_object(portal)
    main.changed_tiles.append((x, y))
    if fov.player_can_see(x, y):
        ui.message('A volatile portal opens. In a few moments it will teleport creatures standing near it.',
                   spells.essence_colors['arcane'])
    return 'success'

def summon_ally(name, duration):
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

    # Select monster type - default to goblin
    import monsters
    if name in monsters.proto.keys():
        summon = main.spawn_monster(name, summon_pos[0], summon_pos[1], team='ally')
        summon.behavior.follow_target = player.instance

        # Set summon duration
        summon.summon_time = duration + libtcod.random_get_int(0, 0, duration)
        return 'success'
    else:
        return 'didnt-take-turn'

def summon_weapon(weapon):
    if len(player.instance.fighter.inventory) >= 26:
        ui.message('You are carrying too many items to summon another.')
        return 'didnt-take-turn'

    summoned_weapon = main.create_item(weapon, material='', quality='')
    if summoned_weapon is None:
        return
    expire_ticker = main.Ticker(15,summon_weapon_on_tick)
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
    effect = effects.StatusEffect('summoned weapon', expire_ticker.max_ticks + 1, summoned_weapon.color)
    player.instance.fighter.apply_status_effect(effect)
    expire_ticker.effect = effect
    main.current_map.tickers.append(expire_ticker)
    return 'success'

def summon_weapon_on_tick(ticker):
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

def learn_ability(ability):
    dat = abilities.data[ability]
    a = abilities.Ability(dat.get('name'), dat.get('description', ''), dat.get('function'), dat.get('cooldown', 0))
    player.instance.perk_abilities.append(a)

import libtcodpy as libtcod
import game as main
import syntax
import fov
import abilities
import effects
import spells
import ui
import ai
import player
import combat
