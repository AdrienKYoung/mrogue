import game as main
import libtcodpy as libtcod
import math
import ui
import consts
import player
import spells
import fov
import effects
import syntax
import pathfinding

class Fighter:

    def __init__(self, hp=1, defense=0, power=0, xp=0, stamina=0, armor=0, evasion=0, accuracy=25, attack_damage=1,
                 damage_variance=0.15, spell_power=0, death_function=None, breath=6,
                 can_breath_underwater=False, resistances=[], weaknesses=[], inventory=[], on_hit=None, base_shred=0,
                 base_guaranteed_shred=0, base_pierce=0, abilities=[], hit_table=None, monster_flags =0, subtype=None,
                 damage_bonus=0, m_str_dice=0, m_str_size=0, monster_str_dice=None, spell_resist=0):
        self.xp = xp
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.death_function = death_function
        self.max_stamina = stamina
        self.stamina = stamina
        self.base_armor = armor
        self.base_evasion = evasion
        self.base_attack_damage = attack_damage
        self.base_damage_variance = damage_variance
        self.base_spell_power = spell_power
        self.base_spell_resist = spell_resist
        self.base_accuracy = accuracy
        self.max_breath = breath
        self.breath = breath
        self.can_breath_underwater = can_breath_underwater
        self.resistances = list(resistances)
        self.weaknesses = list(weaknesses)
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
        self.monster_flags = monster_flags
        self.subtype = subtype

        self.base_damage_bonus = damage_bonus
        self.m_str_dice = m_str_dice
        self.m_str_size = m_str_size
        self.monster_str_dice = monster_str_dice

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
            libtcod.console_print(console, x, y + print_height, '%s %s %s' % (
                syntax.pronoun(self.owner.name).capitalize(),
                syntax.conjugate(self.owner is player.instance, ('are', 'is')),
                effect.name))
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
        if self.owner == player.instance and consts.DEBUG_INVINCIBLE:
            damage = 0

        if damage > 0:
            self.hp -= damage
            if self.hp <= 0:
                self.drop_essence()
                function = self.death_function
                if function is not None:
                    function(self.owner)
                if self.owner != player.instance:
                    player.instance.fighter.xp += self.xp
            self.time_since_last_damaged = 0
        return damage

    def drop_essence(self):
        if hasattr(self.owner, 'essence') and self.owner is not player.instance:
            roll = libtcod.random_get_int(0, 1, 100)
            total = 0
            for m in self.owner.essence:
                total += m[0]
                if roll < total:
                    essence_pickup = main.GameObject(self.owner.x, self.owner.y, '*', 'mote of ' + m[1] + ' essence',
                                             spells.essence_colors[m[1]],
                                             description='A colored orb that glows with elemental potential.',
                                             on_step=player.pick_up_essence, on_tick=main.expire_out_of_vision)
                    essence_pickup.essence_type = m[1]
                    main.current_map.add_object(essence_pickup)
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
                return roll_damage(weapon,self)
        return self.attack_damage * (1.0 - self.damage_variance + libtcod.random_get_float(0, 0, 2 * self.damage_variance))

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
            result = attack_ex(self, target, self.calculate_attack_stamina_cost(), self.accuracy, self.attack_damage, None, self.on_hit,
                           None, self.attack_shred, self.attack_guaranteed_shred, self.attack_pierce)
            if result == 'failed':
                return result
            elif target.fighter is None:
                return result
        return result

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
        tile = main.current_map.tiles[self.owner.x][self.owner.y]
        if tile.is_water and not tile.jumpable \
                and self.owner.movement_type & pathfinding.FLYING != pathfinding.FLYING \
                and self.owner.movement_type & pathfinding.AQUATIC != pathfinding.AQUATIC:  # deep water / deep seawater
            if not (self.can_breath_underwater or self.has_status('waterbreathing')):
                if self.breath > 0:
                    self.breath -= 1
                else:
                    drown_damage = int(self.max_hp / 4)
                    ui.message('%s %s, suffering %d damage!' % (syntax.name(self.owner.name).capitalize(),
                                             syntax.conjugate(self.owner is player.instance,
                                             ('drown', 'drowns')), drown_damage), libtcod.blue)
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
            if effect in self.status_effects:  # It can sometimes be removed in the on-tick function
                self.status_effects.remove(effect)

        # Manage ability cooldowns
        for ability in self.abilities:
            if ability is not None and ability.on_tick is not None:
                ability.on_tick()

    def apply_status_effect(self, new_effect,supress_message=False):
        # check for immunity
        for resist in self.resistances:
            if resist == new_effect.name:
                if fov.player_can_see(self.owner.x, self.owner.y):
                    ui.message('%s %s.' % (syntax.name(self.owner.name).capitalize(), syntax.conjugate(
                                    self.owner is player.instance, ('resist', 'resists'))), libtcod.gray)
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
    def damage_variance(self):
        return self.base_damage_variance

    @property
    def damage_bonus(self):
        return self.base_damage_bonus

    @property
    def attack_damage(self):
        bonus = sum(equipment.attack_damage_bonus for equipment in main.get_all_equipped(self.inventory))
        bonus = int(bonus * mul(effect.attack_power_mod for effect in self.status_effects))
        bonus = 0
        if self.owner.player_stats:
            return max(self.owner.player_stats.str + bonus, 0)
        else:
            str_dice_size = int(self.monster_str_dice.split('+')[0].split('d')[1])
            return max(str_dice_size + bonus, 0)

    @property
    def armor(self):
        bonus = sum(equipment.armor_bonus for equipment in main.get_all_equipped(self.inventory))
        bonus = int(bonus *  mul(effect.armor_mod for effect in self.status_effects))
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
        bonus = int(bonus *  mul(effect.evasion_mod for effect in self.status_effects))
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
        if self.owner.player_stats:
            return self.base_spell_resist + self.owner.player_stats.wiz + bonus
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
        'legs'  : 15,
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
    'water': [
        ('splash','splashes'),
        ('flood','floods'),
        ('blast','blasts'),
        ('drown','drowns')
    ],
    'ice': [
        ('freeze','freezes'),
        ('shatter','shatters')
    ],
    'earth': [
        ('smash','smashes'),
        ('crush','crushes')
    ],
    'air': [
        ('slam','slams'),
        ('shred','shreds'),
        ('blast','blasts')
    ]
}

def roll_damage(weapon, fighter):
    total_damage = 0
    if weapon.weapon_dice is not None:
        d = weapon.weapon_dice.split('d')
        dice_size = max(int(d[1]) + (2 * weapon.attack_damage_bonus), 1)
        for i in range(1, int(d[0]) + 1):
            total_damage += libtcod.random_get_int(0, 1, dice_size)
    for i in range(weapon.str_dice):
        total_damage += libtcod.random_get_int(0, 1, fighter.attack_damage)
    return total_damage

def attack_ex(fighter, target, stamina_cost, accuracy, attack_damage, damage_multiplier, on_hit, verb, shred, guaranteed_shred, pierce):
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
        effect = roll_location_effect(target.fighter.inventory,location)

        damage_mod = location_damage_tables[location]['damage']

        # Daggers deal x3 damage to stunned targets
        weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')
        if weapon and target.fighter.has_status('stunned') and verb != 'bashes':
            damage_mod *= weapon.crit_bonus

        if target.fighter.has_status('stung'):
            damage_mod *= consts.CENTIPEDE_STING_AMPLIFICATION

        if damage_multiplier is not None:
            damage_mod *= damage_multiplier

        # weapon-specific damage verbs
        hit_type = None
        if weapon is not None and weapon.damage_type is not None:
            hit_type = weapon.damage_type
        else:
            hit_type = 'bludgeoning'

        unarmed_str_dice = '1d{}'.format(fighter.attack_damage)
        if fighter.owner is not player.instance and weapon is None:
            unarmed_str_dice = fighter.monster_str_dice

        if weapon is not None:
            damage = roll_damage_ex(weapon.weapon_dice,
                                "{}d{}".format(weapon.str_dice,fighter.attack_damage), target.fighter.armor,
                                fighter.attack_pierce, hit_type, damage_mod, target.fighter.getResists(),
                                target.fighter.getResists(), flat_bonus=fighter.damage_bonus)
        else:
            damage = roll_damage_ex('0d0', unarmed_str_dice, target.fighter.armor,
                                    fighter.attack_pierce, hit_type, damage_mod, target.fighter.getResists(),
                                    target.fighter.getResists(), flat_bonus=fighter.damage_bonus)

        if damage > 0:
            percent_hit = float(damage) / float(target.fighter.max_hp)
            # Trigger on-hit effects
            if on_hit is not None:
                on_hit(fighter.owner, target)
            if weapon is not None and weapon.on_hit is not None:
                for oh in weapon.on_hit:
                    oh(fighter.owner, target)
            # Shred armor
            for i in range(shred):
                if libtcod.random_get_int(0, 0, 2) == 0 and target.fighter.armor > 0:
                    target.fighter.shred += 1
            target.fighter.shred += min(guaranteed_shred, target.fighter.armor)
            # Receive effect
            if effect is not None and percent_hit > 0.1:
                target.fighter.apply_status_effect(effect)

            attack_text_ex(fighter,target,verb,location,damage,hit_type,percent_hit)

            target.fighter.take_damage(damage)
            weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')
            if weapon:
                main.check_breakage(weapon)
            return 'hit'
        else:
            verbs = damage_description_tables['deflected']
            verb = verbs[libtcod.random_get_int(0, 0, len(verbs) - 1)]

            #ui.message('The ' + fighter.owner.name.title() + "'s attack " + verb + ' the ' + target.name + '!', libtcod.grey)
            ui.message('%s attack %s %s' % (
                            syntax.name(fighter.owner.name, possesive=True).capitalize(),
                            verb[0],
                            syntax.name(target.name)), libtcod.grey)
            weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')
            if weapon:
                main.check_breakage(weapon)
            return 'blocked'
    else:
        if verb is None:
            verb = ('attack', 'attacks')
        #ui.message(fighter.owner.name.title() + ' ' + verb + ' ' + target.name + ', but misses!', libtcod.grey)
        ui.message('%s %s %s, but %s!' % (
                            syntax.name(fighter.owner.name).capitalize(),
                            syntax.conjugate(fighter.owner is player.instance, verb),
                            syntax.name(target.name),
                            syntax.conjugate(fighter.owner is player.instance, ('miss', 'misses'))), libtcod.grey)
        return 'miss'

def spell_attack_ex(fighter, target, accuracy, spell_name, base_damage, spell_dice, spell_element, spell_pierce):

    if accuracy is None or roll_to_hit(target, accuracy):
        # Target was hit

        damage_mod = 1

        if target.fighter.has_status('stung'):
            damage_mod *= consts.CENTIPEDE_STING_AMPLIFICATION

        damage = roll_damage_ex(base_damage, "{}d{}".format(spell_dice,fighter.spell_power), target.fighter.spell_resist,
                                spell_pierce, spell_element, damage_mod, target.fighter.getResists(),
                                target.fighter.getResists(), 0)

        if damage > 0:
            attack_text_ex(fighter,target,None,None,damage,spell_element,float(damage) / float(target.fighter.max_hp))

            target.fighter.take_damage(damage)
            weapon = main.get_equipped_in_slot(fighter.inventory, 'right hand')
            if weapon:
                main.check_breakage(weapon)
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
    if damage_dice == '+0':
        damage_dice = '0d0'
    damage = main.roll_dice(damage_dice) + main.roll_dice(stat_dice) + flat_bonus
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
        damage = math.ceil(damage * reduction_factor)
        # After reduction, apply a flat reduction that is a random amount from 0 to the target's armor value
        damage = max(0, damage - libtcod.random_get_int(0, 0, effective_defense))

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

def on_hit_stun(attacker,target):
    scaling_factor = 1
    if(attacker is player.instance):
        scaling_factor = attacker.player_stats.str / 10
    if libtcod.random_get_float(0,0.0,1.0) * scaling_factor > 0.85:
        if attacker == player.instance:
            ui.message("Your " + main.get_equipped_in_slot(player.instance.fighter.inventory,'right hand').owner.name.title() + " rings out!",libtcod.blue)
        target.fighter.apply_status_effect(effects.stunned())

def mul(sequence):
    return reduce(lambda x,y: x * y,sequence,1)
