import libtcodpy as libtcod
import game as main
import consts
import effects
import ui
import ai
import player
import combat
import syntax
import world
import terrain

class Spell:
    def __init__(self, name, function, description, levels, int_requirement = 10):
        self.name = name
        self.function = function
        self.description = description
        self.levels = levels
        self.int_requirement = int_requirement
        self.max_level = len(levels)

def cast_fireball(actor=None,target=None):
    x,y = 0,0
    if actor is None: #player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        (x, y) = ui.target_tile()
        actor = player.instance
    else:
        x = target.x
        y = target.y
    if x is None: return 'cancelled'
    ui.message('The fireball explodes!', libtcod.flame)
    main.create_fire(x,y,10)
    for obj in main.current_map.fighters:
        if obj.distance(x, y) <= consts.FIREBALL_RADIUS:
            combat.spell_attack_ex(actor.fighter,obj,None,'fireball','2d6',2,'fire',0)
    return 'success'


def cast_arcane_arrow(actor=None, target=None):
    x, y = 0, 0
    if actor is None or actor is player.instance:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(consts.TORCH_RADIUS, 'beam_interrupt', default_target=default_target)
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
                combat.spell_attack_ex(actor.fighter, obj, 30, 'arcane arrow', '3d6', 1, 'arcane', 0)
                return 'success'
    return 'failure'


def cast_heat_ray(actor=None,target=None):
    line = None
    if actor is None:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(3, 'beam_interrupt', default_target=default_target)
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
                combat.spell_attack_ex(actor.fighter, obj, None, 'heat ray', '3d4', 1, 'fire', 0)
    return 'success'

def cast_flame_wall(actor=None,target=None):
    x,y = 0,0
    if actor is None: #player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        (x, y) = ui.target_tile()
        actor = player.instance
    else:
        x = target.x
        y = target.y
    main.create_fire(x,y,10)
    return 'success'

def cast_shatter_item(actor=None,target=None):
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
        choices = main.get_objects(x,y)
        if len(choices) > 1:
            target = choices[ui.menu('Which target?',[i.name for i in choices],24)]
        elif len(choices) > 0:
            target = choices[0]
        else:
            return 'cancelled'
        dc += 4
    else:
        x,y = target.x,target.y

    if target is None:
        return 'cancelled'
    item = None
    inventory = None
    if target.fighter is not None:
        inventory = target.fighter.inventory
        if inventory is None or len(inventory) == 0:
            if actor == player.instance:
                ui.message('Target has no items',libtcod.light_blue)
            return 'cancelled'
        item = inventory[main.random_choice_index(inventory)]
        dc += 5
    elif target.item is not None:
        item = target

    if main.roll_dice('1d20') + main.roll_dice('1d{}'.format(actor.fighter.spell_power)) > dc:
        ui.message("{} shatters into pieces!".format(item.name),libtcod.flame)
        if inventory is not None:
            inventory.remove(item)
        item.destroy()
        for obj in main.current_map.fighters:
            if obj.distance(x, y) <= consts.FIREBALL_RADIUS:
                combat.spell_attack_ex(actor.fighter, obj, None, 'shrapnel', '4d4', 1, 'slashing', 0)
        return 'success'
    else:
        ui.message("Shatter failed to break {}!".format(item),libtcod.yellow)
        return 'success'

def cast_magma_bolt(actor=None,target=None):
    x, y = 0, 0
    if actor is None:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        (x, y) = ui.target_tile()
        actor = player.instance
        if x is None: return 'cancelled'
        target = main.get_monster_at_tile(x, y)
    else:
        x = target.x
        y = target.y
    if target is not None:
        combat.spell_attack_ex(actor.fighter, target, None, 'fireball', '3d6', 3, 'fire', 0)
    main.current_map.tiles[x][y].tile_type = 'lava'
    main.current_map.pathfinding.mark_blocked((x, y))
    main.changed_tiles.append((x, y))


def cast_confuse():
    ui.message('Choose a target with left-click, or right-click to cancel.', libtcod.white)
    ui.render_message_panel()
    libtcod.console_flush()
    monster = main.target_monster(consts.CONFUSE_RANGE)
    if monster is None or monster.behavior is None: return 'cancelled'
    else:
        if monster.fighter.apply_status_effect(effects.StatusEffect('confusion', consts.CONFUSE_NUM_TURNS, color=libtcod.pink, on_apply=set_confused_behavior)):
            ui.message('%s %s confused!' % (
                            syntax.name(monster.name).capitalize(),
                            syntax.conjugate(monster is player.instance, ('are', 'is'))), libtcod.light_blue)

def set_confused_behavior(object):
    if object.behavior is not None:
        old_ai = object.behavior.behavior
        object.behavior.behavior = ai.ConfusedMonster(old_ai)
        object.behavior.behavior.owner = object

def cast_lightning():
    monster = main.closest_monster(consts.LIGHTNING_RANGE)
    if monster is None:
        ui.message('No targets in range', libtcod.white)
        return 'cancelled'
    else:
        damage = consts.LIGHTNING_DAMAGE
        ui.message('A bolt of lightning strikes %s! %s %s %d damage.' % (
                    syntax.name(monster.name),
                    syntax.pronoun(monster.name),
                    syntax.conjugate(monster is player.instance, ('suffer', 'suffers')),
                    damage), libtcod.light_blue)
        monster.fighter.take_damage(damage)


def cast_heal():
    if player.instance.fighter.hp == player.instance.fighter.max_hp:
        ui.message('You are already at full health.', libtcod.white)
        return 'cancelled'
        
    ui.message('You feel better.', libtcod.white)
    player.instance.fighter.heal(consts.HEAL_AMOUNT)


def cast_waterbreathing():
    player.instance.fighter.apply_status_effect(effects.StatusEffect('waterbreathing', 31, libtcod.light_azure))


def cast_shielding():
    player.instance.fighter.shred = 0
    player.instance.fighter.apply_status_effect(effects.StatusEffect('shielded', 21, libtcod.dark_blue))


def cast_frog_tongue(frog, target):

    ui.message("The frog's tongue lashes out at you!", libtcod.dark_green)
    result = combat.attack_ex(frog.fighter, target, 0, consts.FROG_TONGUE_ACC, consts.FROG_TONGUE_DMG, None, None, ('pull', 'pulls'), 0, 0, 0)
    if result == 'hit':
        beam = main.beam(frog.x, frog.y, target.x, target.y)
        pull_to = beam[max(len(beam) - 3, 0)]
        target.set_position(pull_to[0], pull_to[1])

def cast_manabolt():
    default = None
    if ui.selected_monster is not None:
        default = ui.selected_monster.x, ui.selected_monster.y
    target = ui.target_tile(consts.MANABOLT_RANGE, 'beam_interrupt', acc_mod=consts.MANABOLT_ACC, default_target=default)
    if target[0] is not None:
        #visual effect
        bolt = main.GameObject(player.instance.x, player.instance.y, 7, 'bolt', color=libtcod.light_blue)
        line = main.beam(player.instance.x, player.instance.y, target[0], target[1])
        main.current_map.add_object(bolt)
        for p in line:
            bolt.set_position(p[0], p[1])
            main.render_map()
            libtcod.console_flush()
        bolt.destroy()
        #game effect
        monster = main.get_monster_at_tile(target[0], target[1])
        if monster is not None:
            if combat.roll_to_hit(monster, player.instance.fighter.accuracy * consts.MANABOLT_ACC):
                ui.message('The manabolt strikes %s, dealing %d damage!' % (syntax.name(monster.name), consts.MANABOLT_DMG), libtcod.light_blue)
                monster.fighter.take_damage(consts.MANABOLT_DMG)
            else:
                ui.message('The manabolt misses %s.' % syntax.name(monster.name), libtcod.gray)
        else:
            ui.message('The manabolt hits the %s.' % main.current_map.tiles[target[0]][target[1]].tile_type, libtcod.light_blue)
        return True
    return False

def cast_ignite():
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


def cast_mend():
    if player.instance.fighter.hp < player.instance.fighter.max_hp:
        player.instance.fighter.heal(consts.MEND_HEAL)
        ui.message('A soft green glow passes over you as your wounds are healed.', libtcod.light_blue)
        return True
    else:
        ui.message('You have no need of mending.', libtcod.light_blue)
        return False


def cast_forge():
    weapon = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
    if weapon is not None and weapon.owner.item.category == 'weapon':
        if weapon.quality == 'artifact':
            ui.message('Your ' + weapon.owner.name + ' shimmers briefly. It cannot be improved further by this magic.', libtcod.orange)
        else:
            ui.message('Your ' + weapon.owner.name + ' glows bright orange!', libtcod.orange)

            new_quality = ''
            if weapon.quality == 'broken':
                new_quality = 'crude'
            elif weapon.quality == 'crude':
                new_quality = ''
            elif weapon.quality == '':
                new_quality = 'military'
            elif weapon.quality == 'military':
                new_quality = 'fine'
            elif weapon.quality == 'fine':
                new_quality = 'masterwork'
            elif weapon.quality == 'masterwork':
                new_quality = 'artifact'
            main.set_quality(weapon, new_quality)
            ui.message('It is now a ' + weapon.owner.name + '.', libtcod.orange)
    elif weapon is not None and weapon.owner.item.category != 'weapon':
        ui.message('Your ' + weapon.owner.name + ' emits a dull glow. This magic was only intended for weapons!', libtcod.orange)
    else:
        ui.message('Your hands tingle briefly. This magic was only intended for weapons!', libtcod.orange)
    return True

charm_blessing_effects = {
    'fire': {
        'buff':effects.berserk,
        'description':'Drive yourself berserk for a bonus to melee damage'
    },
    'earth': {
        'buff':effects.stoneskin,
        'description':'Turn your skin to stone for a bonus to armor'
    },
    'air': {
        'buff':effects.swiftness,
        'description':'Turn your skin to stone for a bonus to armor'
    },
    'water': {
        'buff':effects.serenity,
        'description':'Turn your skin to stone for a bonus to armor'
    },
    'life': {
        'buff':effects.regeneration,
        'description':'Regenerate your wounds over time.'
    }
}

def cast_charm_blessing():
    essence = player.instance.essence[ui.menu("Which essence?",player.instance.essence,24)]
    player.instance.fighter.apply_status_effect(charm_blessing_effects[essence]['buff']())
    player.instance.essence.remove(essence)

charm_summoning_summons = {
    'fire': {
        'summon': 'monster_fire_elemental',
        'duration': 15,
        'description':"Summon a fire elemental. It's attacks are deadly, but it won't last long in this world."
    },
    'earth': {
        'summon': 'monster_earth_elemental',
        'duration': 30,
        'description':"Summon an earth elemental. It moves slowly, but is very durable."
    },
    'air': {
        'summon': 'monster_air_elemental',
        'duration': 30,
        'description':"Summon an air elemental. It flies and moves quickly, but inflicts little damage."
    },
    'water': {
        'summon': 'monster_water_elemental',
        'duration': 30,
        'description': "Summon a water elemental. It does not attack, but rather disables nearby foes."
    },
    'life': {
        'summon': 'monster_lifeplant',
        'duration': 15,
        'description': "Summon a lifeplant. It will slowly heal nearby creatures over time."
    },
    'cold': {
        'summon': 'monster_ice_elemental',
        'duration': 30,
        'description': "Summon an ice elemental. It deals heavy damage, but is fragile."
    },
    'arcane': {
        'summon': 'monster_arcane_construct',
        'duration': 30,
        'description': "Summon an Arcane Construct. This artificial can fire magical energy from a distance, but is fragile."
    },
    'radiant': { #TODO: make divine servant
        'summon': 'monster_divine_servant',
        'duration': 150,
        'description': "Summon a Divine Servant. This heavenly creature will swear to protect you."
    },
    'dark': { #TODO: make shadow demon
        'summon': 'monster_shadow_demon',
        'duration': 150,
        'description': "Summon a Shadow Demon. This vicious creature of darkness will not bend to the will of mortals."
    },
    'void': { #TODO: make void horror
        'summon': 'monster_void_horror',
        'duration': 300,
        'description': "Who can tell what horrors this might summon? I hope you know what you're doing."
    }
}

def cast_charm_summoning():
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
    essence = player.instance.essence[ui.menu("Which essence?",player.instance.essence,24)]
    player.instance.essence.remove(essence)

    # Select monster type - default to goblin
    summon_type = 'monster_goblin'
    import monsters
    if essence in charm_summoning_summons.keys() and charm_summoning_summons[essence]['summon'] in monsters.proto.keys():
        summon_type = charm_summoning_summons[essence]['summon']
    summon = main.spawn_monster(summon_type, summon_pos[0], summon_pos[1], team='ally')
    summon.behavior.follow_target = player.instance

    # Set summon duration
    t = charm_summoning_summons[essence]['duration']
    summon.summon_time = t + libtcod.random_get_int(0, 0, t)


charm_resist_extra_resists = {
    'fire':['burning'],
    'water':['exhaustion'],
    'air':['immobilize'],
    'earth':['stun'],
    'life':['poison'],
    'dark':['rot'],
    'ice':['freeze'],
    'arcane':['silence'],
    'radiant':['judgement'],
    'void':[]
}

def cast_charm_resist():
    if len(player.instance.essence) < 1:
        ui.message("You don't have any essence.", libtcod.light_blue)
        return 'didnt-take-turn'
    essence = player.instance.essence[ui.menu("Which essence?",player.instance.essence,24)]
    player.instance.fighter.apply_status_effect(effects.resistant(element=essence))
    if essence in charm_resist_extra_resists:
        for effect in charm_resist_extra_resists[essence]:
            player.instance.fighter.apply_status_effect(effects.resistant(effect=effect,color=essence_colors[essence]),supress_message=True)
    player.instance.essence.remove(essence)

def cast_potion_essence(essence):
    return lambda : player.pick_up_essence(essence,player.instance)

library = {
    #'manabolt' : Spell('manabolt', { 'normal' : 1 }, cast_manabolt, '[1 normal]',"",0),
    #'mend' : Spell('mend', { 'life' : 1 }, cast_mend, '[1 life]',"",0),
    #'ignite' : Spell('ignite', { 'fire' : 1 }, cast_ignite, '[1 fire]',"",0),
    'spell_heat_ray' : Spell(
        'heat ray',
        cast_heat_ray,
        'Fire a ray of magical heat in a line',
        [
            {'stamina_cost':30,'charges':3},
            {'stamina_cost':25,'charges':4},
            {'stamina_cost':20,'charges':5}
        ],
        10),

    'spell_flame_wall' : Spell(
        'flame wall',
        cast_flame_wall,
        'Create a wall of flames',
        [
            {'stamina_cost':40,'charges':1},
            {'stamina_cost':35,'charges':2}
        ],
        10),

    'spell_fireball' : Spell(
        'fireball',
        cast_fireball,
        'Fling an exploding fireball',
        [
            {'stamina_cost':50,'charges':1},
            {'stamina_cost':45,'charges':2},
            {'stamina_cost':40,'charges':2}
        ],
        10),

    'spell_shatter_item' : Spell(
        'shatter item',
        cast_shatter_item,
        'Overheat items to shatter them',
        [
            {'stamina_cost':50,'charges':2}
            ,{'stamina_cost':40,'charges':3}
        ],
        10),

    'spell_magma_bolt' : Spell(
        'magma bolt',
        cast_magma_bolt,
        'Fire a bolt of roiling magma that melts floors',
        [
            {'stamina_cost':60,'charges':2},
            {'stamina_cost':50,'charges':3},
            {'stamina_cost':40,'charges':4}
        ],
        10)
}

essence_colors = {
    'normal' : libtcod.gray,
    'life' : libtcod.green,
    'fire' : libtcod.flame,
    'earth' : libtcod.sepia,
    'dark' : libtcod.dark_violet,
    'water' : libtcod.azure,
    'air' : libtcod.light_sky,
    'cold' : libtcod.lightest_azure,
    'radiant' : libtcod.lighter_yellow,
    'arcane' : libtcod.fuchsia,
    'void' : libtcod.darker_crimson
}