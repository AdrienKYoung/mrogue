import libtcodpy as libtcod
import game as main
import player
import syntax
import fov
import ui
import effects

def step_on_reed(reed, obj):
    reed.destroy()


def step_on_blightweed(weed, obj):
    if obj.fighter:
        obj.fighter.time_since_last_damaged = 0
        if obj.fighter.armor > 0:
            obj.fighter.get_shredded(1)
            if fov.player_can_see(obj.x, obj.y):
                ui.message('The blightweed thorns shred %s armor!' % syntax.name(obj, possesive=True), libtcod.desaturated_red)

def step_on_snow_drift(x,y,obj):
    if obj is player.instance:
        player.instance.fighter.adjust_stamina(-main.current_map.tiles[x][y].stamina_cost)
    main.current_map.tiles[x][y].tile_type = 'snowy ground'

def step_on_poison(x,y,obj):
    if obj.fighter is not None:
        obj.fighter.apply_status_effect(effects.poison(10))