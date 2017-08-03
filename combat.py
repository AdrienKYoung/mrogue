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

import math

import consts
import fov
import game as main
import libtcodpy as libtcod
import pathfinding
import player
import spells
import syntax
import ui
import effects

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

        self.permanent_ally = False  # Unit will follow player through rooms

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
            s = '%s Accuracy: %d%%' % (syntax.pronoun(self.owner, possesive=True).capitalize(), int(100.0 * get_chance_to_hit(player.instance, self.accuracy())))
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

    def take_damage(self, damage, attacker=None, affect_shred=True, blockable=False, suppress_death_messages=False):
        if self.has_status('invulnerable') or self.has_attribute('attribute_invulnerable'):
            if self.owner is player.instance or fov.player_can_see(self.owner.x, self.owner.y):
                ui.message('%s %s protected by a radiant shield!' %
                           (syntax.name(self.owner).capitalize(),
                            syntax.conjugate(self.owner is player.instance, ('are', 'is'))),
                           spells.essence_colors['radiance'])
            damage = 0

        if self.has_status('cursed') or self.has_status('stung') and damage > 0:
            damage = int(damage * 1.25)

        if self.has_status('vitality'):
            damage = int(damage * 0.5)

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
                    from actions import on_death_actions
                    is_summoned = self.owner.summon_time is not None
                    if not is_summoned:
                        self.drop_essence()
                    self.owner.is_corpse = True
                    death_context = dict(self.death_function)
                    if suppress_death_messages:
                        death_context['suppress_messags'] = True
                    function = on_death_actions.table[death_context['function']]
                    if function is not None:
                        if sh is not None:
                            sh.sh_points = sh.sh_max
                            sh.timer = 0
                            sh.raised = True
                        function(self.owner, death_context)
                    if attacker is not None and attacker.fighter is not None and attacker.fighter.on_get_kill is not None and not is_summoned:
                        attacker.fighter.on_get_kill(attacker,self,damage)
                if affect_shred:
                    self.time_since_last_damaged = 0
        return damage

    def get_shredded(self, amount):
        if amount > 0:
            self.shred += min(amount, self.armor)
            self.time_since_last_damaged = 0

    def get_hit(self, attacker,damage):
        if self.owner.behavior is not None:
            self.owner.behavior.get_hit(attacker)
        if self.on_get_hit is not None:
            from actions import on_damaged_actions
            on_damaged_actions.table[self.on_get_hit](self.owner, attacker, damage)

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

        # Check terrain
        if self.owner.movement_type & pathfinding.FLYING != pathfinding.FLYING:
            if main.current_map.tiles[self.owner.x][self.owner.y].tile_type == 'lava':
                damage = roll_damage('1d200', '0d0', None, 0, ['fire'], 1, self.resistances)
                self.get_shredded(5)
                if damage > 0 and (self.owner is player.instance or fov.player_can_see(self.owner.x, self.owner.y)):
                    ui.message("The lava melts %s, dealing %d damage!" % (syntax.name(self.owner), damage), libtcod.flame)
                self.take_damage(damage)

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
            resist_bonus = 0
            for resist in fighter.resistances.keys():
                if resist == new_effect.name:
                    resist_bonus = fighter.resistances[resist]
                    break
            if not roll_to_hit(fighter.owner, dc, new_effect.target_defense, defense_bonus=resist_bonus):
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
            bonus = weapon.strength_dice_bonus

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
                    if resists[r] != 'immune':
                        resists[r] += e.resistances[r]
                else:
                    resists[r] = e.resistances[r]
        for e in self.status_effects:
            for r in e.resistance_mod.keys():
                if r in resists.keys() and e.resistance_mod[r] != 'immune':
                    if resists[r] != 'immune':
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
        ('prick', 'pricks'),
        ('stab', 'stabs'),
        ('spear', 'spears'),
        ('pierce', 'pierces'),
        ('drive through', 'drives through'),
        ('impale', 'impales')
    ],
    'slashing' : [
        ('nick', 'nicks'),
        ('cut', 'cuts'),
        ('slash', 'slashes'),
        ('lay open', 'lays open'),
        ('cleave through', 'cleaves through')
    ],
    'bludgeoning' : [
        ('strike', 'strikes'),
        ('crack', 'cracks'),
        ('bludgeon', 'bludgeons'),
        ('pummel', 'pummels'),
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
        ('scorch', 'scorches'),
        ('char', 'chars'),
        ('burn', 'burns'),
        ('immolate', 'immolates'),
        ('incinerate', 'incinerates')
    ],
    'cold': [
        ('chill','chills'),
        ('freeze','freezes'),
    ],
    'lightning': [
        ('shock', 'shocks'),
        ('zap', 'zaps'),
        ('jolt', 'jolts'),
        ('electrocute', 'electrocutes'),
    ],
    'radiance': [
        ('smite', 'smites'),
        ('cleanse', 'cleanses'),
        ('disintegrate', 'disintegrates'),
    ],
    'death': [
        ('curse','curses'),
        ('defile', 'defiles'),
        ('torment', 'torments')
    ],
    'acid': [
        ('singe', 'singes'),
        ('burn', 'burns'),
        ('dissolve', 'dissolves'),
        ('melt', 'melts'),
    ],
    'fume': [
        ('choke', 'chokes'),
        ('suffocate', 'suffocates'),
        ('asphyxiate', 'asphyxiates'),
    ]
}

# Deprecated - use attack_physical instead
def attack_ex(fighter, target, stamina_cost, on_hit=None, verb=None, accuracy_modifier=1, damage_multiplier=1, shred_modifier=0,
              guaranteed_shred_modifier=0, pierce_modifier=0, weapon=None, blockable=True):
    return attack_physical(fighter, target, stamina_cost, on_hit, verb, accuracy_modifier, damage_multiplier,
                           shred_modifier, guaranteed_shred_modifier, pierce_modifier, weapon, blockable)

def attack_magical(fighter, target, spell_name, accuracy_bonus=0):
    config = abilities.data[spell_name]
    acc = config.get('accuracy')
    if acc is not None:
        acc += accuracy_bonus
    return attack_magical_ex(fighter.owner, target,
                             accuracy=acc,
                             base_damage_dice=config.get('base_damage', '0d0'),
                             spell_dice_number=config.get('dice', 0),
                             spell_elements=config.get('element', []),
                             flat_damage_bonus=config.get('flat_damage_bonus', 0),
                             pierce=config.get('pierce', 0),
                             shred=config.get('shred', 0),
                             guaranteed_shred=config.get('guaranteed_shred', 0),
                             defense_types=config.get('defense', 'evasion'),
                             damage_types=config.get('damage_types', config.get('element')),
                             blockable=config.get('blockable', False),
                             attack_name=config['name'])

# Used for attacks from spells, charms, non-physical abilities, etc
def attack_magical_ex(attacker, target, accuracy=None, base_damage_dice='0d0', spell_dice_number=0, spell_elements=None, flat_damage_bonus=0,
                      pierce=0, shred=0, guaranteed_shred=0, damage_mod=1, defense_types=None, damage_types=None,
                      blockable=False, attack_name=None):
    if target is None or target.fighter is None:
        return 'failed'  # cannot attack non-fighters
    if target.fighter.has_status('reflect-magic') and attacker is not None and attacker.fighter is not None:
        target = attacker.owner

    # calculate damage dice
    if attacker is None or attacker.fighter is None:
        spell_power = 0
    else:
        spell_power = attacker.fighter.spell_power(spell_elements)
    damage_dice = base_damage_dice
    damage_stat_dice = "{}d{}".format(spell_dice_number, spell_power)

    # calculate damage multiplier
    if attacker is player.instance and main.has_skill('searing_mind'):
        damage_mod *= 1.1
    if target.fighter.has_status('solace'):
        damage_mod *= 0.5

    # calculate shred
    if attacker is player.instance and main.has_skill('spellshards'):
        guaranteed_shred += 1

    # save target's max hp for later
    target_max_hp = target.fighter.max_hp

    # process the attack
    attack_result_data = process_attack(attacker,
                                        target,
                                        accuracy=accuracy,
                                        defense_types=defense_types,
                                        blockable=blockable,
                                        on_hit=None,
                                        damage_base=flat_damage_bonus,
                                        damage_dice=damage_dice,
                                        damage_stat_dice=damage_stat_dice,
                                        damage_multiplier=damage_mod,
                                        pierce=pierce,
                                        shred=shred,
                                        guaranteed_shred=guaranteed_shred,
                                        damage_types=damage_types,
                                        suppress_death_messages=True)
    if attack_result_data['result'] != 'missed':
        damage_taken = attack_result_data['damage taken']
        if damage_taken > 0:
            attack_text(attacker.fighter, target, None, None, damage_taken, damage_types,
                           float(damage_taken) / float(target_max_hp), attack_name=attack_name)
            return_value = 'hit'
        else:
            verbs = damage_description_tables['deflected']
            verb = verbs[libtcod.random_get_int(0, 0, len(verbs) - 1)]
            ui.message('The %s %s %s.' % (attack_name, verb[0], syntax.name(target)), libtcod.gray)
            return_value = 'blocked'

        if attack_result_data['killed target']:
            ui.message('%s %s %s.' % (
                syntax.name(attacker).capitalize(),
                syntax.conjugate(attacker is player.instance, ('kill', 'kills')),
                syntax.name(target, reflexive=attacker).replace('remains of ', '')), libtcod.red)
    else:
        if attack_result_data['evasion method'] == 'evasion':
            verb = ('dodge', 'dodges')
        else:
            verb = ('resist', 'resists')
        ui.message('%s %s the %s.' % (
                            syntax.name(target),
                            syntax.conjugate(attacker is player.instance, verb),
                            attack_name), libtcod.grey)
        return_value = 'miss'
    return return_value

# Used for attacks from weapons, monster melee attacks, things that affect armor, etc
def attack_physical(fighter, target, stamina_cost=0, on_hit=None, verb=None, accuracy_modifier=1, damage_multiplier=1, shred_modifier=0,
              guaranteed_shred_modifier=0, pierce_modifier=0, weapon=None, blockable=True):
    if weapon is None:
        weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')
    if target is None or target.fighter is None:
        return 'failed'  # cannot attack non-fighters

    # check stamina
    if fighter.owner is player.instance:
        if fighter.stamina < stamina_cost:
            ui.message("You can't find the strength to swing your weapon!", libtcod.light_yellow)
            return 'failed'
        else:
            fighter.adjust_stamina(-stamina_cost)

    # calculate accuracy
    accuracy = fighter.accuracy(weapon) * accuracy_modifier

    # defense type
    defense_types = ['evasion']  # physical attacks can be dodged, but not resisted with fortitude/will

    # collect all on-hits
    if on_hit is not None:
        total_on_hit = list(on_hit)
        if weapon is not None and weapon.on_hit is not None:
            for weapon_on_hit in weapon.on_hit:
                total_on_hit.append(weapon_on_hit)
    elif weapon is not None and weapon.on_hit is not None:
        total_on_hit = list(weapon.on_hit)
    else:
        total_on_hit = None

    # find base damage
    damage_base = fighter.damage_bonus()

    # calculate damage dice (of the format 'xdx' where x is an integer)
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
        strength_dice = "{}d{}".format(strength_dice_number, str_dice_size)
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
    damage_dice = weapon_dice
    damage_stat_dice = strength_dice

    # calculate damage multipliers
    damage_mod = damage_multiplier
    # Attacks against stunned targets are critical
    if (target.fighter.has_status('stunned') or target.fighter.has_status('off balance')) and verb != 'bashes':
        if weapon:
            damage_mod *= weapon.crit_bonus
        else:
            damage_mod *= 2.0  # unarmed crit bonus
    if target.fighter.has_status('solace'):
        damage_mod *= 0.5
    if fighter.has_attribute('attribute_rend') and target.fighter.armor < 1:
        damage_mod *= 1.5
    if fighter.owner is player.instance:
        # perks!
        if main.has_skill('find_the_gap') and weapon is not None and weapon.subtype == 'dagger':
            pierce_modifier += 1

        if main.has_skill('ravager') and target.fighter.armor - (fighter.attack_pierce(weapon) + pierce_modifier) < 1:
            damage_mod *= 1.0 + main.skill_value('ravager')

        if main.has_skill('lord_of_the_fray'):
            damage_mod *= 1.25 ** len(main.get_objects(fighter.owner.x, fighter.owner.y, distance=1, condition=lambda
                                                          o: o.fighter is not None and o.fighter.team == 'enemy'))

        if main.has_skill('rising_storm'):
            if hasattr(fighter.owner, 'rising_storm_last_attack') and fighter.owner.rising_storm_last_attack > 2:
                damage_mod *= 1.5
                fighter.remove_status('Rising Storm')
                fighter.owner.rising_storm_last_attack = 0
    damage_mod *= mul(effect.attack_power_mod for effect in fighter.status_effects)
    damage_multiplier = damage_mod

    # calculate pierce
    pierce = fighter.attack_pierce(weapon) + pierce_modifier

    # calculate shred
    shred = fighter.attack_shred(weapon) + shred_modifier
    guaranteed_shred = fighter.attack_guaranteed_shred(weapon) + guaranteed_shred_modifier

    # acquire damage types
    if weapon is not None and weapon.damage_types is not None:
        damage_types = weapon.damage_types
    else:
        # TODO: different damage types for other unarmed attacks (e.g. a bite that deals piercing damage)
        damage_types = ['bludgeoning']

    # save target's max hp for later
    target_max_hp = target.fighter.max_hp

    # process the attack with the data collected
    attack_result = process_attack(attacker=fighter.owner,
                                   target=target,
                                   accuracy=accuracy,
                                   defense_types=defense_types,
                                   blockable=blockable,
                                   on_hit=total_on_hit,
                                   damage_base=damage_base,
                                   damage_dice=damage_dice,
                                   damage_stat_dice=damage_stat_dice,
                                   damage_multiplier=damage_multiplier,
                                   pierce=pierce,
                                   shred=shred,
                                   guaranteed_shred=guaranteed_shred,
                                   damage_types=damage_types,
                                   suppress_death_messages=True)
    # process post-attack
    if attack_result['result'] != 'missed':
        # Check weapon breakage
        if weapon is not None:
            main.check_breakage(weapon)
        damage_taken = attack_result['damage taken']
        if damage_taken > 0:
            # Print damage text
            percent_hit = float(damage_taken) / float(target_max_hp)
            attack_text(fighter,target,verb,None,damage_taken,damage_types,percent_hit)
            # Apply perk effects
            if fighter.owner is player.instance:
                if target.fighter is not None and main.has_skill('fist_of_foretold_demise') and weapon is None:
                    target.fighter.apply_status_effect(effects.doom(stacks=main.roll_dice('1d2')))

                if main.has_skill('cut_and_run') and weapon.subtype == 'dagger':
                    fighter.apply_status_effect(effects.free_move())

                if main.has_skill('wild_swings') and weapon.subtype == 'axe':
                    for t in main.get_objects(target.x,target.y,distance=1,
                                          condition=lambda o: o.fighter is not None and o.fighter.team is not 'ally'):
                        if t != target:
                            t.fighter.take_damage(main.roll_dice('1d6'), attacker=fighter.owner, blockable=True)

                if main.has_skill('gatekeeper') and target.fighter is not None:
                    if libtcod.random_get_int(0,0,10 + target.fighter.armor) < 5:
                        common.knock_back(fighter.owner,target)

            return_value = 'hit'
        else:  # if damage is zero
            verbs = damage_description_tables['deflected']
            verb = verbs[libtcod.random_get_int(0, 0, len(verbs) - 1)]
            ui.message('%s attack %s %s' % (
                syntax.name(fighter.owner, possesive=True).capitalize(),
                verb[1],
                syntax.name(target)), libtcod.grey)
            return_value = 'blocked'
        if attack_result['killed target']:
            ui.message('%s %s %s.' % (
                syntax.name(fighter.owner).capitalize(),
                syntax.conjugate(fighter.owner is player.instance, ('kill', 'kills')),
                syntax.name(target, reflexive=fighter.owner).replace('remains of ', '')), libtcod.red)
    else:
        if target is player.instance and main.has_skill('riposte'):
            fighter.apply_status_effect(effects.off_balance())
        if verb is None:
            verb = ('attack', 'attacks')
        ui.message('%s %s %s, but %s!' % (
                            syntax.name(fighter.owner).capitalize(),
                            syntax.conjugate(fighter.owner is player.instance, verb),
                            syntax.name(target),
                            syntax.conjugate(fighter.owner is player.instance, ('miss', 'misses'))), libtcod.grey)
        return_value = 'miss'
    return return_value

# Used for the number-crunching of any generic attack. Is called from attack_physical and attack_magical
def process_attack(attacker, target,
                  accuracy=None,
                  defense_types=None, # evasion, will, fortitude...
                  blockable=False, # deals damage to shields
                  on_hit=None,
                  damage_base=0, # flat bonus
                  damage_dice=None,
                  damage_stat_dice=None, # strength/spell power dice
                  damage_multiplier=1,
                  pierce=0,
                  shred=0,
                  guaranteed_shred=0,
                  damage_types=None, # fire, piercing, acid...
                  suppress_death_messages=False):

    if damage_types is None:
        damage_types = ['bludgeoning']
    if target is None or target.fighter is None:
        return  # Cannot attack non-fighters
    attack_result_data = {
        'result' : 'missed',
        'evasion method' : None,
        'damage taken' : 0,
        'shredded' : 0,
        'killed target' : False,
    }

    # Check for hit - check against all defense types. If any fail, the attack misses.
    hit = True
    if accuracy is not None and defense_types is not None:  # an accuracy of None or a lack of defense types = auto-hit
        for defense_type in defense_types:
            if hit and not roll_to_hit(target,accuracy, defense_type):
                hit = False
                attack_result_data['evasion method'] = defense_type
    if hit:
        # Calculate damage
        armor = target.fighter.armor
        resists = target.fighter.resistances
        damage = roll_damage(damage_dice, damage_stat_dice, armor, pierce, damage_types, damage_multiplier, resists,
                                damage_base)
        # Take damage
        damage_taken = target.fighter.take_damage(damage, attacker, affect_shred=True, blockable=blockable,
                                                  suppress_death_messages=suppress_death_messages)

        if damage_taken == 'blocked':
            attack_result_data['result'] = 'blocked'
        else:
            attack_result_data['result'] = 'hit'
            attack_result_data['damage taken'] = damage_taken

        # Check if the target died
        if target.fighter is None:
            attack_result_data['killed target'] = True
        else:
            # Calculate shred
            if (shred > 0 or guaranteed_shred > 0) and not target.fighter.has_status('invulnerable'):
                to_shred = guaranteed_shred
                for i in range(shred):
                    if libtcod.random_get_int(0, 0, 4) == 0:
                        to_shred += 1
                attack_result_data['shredded'] = to_shred
                target.fighter.get_shredded(to_shred)

            # Apply on-hit effects
            if damage_taken != 'blocked' and damage_taken > 0 and target.fighter is not None:
                # Increase judgement stacks
                if target.fighter.has_status('judgement'):
                    target.fighter.apply_status_effect(effects.judgement(stacks=main.roll_dice('1d4')))
                # Trigger on-hit effects
                from actions import on_hit_actions
                if on_hit is not None:
                    for h in on_hit:
                        on_hit_actions.table[h](attacker, target, damage_taken)
    return attack_result_data

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
# Calculate the damage from an attack, taking into account armor, weaknesses, resistances, immunities, etc...
def roll_damage(damage_dice, stat_dice, defense, pierce, damage_types, damage_multiplier=1, resists=None,
                   flat_bonus=0):
    damage_mod = damage_multiplier

    if resists is not None:
        for d_t in damage_types:
            if d_t in resists.keys():
                if resists[d_t] == 'immune':
                    damage_mod = 0
                else:
                    damage_mod *= resist_values[max(min(resists[d_t], 4), -4)]

    #calculate damage
    damage = main.roll_dice(damage_dice, normalize_size=4) + main.roll_dice(stat_dice, normalize_size=4) + flat_bonus
    damage = int(float(damage) * damage_mod)
    if damage == 0:
        return 0  # exit early if damage is zero

    # Apply damage reduction from armor for physical attacks
    if defense is not None and is_physical(damage_types):
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

    return int(math.ceil(damage))

def attack_text(fighter,target,verb,location,damage,damage_types,severity,attack_name=None):
    # Early exit if the attacker and target are not visible
    if fighter.owner is not player.instance and target is not player.instance and \
        not fov.player_can_see(target.x, target.y) and not fov.player_can_see(fighter.owner.x, fighter.owner.y):
        return

    # Choose a damage type from the types provided, or default to 'bludgeoning'
    if damage_types is None or len(damage_types) < 1:
        damage_type = 'bludgeoning'
    else:
        damage_type = damage_types[libtcod.random_get_int(0, 0, len(damage_types) - 1)]
    # Choose a verb based on damage type and severity, or default to 'hit'
    if verb is None:
        if damage_type in damage_description_tables.keys():
            verb = main.normalized_choice(damage_description_tables[damage_type], severity)
        else:
            verb = ('hit', 'hits')
    # Set the target's name - check to see if it should be of the type 'itself'/'yourself' and if it can be seen
    if target is player.instance or fighter.owner is player.instance or fov.player_can_see(target.x, target.y):
        target_name = syntax.name(target, reflexive=fighter.owner).replace('remains of ', '')
    else:
        target_name = 'something'

    if fighter is None or attack_name is not None:
        # Output a message of the format 'The [attack name] [verb]s [target] for [damage] damage!'
        if attack_name is None:
            attack_name = 'attack'
        message = 'The %s %s %s' % (attack_name, verb[1], target_name)
        if location is not None:
            message += ' in the %s' % location
        if damage is not None:
            message += ' for %d damage' % damage
        message += '!'
        ui.message(message, libtcod.gray)
    else:
        # Output a message of the format '[attacker] [verb]s [target] for [damage] damage!'
        if fighter is None or not fov.player_can_see(fighter.owner.x, fighter.owner.y):
            name = 'something'
            is_player = False
        else:
            name = syntax.name(fighter.owner)
            is_player = fighter.owner is player.instance
        message = '%s %s %s' % (name.capitalize(), syntax.conjugate(is_player, verb), target_name)
        if location is not None:
            message += ' in the %s' % location
        if damage is not None:
            message += ' for %d damage' % damage
        message += '!'
        ui.message(message, libtcod.gray)

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

def roll_to_hit(target,  accuracy, defense_type='evasion', defense_bonus=0):
    return libtcod.random_get_float(0, 0, 1) < get_chance_to_hit(target, accuracy, defense_type=defense_type, defense_bonus=defense_bonus)

def get_chance_to_hit(target, accuracy, defense_type='evasion', defense_bonus=0):
    if defense_type is None:
        return 1.0
    elif defense_type == 'will':
        return 1.0 - float(target.fighter.will + defense_bonus) / float(max(accuracy, target.fighter.will + 1))
    elif defense_type == 'fortitude':
        return 1.0 - float(target.fighter.fortitude + defense_bonus) / float(max(accuracy, target.fighter.fortitude + 1))
    elif defense_type == 'evasion':
        if target.fighter.has_status('stunned') or target.fighter.has_status('frozen'):
            return 1.0
        if target.behavior and (target.behavior.ai_state == 'resting' or target.behavior.ai_state == 'wandering'):
            return 1.0
        return 1.0 - float(target.fighter.evasion + defense_bonus) / float(max(accuracy, target.fighter.evasion + 1))
    else:
        return 1.0

def is_physical(damage_types):
    return 'bludgeoning' in damage_types or \
           'slashing' in damage_types or \
           'stabbing' in damage_types or \
           'physical' in damage_types

def mul(sequence):
    return reduce(lambda x,y: x * y,sequence,1)

from actions import common
from actions import abilities
