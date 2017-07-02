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

import libtcodpy as libtcod
import game as main
import combat
import effects
import player
import syntax
import ui
import spells
import common

def pickaxe_dig(dx, dy):
    result = common.dig(player.instance.x + dx, player.instance.y + dy)
    if result == 'failed':
        ui.message('You cannot dig there.', libtcod.orange)
    else:
        item = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
        if item is not None:
            main.check_breakage(item)

def recover_shield(actor, target, context):
    if actor is not player.instance:  # this should only ever be used by the player
        return 'failure'
    sh = player.instance.fighter.get_equipped_shield()
    if sh is not None:
        cost = sh.sh_raise_cost
        if player.instance.fighter.stamina >= cost:
            player.instance.fighter.adjust_stamina(-sh.sh_raise_cost)
            sh.sh_raise()
            return 'success'
        else:
            ui.message("You don't have enough stamina to raise your shield (Need %d)." % sh.sh_raise_cost, libtcod.gray)
            return 'didnt-take-turn'
    else:
        ui.message("You have no shield to raise.", libtcod.gray)
        return 'didnt-take-turn'


def offhand_shot(actor, target):
    weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'left hand')
    ui.render_projectile((actor.x, actor.y), (target.x, target.y), libtcod.white)
    combat.attack_ex(actor.fighter,target,0,verb=("shoot","shoots"),weapon=weapon)

def potion_essence(essence):
    return lambda : use_gem(essence)

def use_gem(essence):
    if player.instance.fighter.item_equipped_count('equipment_ring_of_alchemy') > 0:
        old_essence = essence
        essence = main.opposite_essence(essence)
        if old_essence != essence:
            ui.message('Your ring of alchemy glows!', spells.essence_colors[essence])
    player.pick_up_essence(essence, player.instance)

def waterbreathing():
    player.instance.fighter.apply_status_effect(effects.StatusEffect('waterbreathing', 31, libtcod.light_azure))

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