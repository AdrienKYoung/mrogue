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

class Fighter:

    def __init__(self, hp=1, stamina=0, armor=0, evasion=0, accuracy=25, spell_power=0, death_function=None, breath=6,
                 can_breath_underwater=False, resistances=[], weaknesses=[], inventory=[], on_hit=None, base_shred=0,
                 base_guaranteed_shred=0, base_pierce=0, abilities=[], hit_table=None, monster_flags =0, subtype=None,
                 damage_bonus=0, monster_str_dice=None, spell_resist=0, team='enemy', on_get_hit=None, stealth=None,
                 attributes=[], _range=1):
        self.owner = None
        self.base_max_hp = hp
        self.hp = hp
        self.death_function = death_function
        self.max_stamina = stamina
        self.stamina = stamina
        self.base_armor = armor
        self.base_evasion = evasion
        self.base_spell_power = spell_power
        self.base_spell_resist = spell_resist
        self.base_accuracy = accuracy
        self.max_breath = breath
        self.breath = breath
        self.can_breath_underwater = can_breath_underwater
        self.resistances = list(resistances)
        self.weaknesses = list(weaknesses)
        self.inventory = list(inventory)
        self.attributes = list(attributes)
        self.base_shred = base_shred
        self.base_guaranteed_shred = base_guaranteed_shred
        self.base_pierce = base_pierce
        self.status_effects = []
        self.on_hit = on_hit
        self.shred = 0
        self.time_since_last_damaged = 0
        self.abilities = abilities
        self.hit_table = hit_table
        self.monster_flags = monster_flags
        self.subtype = subtype
        self.team = team
        self.on_get_hit = on_get_hit
        self.stealth = stealth
        self.range = _range

        self.base_damage_bonus = damage_bonus
        self.monster_str_dice = monster_str_dice

    def print_description(self, console, x, y, width):
        print_height = 1
        # Print ally status
        if self.team == 'ally':
            libtcod.console_set_default_foreground(console, libtcod.blue)
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
            s = 'Your Accuracy: %d%%' % int(100.0 * get_chance_to_hit(self.owner, player.instance.fighter.accuracy))
            s += '%'
            libtcod.console_print(console, x, y + print_height, s)
            print_height += 1
            s = '%s Accuracy: %d%%' % (syntax.pronoun(self.owner.name, possesive=True).capitalize(), int(100.0 * get_chance_to_hit(player.instance, self.accuracy)))
            s += '%'
            libtcod.console_print(console, x, y + print_height, s)
            print_height += 1

        for effect in self.status_effects:
            libtcod.console_set_default_foreground(console, effect.color)
            libtcod.console_print(console, x, y + print_height, effect.description)
            print_height += 1
        libtcod.console_set_default_foreground(console, libtcod.white)

        return print_height

    def adjust_stamina(self, amount):
        self.stamina += amount
        if self.stamina < 0:
            self.stamina = 0
        if self.stamina > self.max_stamina:
            self.stamina = self.max_stamina

    def take_damage(self, damage, attacker=None):
        if self.owner == player.instance and consts.DEBUG_INVINCIBLE:
            damage = 0

        if damage > 0:
            self.get_hit(attacker,damage)
            self.hp -= damage
            if self.hp <= 0:
                self.drop_essence()
                self.owner.is_corpse = True
                function = self.death_function
                if function is not None:
                    function(self.owner)
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
            stamina_cost = int(stamina_cost * (1.0 + main.skill_value('combat_training')))
        return stamina_cost

    def calculate_attack_count(self):

        if self.owner is player.instance:
            speed = self.attack_speed
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
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def on_tick(self, object=None):
        # Track time since damaged (for repairing shred)
        self.time_since_last_damaged += 1
        if self.time_since_last_damaged >= 20 and self.shred > 0:
            self.shred = 0
            if self.owner is player.instance:
                ui.message('You repair your armor')

        # Manage breath/drowning
        tile = main.current_map.tiles[self.owner.x][self.owner.y]
        if tile.is_water and not tile.jumpable \
                and self.owner.movement_type & pathfinding.FLYING != pathfinding.FLYING \
                and self.owner.movement_type & pathfinding.AQUATIC != pathfinding.AQUATIC:  # deep water / deep seawater
            if not (self.can_breath_underwater or self.has_status('waterbreathing') or self.has_status('lichform') or
                    self is player.instance and main.has_skill('aquatic')):
                if self.breath > 0:
                    self.breath -= 1
                else:
                    drown_damage = int(self.max_hp / 4)
                    ui.message('%s %s, suffering %d damage!' % (syntax.name(self.owner.name).capitalize(),
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
            if effect.on_end is not None:
                effect.on_end(self.owner)
            if effect in self.status_effects:  # It can sometimes be removed in the on-tick function
                self.status_effects.remove(effect)

        # Manage ability cooldowns
        for ability in self.abilities:
            if ability is not None and ability.on_tick is not None:
                ability.on_tick()

    def apply_status_effect(self, new_effect,supress_message=False):
        # check for immunity
        if new_effect.name == 'burning' and self.owner is player.instance and main.has_skill('pyromaniac'):
            return False

        for resist in self.resistances:
            if resist == new_effect.name:
                if fov.player_can_see(self.owner.x, self.owner.y):
                    ui.message('%s %s.' % (syntax.name(self.owner.name).capitalize(), syntax.conjugate(
                                    self.owner is player.instance, ('resist', 'resists'))), libtcod.gray)
                return False
        # check for existing matching effects
        add_effect = True
        for effect in self.status_effects:
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

        if add_effect:
            self.status_effects.append(new_effect)
        if new_effect.on_apply is not None:
            new_effect.on_apply(self.owner)
        if new_effect.message is not None and self.owner is player.instance and not supress_message:
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
                return

    def has_atribute(self, name):
        if self.owner is player.instance:
            return main.has_skill(name)
        else:
            return name in self.attributes

    @property
    def accuracy(self):
        if self.base_accuracy == 0:
            return 0
        bonus = sum(equipment.accuracy_bonus for equipment in main.get_all_equipped(self.inventory))
        bonus = int(bonus *  mul(effect.accuracy_mod for effect in self.status_effects))
        if self.owner.player_stats and main.get_equipped_in_slot(self.inventory, 'right hand'):
            bonus -= 5 * max(main.get_equipped_in_slot(self.inventory, 'right hand').str_requirement - self.owner.player_stats.str, 0)

        return max(self.base_accuracy + bonus, 1)

    @property
    def damage_bonus(self):
        return self.base_damage_bonus

    @property
    def strength_dice_size(self):
        bonus = sum(equipment.strength_dice_bonus for equipment in main.get_all_equipped(self.inventory))
        if self.owner.player_stats:
            return max(self.owner.player_stats.str + bonus, 0)
        else:
            str_dice_size = int(self.monster_str_dice.split('+')[0].split('d')[1])
            return max(str_dice_size + bonus, 0)

    @property
    def armor(self):
        bonus = sum(equipment.armor_bonus for equipment in main.get_all_equipped(self.inventory))
        bonus = int(bonus * mul(effect.armor_mod for effect in self.status_effects))
        if self.owner is player.instance and main.has_skill('Iron Skin'):
            has_armor = False
            for item in main.get_all_equipped(self.inventory):
                if item.owner.item.category == 'armor':
                    has_armor = True
                    break
            if not has_armor:
                bonus += 3
        if self.has_status('shielded'):
            bonus += 2
        if main.has_skill('guardian_of_light') and (self.owner is player.instance or self.team == 'ally'):
            bonus += 2
        return max(self.base_armor + bonus - self.shred, 0)

    @property
    def attack_shred(self):
        bonus = sum(equipment.shred_bonus for equipment in main.get_all_equipped(self.inventory))
        bonus = int(bonus *  mul(effect.shred_mod for effect in self.status_effects))
        return max(self.base_shred + bonus, 0)

    @property
    def attack_guaranteed_shred(self):
        bonus = sum(equipment.guaranteed_shred_bonus for equipment in main.get_all_equipped(self.inventory))
        return max(self.base_guaranteed_shred + bonus, 0)

    @property
    def attack_pierce(self):
        bonus = sum(equipment.pierce_bonus for equipment in main.get_all_equipped(self.inventory))
        bonus = int(bonus *  mul(effect.pierce_mod for effect in self.status_effects))
        return max(self.base_pierce + bonus, 0)

    @property
    def evasion(self):
        bonus = sum(equipment.evasion_bonus for equipment in main.get_all_equipped(self.inventory))
        bonus = int(bonus * mul(effect.evasion_mod for effect in self.status_effects))
        if self.has_status('sluggish'):
            bonus -= 5
        if self.owner.player_stats:
            return max(self.base_evasion + self.owner.player_stats.agi + bonus, 0)
        else:
            return max(self.base_evasion + bonus, 0)

    @property
    def spell_power(self):
        bonus = sum(equipment.spell_power_bonus for equipment in main.get_all_equipped(self.inventory))
        bonus = int(bonus * mul(effect.spell_power_mod for effect in self.status_effects))
        if self.owner.player_stats:
            return self.base_spell_power + self.owner.player_stats.int + bonus
        else:
            return self.base_spell_power + bonus

    @property
    def spell_resist(self):
        bonus = sum(equipment.spell_resist_bonus for equipment in main.get_all_equipped(self.inventory))
        bonus = int(bonus * mul(effect.spell_resist_mod for effect in self.status_effects))
        if self.owner.player_stats:
            return self.base_spell_resist + int(self.owner.player_stats.wiz/4) + bonus
        else:
            return self.base_spell_resist + bonus

    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment in main.get_all_equipped(self.inventory))
        return self.base_max_hp + bonus

    @property
    def attack_speed(self):
        # NOTE: this is a player-only stat
        if self.owner.player_stats:
            bonus = sum(equipment.attack_speed_bonus for equipment in main.get_all_equipped(self.inventory))
            bonus = int(bonus * mul(effect.attack_speed_mod for effect in self.status_effects))
            return self.owner.player_stats.agi + bonus
        else:
            return 0

    @property
    def equip_weight(self):
        if self.owner is not player.instance:
            return 0
        return sum(equipment.weight for equipment in main.get_all_equipped(self.inventory))

    @property
    def max_equip_weight(self):
        if self.owner is not player.instance:
            return 0
        return self.owner.player_stats.str * 2

    def getResists(self):
        from_equips = reduce(lambda a,b: a | set(b.resistances), main.get_all_equipped(self.inventory), set())
        from_effects = reduce(lambda a,b: a | set(b.resistance_mod), self.status_effects, set())
        return list(set(self.resistances) | from_equips | from_equips)

    def getWeaknesses(self):
        from_effects = reduce(lambda a, b: a | set(b.weakness_mod), self.status_effects, set())
        return list(set(self.weaknesses) | from_effects)


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
    'radiant': [
        ('smite', 'smites'),
        ('disintegrate', 'disintegrates'),
    ],
    'death': [
        ('curse','curse'),
        ('defile', 'defiles'),
        ('torment', 'torments')
    ]
}

def attack_ex(fighter, target, stamina_cost, on_hit=None, verb=None, accuracy_modifier=1, damage_multiplier=1, shred_modifier=0,
              guaranteed_shred_modifier=0, pierce_modifier=0):
    # check stamina
    if main.has_skill('combat_training'):
        stamina_cost *= main.skill_value('combat_training')

    if fighter.owner.name == 'player':
        if fighter.stamina < stamina_cost:
            ui.message("You can't find the strength to swing your weapon!", libtcod.light_yellow)
            return 'failed'
        else:
            fighter.adjust_stamina(-stamina_cost)

    if roll_to_hit(target, fighter.accuracy * accuracy_modifier):
        # Target was hit

        #Determine location based effects
        location = roll_hit_location(target.fighter.hit_table)
        effect = roll_location_effect(target.fighter.inventory,location)

        damage_mod = location_damage_tables[location]['damage']

        # Attacks against stunned targets are critical
        weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')
        if weapon and ((target.fighter.has_status('stunned') and verb != 'bashes')
                       or target.fighter.has_status('off balance')):
            damage_mod *= weapon.crit_bonus

        if target.fighter.has_status('stung'):
            damage_mod *= consts.CENTIPEDE_STING_AMPLIFICATION

        if target.fighter.has_status('solace'):
            damage_mod *= 0.5

        if fighter.has_atribute('attribute_rend') and target.fighter.armor - (fighter.attack_pierce + pierce_modifier) < 1:
            damage_mod *= 1.5

        if fighter.owner is player.instance:
            #perks!
            if main.has_skill('ravager') and target.fighter.armor - (fighter.attack_pierce + pierce_modifier) < 1:
                damage_mod *= main.skill_value('ravager')

            if main.has_skill('find_the_gap') and weapon.subtype == 'dagger':
                pierce_modifier += 1

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
        if weapon is not None and weapon.damage_type is not None:
            hit_type = weapon.damage_type
        else:
            hit_type = 'bludgeoning'

        # dark immunity
        if target.fighter.has_status('lichform') and hit_type == 'dark':
            ui.message('%s %s unnaffected by dark energy!' % (
                syntax.name(target.name),
                syntax.conjugate(fighter.owner is player.instance, ('are', 'is'))),
                       libtcod.darker_crimson)
            return 'immune'

        # perks
        if fighter.owner is player.instance:
            if main.has_skill('find_the_gap') and weapon is not None and weapon.subtype == 'dagger':
                pierce_modifier += 1

        subtype = 'unarmed'
        if weapon is not None:
            subtype = weapon.subtype

        str_dice_size = fighter.strength_dice_size
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
                            fighter.attack_pierce + pierce_modifier, hit_type, damage_mod, target.fighter.getResists(),
                            target.fighter.getWeaknesses(), flat_bonus=fighter.damage_bonus)

        if damage > 0:
            percent_hit = float(damage) / float(target.fighter.max_hp)
            # Shred armor
            for i in range(fighter.attack_shred + shred_modifier):
                if libtcod.random_get_int(0, 0, 2) == 0 and target.fighter.armor > 0:
                    target.fighter.shred += 1
            target.fighter.shred += min(fighter.attack_guaranteed_shred + guaranteed_shred_modifier, target.fighter.armor)
            # Receive effect
            if effect is not None and percent_hit > 0.1:
                target.fighter.apply_status_effect(effect)

            attack_text_ex(fighter,target,verb,location,damage,hit_type,percent_hit)

            target.fighter.take_damage(damage)
            # Trigger on-hit effects
            if on_hit is not None:
                if isinstance(on_hit,(list,set,tuple)):
                    for h in on_hit:
                        h(fighter.owner, target, damage)
                else:
                    on_hit(fighter.owner, target, damage)
            if weapon is not None and weapon.on_hit is not None:
                for oh in weapon.on_hit:
                    oh(fighter.owner, target, damage)
            weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')
            if weapon:
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
                            t.fighter.take_damage(main.roll_dice('1d6'),fighter)

                if main.has_skill('gatekeeper') and target.fighter is not None:
                    if libtcod.random_get_int(0,0,10 + target.fighter.armor) < 5:
                        actions.knock_back(fighter.owner,target)

            return 'hit'
        else:
            verbs = damage_description_tables['deflected']
            verb = verbs[libtcod.random_get_int(0, 0, len(verbs) - 1)]

            #ui.message('The ' + fighter.owner.name.title() + "'s attack " + verb + ' the ' + target.name + '!', libtcod.grey)
            ui.message('%s attack %s %s' % (
                            syntax.name(fighter.owner.name, possesive=True).capitalize(),
                            verb[1],
                            syntax.name(target.name)), libtcod.grey)
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
                            syntax.name(fighter.owner.name).capitalize(),
                            syntax.conjugate(fighter.owner is player.instance, verb),
                            syntax.name(target.name),
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


def spell_attack_ex(fighter, target, accuracy, base_damage, spell_dice, spell_element, spell_pierce, spell_shred = 0, damage_mod=1):
    if target.fighter.has_status('reflect-magic'):
        target = fighter.owner

    #dark immunity
    if target.fighter.has_status('lichform') and spell_element == 'dark':
        ui.message('%s %s unnaffected by dark energy!' % (
            syntax.name(target.name),
            syntax.conjugate(fighter.owner is player.instance, ('are', 'is'))),
            libtcod.darker_crimson)
        return

    if accuracy is None or roll_to_hit(target, accuracy):
        # Target was hit
        if target.fighter.has_status('stung'):
            damage_mod *= consts.CENTIPEDE_STING_AMPLIFICATION

        if fighter.owner is player.instance and main.has_skill('searing_mind'):
            damage_mod *= 1.1

        if target.fighter.has_status('solace'):
            damage_mod *= 0.5

        spell_power = fighter.spell_power
        if fighter.owner is player.instance:
            spell_power += main.skill_value("{}_affinity".format(spell_element))

        damage = roll_damage_ex(base_damage, "{}d{}".format(spell_dice, spell_power),
                                target.fighter.spell_resist, spell_pierce, spell_element, damage_mod,
                                target.fighter.getResists(), target.fighter.getWeaknesses(), 0)

        if damage > 0:
            attack_text_ex(fighter,target,None,None,damage,spell_element,float(damage) / float(target.fighter.max_hp))
            target.fighter.take_damage(damage)
            # Shred armor

            if fighter.owner is player.instance and main.has_skill('spellshards'):
                spell_shred += 2

            for i in range(spell_shred):
                if libtcod.random_get_int(0, 0, 2) == 0 and target.fighter.armor > 0:
                    target.fighter.shred += 1
            return 'hit'
        else:
            verbs = damage_description_tables['deflected']
            verb = verbs[libtcod.random_get_int(0, 0, len(verbs) - 1)]
            ui.message('%s attack %s %s' % (
                            syntax.name(fighter.owner.name, possesive=True).capitalize(),
                            verb[0],
                            syntax.name(target.name)), libtcod.grey)
            weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')
            if weapon:
                main.check_breakage(weapon)
            return 'blocked'
    else:
        #ui.message(fighter.owner.name.title() + ' ' + verb + ' ' + target.name + ', but misses!', libtcod.grey)
        ui.message('%s %s %s, but %s!' % (
                            syntax.name(fighter.owner.name).capitalize(),
                            syntax.conjugate(fighter.owner is player.instance, ('attack', 'attacks')),
                            syntax.name(target.name),
                            syntax.conjugate(fighter.owner is player.instance, ('miss', 'misses'))), libtcod.grey)
        return 'miss'

def roll_damage_ex(damage_dice, stat_dice, defense, pierce, damage_type, damage_modifier_ex, resists,weaknesses, flat_bonus=0):
    damage_mod = damage_modifier_ex

    if damage_type in resists:
        damage_mod *= consts.RESISTANCE_FACTOR
    if type in weaknesses:
        damage_mod *= consts.WEAKNESS_FACTOR

    #calculate damage
    damage = main.roll_dice(damage_dice, normalize_size=4) + main.roll_dice(stat_dice, normalize_size=4) + flat_bonus
    damage = int(float(damage) * damage_mod)

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
        damage = math.ceil(damage * 1-reduction_factor)
        # After reduction, apply a flat reduction that is a random amount from 0 to the target's armor value
        damage = max(0, damage - libtcod.random_get_int(0, 0, effective_defense))
    else:
        damage = int(damage * (1.0 + main.skill_value('ravager')))

    return int(math.ceil(damage))

def attack_text_ex(fighter,target,verb,location,damage,damage_type,severity):
    if verb is None:
        verb = main.normalized_choice(damage_description_tables[damage_type], severity)

    target_name = syntax.name(target.name)

    if damage is not None:
        if location is not None:
            ui.message('%s %s %s in the %s for %s%d damage!' % (
                syntax.name(fighter.owner.name).capitalize(),
                syntax.conjugate(fighter.owner is player.instance, verb),
                target_name, location,
                syntax.relative_adjective(damage, damage, ['an increased ', 'a reduced ']),
                damage), libtcod.grey)
        else:
            ui.message('%s %s %s for %s%d damage!' % (
                syntax.name(fighter.owner.name).capitalize(),
                syntax.conjugate(fighter.owner is player.instance, verb),
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

def roll_to_hit(target,  accuracy):
    return libtcod.random_get_float(0, 0, 1) < get_chance_to_hit(target, accuracy)


def get_chance_to_hit(target, accuracy):
    if target.fighter.has_status('stunned'):
        return 1.0
    if target.behavior and (target.behavior.ai_state == 'resting' or target.behavior.ai_state == 'wandering'):
        return 1.0
    return 1.0 - float(target.fighter.evasion) / float(max(accuracy, target.fighter.evasion + 1))

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
    damage = roll_damage_ex('1d10', '0d0', target.fighter.spell_resist, 5, 'lightning', 1.0,
                            target.fighter.getResists(), target.fighter.getWeaknesses())

    if damage > 0:
        attack_text_ex(attacker.fighter, target, None, None, damage, 'lightning', float(damage) / float(target.fighter.max_hp))

        target.fighter.take_damage(damage)
        for adj in main.adjacent_tiles_diagonal(target.x, target.y):
            for obj in main.current_map.fighters:
                if obj.x == adj[0] and obj.y == adj[1] and obj.fighter.team != attacker.fighter.team and obj not in zapped:
                    on_hit_chain_lightning(attacker, obj, damage, zapped)
    else:
        ui.message('The shock does not damage %s' % syntax.name(target.name), libtcod.grey)

def on_hit_lifesteal(attacker, target, damage):
    attacker.fighter.heal(damage)

def on_hit_knockback(attacker, target, damage, force=6):
    if target.fighter is None:
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
            against = syntax.name(main.current_map.tiles[target.x + direction[0]][target.y + direction[1]].name)
        else:
            against = 'the ' + against.name
        if not target.move(direction[0], direction[1]):
            # Could not move
            damage = roll_damage_ex('%dd4' % steps, '0d0', target.fighter.armor, 0, 'budgeoning', 1.0,
                                    target.fighter.getResists(), target.fighter.getWeaknesses())
            ui.message('%s %s backwards and collides with %s, taking %d damage.' % (
                syntax.name(target.name).capitalize(),
                syntax.conjugate(target is player.instance, ('fly', 'flies')),
                against,
                damage), libtcod.gray)
            target.fighter.take_damage(damage)
            steps = force + 1

def on_hit_reanimate(attacker, target, damage):
    main.raise_dead(attacker,target)

def mul(sequence):
    return reduce(lambda x,y: x * y,sequence,1)
