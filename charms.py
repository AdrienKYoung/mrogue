import libtcodpy as libtcod
import game as main
import syntax
import ui
import player
import combat
import actions
import spells
import effects
import dungeon
import mapgen
import fov

def select_essence(data,options='any'):
    if len(player.instance.essence) < 1:
        ui.message("You don't have any essence.", libtcod.light_blue)
        return 'didnt-take-turn'
    return ui.choose_essence_from_pool(data)

def shard_of_creation():
    essence = select_essence(spells.charm_shard_of_creation)
    if essence is None:
        return 'didnt-take-turn'

    ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
    (x, y) = ui.target_tile(5)

    if x is None:
        return 'didnt-take-turn'

    terrain = None
    if essence == 'fire':
        terrain = 'lava'
    elif essence == 'life':
        terrain = 'grass floor'
    elif essence == 'earth':
        terrain = dungeon.branches[main.current_map.branch]['default_wall']
    elif essence == 'water':
        terrain = 'shallow water'

    tiles = main.adjacent_tiles_orthogonal(x,y)
    tiles.append((x,y))

    if terrain is not None:
        main.create_temp_terrain(terrain,tiles,100)
        if terrain == 'shallow water':
            main.create_temp_terrain('deep water', [(x, y)], 100)
        if terrain == 'grass floor':
            mapgen.scatter_reeds(tiles, 75)
        player.instance.essence.remove(essence)
        for t in tiles:
            blocks = main.current_map.tiles[t[0]][t[1]].blocks_sight or \
                     len(main.get_objects(t[0], t[1], lambda o: o.blocks_sight)) > 0
            fov.set_fov_properties(t[0], t[1], blocks)
        return 'success'
    else:
        return 'didnt-take-turn'

def farmers_talisman():
    essence = select_essence(spells.charm_farmers_talisman)
    if essence is None:
        return 'didnt-take-turn'

    result = 'didnt-take-turn'

    if essence == 'life':
        result = actions.summon_ally('monster_lifeplant',15)
    elif essence == 'earth':
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(1)
        if x is None:
            return 'didnt-take-turn'
        direction = x - player.instance.x, y - player.instance.y
        depth = 3 + libtcod.random_get_int(0, 1, 3)
        result = actions.dig_line(player.instance.x, player.instance.y, direction[0], direction[1], depth)

    if result == 'success':
        player.instance.essence.remove(essence)
    return result

def primal_totem():
    essence = select_essence(spells.charm_primal_totem)
    if essence is None:
        return 'didnt-take-turn'

    result = 'didnt-take-turn'

    if essence == 'fire':
        result = actions.berserk_self(player.instance)
    elif essence == 'air':
        result = actions.battle_cry(player.instance)
    elif essence == 'death':
        result = actions.summon_weapon('weapon_soul_reaper')

    if result == 'success':
        player.instance.essence.remove(essence)
    return result

def holy_symbol():
    essence = select_essence(spells.charm_holy_symbol)
    if essence is None:
        return 'didnt-take-turn'

    result = 'didnt-take-turn'

    if essence == 'life':
        result = actions.mass_heal(player.instance)
    elif essence == 'water':
        result = actions.mass_cleanse(player.instance)
    elif essence == 'radiant':
        result = actions.mass_reflect(player.instance)

    if result == 'success':
        player.instance.essence.remove(essence)
    return result

def charm_resist():
    essence = select_essence(spells.charm_resist_effects)
    if essence is None:
        return 'didnt-take-turn'
    player.instance.fighter.apply_status_effect(effects.resistant(element=essence))
    if essence in spells.charm_resist_effects:
        for effect in spells.charm_resist_effects[essence]['resists']:
            player.instance.fighter.apply_status_effect(
                effects.resistant(effect=effect, color=spells.essence_colors[essence]), supress_message=True)
    player.instance.essence.remove(essence)

def charm_raw():
    essence = select_essence(spells.charm_raw_effects)
    if essence is None:
        return 'didnt-take-turn'

    if essence == 'fire':
        result = actions.flame_wall()
    elif essence == 'life':
        result = actions.heal(amount=20, use_percentage=False)
    elif essence == 'earth':
        result = actions.hardness()
    elif essence == 'water':
        result = actions.cleanse()
    elif essence == 'cold':
        result = actions.flash_frost()
    elif essence == 'air':
        result = player.jump(player.instance, 3, 0)
        if result != 'didnt-take-turn':
            ui.message('A gust of air lifts you to your destination', spells.essence_colors['air'])
    elif essence == 'arcane':
        result = 'didnt-take-turn' #TODO: teleport
    elif essence == 'death':
        result = actions.raise_zombie()
    elif essence == 'radiant':
        result = actions.invulnerable()
    elif essence == 'void':
        result = 'didnt-take-turn' #TODO: mutate self
    else:
        result = 'didnt-take-turn'

    if result != 'didnt-take-turn' and result != 'cancelled':
        player.instance.essence.remove(essence)
    return result