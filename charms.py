import libtcodpy as libtcod
import game as main
import syntax
import ui
import player
import combat
import actions
import spells
import effects

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
        terrain = 'stone wall'
    elif essence == 'water':
        terrain = 'shallow water'

    tiles = main.adjacent_tiles_orthogonal(x,y)
    tiles.append((x,y))

    if terrain is not None:
        main.create_temp_terrain(terrain,tiles,100)
        player.instance.essence.remove(essence)
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
        (x, y) = ui.target_tile(2)
        if x is None:
            return 'didnt-take-turn'
        result = actions.dig(x - player.instance.x, y - player.instance.y)

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

    result = 'success'

    if essence == 'fire':
        result = actions.flame_wall()
    elif essence == 'life':
        result = actions.heal(amount=0.10, use_percentage=True)
    elif essence == 'earth':
        result = actions.shielding()
    elif essence == 'water':
        result = actions.cleanse()
    elif essence == 'cold':
        result = actions.flash_frost()
    elif essence == 'wind':
        player.jump(player.instance, 3, 0)
    elif essence == 'arcane':
        result = 'didnt-take-turn'
    elif essence == 'death':
        result = actions.raise_zombie()
    elif essence == 'radiant':
        result = actions.invulnerable()
    elif essence == 'void':
        result = 'didnt-take-turn'
    else:
        result = 'didnt-take-turn'

    if result != 'didnt-take-turn' and result != 'cancelled':
        player.instance.essence.remove(essence)
    return result