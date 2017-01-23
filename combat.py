import game as main
import libtcodpy as libtcod
import math
import ui
import consts
import player
import spells
import fov
import effects

class Fighter:

    def __init__(self, hp=1, defense=0, power=0, xp=0, stamina=0, armor=0, evasion=0, accuracy=25, attack_damage=1,
                 damage_variance=0.15, spell_power=0, death_function=None, loot_table=None, breath=6,
                 can_breath_underwater=False, resistances=[], inventory=[], on_hit=None, base_shred=0,
                 base_guaranteed_shred=0, base_pierce=0, abilities=[], hit_table=None):
        self.xp = xp
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.death_function = death_function
        self.max_stamina = stamina
        self.stamina = stamina
        self.loot_table = loot_table
        self.base_armor = armor
        self.base_evasion = evasion
        self.base_attack_damage = attack_damage
        self.base_damage_variance = damage_variance
        self.base_spell_power = spell_power
        self.base_accuracy = accuracy
        self.max_breath = breath
        self.breath = breath
        self.can_breath_underwater = can_breath_underwater
        self.resistances = list(resistances)
        self.inventory = list(inventory)
        self.base_shred = base_shred
        self.base_guaranteed_shred = base_guaranteed_shred
        self.base_pierce = base_pierce
        self.status_effects = []
        self.on_hit = on_hit
        self.shred = 0
        self.time_since_last_damaged = 0
        self.abilities = abilities
        self.hit_table = hit_table

    def print_description(self, console, x, y, width):
        print_height = 1
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
        libtcod.console_set_default_foreground(console, libtcod.white)
        s = 'Your Accuracy: %d%%' % int(100.0 * get_chance_to_hit(self.owner, player.instance.fighter.accuracy))
        s += '%'
        libtcod.console_print(console, x, y + print_height, s)
        print_height += 1
        s = 'Its Accuracy: %d%%' % int(100.0 * get_chance_to_hit(player.instance, self.accuracy))
        s += '%'
        libtcod.console_print(console, x, y + print_height, s)
        print_height += 1

        for effect in self.status_effects:
            libtcod.console_set_default_foreground(console, effect.color)
            libtcod.console_print(console, x, y + print_height, 'It is ' + effect.name)
            print_height += 1
        libtcod.console_set_default_foreground(console, libtcod.white)

        return print_height

    def adjust_stamina(self, amount):
        self.stamina += amount
        if self.stamina < 0:
            self.stamina = 0
        if self.stamina > self.max_stamina:
            self.stamina = self.max_stamina

    def take_damage(self, damage):
        if self.has_status('stung'):
            damage *= consts.CENTIPEDE_STING_AMPLIFICATION
            damage = int(damage)
        if damage > 0:
            self.hp -= damage
            if self.hp <= 0:
                self.drop_mana()
                function = self.death_function
                if function is not None:
                    function(self.owner)
                if self.owner != player.instance:
                    player.instance.fighter.xp += self.xp
            self.time_since_last_damaged = 0

    def drop_mana(self):
        if hasattr(self.owner, 'mana') and self.owner is not player.instance:
            roll = libtcod.random_get_int(0, 1, 100)
            total = 0
            for m in self.owner.mana:
                total += m[0]
                if roll < total:
                    mana_pickup = main.GameObject(self.owner.x, self.owner.y, '*', 'mote of ' + m[1] + ' mana',
                                             spells.mana_colors[m[1]],
                                             description='A colored orb that glows with magical potential.',
                                             on_step=player.pick_up_mana, on_tick=main.expire_out_of_vision)
                    mana_pickup.mana_type = m[1]
                    main.current_cell.add_object(mana_pickup)
                    return

    def calculate_attack_stamina_cost(self):
        stamina_cost = 0
        if self.owner is player.instance:
            stamina_cost = consts.UNARMED_STAMINA_COST / (self.owner.player_stats.str / consts.UNARMED_STAMINA_COST)
            if main.get_equipped_in_slot(self.inventory, 'right hand') is not None:
                stamina_cost = int((float(main.get_equipped_in_slot(self.inventory, 'right hand').stamina_cost) /
                                    (float(self.owner.player_stats.str) / float(
                                        main.get_equipped_in_slot(self.inventory, 'right hand').str_requirement))))
        return stamina_cost

    def calculate_damage(self):
        if self.inventory and len(self.inventory) > 0:
            weapon = main.get_equipped_in_slot(self.inventory, 'right hand')
            if weapon is not None:
                total_damage = 0
                if weapon.weapon_dice is not None:
                    d = weapon.weapon_dice.split('d')
                    for i in range(1, int(d[0]) + 1):
                        total_damage += libtcod.random_get_int(0, 1, int(d[1]))
                for i in range(weapon.str_dice):
                    total_damage += libtcod.random_get_int(0, 1, self.attack_damage)
                return total_damage
        return self.attack_damage * (1.0 - self.damage_variance + libtcod.random_get_float(0, 0, 2 * self.damage_variance))

    def attack(self, target):
        return attack_ex(self, target, self.calculate_attack_stamina_cost(), self.accuracy, self.attack_damage, self.damage_variance, self.on_hit,
                       'attacks', self.attack_shred, self.attack_guaranteed_shred, self.attack_pierce)

    def heal(self, amount):
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
        if main.current_cell.map[self.owner.x][self.owner.y].tile_type == 'deep water':
            if not (self.can_breath_underwater or self.has_status('waterbreathing')):
                if self.breath > 0:
                    self.breath -= 1
                else:
                    drown_damage = int(self.max_hp / 4)
                    ui.message('The ' + self.owner.name + ' drowns, suffering ' + str(drown_damage) + ' damage!',
                            libtcod.blue)
                    self.take_damage(drown_damage)
        elif self.breath < self.max_breath:
            self.breath += 1

        # Manage status effect timers
        removed_effects = []
        for effect in self.status_effects:
            if effect.on_tick is not None:
                effect.on_tick(object=self.owner)
            if effect.time_limit is not None:
                effect.time_limit -= 1
                if effect.time_limit == 0:
                    removed_effects.append(effect)
        for effect in removed_effects:
            if effect.on_end is not None:
                effect.on_end(self.owner)
            self.status_effects.remove(effect)

        # Manage ability cooldowns
        for ability in self.abilities:
            if ability is not None and ability.on_tick is not None:
                ability.on_tick()

    def apply_status_effect(self, new_effect):
        # check for immunity
        for resist in self.resistances:
            if resist == new_effect.name:
                if fov.player_can_see(self.owner.x, self.owner.y):
                    ui.message('The ' + self.owner.name + ' resists.', libtcod.gray)
                return False
        # check for existing matching effects
        for effect in self.status_effects:
            if effect.name == new_effect.name:
                # refresh the effect
                effect.time_limit = new_effect.time_limit
                return True
        self.status_effects.append(new_effect)
        if new_effect.on_apply is not None:
            new_effect.on_apply(self.owner)
        if new_effect.message is not None and self.owner is player.instance:
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

    @property
    def accuracy(self):
        bonus = sum(equipment.accuracy_bonus for equipment in main.get_all_equipped(self.inventory))
        if self.owner.player_stats and main.get_equipped_in_slot(self.inventory, 'right hand'):
            bonus -= 5 * max(main.get_equipped_in_slot(self.inventory, 'right hand').str_requirement - self.owner.player_stats.str, 0)

        return max(self.base_accuracy + bonus, 1)

    @property
    def damage_variance(self):
        return self.base_damage_variance

    @property
    def attack_damage(self):
        bonus = sum(equipment.attack_damage_bonus for equipment in main.get_all_equipped(self.inventory))
        bonus = 0
        if self.owner.player_stats:
            return max(self.base_attack_damage + self.owner.player_stats.str + bonus, 0)
        else:
            return max(self.base_attack_damage + bonus, 0)

    @property
    def armor(self):
        bonus = sum(equipment.armor_bonus for equipment in main.get_all_equipped(self.inventory))
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
        return max(self.base_armor + bonus - self.shred, 0)

    @property
    def attack_shred(self):
        bonus = sum(equipment.shred_bonus for equipment in main.get_all_equipped(self.inventory))
        return max(self.base_shred + bonus, 0)

    @property
    def attack_guaranteed_shred(self):
        bonus = sum(equipment.guaranteed_shred_bonus for equipment in main.get_all_equipped(self.inventory))
        return max(self.base_guaranteed_shred + bonus, 0)

    @property
    def attack_pierce(self):
        bonus = sum(equipment.pierce_bonus for equipment in main.get_all_equipped(self.inventory))
        return max(self.base_pierce + bonus, 0)

    @property
    def evasion(self):
        bonus = sum(equipment.evasion_bonus for equipment in main.get_all_equipped(self.inventory))
        if self.owner.player_stats:
            return max(self.base_evasion + self.owner.player_stats.agi + bonus, 0)
        else:
            return max(self.base_evasion + bonus, 0)

    @property
    def spell_power(self):
        bonus = sum(equipment.spell_power_bonus for equipment in main.get_all_equipped(self.inventory))
        if self.owner.player_stats:
            return self.base_spell_power + self.owner.player_stats.int + bonus
        else:
            return self.base_spell_power + bonus

    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment in main.get_all_equipped(self.inventory))
        return self.base_max_hp + bonus

hit_tables = {
    'default': {
        'body' : 60,
        'head'  : 15,
        'arms'  : 15,
        'legs'  : 10,
        #'feet'  : 5,
        #'hands' : 5
    },
    'insect': {
        'body'  : 60,
        'head'  : 30,
        'legs'  : 10
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
    'legs' : {
        'damage':0.75,
        'effect':effects.immobilized,
        'effect_chance':0.7,
    },
    'stem' : {
        'damage':1.0
    }
}

def attack_ex(fighter, target, stamina_cost, accuracy, attack_damage, damage_variance, on_hit, verb, shred, guaranteed_shred, pierce):
    # check stamina
    if fighter.owner.name == 'player':
        if fighter.stamina < stamina_cost:
            ui.message("You can't find the strength to swing your weapon!", libtcod.light_yellow)
            return 'failed'
        else:
            fighter.adjust_stamina(-stamina_cost)

    if roll_to_hit(target, accuracy):
        # Target was hit

        #Determine location based effects
        location = roll_hit_location(target.fighter.hit_table)
        effect = roll_location_effect(target,location)

        damage = fighter.calculate_damage() * location_damage_tables[location]['damage']
        # Daggers deal x3 damage to stunned targets
        weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')
        if weapon and weapon.base_id and weapon.base_id == 'equipment_dagger' and target.fighter.has_status('stunned') and verb != 'bashes':
            damage *= 3

        # calculate damage reduction
        effective_armor = target.fighter.armor - pierce
        # without armor, targets receive no damage reduction!
        if effective_armor > 0:
            # Damage is reduced by 25% + 5% for every point of armor up to 5 armor (50% reduction)
            reduction_factor = consts.ARMOR_REDUCTION_BASE + consts.ARMOR_REDUCTION_STEP * min(effective_armor, consts.ARMOR_REDUCTION_DROPOFF)
            # For every point of armor after 5, damage is further reduced by 2.5% (15+ armor = 100% reduction!)
            if effective_armor > consts.ARMOR_REDUCTION_DROPOFF:
                reduction_factor += 0.5 * consts.ARMOR_REDUCTION_STEP * (effective_armor - consts.ARMOR_REDUCTION_DROPOFF)
            # Apply damage reduction
            damage = int(math.ceil(damage * reduction_factor))
            # After reduction, apply a flat reduction that is a random amount from 0 to the target's armor value
            damage = max(0, damage - libtcod.random_get_int(0, 0, effective_armor))
        else:
            damage = int(math.ceil(damage))

        if damage > 0:
            # Trigger on-hit effects
            if on_hit is not None:
                on_hit(fighter.owner, target)
            # Shred armor
            for i in range(shred):
                if libtcod.random_get_int(0, 0, 2) == 0 and target.fighter.armor > 0:
                    target.fighter.shred += 1
            target.fighter.shred += min(guaranteed_shred, target.fighter.armor)
            # Receive effect
            if effect is not None:
                target.fighter.apply_status_effect(effect)
            # Take damage
            ui.message(fighter.owner.name.capitalize() + ' ' + verb + ' ' + target.name + ' in the ' + location + ' for ' + str(damage) + ' damage!', libtcod.grey)
            target.fighter.take_damage(damage)
            weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')
            if weapon:
                main.check_breakage(weapon)
            return 'hit'
        else:
            ui.message(fighter.owner.name.capitalize() + ' ' + verb + ' ' + target.name + ', but the attack is deflected!', libtcod.grey)
            weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')
            if weapon:
                main.check_breakage(weapon)
            return 'blocked'
    else:
        ui.message(fighter.owner.name.capitalize() + ' ' + verb + ' ' + target.name + ', but misses!', libtcod.grey)
        return 'miss'


def roll_hit_location(table):
    if table is None:
        table = 'default'
    return main.random_choice(hit_tables[table])

def roll_location_effect(target, location):
    location_effect = location_damage_tables[location]
    if location_effect.get('effect') is not None and location_effect.get('effect_chance'):
        equipped = main.get_equipped_in_slot(target.fighter.inventory,location)
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
    return 1.0 - float(target.fighter.evasion) / float(max(accuracy, target.fighter.evasion + 1))