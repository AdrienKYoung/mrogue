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

import game as main
import libtcodpy as libtcod
import math
import ui
import consts
import player
import fov
import syntax
import pathfinding
import abilities
import actions
import spells

class Fighter:

    def __init__(self, hp=1, stamina=0, armor=0, evasion=0, accuracy=25, spell_power=0, death_function=None, breath=6,
                 can_breath_underwater=False, resistances={}, inventory=[], on_hit=None, base_shred=0,
                 base_guaranteed_shred=0, base_pierce=0, abilities=[], hit_table=None, monster_flags =0, subtype=None,
                 damage_bonus=0, monster_str_dice=None, team='enemy', on_get_hit=None, stealth=None,
                 attributes=[], _range=1, on_get_kill=None, will=0, fortitude=0):
        self.owner = None
        self.base_max_hp = hp
        self.hp = hp
        self.death_function = death_function
        self.max_stamina = stamina
        self.stamina = stamina
        self.base_armor = armor
        self.base_evasion = evasion
        self.base_spell_power = spell_power
        self.base_accuracy = accuracy
        self.max_breath = breath
        self.breath = breath
        self.can_breath_underwater = can_breath_underwater
        self._resistances = dict(resistances)
        self.inventory = list(inventory)
        self.attributes = list(attributes)
        self.base_shred = base_shred
        self.base_guaranteed_shred = base_guaranteed_shred
        self.base_pierce = base_pierce
        self.status_effects = []
        self.on_hit = on_hit
        self.shred = 0
        self.time_since_last_damaged = 0
        self._abilities = abilities
        self.hit_table = hit_table
        self.monster_flags = monster_flags
        self.subtype = subtype
        self.team = team
        self.on_get_hit = on_get_hit
        self.stealth = stealth
        self.range = _range
        self.on_get_kill = on_get_kill
        self.base_will = will
        self.base_fortitude = fortitude

        self.base_damage_bonus = damage_bonus
        self.monster_str_dice = monster_str_dice

    def print_description(self, console, x, y, width):
        if self.owner is player.instance:
            y += 1
            return ui.character_info_screen(console, x, y, width)

        print_height = 1
        # Print ally status
        if self.team == 'ally':
            libtcod.console_set_default_foreground(console, libtcod.dark_sky)
            libtcod.console_print(console, x, y + print_height, 'ALLY')
            print_height += 2

        # Print health
        libtcod.console_set_default_foreground(console, libtcod.dark_red)
        libtcod.console_print(console, x, y + print_height, 'HP: %d/%d' % (self.hp, self.max_hp))
        print_height += 1
        # Print armor
        if self.shred > 0:
            libtcod.console_set_default_foreground(console, libtcod.yellow)
        else:
            libtcod.console_set_default_foreground(console, libtcod.white)
        libtcod.console_print(console, x, y + print_height, 'Armor: %d' % self.armor)
        if self.shred > 0:
            libtcod.console_print(console, x + 10, y + print_height, '(%d)' % (self.armor + self.shred))
        print_height += 1
        # Print accuracy
        if self.owner is not player.instance:
            libtcod.console_set_default_foreground(console, libtcod.white)
            s = 'Your Accuracy: %d%%' % int(100.0 * get_chance_to_hit(self.owner, player.instance.fighter.accuracy()))
            s += '%'
            libtcod.console_print(console, x, y + print_height, s)
            print_height += 1
            s = '%s Accuracy: %d%%' % (syntax.pronoun(self.owner.name, possesive=True).capitalize(), int(100.0 * get_chance_to_hit(player.instance, self.accuracy())))
            s += '%'
            libtcod.console_print(console, x, y + print_height, s)
            print_height += 1

        for e in self.status_effects:
            libtcod.console_set_default_foreground(console, e.color)
            h = libtcod.console_get_height_rect(console, x, y + print_height, width - 4, 10, e.description)
            libtcod.console_print_rect(console, x, y + print_height, width - 4, h, e.description)
            print_height += h

        libtcod.console_set_default_foreground(console, libtcod.white)

        return print_height

    def adjust_stamina(self, amount):
        self.stamina += amount
        if self.stamina < 0:
            self.stamina = 0
        if self.stamina > self.max_stamina:
            self.stamina = self.max_stamina

    def take_damage(self, damage, attacker=None, affect_shred=True, blockable=False):
        if self.has_status('invulnerable') or self.has_attribute('attribute_invulnerable'):
            if self.owner is player.instance or fov.player_can_see(self.owner.x, self.owner.y):
                ui.message('%s %s protected by a radiant shield!' %
                           (syntax.name(self.owner).capitalize(),
                            syntax.conjugate(self.owner is player.instance, ('are', 'is'))),
                           spells.essence_colors['radiance'])
            damage = 0

        if self.has_status('cursed') or self.has_status('stung') and damage > 0:
            damage = int(damage * 1.25)

        if damage > 0:
            sh = self.get_equipped_shield()
            if blockable and sh is not None and sh.raised and sh.sh_points > 0:
                sh.sh_points -= damage
                sh.sh_timer = sh.sh_recovery
                if sh.sh_points <= 0:
                    sh.sh_points = 0
                    sh.raised = False
                    ui.message('%s shield is knocked away!' % syntax.name(self.owner, possesive=True).capitalize(), libtcod.blue)
                return 'blocked'
            else:
                self.get_hit(attacker,damage)
                self.hp -= damage
                if self.hp <= 0:
                    is_summoned = self.owner.summon_time is not None
                    if not is_summoned:
                        self.drop_essence()
                    self.owner.is_corpse = True
                    function = self.death_function
                    if function is not None:
                        if sh is not None:
                            sh.sh_points = sh.sh_max
                            sh.timer = 0
                            sh.raised = True
                        function(self.owner)
                    if attacker is not None and attacker.fighter is not None and attacker.fighter.on_get_kill is not None and not is_summoned:
                        attacker.fighter.on_get_kill(attacker,self,damage)
                if affect_shred:
                    self.time_since_last_damaged = 0
        return damage

    def get_hit(self, attacker,damage):
        if self.owner.behavior:
            self.owner.behavior.get_hit(attacker)
        if self.on_get_hit:
            self.on_get_hit(self.owner, attacker, damage)

    def drop_essence(self):
        if hasattr(self.owner, 'essence') and self.owner is not player.instance:
            roll = libtcod.random_get_int(0, 1, 100)
            total = 0
            for m in self.owner.essence:
                total += m[0]
                if roll < total + total * main.skill_value('essence_hunter'):
                    main.spawn_essence(self.owner.x, self.owner.y,m[1])
                    return

    def calculate_attack_stamina_cost(self):
        stamina_cost = 0
        if self.owner is player.instance:
            stamina_cost = consts.UNARMED_STAMINA_COST / (self.owner.player_stats.str / consts.UNARMED_STAMINA_COST)
            if main.get_equipped_in_slot(self.inventory, 'right hand') is not None:
                stamina_cost = int((float(main.get_equipped_in_slot(self.inventory, 'right hand').stamina_cost) /
                                    (float(self.owner.player_stats.str) / float(
                                        main.get_equipped_in_slot(self.inventory, 'right hand').str_requirement))))
            stamina_cost = int(stamina_cost * (1.0 - main.skill_value('combat_training')))
        return stamina_cost

    def calculate_attack_count(self):

        if self.owner is player.instance:
            speed = self.attack_speed()
        else:
            return 1  # monsters always get 1 attack per turn (though their turns may be faster)

        weapon = main.get_equipped_in_slot(self.inventory, 'right hand')
        if weapon is None:
            delay = 10
        else:
            delay = weapon.attack_delay

        dm = divmod(speed, delay)
        attacks = dm[0]
        remainder = float(dm[1]) / float(delay)
        if libtcod.random_get_float(0, 0.0, 1.0) < remainder:
            attacks += 1
        attacks = max(attacks, 1)
        return attacks

    def attack(self, target):
        result = 'failed'
        attacks = self.calculate_attack_count()
        if target.fighter is None:
            return 'failed'
        if target.fighter.stealth is not None and target.fighter.stealth < self.owner.distance_to(target):
            return 'failed' # cannot attack targets that cannot be seen
        for i in range(attacks):
            result = attack_ex(self, target, self.calculate_attack_stamina_cost(), on_hit=self.on_hit)
            if result == 'failed':
                return result
            elif target.fighter is None:
                return result
        return result

    def heal(self, amount):
        if self.owner is player.instance and main.has_skill('vitality'):
            amount = int(amount * 1.25)
        if self.has_status('toxic'):
            amount = int(amount / 2)
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def item_equipped_count(self, name):
        match = []
        for item in main.get_all_equipped(self.inventory):
            if item.base_id == name:
                match.append(item)
        return len(match)
        #return len([e.base_id == name for e in main.get_all_equipped(self.inventory)])

    def on_tick(self, object=None):
        # Track time since damaged (for repairing shred)
        self.time_since_last_damaged += 1
        mending_count = self.item_equipped_count('equipment_ring_of_mending')
        if mending_count > 0:
            repair_time = 20 / (mending_count * 2)
        else:
            repair_time = 20
        if self.time_since_last_damaged >= repair_time and self.shred > 0:
            self.shred = 0
            if self.owner is player.instance:
                ui.message('You repair your armor')

        # Track shield recovery timer
        sh = self.get_equipped_shield()
        if sh is not None and sh.sh_timer > 0:
            sh.sh_timer -= 1
            if sh.sh_timer <= 0:
                sh.sh_raise()

        # Manage breath/drowning
        tile = main.current_map.tiles[self.owner.x][self.owner.y]
        if tile.is_water and not tile.jumpable \
                and self.owner.movement_type & pathfinding.FLYING != pathfinding.FLYING \
                and self.owner.movement_type & pathfinding.AQUATIC != pathfinding.AQUATIC:  # deep water / deep seawater
            if not (self.can_breath_underwater or self.has_status('waterbreathing') or self.has_status('lichform') or
                    self is player.instance and main.has_skill('aquatic') or self.item_equipped_count("equipment_ring_of_waterbreathing") > 0):
                if self.breath > 0:
                    self.breath -= 1
                else:
                    drown_damage = int(self.max_hp / 4)
                    ui.message('%s %s, suffering %d damage!' % (syntax.name(self.owner).capitalize(),
                                             syntax.conjugate(self.owner is player.instance,
                                             ('drown', 'drowns')), drown_damage), libtcod.blue)

                    self.take_damage(drown_damage)
                    if self.hp < 1 and main.has_skill('grip_of_the_depths'):
                        player.instance.fighter.adjust_stamina('50')
                        if main.roll_dice('1d20') > 18:
                            main.spawn_essence(self.owner.x,self.owner.y,'water')
        elif self.breath < self.max_breath:
            self.breath += 1

        # Manage status effect timers
        removed_effects = []
        for effect in self.status_effects:
            if effect.on_tick is not None:
                effect.on_tick(effect, object=self.owner)
            if effect.time_limit is not None:
                effect.time_limit -= 1
                if effect.time_limit == 0:
                    removed_effects.append(effect)
        for effect in removed_effects:
            if effect in self.status_effects:  # It can sometimes be removed in the on-tick function
                self.status_effects.remove(effect)
            if effect.on_end is not None:
                effect.on_end(effect,self.owner)

        # Manage ability cooldowns
        for ability in self.abilities:
            if ability is not None and ability.on_tick is not None:
                ability.on_tick()


    def apply_status_effect(self, new_effect, dc=20, source_fighter=None, supress_message=False):
        fighter = self
        if self.has_status('reflect-magic') and new_effect.target_defense is not None and source_fighter is not None:
            fighter = source_fighter

        # check for immunity
        if new_effect.name == 'burning' and fighter.owner is player.instance and main.has_skill('pyromaniac'):
            return False
        for resist in fighter.immunities:
            if resist == new_effect.name:
                if fov.player_can_see(fighter.owner.x, fighter.owner.y):
                    ui.message('%s %s.' % (syntax.name(fighter.owner).capitalize(), syntax.conjugate(
                        fighter.owner is player.instance, ('are immune', 'is immune'))), libtcod.gray)
                return False

        # roll to hit
        if new_effect.target_defense is not None:
            if not roll_to_hit(fighter.owner, dc, new_effect.target_defense):
                if fov.player_can_see(fighter.owner.x, fighter.owner.y):
                    ui.message('%s %s.' % (syntax.name(fighter.owner).capitalize(), syntax.conjugate(
                        fighter.owner is player.instance, ('resist', 'resists'))), libtcod.gray)
                return False

        if new_effect.time_limit is not None:
           new_effect.time_limit = int(new_effect.time_limit *
                                       (1 - (fighter.item_equipped_count('equipment_ring_of_fortitude') * 0.3)))


        # check for existing matching effects
        add_effect = True
        for effect in fighter.status_effects:
            if effect.name == new_effect.name:
                if 'refresh' in new_effect.stacking_behavior:
                    # refresh the effect
                    effect.time_limit = new_effect.time_limit
                    add_effect = False
                if 'extend' in new_effect.stacking_behavior:
                    effect.time_limit += new_effect.time_limit
                    add_effect = False
                if 'stack' in new_effect.stacking_behavior:
                    #add to current stack
                    effect.stacks += new_effect.stacks
                    add_effect = False
                if 'unique' == new_effect.stacking_behavior:
                    add_effect = False
                    supress_message = True
                if 'duplicate' == new_effect.stacking_behavior:
                    add_effect = True
                if 'ignore' in new_effect.stacking_behavior:
                    add_effect = False

        if add_effect:
            fighter.status_effects.append(new_effect)
        if new_effect.on_apply is not None:
            new_effect.on_apply(new_effect, fighter.owner)
        if new_effect.message is not None and fighter.owner is player.instance and not supress_message:
            ui.message(new_effect.message, new_effect.color)

        return True

    def has_status(self, name):
        for effect in self.status_effects:
            if effect.name == name:
                return True
        return False

    def remove_status(self, name):
        for effect in self.status_effects:
            if effect.name == name:
                self.status_effects.remove(effect)
                if effect.on_end is not None:
                    effect.on_end(effect, self.owner)
                return

    def has_attribute(self, name):
        if self.owner is player.instance:
            return main.has_skill(name)
        else:
            return name in self.attributes

    def has_flag(self, flag):
        return self.monster_flags is not None and self.monster_flags & flag == flag

    def accuracy(self, weapon=None):
        if weapon is None:
            weapon = main.get_equipped_in_slot(self.inventory, 'right hand')

        flat_bonus = 0
        if weapon is not None:
            flat_bonus = weapon.accuracy_bonus

        if self.base_accuracy == 0:
            return 0

        flat_bonus += sum(equipment.accuracy_bonus for equipment in main.get_all_equipped(self.inventory) if equipment.category != "weapon")
        mod = int(mul(effect.accuracy_mod for effect in self.status_effects))
        if self.has_status('oiled'):
            flat_bonus -= 3
        if self.has_status('focused'):
            flat_bonus += 5 + (main.has_skill('focus') * 8)
        if self.owner.player_stats and weapon is not None:
            flat_bonus -= 5 * max(weapon.str_requirement - self.owner.player_stats.str, 0)

        return max(int((self.base_accuracy + flat_bonus) * mod), 1)

    def damage_bonus(self):
        return self.base_damage_bonus

    def strength_dice_size(self, weapon=None):
        if weapon is None:
            weapon = main.get_equipped_in_slot(self.inventory, 'right hand')

        bonus = 0
        if weapon is not None:
            bonus = weapon._strength_dice_bonus

        bonus += sum(equipment.strength_dice_bonus for equipment in main.get_all_equipped(self.inventory) if equipment.category != "weapon")
        if self.owner.player_stats:
            return max(self.owner.player_stats.str + bonus, 0)
        else:
            str_dice_size = int(self.monster_str_dice.split('+')[0].split('d')[1])
            return max(str_dice_size + bonus, 0)

    @property
    def abilities(self):
        if self.owner is player.instance:
            return player.get_abilities()
        else:
            a = []
            for ability in self._abilities:
                a.append(ability)
            for item in main.get_all_equipped(self.inventory):
                if item.owner.item.ability:
                    a.append(item.owner.item.ability)
            return a

    def add_ability(self,ability):
        if self.owner is player.instance:
            raise Exception("Not implemented for player")
        else:
            if hasattr(ability,'__iter__'):
                for a in ability:
                    self._abilities.append(a)
            else:
                self._abilities.append(ability)

    @property
    def shield(self):
        sh = self.get_equipped_shield()
        if sh is not None:
            return sh.sh_points
        return 0

    @property
    def armor(self):
        bonus = sum(equipment.armor_bonus for equipment in main.get_all_equipped(self.inventory))
        bonus = int(bonus * mul(effect.armor_mod for effect in self.status_effects))
        if self.has_status('stoneskin'):
            bonus += 2
        if self.has_status('frozen'):
            bonus += 5
        if main.has_skill('guardian_of_light') and (self.owner is player.instance or self.team == 'ally'):
            bonus += 2
        return max(self.base_armor + bonus - self.shred, 0)

    def attack_shred(self,weapon=None):
        if weapon is None:
            weapon = main.get_equipped_in_slot(self.inventory, 'right hand')

        flat_bonus = 0
        if weapon is not None:
            flat_bonus = weapon.shred_bonus

        flat_bonus += sum(equipment.shred_bonus for equipment in main.get_all_equipped(self.inventory) if equipment.category != "weapon")
        bonus = int(mul(effect.shred_mod for effect in self.status_effects))
        return max((self.base_shred + flat_bonus) * bonus, 0)

    def attack_guaranteed_shred(self,weapon=None):
        if weapon is None:
            weapon = main.get_equipped_in_slot(self.inventory, 'right hand')

        flat_bonus = 0
        if weapon is not None:
            flat_bonus = weapon.guaranteed_shred_bonus

        flat_bonus += sum(equipment.guaranteed_shred_bonus for equipment in main.get_all_equipped(self.inventory) if equipment.category != "weapon")
        return max((self.base_guaranteed_shred + flat_bonus), 0)

    def attack_pierce(self,weapon=None):
        if weapon is None:
            weapon = main.get_equipped_in_slot(self.inventory, 'right hand')

        flat_bonus = 0
        if weapon is not None:
            flat_bonus = weapon.pierce_bonus
        bonus = int(mul(effect.pierce_mod for effect in self.status_effects))

        flat_bonus += sum(equipment.pierce_bonus for equipment in main.get_all_equipped(self.inventory) if equipment.category != "weapon")
        return max((self.base_pierce + flat_bonus) * bonus, 0)

    @property
    def evasion(self):
        bonus = sum(equipment.evasion_bonus for equipment in main.get_all_equipped(self.inventory))
        mul_bonus = 1.0 * mul(effect.evasion_mod for effect in self.status_effects)
        if self.has_status('sluggish') or self.has_status('cursed'):
            bonus -= 5
        if self.owner.player_stats:
            return max(int((self.base_evasion + (self.owner.player_stats.agi / 3) + bonus) * mul_bonus), 0)
        else:
            return max(int((self.base_evasion + bonus) * mul_bonus), 0)

    @property
    def will(self):
        bonus = sum(equipment.will_bonus for equipment in main.get_all_equipped(self.inventory))
        mul_bonus = 1.0 * mul(effect.will_mod for effect in self.status_effects)
        if self.owner.player_stats:
            return max(int((self.base_will + (self.owner.player_stats.wiz / 3) + bonus) * mul_bonus), 0)
        else:
            return max(int((self.base_will + bonus) * mul_bonus), 0)

    @property
    def fortitude(self):
        bonus = sum(equipment.fortitude_bonus for equipment in main.get_all_equipped(self.inventory))
        mul_bonus = 1.0 * mul(effect.fortitude_mod for effect in self.status_effects)
        if self.owner.player_stats:
            return max(int((self.base_fortitude + (self.owner.player_stats.con / 3) + bonus) * mul_bonus), 0)
        else:
            return max(int((self.base_fortitude + bonus) * mul_bonus), 0)

    @property
    def spell_power(self, elements=[]):
        bonus = sum(equipment.spell_power_bonus for equipment in main.get_all_equipped(self.inventory))
        mul_bonus = 1.0 * mul(effect.spell_power_mod for effect in self.status_effects)
        if self.owner.player_stats:
            for s_e in elements:
                bonus += main.skill_value("{}_affinity".format(s_e))
            return int((self.base_spell_power + self.owner.player_stats.int + bonus) * mul_bonus)
        else:
            return int((self.base_spell_power + bonus) * mul_bonus)

    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment in main.get_all_equipped(self.inventory))
        return self.base_max_hp + bonus

    @property
    def stamina_regen(self):
        bonus = sum(equipment.stamina_regen for equipment in main.get_all_equipped(self.inventory))
        return bonus

    def attack_speed(self,weapon=None):
        # NOTE: this is a player-only stat
        if self.owner.player_stats:
            if weapon is None:
                weapon = main.get_equipped_in_slot(self.inventory, 'right hand')

            flat_bonus = 0
            if weapon is not None:
                flat_bonus = weapon.attack_speed_bonus
            bonus = int(mul(effect.attack_speed_mod for effect in self.status_effects))

            flat_bonus += sum(equipment.attack_speed_bonus for equipment in main.get_all_equipped(self.inventory))
            return max((self.owner.player_stats.agi + flat_bonus) * bonus, 0)
        else:
            return 0

    @property
    def equip_weight(self):
        if self.owner is not player.instance:
            return 0
        w = 0
        for equipment in main.get_all_equipped(self.inventory):
            if equipment.weight and equipment.weight > 0:
                w += equipment.weight
        return w

    @property
    def max_equip_weight(self):
        if self.owner is not player.instance:
            return 0
        bonus = 0
        for i in main.get_all_equipped(self.inventory):
            if i.weight < 0:
                bonus += -i.weight
        return self.owner.player_stats.str * 2 + bonus

    @property
    def resistances(self):
        resists = dict(self._resistances)
        for e in main.get_all_equipped(self.inventory):
            for r in e.resistances.keys():
                if r in resists.keys() and e.resistances[r] != 'immune':
                    resists[r] += e.resistances[r]
                else:
                    resists[r] = e.resistances[r]
        for e in self.status_effects:
            for r in e.resistance_mod.keys():
                if r in resists.keys() and e.resistance_mod[r] != 'immune':
                    resists[r] += e.resistance_mod[r]
                else:
                    resists[r] = e.resistance_mod[r]

        return resists

    @property
    def immunities(self):
        i = []
        for resist in self.resistances.keys():
            if self.resistances[resist] == 'immune':
                i.append(resist)
        return i

    def get_equipped_shield(self):
        shield = main.get_equipped_in_slot(self.inventory, 'floating shield')
        if shield is None:
            shield = main.get_equipped_in_slot(self.inventory, 'left hand')
        if shield is not None\
                and hasattr(shield, 'sh_points')\
                and hasattr(shield, 'sh_recovery')\
                and hasattr(shield, 'sh_raise_cost'):
            return shield
        return None


hit_tables = {
    'default': {
        'body' : 60,
        'head'  : 10,
        'arms'  : 15,
        'legs'  : 15
    },
    'beast': {
        'body'  : 50,
        'head'  : 20,
        'legs'  : 30
    },
    'insect': {
        'body'  : 60,
        'head'  : 30,
        'legs'  : 10
    },
    'avian': {
        'body' : 60,
        'head'  : 10,
        'wings'  : 25,
        'legs'  : 5
    },
    'plant': {
        'stem'  : 100
    }
}

import effects
location_damage_tables = {
    'body' : {
        'damage':1.0,
    },
    'head' : {
        'damage':1.2,
        'effect':effects.stunned,
        'effect_chance':0.5
    },
    'arms' : {
        'damage':0.75,
        'effect':effects.exhausted,
        'effect_chance':0.5,
    },
    'wings' : {
        'damage':0.75,
        'effect':effects.exhausted,
        'effect_chance':0.5,
    },
    'legs' : {
        'damage':0.75,
        'effect':effects.immobilized,
        'effect_chance':0.7,
    },
    'stem' : {
        'damage':1.0
    }
}

damage_description_tables = {
    'stabbing' : [
        ('stab', 'stabs'),
        ('spear', 'spears'),
        ('drive through', 'drives through'),
        ('impale', 'impales')
    ],
    'slashing' : [
        ('cut', 'cuts'),
        ('slash', 'slashes'),
        ('lay open', 'lays open'),
        ('cleave through', 'cleaves through')
    ],
    'bludgeoning' : [
        ('strike', 'strikes'),
        ('crack', 'cracks'),
        ('smash', 'smashes'),
        ('shatter', 'shatters')
    ],
    'deflected' : [
        ('deflect off', 'deflects off'),
        ('bounce off', 'bounces off'),
        ('glance off', 'glances off'),
        ('graze', 'grazes')
    ],
    'fire': [
        ('char', 'chars'),
        ('burn', 'burns'),
        ('immolate', 'immolates'),
        ('incinerate', 'incinerates')
    ],
    'cold': [
        ('freeze','freezes'),
        ('shatter','shatters')
    ],
    'lightning': [
        ('shock', 'shocks'),
        ('zap', 'zaps'),
        ('jolt', 'jolts'),
        ('electrocute', 'electrocutes'),
    ],
    'radiance': [
        ('smite', 'smites'),
        ('disintegrate', 'disintegrates'),
    ],
    'death': [
        ('curse','curses'),
        ('defile', 'defiles'),
        ('torment', 'torments')
    ]
}

def attack_ex(fighter, target, stamina_cost, on_hit=None, verb=None, accuracy_modifier=1, damage_multiplier=1, shred_modifier=0,
              guaranteed_shred_modifier=0, pierce_modifier=0, weapon=None, blockable=True):
    if weapon is None:
        weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')

    # check stamina
    if fighter.owner.name == 'player':
        if fighter.stamina < stamina_cost:
            ui.message("You can't find the strength to swing your weapon!", libtcod.light_yellow)
            return 'failed'
        else:
            fighter.adjust_stamina(-stamina_cost)

    if roll_to_hit(target, fighter.accuracy(weapon) * accuracy_modifier):
        # Target was hit

        #Determine location based effects
        location = roll_hit_location(target.fighter.hit_table)
        effect = roll_location_effect(target.fighter.inventory,location)

        damage_mod = location_damage_tables[location]['damage']

        # Attacks against stunned targets are critical

        if weapon and ((target.fighter.has_status('stunned') and verb != 'bashes')
                       or target.fighter.has_status('off balance')):
            damage_mod *= weapon.crit_bonus

        if target.fighter.has_status('stung'):
            damage_mod *= consts.CENTIPEDE_STING_AMPLIFICATION

        if target.fighter.has_status('solace'):
            damage_mod *= 0.5

        if fighter.has_attribute('attribute_rend') and target.fighter.armor - (fighter.attack_pierce(weapon) + pierce_modifier) < 1:
            damage_mod *= 1.5

        if fighter.owner is player.instance:
            #perks!
            if main.has_skill('find_the_gap') and weapon.subtype == 'dagger':
                pierce_modifier += 1

            if main.has_skill('ravager') and target.fighter.armor - (fighter.attack_pierce(weapon) + pierce_modifier) < 1:
                damage_mod *= 1.0 + main.skill_value('ravager')

            if main.has_skill('lord_of_the_fray'):
                damage_mod *= 1.1 * len(main.get_objects(fighter.owner.x,fighter.owner.y,distance=1,
                                            condition=lambda o: o.fighter is not None and o.fighter.team == 'enemy'))

            if main.has_skill('rising_storm'):
                if hasattr(fighter.owner,'rising_storm_last_attack') and fighter.owner.rising_storm_last_attack > 2:
                    damage_mod *= 1.5
                    fighter.owner.rising_storm_last_attack = 0

        damage_mod *= mul(effect.attack_power_mod for effect in fighter.status_effects)

        if damage_multiplier is not None:
            damage_mod *= damage_multiplier

        # weapon-specific damage verbs
        if weapon is not None and weapon.damage_types is not None:
            hit_type = weapon.damage_types
        else:
            hit_type = ['bludgeoning']

        # perks
        if fighter.owner is player.instance:
            if main.has_skill('find_the_gap') and weapon is not None and weapon.subtype == 'dagger':
                pierce_modifier += 1

        subtype = 'unarmed'
        if weapon is not None:
            subtype = weapon.subtype

        str_dice_size = fighter.strength_dice_size(weapon)
        if fighter.owner is player.instance:
            str_dice_size += main.skill_value("{}_mastery".format(subtype))

        weapon_dice = '0d0'
        strength_dice = '0d0'
        if weapon is not None:
            weapon_dice = weapon.weapon_dice
            strength_dice_number = weapon.str_dice
            if fighter.owner is player.instance and main.has_skill('martial_paragon'):
                strength_dice_number += 1
            strength_dice = "{}d{}".format(strength_dice_number,str_dice_size)
        elif fighter.owner is not player.instance:
            strength_dice = fighter.monster_str_dice
        else:
            strength_dice_number = 1
            if main.has_skill('martial_paragon'):
                strength_dice_number += 1
            if main.has_skill('steel_fist'):
                weapon_dice = '1d6'
                strength_dice_number += 1
            strength_dice = "{}d{}".format(strength_dice_number, str_dice_size)

        damage = roll_damage_ex(weapon_dice,strength_dice, target.fighter.armor,
                            fighter.attack_pierce(weapon) + pierce_modifier, hit_type, damage_mod, target.fighter.resistances, flat_bonus=fighter.damage_bonus())

        # Shred armor
        if not target.fighter.has_status('invulnerable'):
            shred = fighter.attack_shred(weapon) + shred_modifier
            for i in range(shred):
                if libtcod.random_get_int(0, 0, 4) == 0 and target.fighter.armor > 0:
                    target.fighter.shred += 1
            target.fighter.shred += min(fighter.attack_guaranteed_shred(weapon) + guaranteed_shred_modifier,
                                        target.fighter.armor)

        if damage > 0:
            percent_hit = float(damage) / float(target.fighter.max_hp)
            # Receive effect
            if effect is not None and percent_hit > 0.1:
                target.fighter.apply_status_effect(effect)

            attack_text_ex(fighter,target,verb,location,damage,hit_type,percent_hit)


            result = target.fighter.take_damage(damage, attacker=fighter.owner, blockable=blockable)
            if result != 'blocked' and result > 0:
                # Trigger on-hit effects
                if on_hit is not None and target.fighter is not None:
                    if isinstance(on_hit,(list,set,tuple)):
                        for h in on_hit:
                            h(fighter.owner, target, damage)
                    else:
                        on_hit(fighter.owner, target, damage)
                if weapon is not None and weapon.on_hit is not None:
                    for oh in weapon.on_hit:
                        oh(fighter.owner, target, damage)

                if target.fighter is not None and target.fighter.has_status('judgement'):
                    target.fighter.apply_status_effect(effects.judgement(stacks=main.roll_dice('1d4')))

            if weapon is not None:
                main.check_breakage(weapon)

            if fighter.owner is player.instance:
                if target.fighter is not None and main.has_skill('fist_of_foretold_demise') and weapon is None:
                    target.fighter.apply_status_effect(effects.doom(stacks=main.roll_dice('1d2')))

                if main.has_skill('cut_and_run') and weapon.subtype == 'dagger':
                    fighter.apply_status_effect(effects.free_move())

                if main.has_skill('wild_swings') and weapon.subtype == 'axe':
                    for t in main.get_objects(target.x,target.y,distance=1,
                                              condition=lambda o: o.fighter is not None and o.fighter.team is not 'ally'):
                        if t != target:
                            t.fighter.take_damage(main.roll_dice('1d6'), attacker=fighter.owner)

                if main.has_skill('gatekeeper') and target.fighter is not None:
                    if libtcod.random_get_int(0,0,10 + target.fighter.armor) < 5:
                        actions.knock_back(fighter.owner,target)

            return 'hit'
        else:
            verbs = damage_description_tables['deflected']
            verb = verbs[libtcod.random_get_int(0, 0, len(verbs) - 1)]

            #ui.message('The ' + fighter.owner.name.title() + "'s attack " + verb + ' the ' + target.name + '!', libtcod.grey)
            ui.message('%s attack %s %s' % (
                            syntax.name(fighter.owner, possesive=True).capitalize(),
                            verb[1],
                            syntax.name(target)), libtcod.grey)
            weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')
            if weapon:
                main.check_breakage(weapon)
            return 'blocked'
    else:
        if target is player.instance and main.has_skill('riposte'):
            fighter.apply_status_effect(effects.off_balance())

        if verb is None:
            verb = ('attack', 'attacks')
        #ui.message(fighter.owner.name.title() + ' ' + verb + ' ' + target.name + ', but misses!', libtcod.grey)
        ui.message('%s %s %s, but %s!' % (
                            syntax.name(fighter.owner).capitalize(),
                            syntax.conjugate(fighter.owner is player.instance, verb),
                            syntax.name(target),
                            syntax.conjugate(fighter.owner is player.instance, ('miss', 'misses'))), libtcod.grey)
        return 'miss'

def spell_attack(fighter,target,spell_name):
    config = abilities.data[spell_name]
    return spell_attack_ex(fighter,target,
                    config.get('accuracy'),
                    config.get('base_damage','0d0'),
                    config.get('dice',0),
                    config['element'],
                    config.get('peirce',0),
                    config.get('shred',0))


def spell_attack_ex(fighter, target, accuracy, base_damage, spell_dice, spell_elements, pierce, shred = 0,
                    damage_mod=1, defense_type='evasion'):
    if target.fighter.has_status('reflect-magic'):
        target = fighter.owner

    if accuracy is None or roll_to_hit(target, accuracy, defense_type=defense_type):
        # Target was hit
        if target.fighter.has_status('stung'):
            damage_mod *= consts.CENTIPEDE_STING_AMPLIFICATION

        if fighter is not None and fighter.owner is player.instance and main.has_skill('searing_mind'):
            damage_mod *= 1.1

        if target.fighter.has_status('solace'):
            damage_mod *= 0.5

        if fighter is None:
            spell_power = 0
        else:
            spell_power = fighter.spell_power

        damage = roll_damage_ex(base_damage, "{}d{}".format(spell_dice, spell_power),
                                target.fighter.armor, pierce, spell_elements, damage_mod,
                                target.fighter.resistances, 0)

        if damage > 0:
            attack_text_ex(fighter,target,None,None,damage,spell_elements,float(damage) / float(target.fighter.max_hp))
            attacker = None
            if fighter is not None:
                attacker = fighter.owner
            target.fighter.take_damage(damage, attacker=attacker)

            if target.fighter is not None:
                # Shred armor
                if fighter is not None and fighter.owner is player.instance and main.has_skill('spellshards'):
                    shred += 2

                for i in range(shred):
                    if libtcod.random_get_int(0, 0, 4) == 0 and target.fighter.armor > 0:
                        target.fighter.shred += 1
            return 'hit'
        else:
            if fighter is None:
                name = "something's"
            else:
                name = syntax.name(fighter.owner, possesive=True)
            verbs = damage_description_tables['deflected']
            verb = verbs[libtcod.random_get_int(0, 0, len(verbs) - 1)]
            ui.message('%s attack %s %s' % (
                            name.capitalize(),
                            verb[0],
                            syntax.name(target)), libtcod.grey)
            return 'blocked'
    else:
        if fighter is None:
            name = 'something'
            is_player = False
        else:
            name = syntax.name(fighter.owner)
            is_player = fighter.owner is player.instance
        ui.message('%s %s %s, but %s!' % (
                            name.capitalize(),
                            syntax.conjugate(is_player, ('attack', 'attacks')),
                            syntax.name(target),
                            syntax.conjugate(is_player, ('miss', 'misses'))), libtcod.grey)
        return 'miss'

resist_values = {
    -4 : 7.7,
    -3 : 4.6,
    -2 : 2.7,
    -1 : 1.6,
    0 : 1.0,
    1 : 0.6,
    2 : 0.36,
    3 : 0.216,
    4 : 0.13,
}
def roll_damage_ex(damage_dice, stat_dice, defense, pierce, damage_types, damage_modifier_ex, resists, flat_bonus=0):
    damage_mod = damage_modifier_ex

    for d_t in damage_types:
        if d_t in resists.keys():
            if resists[d_t] == 'immune':
                damage_mod = 0
            else:
                damage_mod *= resist_values[max(min(resists[d_t], 4), -4)]

    #calculate damage
    damage = main.roll_dice(damage_dice, normalize_size=4) + main.roll_dice(stat_dice, normalize_size=4) + flat_bonus
    damage = int(float(damage) * damage_mod)

    if 'bludgeoning' in damage_types or 'slashing' in damage_types or 'stabbing' in damage_types:
        # calculate damage reduction
        effective_defense = defense - pierce
        # without armor, targets receive no damage reduction!
        if effective_defense > 0:
            # Damage is reduced by 25% + 5% for every point of armor up to 5 armor (50% reduction)
            reduction_factor = consts.ARMOR_REDUCTION_BASE + consts.ARMOR_REDUCTION_STEP * min(effective_defense,
                                                                                               consts.ARMOR_REDUCTION_DROPOFF)
            # For every point of armor after 5, damage is further reduced by 2.5% (15+ armor = 100% reduction!)
            if effective_defense > consts.ARMOR_REDUCTION_DROPOFF:
                reduction_factor += 0.5 * consts.ARMOR_REDUCTION_STEP * (
                    effective_defense - consts.ARMOR_REDUCTION_DROPOFF)
            # Apply damage reduction
            damage = math.ceil(damage * (1 - reduction_factor))
            # After reduction, apply a flat reduction that is a random amount from 0 to the target's armor value
            damage = max(0, damage - libtcod.random_get_int(0, 0, effective_defense))
        else:
            damage = int(damage * (1.0 + main.skill_value('ravager')))

    return int(math.ceil(damage))

def attack_text_ex(fighter,target,verb,location,damage,damage_types,severity):
    damage_type = damage_types[libtcod.random_get_int(0, 0, len(damage_types) - 1)]

    if verb is None:
        verb = main.normalized_choice(damage_description_tables[damage_type], severity)

    target_name = syntax.name(target)

    if fighter is None:
        name = 'something'
        is_player = False
    else:
        name = syntax.name(fighter.owner)
        is_player = fighter.owner is player.instance

    if damage is not None:
        if location is not None:
            ui.message('%s %s %s in the %s for %s%d damage!' % (
                name.capitalize(),
                syntax.conjugate(is_player, verb),
                target_name, location,
                syntax.relative_adjective(damage, damage, ['an increased ', 'a reduced ']),
                damage), libtcod.grey)
        else:
            ui.message('%s %s %s for %s%d damage!' % (
                name.capitalize(),
                syntax.conjugate(is_player, verb),
                target_name,
                syntax.relative_adjective(damage, damage, ['an increased ', 'a reduced ']),
                damage), libtcod.grey)

def roll_hit_location(table):
    if table is None:
        table = 'default'
    return main.random_choice(hit_tables[table])

def roll_location_effect(inventory, location):
    location_effect = location_damage_tables[location]
    if location_effect.get('effect') is not None and location_effect.get('effect_chance'):
        equipped = main.get_equipped_in_slot(inventory,location)
        location_resist = (equipped.armor_bonus if equipped is not None else 0) / consts.ARMOR_LOCATION_RESIST_FACTOR
        if location_effect['effect_chance'] < libtcod.random_get_float(0, 0.0, 1.0) and \
                        libtcod.random_get_float(0, 0.0, 1.0) > location_resist:
            return location_effect['effect']()
        else:
            return None
    else:
        return None

def roll_to_hit(target,  accuracy, defense_type='evasion'):
    return libtcod.random_get_float(0, 0, 1) < get_chance_to_hit(target, accuracy, defense_type=defense_type)

def get_chance_to_hit(target, accuracy, defense_type='evasion'):
    if defense_type == 'will':
        return 1.0 - float(target.fighter.will) / float(max(accuracy, target.fighter.will + 1))
    elif defense_type == 'fortitude':
        return 1.0 - float(target.fighter.fortitude) / float(max(accuracy, target.fighter.fortitude + 1))
    elif defense_type == 'evasion':
        if target.fighter.has_status('stunned') or target.fighter.has_status('frozen'):
            return 1.0
        if target.behavior and (target.behavior.ai_state == 'resting' or target.behavior.ai_state == 'wandering'):
            return 1.0
        return 1.0 - float(target.fighter.evasion) / float(max(accuracy, target.fighter.evasion + 1))
    else:
        return 1.0

def on_hit_burn(attacker, target, damage):
    if target.fighter is None:
        return
    if libtcod.random_get_int(0, 1, 10) <= 7:
        target.fighter.apply_status_effect(effects.burning())

def on_hit_freeze(attacker, target, damage):
    if target.fighter is None:
        return
    if libtcod.random_get_int(0, 1, 10) <= 3:
        target.fighter.apply_status_effect(effects.frozen(duration=3))

def on_hit_slow(attacker, target, damage):
    if target.fighter is None:
        return
    if libtcod.random_get_int(0, 1, 10) <= 7:
        target.fighter.apply_status_effect(effects.slowed(duration=5))

def on_hit_sluggish(attacker, target, damage):
    if target.fighter is None:
        return
    if libtcod.random_get_int(0, 1, 10) <= 7:
        target.fighter.apply_status_effect(effects.sluggish(duration=5))

def on_hit_chain_lightning(attacker, target, damage, zapped=None):
    if zapped is None:
        zapped = [target]
    else:
        zapped.append(target)
    if target.fighter is None:
        return
    damage = roll_damage_ex('1d10', '0d0', target.fighter.armor, 5, 'lightning', 1.0,
                            target.fighter.resistances)

    if damage > 0:
        attack_text_ex(attacker.fighter, target, None, None, damage, 'lightning', float(damage) / float(target.fighter.max_hp))

        target.fighter.take_damage(damage, attacker=attacker)
        for adj in main.adjacent_tiles_diagonal(target.x, target.y):
            for obj in main.current_map.fighters:
                if obj.x == adj[0] and obj.y == adj[1] and obj.fighter.team != attacker.fighter.team and obj not in zapped:
                    on_hit_chain_lightning(attacker, obj, damage, zapped)
    else:
        ui.message('The shock does not damage %s' % syntax.name(target), libtcod.grey)

def on_hit_lifesteal(attacker, target, damage):
    attacker.fighter.heal(damage)

def on_hit_knockback(attacker, target, damage, force=6):
    if target.fighter is None:
        return

    if 'displacement' in target.fighter.immunities:
        if fov.player_can_see(target.x, target.y):
            ui.message('%s %s.' % (syntax.name(target).capitalize(), syntax.conjugate(
                target is player.instance, ('resist', 'resists'))), libtcod.gray)
        return

    diff_x = target.x - attacker.x
    diff_y = target.y - attacker.y
    if diff_x > 0:
        diff_x = diff_x / abs(diff_x)
    if diff_y > 0:
        diff_y = diff_y / abs(diff_y)
    direction = (diff_x, diff_y)

    steps=0
    while steps <= force:
        steps += 1
        against = main.get_objects(target.x + direction[0], target.y + direction[1], lambda o: o.blocks)
        if against is None or len(against) == 0:
            against = syntax.name(main.current_map.tiles[target.x + direction[0]][target.y + direction[1]])
        else:
            against = 'the ' + against.name
        if not target.move(direction[0], direction[1]):
            # Could not move
            damage = roll_damage_ex('%dd4' % steps, '0d0', target.fighter.armor, 0, 'budgeoning', 1.0,
                                    target.fighter.resistances)
            ui.message('%s %s backwards and collides with %s, taking %d damage.' % (
                syntax.name(target).capitalize(),
                syntax.conjugate(target is player.instance, ('fly', 'flies')),
                against,
                damage), libtcod.gray)
            target.fighter.take_damage(damage, attacker=attacker)
            steps = force + 1

def on_hit_reanimate(attacker, target, damage):
    main.raise_dead(attacker,target)

def mul(sequence):
    return reduce(lambda x,y: x * y,sequence,1)
