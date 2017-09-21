import libtcodpy as libtcod
import game as main
import syntax
import ui
import player
import combat
import actions
import spells
import effects
import fov

def select_essence(data,options='any'):
    if len(player.instance.essence) < 1:
        ui.message("You don't have any essence.", libtcod.light_blue)
        return 'didnt-take-turn'
    return ui.choose_essence_from_pool(data)

def get_charm_data(charm):
    if charm.use_function == charm_raw:
        return spells.charm_raw_effects
    elif charm.use_function == charm_resist:
        return spells.charm_resist_effects
    elif charm.use_function == farmers_talisman:
        return spells.charm_farmers_talisman
    elif charm.use_function == holy_symbol:
        return spells.charm_holy_symbol
    elif charm.use_function == primal_totem:
        return spells.charm_primal_totem
    elif charm.use_function == shard_of_creation:
        return spells.charm_shard_of_creation
    elif charm.use_function == volatile_orb:
        return spells.charm_volatile_orb
    elif charm.use_function == elementalists_lens:
        return spells.charm_elementalists_lens
    elif charm.use_function == prayer_beads:
        return spells.charm_prayer_beads
    elif charm.use_function == alchemists_flask:
        return spells.charm_alchemists_flask

def print_charm_description(charm, console, x, y, width):
    data = get_charm_data(charm)
    draw_height = 1

    if charm.charges is not None:
        libtcod.console_set_default_foreground(console, libtcod.white)
        libtcod.console_print(console, x + 1, y + draw_height, 'Charges: %d' % charm.charges)
        draw_height += 2

    libtcod.console_print(console, x + 1, y + draw_height, 'Abilities:')
    draw_height += 1
    libtcod.console_set_default_foreground(console, libtcod.dark_gray)
    for i in range(min(width, 20)):
        libtcod.console_put_char(console, x + 1 + i, y + draw_height, '=')
    draw_height += 1
    for element in data.keys():
        if element == 'void':
            continue #seeeeecret!
        libtcod.console_set_default_foreground(console, spells.essence_colors[element])
        libtcod.console_print(console, x + 1, y + draw_height, element.capitalize())
        libtcod.console_set_default_foreground(console, libtcod.white)
        for j in range(len(element) + 2, 10):
            libtcod.console_put_char(console, x + j, y + draw_height, '-')
        libtcod.console_print(console, x + 11, y + draw_height, data[element]['name'].title())
        draw_height += 1
    return draw_height

def shard_of_creation():
    essence = select_essence(spells.charm_shard_of_creation)
    if essence is None:
        return 'didnt-take-turn'

    if essence == 'fire':
        ability = 'ability_create_terrain_lava'
    elif essence == 'life':
        ability = 'ability_create_terrain_grass'
    elif essence == 'earth':
        ability = 'ability_create_terrain_wall'
    elif essence == 'water':
        ability = 'ability_create_terrain_water'
    else:
        return 'failure'

    result = actions.invoke_ability(ability, player.instance)
    if result == 'success':
        player.instance.essence.remove(essence)
    return result

def farmers_talisman():
    essence = select_essence(spells.charm_farmers_talisman)
    if essence is None:
        return 'didnt-take-turn'

    result = 'didnt-take-turn'

    if essence == 'life':
        result = actions.invoke_ability('ability_summon_lifeplant', player.instance)
    elif essence == 'earth':
        result = actions.invoke_ability('ability_dig', player.instance)

    if result == 'success':
        player.instance.essence.remove(essence)
    return result

def primal_totem():
    essence = select_essence(spells.charm_primal_totem)
    if essence is None:
        return 'didnt-take-turn'

    result = 'didnt-take-turn'

    if essence == 'fire':
        result = actions.invoke_ability('ability_berserk', player.instance)
    elif essence == 'air':
        player.instance.fighter.adjust_stamina(100)
        ui.message('Fresh air fills your lungs!', spells.essence_colors['air'])
        result = 'success'
    elif essence == 'death':
        result = actions.invoke_ability('ability_summon_soul_reaper', player.instance)

    if result == 'success':
        player.instance.essence.remove(essence)
    return result

def holy_symbol():
    essence = select_essence(spells.charm_holy_symbol)
    if essence is None:
        return 'didnt-take-turn'

    result = 'didnt-take-turn'

    if essence == 'life':
        result = actions.invoke_ability('ability_mass_heal', player.instance)
    elif essence == 'water':
        result = actions.invoke_ability('ability_holy_water', player.instance)
    elif essence == 'radiance':
        result = actions.invoke_ability('ability_mass_reflect', player.instance)

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
    from actions import charm_actions, common, spell_actions, monster_actions, abilities
    essence = select_essence(spells.charm_raw_effects)
    if essence is None:
        return 'didnt-take-turn'

    elif essence == 'fire':
        result = actions.invoke_ability('ability_flame_wall', player.instance)
    elif essence == 'life':
        result = common.heal(amount=20, use_percentage=False)
    elif essence == 'earth':
        result = charm_actions.hardness(player.instance)
    elif essence == 'water':
        result = charm_actions.cleanse()
    elif essence == 'cold':
        result = actions.invoke_ability('ability_flash_frost', player.instance)
    elif essence == 'air':
        result = player.jump(player.instance, 3, 0)
        if result != 'didnt-take-turn':
            ui.message('A gust of air lifts you to your destination', spells.essence_colors['air'])
    elif essence == 'arcane':
        result = actions.invoke_ability('ability_teleportal', player.instance)
    elif essence == 'death':
        result = actions.invoke_ability('ability_raise_zombie', player.instance)
    elif essence == 'radiance':
        result = charm_actions.invulnerable(player.instance, player.instance, None)
    elif essence == 'void':
        result = charm_actions.demon_power(player.instance, player.instance, None)
    else:
        result = 'didnt-take-turn'

    if result != 'didnt-take-turn' and result != 'cancelled':
        player.instance.essence.remove(essence)
    return result

def volatile_orb():
    essence = select_essence(spells.charm_volatile_orb)
    if essence is None:
        return 'didnt-take-turn'

    result = 'didnt-take-turn'

    if essence == 'fire':
        result = actions.invoke_ability('ability_fire_bomb', player.instance)
    elif essence == 'cold':
        result = actions.invoke_ability('ability_ice_bomb', player.instance)
    elif essence == 'arcane':
        result = actions.invoke_ability('ability_time_bomb', player.instance)

    if result != 'didnt-take-turn' and result != 'cancelled':
        player.instance.essence.remove(essence)
    return result

def elementalists_lens():
    essence = select_essence(spells.charm_elementalists_lens)
    if essence is None:
        return 'didnt-take-turn'

    result = actions.invoke_ability('ability_summon_' + essence + '_elemental', player.instance)

    if result != 'didnt-take-turn' and result != 'cancelled':
        ui.message('An elemental appears before you.', color=spells.essence_colors[essence])
        player.instance.essence.remove(essence)
    return result

def prayer_beads():
    essence = select_essence(spells.charm_prayer_beads)
    if essence is None:
        return 'didnt-take-turn'

    result = 'didnt-take-turn'

    if essence == 'life':
        result = actions.invoke_ability('ability_healing_trance', player.instance)
    elif essence == 'air':
        player.instance.fighter.apply_status_effect(effects.levitating())
        result = 'success'

    if result != 'didnt-take-turn' and result != 'cancelled':
        player.instance.essence.remove(essence)
    return result

def alchemists_flask():
    essence = select_essence(spells.charm_alchemists_flask)
    if essence is None:
        return 'didnt-take-turn'

    result = 'didnt-take-turn'
    if essence == 'water':
        result = actions.invoke_ability('ability_acid_flask', player.instance)
    elif essence == 'cold':
        result = actions.invoke_ability('ability_frostfire', player.instance)
    elif essence == 'life':
        result = actions.invoke_ability('ability_vitality_potion', player.instance)

    if result != 'didnt-take-turn' and result != 'cancelled':
        player.instance.essence.remove(essence)
    return result