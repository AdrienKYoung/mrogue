import libtcodpy as libtcod
import math
import shelve
import consts
import terrain

#############################################
# Classes
#############################################

class Equipment:
    def __init__(self, slot, category, max_hp_bonus=0, attack_damage_bonus=0,
                 armor_bonus=0, evasion_bonus=0, spell_power_bonus=0, stamina_cost=0, str_requirement=0, shred_bonus=0,
                 guaranteed_shred_bonus=0, pierce=0, accuracy=0, ctrl_attack=None, ctrl_attack_desc=None,
                 break_chance=0.0, weapon_dice=None, str_dice=None):
        self.max_hp_bonus = max_hp_bonus
        self.slot = slot
        self.category = category
        self.is_equipped = False
        self.attack_damage_bonus = attack_damage_bonus
        self.armor_bonus = armor_bonus
        self.evasion_bonus = evasion_bonus
        self.spell_power_bonus = spell_power_bonus
        self.stamina_cost = stamina_cost
        self.str_requirement = str_requirement
        self.shred_bonus=shred_bonus
        self.guaranteed_shred_bonus=guaranteed_shred_bonus
        self.pierce_bonus = pierce
        self.accuracy_bonus = accuracy
        self.ctrl_attack = ctrl_attack
        self.break_chance = break_chance
        self.ctrl_attack_desc = ctrl_attack_desc
        self.weapon_dice = weapon_dice
        self.str_dice = str_dice

    def toggle(self):
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()
            
    def equip(self):
        old_equipment = get_equipped_in_slot(player.fighter.inventory, self.slot)
        if old_equipment is not None:
            old_equipment.dequip()
        self.is_equipped = True
        ui.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.orange)
        
    def dequip(self):
        self.is_equipped = False
        ui.message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.orange)

    def print_description(self, console, x, y, width):
        print_height = 1
        if self.str_requirement != 0:
            if player.player_stats.str < self.str_requirement:
                libtcod.console_set_default_foreground(console, libtcod.red)
            else:
                libtcod.console_set_default_foreground(console, libtcod.green)
            libtcod.console_print(console, x, y + print_height, 'Strength Required: ' + str(self.str_requirement))
            print_height += 1
            libtcod.console_set_default_foreground(console, libtcod.white)
        libtcod.console_print(console, x, y + print_height, 'Slot: ' + self.slot)
        print_height += 1
        if self.armor_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Armor: ' + str(self.armor_bonus))
            print_height += 1
        if self.attack_damage_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Damage: ' + str(self.attack_damage_bonus))
            print_height += 1
        if self.accuracy_bonus != 0:
            acc_str = 'Accuracy: '
            if self.accuracy_bonus > 0:
                acc_str += '+'
            libtcod.console_print(console, x, y + print_height, acc_str + str(self.accuracy_bonus))
            print_height += 1
        if self.evasion_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Evade: ' + str(self.evasion_bonus))
            print_height += 1
        if self.guaranteed_shred_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Auto-shred: ' + str(self.guaranteed_shred_bonus))
            print_height += 1
        if self.max_hp_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Bonus HP: ' + str(self.max_hp_bonus))
            print_height += 1
        if self.pierce_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Pierce: ' + str(self.pierce_bonus))
            print_height += 1
        if self.shred_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Shred: ' + str(self.shred_bonus))
            print_height += 1
        if self.spell_power_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Spell Power: ' + str(self.spell_power_bonus))
            print_height += 1
        if self.break_chance > 0:
            libtcod.console_print(console, x, y + print_height, 'It has a ' + str(self.break_chance) + '%%' + ' chance to break when used.')
            print_height += 1
        if self.ctrl_attack_desc:
            libtcod.console_set_default_foreground(console, libtcod.azure)
            text = 'Ctrl+attack: ' + self.ctrl_attack_desc
            h = libtcod.console_get_height_rect(console, x, y + print_height, width, consts.SCREEN_HEIGHT, text)
            libtcod.console_print_rect(console, x, y + print_height + 1, width, h, text)
            print_height += h + 1
            libtcod.console_set_default_foreground(console, libtcod.white)


        return print_height

class Item:
    def __init__(self, category, use_function=None, learn_spell=None, type='item', ability=None):
        self.category = category
        self.use_function = use_function
        self.type = type
        self.learn_spell = learn_spell
        self.ability = ability
        
    def pick_up(self):
        if self.type == 'item':
            if len(player.fighter.inventory) >= 26:
                ui.message('Your inventory is too full to pick up ' + self.owner.name)
            else:
                player.fighter.inventory.append(self.owner)
                self.owner.destroy()
                ui.message('You picked up a ' + self.owner.name + '!', libtcod.light_grey)
                equipment = self.owner.equipment
                if equipment and get_equipped_in_slot(player.fighter.inventory,equipment.slot) is None:
                    equipment.equip()
        elif self.type == 'spell':
            if len(memory) >= player.player_stats.max_memory:
                ui.message('You cannot hold any more spells in your memory!', libtcod.purple)
            else:
                memory.append(self.owner)
                self.owner.destroy()
                ui.message(str(self.owner.name) + ' has been added to your memory.', libtcod.purple)
            
    def use(self):
        if self.owner.equipment:
            self.owner.equipment.toggle()
            return
        if self.use_function is not None:
            if self.use_function() != 'cancelled':
                if self.type == 'item':
                    player.fighter.inventory.remove(self.owner)
                elif self.type == 'spell':
                    memory.remove(self.owner)
            else:
                return 'cancelled'
        elif self.learn_spell is not None:
            spell = spells.spell_library[self.learn_spell]
            if spell in player.known_spells:
                ui.message('You already know this spell.', libtcod.light_blue)
                return 'cancelled'
            else:
                player.known_spells.append(spell)
                ui.message('You have mastered ' + spell.name + '!', libtcod.light_blue)
                player.fighter.inventory.remove(self.owner)
        else:
            ui.message('The ' + self.owner.name + ' cannot be used.')

                
    def drop(self):
        if self.owner.equipment:
            self.owner.equipment.dequip();
        objects.append(self.owner)
        player.fighter.inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        ui.message('You dropped a ' + self.owner.name + '.', libtcod.white)

    def get_options_list(self):
        options = []
        if self.use_function is not None or self.learn_spell is not None:
            options.append('Use')
        if self.owner.equipment:
            if self.owner.equipment.is_equipped:
                options.append('Unequip')
            else:
                options.append('Equip')
        options.append('Drop')
        return options

    def print_description(self, console, x, y, width):
        print_height = 0

        if self.owner.equipment:
            print_height += self.owner.equipment.print_description(console, x, y + print_height, width)

        return print_height


class PlayerStats:

    def __init__(self, int=10, wiz=10, str=10, agi=10):
        self.base_int = int
        self.base_wiz = wiz
        self.base_str = str
        self.base_agi = agi

    @property
    def int(self):
        return self.base_int

    @property
    def wiz(self):
        return self.base_wiz

    @property
    def str(self):
        return self.base_str

    @property
    def agi(self):
        return self.base_agi

    @property
    def max_memory(self):
        return 3 + int(math.floor(self.wiz / 4))

    @property
    def max_mana(self):
        return 1 + int(math.floor(self.wiz / 4))


class Fighter:

    def __init__(self, hp=1, defense=0, power=0, xp=0, stamina=0, armor=0, evasion=0, accuracy=25, attack_damage=1,
                 damage_variance=0.15, spell_power=0, death_function=None, loot_table=None, breath=6,
                 can_breath_underwater=False, resistances=[], inventory=[], on_hit=None, base_shred=0,
                 base_guaranteed_shred=0, base_pierce=0, abilities=[]):
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


    def print_description(self, console, x, y, width):
        print_height = 1
        #print_height = libtcod.console_get_height_rect(console, x, y, width, consts.SCREEN_HEIGHT, 'This is a fighter description')
        #libtcod.console_print_rect(console, x, y, width, consts.SCREEN_HEIGHT, 'This is a fighter description')
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
        s = 'Your Accuracy: %d%%' % int(100.0 * get_chance_to_hit(self.owner, player.fighter.accuracy))
        s += '%'
        libtcod.console_print(console, x, y + print_height, s)
        print_height += 1
        s = 'Its Accuracy: %d%%' % int(100.0 * get_chance_to_hit(player, self.accuracy))
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
                if self.owner != player:
                    player.fighter.xp += self.xp
            self.time_since_last_damaged = 0

    def drop_mana(self):
        if hasattr(self.owner, 'mana') and self.owner is not player:
            roll = libtcod.random_get_int(0, 1, 100)
            total = 0
            for m in self.owner.mana:
                total += m[0]
                if roll < total:
                    mana_pickup = GameObject(self.owner.x, self.owner.y, '*', 'mote of ' + m[1] + ' mana',
                                             spells.mana_colors[m[1]],
                                             description='A colored orb that glows with magical potential.',
                                             on_step=pick_up_mana, on_tick=expire_out_of_vision)
                    mana_pickup.mana_type = m[1]
                    objects.append(mana_pickup)
                    return

    def calculate_attack_stamina_cost(self):
        stamina_cost = 0
        if self.owner is player:
            stamina_cost = consts.UNARMED_STAMINA_COST / (self.owner.player_stats.str / consts.UNARMED_STAMINA_COST)
            if get_equipped_in_slot(self.inventory, 'right hand') is not None:
                stamina_cost = int((float(get_equipped_in_slot(self.inventory, 'right hand').stamina_cost) /
                                    (float(self.owner.player_stats.str) / float(
                                        get_equipped_in_slot(self.inventory, 'right hand').str_requirement))))
        return stamina_cost

    def calculate_damage(self):
        if self.inventory and len(self.inventory) > 0:
            weapon = get_equipped_in_slot(self.inventory, 'right hand')
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
        return self.attack_ex(target, self.calculate_attack_stamina_cost(), self.accuracy, self.attack_damage, self.damage_variance, self.on_hit,
                       'attacks', self.attack_shred, self.attack_guaranteed_shred, self.attack_pierce)

    def attack_ex(self, target, stamina_cost, accuracy, attack_damage, damage_variance, on_hit, verb, shred, guaranteed_shred, pierce):
        # check stamina
        if self.owner.name == 'player':
            if self.stamina < stamina_cost:
                ui.message("You can't find the strength to swing your weapon!", libtcod.light_yellow)
                return 'failed'
            else:
                self.adjust_stamina(-stamina_cost)

        if roll_to_hit(target, accuracy):
            # Target was hit
            damage = self.calculate_damage()
            # Daggers deal x3 damage to stunned targets
            weapon = get_equipped_in_slot(self.inventory, 'right hand')
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

            #damage *= (consts.ARMOR_FACTOR / (consts.ARMOR_FACTOR + target.fighter.armor))
            #damage = math.ceil(damage)
            #damage = int(damage)
            if damage > 0:
                # Trigger on-hit effects
                if on_hit is not None:
                    on_hit(self.owner, target)
                # Shred armor
                for i in range(shred):
                    if libtcod.random_get_int(0, 0, 2) == 0 and target.fighter.armor > 0:
                        target.fighter.shred += 1
                target.fighter.shred += min(guaranteed_shred, target.fighter.armor)
                # Take damage
                ui.message(self.owner.name.capitalize() + ' ' + verb + ' ' + target.name + ' for ' + str(damage) + ' damage!', libtcod.grey)
                target.fighter.take_damage(damage)
                weapon = get_equipped_in_slot(self.inventory, 'right hand')
                if weapon:
                    check_breakage(weapon)
                return 'hit'
            else:
                ui.message(self.owner.name.capitalize() + ' ' + verb + ' ' + target.name + ', but the attack is deflected!', libtcod.grey)
                weapon = get_equipped_in_slot(self.inventory, 'right hand')
                if weapon:
                    check_breakage(weapon)
                return 'blocked'
        else:
            ui.message(self.owner.name.capitalize() + ' ' + verb + ' ' + target.name + ', but misses!', libtcod.grey)
            return 'miss'

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def on_tick(self, object=None):
        # Track time since damaged (for repairing shred)
        self.time_since_last_damaged += 1
        if self.time_since_last_damaged >= 20 and self.shred > 0:
            self.shred = 0
            if self.owner is player:
                ui.message('You repair your armor')

        # Manage breath/drowning
        if dungeon_map[self.owner.x][self.owner.y].tile_type == 'deep water':
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
        if new_effect.message is not None and self.owner is player:
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
        bonus = sum(equipment.accuracy_bonus for equipment in get_all_equipped(self.inventory))
        if self.owner.player_stats and get_equipped_in_slot(self.inventory, 'right hand'):
            bonus -= 5 * max(get_equipped_in_slot(self.inventory, 'right hand').str_requirement - self.owner.player_stats.str, 0)

        return max(self.base_accuracy + bonus, 1)

    @property
    def damage_variance(self):
        return self.base_damage_variance

    @property
    def attack_damage(self):
        bonus = sum(equipment.attack_damage_bonus for equipment in get_all_equipped(self.inventory))
        bonus = 0
        if self.owner.player_stats:
            return max(self.base_attack_damage + self.owner.player_stats.str + bonus, 0)
        else:
            return max(self.base_attack_damage + bonus, 0)

    @property
    def armor(self):
        bonus = sum(equipment.armor_bonus for equipment in get_all_equipped(self.inventory))
        if self.owner is player and has_skill('Iron Skin'):
            has_armor = False
            for item in get_all_equipped(self.inventory):
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
        bonus = sum(equipment.shred_bonus for equipment in get_all_equipped(self.inventory))
        return max(self.base_shred + bonus, 0)

    @property
    def attack_guaranteed_shred(self):
        bonus = sum(equipment.guaranteed_shred_bonus for equipment in get_all_equipped(self.inventory))
        return max(self.base_guaranteed_shred + bonus, 0)

    @property
    def attack_pierce(self):
        bonus = sum(equipment.pierce_bonus for equipment in get_all_equipped(self.inventory))
        return max(self.base_pierce + bonus, 0)

    @property
    def evasion(self):
        bonus = sum(equipment.evasion_bonus for equipment in get_all_equipped(self.inventory))
        if self.owner.player_stats:
            return max(self.base_evasion + self.owner.player_stats.agi + bonus, 0)
        else:
            return max(self.base_evasion + bonus, 0)

    @property
    def spell_power(self):
        bonus = sum(equipment.spell_power_bonus for equipment in get_all_equipped(self.inventory))
        if self.owner.player_stats:
            return self.base_spell_power + self.owner.player_stats.int + bonus
        else:
            return self.base_spell_power + bonus

    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.inventory))
        return self.base_max_hp + bonus

class GameObject:

    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None, equipment=None,
                 player_stats=None, always_visible=False, interact=None, description=None, on_create=None,
                 update_speed=1.0, misc=None, blocks_sight=False, on_step=None, burns=False, on_tick=None, elevation=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.always_visible = always_visible
        self.interact = interact
        self.description = description
        self.on_create = on_create
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        if self.ai:
            self.ai = AI_General(update_speed, ai)
            self.ai.owner = self
            self.ai.behavior.owner = self
        self.item = item
        if self.item:
            self.item.owner = self
        self.equipment = equipment
        if self.equipment:
            self.equipment.owner = self
            self.item = Item(self.equipment.category)
            self.item.owner = self
        self.player_stats = player_stats
        if self.player_stats:
            self.player_stats.owner = self
        if on_create is not None:
            on_create(self)
        self.misc = misc
        if self.misc:
            self.misc.owner = self
        self.blocks_sight = blocks_sight
        self.on_step = on_step
        self.burns = burns
        self.on_tick_specified = on_tick
        if elevation is None:
            if dungeon_map is not None:
                self.elevation = dungeon_map[self.x][self.y].elevation
            else:
                self.elevation = 0
        else:
            self.elevation = elevation

    def print_description(self, console, x, y, width):
        height = libtcod.console_get_height_rect(console, x, y, width, consts.SCREEN_HEIGHT, self.description)
        draw_height = y
        #libtcod.console_print(console, x, draw_height, self.name.capitalize())
        #draw_height += 2
        libtcod.console_print_rect(console, x, draw_height, width, height, self.description)
        draw_height += height
        if self.item:
            h = self.item.print_description(console, x, draw_height, width)
            draw_height += h
            height += h
        if self.fighter:
            h = self.fighter.print_description(console, x, draw_height, width)
            draw_height += h
            height += h
        return height

    def on_create(self):
        if self.blocks_sight:
            fov.set_fov_properties(self.x, self.y, self.blocks_sight, self.elevation)

    def set_position(self, x, y):

        # If the object is not moving, skip this function.
        if self.x == x and self.y == y:
            return

        # Update the tile we left for the renderer
        global changed_tiles
        changed_tiles.append((self.x, self.y))

        # Update fov maps (if this object affects fov)
        if self.blocks_sight:
            fov.set_fov_properties(self.x, self.y, dungeon_map[self.x][self.y].blocks_sight, self.elevation)
            fov.set_fov_properties(x, y, True, self.elevation)

        # Update the pathfinding map - mark our previous space as passable and our new space as impassable
        if pathfinding.map and self.blocks:
            pathfinding.map.mark_impassable((x, y))
            pathfinding.map.mark_passable((self.x, self.y))

        # Update the object's position/elevation
        self.x = x
        self.y = y
        old_elev = self.elevation
        self.elevation = dungeon_map[x][y].elevation

        # Check for objects with 'stepped_on' functions on our new space (xp, mana, traps, etc)
        stepped_on = get_objects(self.x, self.y, lambda o: o.on_step)
        if len(stepped_on) > 0:
            for obj in stepped_on:
                obj.on_step(obj, self)

        # If the player moved, recalculate field of view, checking for elevation changes
        if self is player:
            if old_elev != self.elevation:
                fov.set_view_elevation(self.elevation)
            fov.set_fov_recompute()

    def move(self, dx, dy):

        blocked = is_blocked(self.x + dx, self.y + dy, self.elevation)
        if blocked and dungeon_map[self.x][self.y].tile_type == 'ramp':
            blocked = is_blocked(self.x + dx, self.y + dy, self.elevation - 1)

        if not blocked:
            if self.fighter is not None:
                if self.fighter.has_status('immobilized'):
                    return True
                web = object_at_tile(self.x, self.y, 'spiderweb')
                if web is not None and not self.name == 'tunnel spider':
                    ui.message('The ' + self.name + ' struggles against the web.')
                    web.destroy()
                    return True
                cost = dungeon_map[self.x][self.y].stamina_cost
                if cost > 0 and self is player: # only the player cares about stamina costs (at least for now. I kind of like it this way) -T
                    if self.fighter.stamina >= cost:
                        self.fighter.adjust_stamina(-cost)
                    else:
                        ui.message("You don't have the stamina leave this space!", libtcod.light_yellow)
                        return False
                else:
                    self.fighter.adjust_stamina(consts.STAMINA_REGEN_MOVE)     # gain stamina for moving across normal terrain

            self.set_position(self.x + dx, self.y + dy)
            return True

    def draw(self, console):
        if fov.player_can_see(self.x, self.y):
            if ui.selected_monster is self:
                libtcod.console_put_char_ex(console, self.x, self.y, self.char, libtcod.black, self.color)
            else:
                libtcod.console_set_default_foreground(console, self.color)
                libtcod.console_put_char(console, self.x, self.y, self.char, libtcod.BKGND_NONE)
        elif self.always_visible and dungeon_map[self.x][self.y].explored:
            shaded_color = libtcod.Color(self.color[0], self.color[1], self.color[2])
            libtcod.color_scale_HSV(shaded_color, 0.1, 0.4)
            libtcod.console_set_default_foreground(console, shaded_color)
            libtcod.console_put_char(console, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def move_towards(self, target_x, target_y):
        if self.x == target_x and self.y == target_y:
            return

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def move_astar(self, target_x, target_y):
        if self.x == target_x and self.y == target_y:
            return 'already here'

        if not pathfinding.map:
            self.move_astar_old(target_x, target_y)
            return 'no map'
        else:
            if not pathfinding.map.is_accessible((target_x, target_y)):
                closest_adjacent = None
                closest = 10000
                for adj in adjacent_tiles_diagonal(target_x, target_y):
                    if is_blocked(adj[0], adj[1], dungeon_map[target_x][target_y].elevation):
                        continue
                    dist = self.distance(adj[0], adj[1])
                    if dist < closest:
                        closest = dist
                        closest_adjacent = adj
                if closest_adjacent is None:
                    self.move_towards(target_x, target_y)
                    return 'no adjacent'
                else:
                    target_x = closest_adjacent[0]
                    target_y = closest_adjacent[1]

            path = pathfinding.map.a_star_search((self.x, self.y), (target_x, target_y))

            if consts.DEBUG_DRAW_PATHS:
                pathfinding.draw_path(path)

            if path != 'failure' and 0 < len(path) < 25:
                # find the next coordinate in the computed full path
                x, y = path[1]
                if x or y:
                    if dungeon_map[x][y].blocks:
                        pathfinding.map.mark_impassable((x, y))  # bandaid fix - hopefully paths will self-correct now
                    else:
                        self.move_towards(x, y)
            else:
                # Use the old(er) function instead
                self.move_towards(target_x, target_y)
                return 'failure'

    def move_astar_old(self, target_x, target_y):

        if self.x == target_x and self.y == target_y:
            return

        fov = libtcod.map_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)
        
        # Scan the map and set all walls to unwalkable
        for y1 in range(consts.MAP_HEIGHT):
            for x1 in range(consts.MAP_WIDTH):
                terrain = dungeon_map[x1][y1].blocks
                elev = self.elevation != dungeon_map[x1][y1].elevation and dungeon_map[x1][y1].tile_type != 'ramp'
                blocks = terrain or elev
                libtcod.map_set_properties(fov, x1, y1, not dungeon_map[x1][y1].blocks_sight, not blocks)
        
        # Scan all objects to see if there are objects that must be navigated around
        for obj in objects:
            if obj.blocks and obj != self and not (obj.x == target_x and obj.y == target_y):
                libtcod.map_set_properties(fov, obj.x, obj.y, True, False)
                
        # 1.41 is the diagonal cost of movement. Set to 1 to equal axial movement, or 0 to disallow diagonals
        my_path = libtcod.path_new_using_map(fov, 1.41)
        libtcod.path_compute(my_path, self.x, self.y, target_x, target_y)
        
        # check if the path exists, and in this case, also the path is shorter than 25 tiles
        # if the path is too long (travels around rooms and hallways) just use basic AI instead
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            # find the next coordinate in the computed full path
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                self.move_towards(x, y)
        else:
            # Use the old function instead
            self.move_towards(target_x, target_y)
            
        # delete path to free memory
        libtcod.path_delete(my_path)
        
    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)
        
    def send_to_back(self):
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def on_tick(self, object=None):
        if self.on_tick_specified:
            self.on_tick_specified(object)
        if self.fighter:
            self.fighter.on_tick()
        if self.misc and hasattr(self.misc, 'on_tick'):
            self.misc.on_tick(object)

    def destroy(self):
        global changed_tiles
        if self.blocks_sight:
            fov.set_fov_properties(self.x, self.y, dungeon_map[self.x][self.y].blocks_sight, self.elevation)
        if self.blocks and pathfinding.map:
            pathfinding.map.mark_passable((self.x, self.y))
        changed_tiles.append((self.x, self.y))
        objects.remove(self)


class Tile:
    
    def __init__(self, tile_type='stone floor'):
        self.explored = False
        self.tile_type = tile_type
        self.no_overwrite = False
        self.elevation = 0

    @property
    def name(self):
        return terrain.data[self.tile_type].name

    @property
    def blocks(self):
        return terrain.data[self.tile_type].blocks

    @property
    def blocks_sight(self):
        return terrain.data[self.tile_type].blocks_sight

    @property
    def tile_char(self):
        return terrain.data[self.tile_type].char

    @property
    def color_fg(self):
        return terrain.data[self.tile_type].foreground_color

    @property
    def color_bg(self):
        return terrain.data[self.tile_type].background_color

    @property
    def description(self):
        return terrain.data[self.tile_type].description

    @property
    def stamina_cost(self):
        return terrain.data[self.tile_type].stamina_cost

    @property
    def jumpable(self):
        return terrain.data[self.tile_type].jumpable

    @property
    def flammable(self):
        return terrain.data[self.tile_type].flammable

    @property
    def diggable(self):
        return terrain.data[self.tile_type].diggable

                
#############################################
# General Functions
#############################################


def has_skill(name):
    if name == 'Adrien':
        return False  # OOH, BURN!
    for skill in learned_skills:
        if skill.name == name:
            return True
    return False


def expire_out_of_vision(obj):
    if not fov.player_can_see(obj.x, obj.y):
        obj.destroy()


def pick_up_mana(mana, obj):
    if obj is player and len(player.mana) < player.player_stats.max_mana:
        player.mana.append(mana.mana_type)
        ui.message('You are infused with magical power.', mana.color)
        mana.destroy()


def pick_up_xp(xp, obj):
    if obj is player:
        player.fighter.xp += consts.XP_ORB_AMOUNT_MIN + \
                             libtcod.random_get_int(0, 0, consts.XP_ORB_AMOUNT_MAX - consts.XP_ORB_AMOUNT_MIN)
        check_level_up()
        xp.destroy()


def step_on_reed(reed, obj):
    reed.destroy()


def adjacent_tiles_orthogonal(x, y):
    adjacent = []
    if x > 0:
        adjacent.append((x - 1, y))
    if x < consts.MAP_WIDTH - 1:
        adjacent.append((x + 1, y))
    if y > 0:
        adjacent.append((x, y - 1))
    if y < consts.MAP_WIDTH - 1:
        adjacent.append((x, y + 1))
    return adjacent


def adjacent_tiles_diagonal(x, y):
    adjacent = []
    for i_y in range(y - 1, y + 2):
        for i_x in range(x - 1, x + 2):
            if 0 <= i_x < consts.MAP_WIDTH and 0 <= i_y < consts.MAP_HEIGHT and not (i_x == x and i_y == y):
                adjacent.append((i_x, i_y))
    return adjacent


def is_adjacent_orthogonal(a_x, a_y, b_x, b_y):
    return (abs(a_x - b_x) <= 1 and a_y == b_y) or (abs(a_y - b_y) <= 1 and a_x == b_x)


def is_adjacent_diagonal(a_x, a_y, b_x, b_y):
    return abs(a_x - b_x) <= 1 and abs(a_y - b_y) <= 1


def blastcap_explode(blastcap):
    global changed_tiles

    blastcap.fighter = None
    ui.message('The blastcap explodes with a BANG, stunning nearby creatures!', libtcod.gold)
    for obj in objects:
        if obj.fighter and is_adjacent_orthogonal(blastcap.x, blastcap.y, obj.x, obj.y):
            if obj.fighter.apply_status_effect(effects.StatusEffect('stunned', consts.BLASTCAP_STUN_DURATION, libtcod.light_yellow)):
                ui.message('The ' + obj.name + ' is stunned!', libtcod.gold)

    if ui.selected_monster is blastcap:
        changed_tiles.append((blastcap.x, blastcap.y))
        ui.selected_monster = None
        ui.auto_target_monster()

    blastcap.destroy()
    return


def centipede_on_hit(attacker, target):
    target.fighter.apply_status_effect(effects.StatusEffect('stung', consts.CENTIPEDE_STING_DURATION, libtcod.flame))


def clamp(value, min_value, max_value):
    if value < min_value:
        value = min_value
    if value > max_value:
        value = max_value
    return value


def roll_to_hit(target,  accuracy):
    return libtcod.random_get_float(0, 0, 1) < get_chance_to_hit(target, accuracy)


def get_chance_to_hit(target, accuracy):
    if target.fighter.has_status('stunned'):
        return 1.0

    return 1.0 - float(target.fighter.evasion) / float(max(accuracy, target.fighter.evasion + 1))


def random_position_in_circle(radius):
    r = libtcod.random_get_float(0, 0.0, float(radius))
    theta = libtcod.random_get_float(0, 0.0, 2.0 * math.pi)
    return int(round(r * math.cos(theta))), int(round(r * math.sin(theta)))


def object_at_tile(x, y, name):
    for obj in objects:
        if obj.x == x and obj.y == y and obj.name == name:
            return obj
    return None


# on_create function of tunnel spiders. Creates a web at the spiders location and several random adjacent spaces
def tunnel_spider_spawn_web(obj):
    adjacent = adjacent_tiles_diagonal(obj.x, obj.y)
    webs = [(obj.x, obj.y)]
    for a in adjacent:
        if libtcod.random_get_int(0, 0, 2) == 0 and not dungeon_map[a[0]][a[1]].blocks:
            webs.append(a)
    for w in webs:
        make_spiderweb(w[0], w[1])


# creates a spiderweb at the target location
def make_spiderweb(x, y):
    web = GameObject(x, y, '*', 'spiderweb', libtcod.lightest_gray,
                     description='a web of spider silk. Stepping into a web will impede movement for a turn.',
                     burns=True)
    objects.append(web)
    web.send_to_back()


def get_all_equipped(equipped_list):
    result = []
    for item in equipped_list:
        if item.equipment and item.equipment.is_equipped:
            result.append(item.equipment)
    return result


def get_equipped_in_slot(equipped_list,slot):
    for obj in equipped_list:
        if obj.equipment and obj.equipment.is_equipped and obj.equipment.slot == slot:
            return obj.equipment
    return None


def from_dungeon_level(table):
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0


def random_choice(chances_dict):
    chances = chances_dict.values()
    strings = chances_dict.keys()
    return strings[random_choice_index(chances)]


def random_choice_index(chances):
    dice = libtcod.random_get_int(0, 1, sum(chances))
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
        if dice <= running_sum:
            return choice
        choice += 1


def check_level_up():
    next = consts.LEVEL_UP_BASE + player.level * consts.LEVEL_UP_FACTOR
    if player.fighter.xp >= next:
        level_up()
        player.fighter.xp = player.fighter.xp - next


def level_up(altar = None):
    global learned_skills

    player.level += 1
    ui.message('You grow stronger! You have reached level ' + str(player.level) + '!', libtcod.green)
    choice = None
    while choice == None:
        choice = ui.menu('Level up! Choose a stat to raise:\n',
        ['Constitution (+20 HP, from ' + str(player.fighter.base_max_hp) + ')',
            'Strength (+1 attack, from ' + str(player.fighter.base_power) + ')',
            'Agility (+1 defense, from ' + str(player.fighter.base_defense) + ')',
            'Intelligence (increases spell damage)',
            'Wisdom (increases spell slots, spell utility)'
         ], consts.LEVEL_SCREEN_WIDTH)

    if choice == 0:
        player.fighter.max_hp += 20
        player.fighter.hp += 20
    elif choice == 1:
        player.player_stats.str += 1
    elif choice == 2:
        player.player_stats.agi += 1
    elif choice == 3:
        player.player_stats.int += 1
    elif choice == 4:
        player.player_stats.wiz += 1

    if player.level % 3 == 0:
        skill = ui.skill_menu(add_skill=True)
        if skill is not None and skill not in learned_skills:
            learned_skills.append(skill)

    if altar:
        altar.destroy()


def next_level():
    global dungeon_level, changed_tiles

    ui.message('You descend...', libtcod.white)
    dungeon_level += 1
    generate_level()
    #initialize_fov()

    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            changed_tiles.append((x, y))


def player_death(player):
    global game_state
    ui.message('You\'re dead, sucka.', libtcod.grey)
    game_state = 'dead'
    player.char = '%'
    player.color = libtcod.darker_red


def bomb_beetle_corpse_tick(object=None):
    if object is None:
        return
    object.bomb_timer -= 1
    if object.bomb_timer > 2:
        object.color = libtcod.black
    elif object.bomb_timer > 1:
        object.color = libtcod.darkest_red
    elif object.bomb_timer > 0:
        object.color = libtcod.red
    elif object.bomb_timer <= 0:
        ui.message('The bomb beetle corpse explodes!', libtcod.orange)
        create_fire(object.x, object.y, 10)
        for tile in adjacent_tiles_diagonal(object.x, object.y):
            if libtcod.random_get_int(0, 0, 3) != 0:
                create_fire(tile[0], tile[1], 10)
            monster = get_monster_at_tile(tile[0], tile[1])
            if monster is not None:
                monster.fighter.take_damage(consts.BOMB_BEETLE_DAMAGE)
                if monster.fighter is not None:
                    monster.fighter.apply_status_effect(effects.burning())
        object.destroy()


def bomb_beetle_death(beetle):

    if beetle.fighter.loot_table is not None:
        drop = get_loot(beetle.fighter)
        if drop:
            objects.append(drop)
            drop.send_to_back()

    ui.message(beetle.name.capitalize() + ' is dead!', libtcod.red)
    beetle.char = 149
    beetle.color = libtcod.black
    beetle.blocks = True
    beetle.fighter = None
    beetle.ai = None
    beetle.name = 'beetle bomb'
    beetle.description = 'The explosive carapace of a blast beetle. In a few turns, it will explode!'
    beetle.bomb_timer = 3
    beetle.on_tick = bomb_beetle_corpse_tick

    if ui.selected_monster is beetle:
        changed_tiles.append((beetle.x, beetle.y))
        ui.selected_monster = None
        ui.auto_target_monster()


def monster_death(monster):
    global changed_tiles

    if monster.fighter.loot_table is not None:
        drop = get_loot(monster.fighter)
        if drop:
            objects.append(drop)
            drop.send_to_back()

    if hasattr(monster.fighter,'inventory') and len(monster.fighter.inventory) > 0:
        for item in monster.fighter.inventory:
            item.x = monster.x
            item.y = monster.y
            objects.append(item)
            item.send_to_back()


    ui.message(monster.name.capitalize() + ' is dead!', libtcod.red)
    monster.char = '%'
    monster.color = libtcod.darker_red
    monster.blocks = False
    if pathfinding.map:
        pathfinding.map.mark_passable((monster.x, monster.y))
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()

    if ui.selected_monster is monster:
        changed_tiles.append((monster.x, monster.y))
        ui.selected_monster = None
        ui.auto_target_monster()


def target_monster(max_range=None):
    while True:
        (x, y) = ui.target_tile(max_range)
        if x is None:
            return None
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj is not player:
                return obj
        return None


def get_monster_at_tile(x, y):
    for obj in objects:
        if obj.x == x and obj.y == y and obj.fighter and obj is not player:
            return obj
    return None


def object_at_coords(x, y):
    global dungeon_map

    ops = [t for t in objects if (t.x == x and t.y == y)]
    if len(ops) > 1:
        menu_choice = ui.menu("Which object?", [o.name for o in ops], 40)
        if menu_choice is not None:
            return ops[menu_choice]
        else:
            return None
    elif len(ops) == 0:
        return dungeon_map[x][y]
    else:
        return ops[0]





def beam(sourcex, sourcey, destx, desty):
    libtcod.line_init(sourcex, sourcey, destx, desty)
    line_x, line_y = libtcod.line_step()
    beam_values = []
    while line_x is not None:
        coord = line_x, line_y
        beam_values.append(coord)
        line_x, line_y = libtcod.line_step()
    # beam_values.append(destx, desty) TODO: need to test this
    return beam_values


def beam_interrupt(sourcex, sourcey, destx, desty):
    libtcod.line_init(sourcex, sourcey, destx, desty)
    line_x, line_y = libtcod.line_step()
    while line_x is not None:
        if is_blocked(line_x, line_y, dungeon_map[sourcex][sourcey].elevation):  # beam interrupt scans until it hits something
            return line_x, line_y
        line_x, line_y = libtcod.line_step()
    return destx, desty


def closest_monster(max_range):
    closest_enemy = None
    closest_dist = max_range + 1

    for object in objects:
        if object.fighter and not object == player and fov.player_can_see(object.x, object.y):
            dist = player.distance_to(object)
            if dist < closest_dist:
                closest_dist = dist
                closest_enemy = object
    return closest_enemy



def in_bounds(x, y):
    return x >= 0 and y >= 0 and x < consts.MAP_WIDTH and y < consts.MAP_HEIGHT


def is_blocked(x, y, elevation=None):

    if elevation is not None and dungeon_map[x][y].elevation != elevation and dungeon_map[x][y].tile_type != 'ramp':
        return True

    if dungeon_map[x][y].blocks:
        return True

    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False


def get_room_spawns(room):
    return [[k, libtcod.random_get_int(0, v[0], v[1])] for (k, v) in room['spawns'].items()]


def spawn_monster(name, x, y):
    if consts.DEBUG_NO_MONSTERS:
        return None
    if not is_blocked(x, y):
        p = monsters.proto[name]
        death = monster_death
        if p.get('death_function'):
            death = p.get('death_function')
        fighter_component = Fighter(hp=p['hp'], attack_damage=p['attack_damage'], armor=p['armor'],
                                    evasion=p['evasion'], accuracy=p['accuracy'], xp=0,
                                    death_function=death, loot_table=loot.table[p.get('loot', 'default')],
                                    can_breath_underwater=True, resistances=p['resistances'],
                                    inventory=spawn_monster_inventory(p.get('equipment')), on_hit=p.get('on_hit'),
                                    base_shred=p.get('shred', 0),
                                    base_guaranteed_shred=p.get('guaranteed_shred', 0),
                                    base_pierce=p.get('pierce', 0))
        if p.get('attributes'):
            fighter_component.abilities = [create_ability(a) for a in p['attributes'] if a.startswith('ability_')]
        ai = None
        if p.get('ai'):
            ai = p.get('ai')()
        monster = GameObject(x, y, p['char'], p['name'], p['color'], blocks=True, fighter=fighter_component,
                             ai=ai, description=p['description'], on_create=p.get('on_create'), update_speed=p['speed'])
        if p.get('mana'):
            monster.mana = p.get('mana')
        monster.elevation = dungeon_map[x][y].elevation
        objects.append(monster)
        return monster
    return None


def spawn_monster_inventory(proto):
    result = []
    if proto:
        for slot in proto:
            equip = random_choice(slot)
            if equip != 'none':
                result.append(create_item(equip, material=loot.choose_material(-10), quality=loot.choose_quality(-10)))
    return result


def create_ability(name):
    if name in abilities.data:
        a = abilities.data[name]
        return abilities.Ability(a.get('name'), a.get('description'), a['function'], a.get('cooldown'))
    else:
        return None


def create_item(name, material=None, quality=None):
    p = loot.proto[name]
    ability = None
    if p.get('ability') is not None and p.get('ability') in abilities.data:
        ability = create_ability(p.get('ability'))
    item_component = Item(category=p['category'], use_function=p.get('on_use'), type=p['type'], learn_spell=p.get('learn_spell'), ability=ability)
    equipment_component = None
    if p['category'] == 'weapon' or p['category'] == 'armor':
        equipment_component = Equipment(
            slot=p['slot'],
            category=p['category'],
            attack_damage_bonus=p.get('attack_damage_bonus', 0),
            armor_bonus=p.get('armor_bonus', 0),
            max_hp_bonus=p.get('max_hp_bonus', 0),
            evasion_bonus=p.get('evasion_bonus', 0),
            spell_power_bonus=p.get('spell_power_bonus', 0),
            stamina_cost=p.get('stamina_cost', 0),
            str_requirement=p.get('str_requirement', 0),
            shred_bonus=p.get('shred', 0),
            guaranteed_shred_bonus=p.get('guaranteed_shred', 0),
            pierce=p.get('pierce', 0),
            accuracy=p.get('accuracy', 0),
            ctrl_attack=p.get('ctrl_attack'),
            ctrl_attack_desc=p.get('ctrl_attack_desc'),
            break_chance=p.get('break', 0),
            weapon_dice=p.get('weapon_dice'),
            str_dice=p.get('str_dice', 0)
        )
        if equipment_component.category == 'weapon':
            equipment_component.base_id = name
            # Material/Quality
            if material is None:
                material = random_choice(
                    {
                        'wooden' : 10,
                        'bronze' : 15,
                        'iron' : 65,
                        'steel' : 10,
                        'crystal' : 1,
                        'meteor' : 1,
                        'blightstone' : 1,
                     }
                )
            equipment_component.material = material
            equipment_component.attack_damage_bonus += loot.weapon_materials[material]['dmg']
            equipment_component.accuracy_bonus += loot.weapon_materials[material]['acc']
            equipment_component.shred_bonus += loot.weapon_materials[material].get('shred', 0)
            equipment_component.pierce_bonus += loot.weapon_materials[material].get('pierce', 0)
            equipment_component.guaranteed_shred_bonus += loot.weapon_materials[material].get('autoshred', 0)
            equipment_component.break_chance += loot.weapon_materials[material].get('break', 0.0)
            if quality is None:
                quality = random_choice(
                    {
                        'broken' : 5,
                        'crude' : 5,
                        '' : 75,
                        'military' : 10,
                        'fine' : 10,
                        'masterwork' : 5,
                        'artifact' : 1,
                     }
                )
            equipment_component.quality = quality
            equipment_component.attack_damage_bonus += loot.weapon_qualities[quality]['dmg']
            equipment_component.accuracy_bonus += loot.weapon_qualities[quality]['acc']
            equipment_component.shred_bonus += loot.weapon_qualities[quality].get('shred', 0)
            equipment_component.pierce_bonus += loot.weapon_qualities[quality].get('pierce', 0)
            equipment_component.guaranteed_shred_bonus += loot.weapon_qualities[quality].get('autoshred', 0)
            equipment_component.break_chance += loot.weapon_qualities[quality].get('break', 0.0)

    go = GameObject(0, 0, p['char'], p['name'], p.get('color', libtcod.white), item=item_component,
                      equipment=equipment_component, always_visible=True, description=p.get('description'))
    if ability is not None:
        go.item.ability = ability
    if hasattr(equipment_component, 'material'):
        go.name = equipment_component.material + ' ' + go.name
    if hasattr(equipment_component, 'quality') and equipment_component.quality != '':
        go.name = equipment_component.quality + ' ' + go.name
    go.name = go.name.title()
    return go


def spawn_item(name, x, y, material=None, quality=None):
        item = create_item(name, material, quality)
        item.x = x
        item.y = y
        objects.append(item)
        item.send_to_back()


def set_quality(equipment, quality):
    # set to default
    p = loot.proto[equipment.base_id]
    equipment.attack_damage_bonus = p.get('attack_damage_bonus', 0)
    equipment.accuracy_bonus = p.get('accuracy', 0)
    equipment.shred_bonus = p.get('shred', 0)
    equipment.pierce_bonus = p.get('pierce', 0)
    equipment.guaranteed_shred_bonus = p.get('guaranteed_shred', 0)
    equipment.break_chance = p.get('break', 0)
    equipment.owner.name = p['name']
    # assign quality
    equipment.quality = quality
    equipment.attack_damage_bonus += loot.weapon_qualities[quality]['dmg']
    equipment.accuracy_bonus += loot.weapon_qualities[quality]['acc']
    equipment.shred_bonus += loot.weapon_qualities[quality].get('shred', 0)
    equipment.pierce_bonus += loot.weapon_qualities[quality].get('pierce', 0)
    equipment.guaranteed_shred_bonus += loot.weapon_qualities[quality].get('autoshred', 0)
    equipment.break_chance = loot.weapon_qualities[quality].get('break', 0.0)
    # update name
    go = equipment.owner
    if hasattr(equipment, 'material'):
        go.name = equipment.material + ' ' + go.name
    if hasattr(equipment, 'quality') and equipment.quality != '':
        go.name = equipment.quality + ' ' + go.name
    go.name = go.name.title()


def check_breakage(equipment):
    if equipment.break_chance and equipment.break_chance > 0.0:
        roll = libtcod.random_get_double(0, 0, 1.0)
        roll *= 100.0
        if roll < equipment.break_chance:
            # broken!
            ui.message('The ' + equipment.owner.name + ' breaks!', libtcod.white)
            set_quality(equipment, 'broken')
            return True
        else:
            return False
    else:
        return False


def create_fire(x,y,temp):
    global changed_tiles

    tile = dungeon_map[x][y]
    if tile.tile_type == 'shallow water' or tile.tile_type == 'deep water' or tile.blocks:
        return
    component = FireBehavior(temp)
    obj = GameObject(x,y,'^','Fire',libtcod.red,misc=component)
    objects.append(obj)
    if temp > 4 and tile.tile_type != 'ramp':
        dungeon_map[x][y].tile_type = 'scorched floor'
    for obj in get_objects(x, y, condition=lambda o: o.burns):
        obj.destroy()
    changed_tiles.append((x, y))


def place_objects(tiles):
    if len(tiles) == 0:
        return
    max_items = from_dungeon_level([[1, 1], [2, 4], [4, 7]])
    #item_chances = {'potion_healing':65, 'scroll_lightning':10, 'scroll_confusion':10, 'scroll_fireball':10, 'scroll_forge':5 }
    #item_chances['equipment_longsword'] = 15
    #item_chances['equipment_shield'] = 20
    #item_chances['equipment_spear'] = 15

    table = dungeon.table[get_dungeon_level()]['versions']
    for i in range(libtcod.random_get_int(0, 0, 4)):  # temporary line to spawn multiple monster groups in a room
        spawns = get_room_spawns(table[random_choice_index([e['weight'] for e in table])])
        for s in spawns:
            for n in range(0,s[1]):
                random_pos = tiles[libtcod.random_get_int(0, 0, len(tiles) - 1)]
                #x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
                #y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
                spawn_monster(s[0], random_pos[0], random_pos[1])
                tiles.remove(random_pos)
                if len(tiles) == 0:
                    return

    num_items = libtcod.random_get_int(0, 0, max_items)
    for i in range(num_items):
        #x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        #y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
        random_pos = tiles[libtcod.random_get_int(0, 0, len(tiles) - 1)]

        if not is_blocked(random_pos[0], random_pos[1]):
            #choice = random_choice(item_chances)
            #spawn_item(choice, random_pos[0], random_pos[1])
            item = loot.item_from_table(dungeon_level * 5)
            item.x = random_pos[0]
            item.y = random_pos[1]
            objects.append(item)
            item.send_to_back()
            tiles.remove(random_pos)
            if len(tiles) == 0:
                return

    for i in range(2):
        random_pos = tiles[libtcod.random_get_int(0, 0, len(tiles) - 1)]
        objects.append(GameObject(random_pos[0], random_pos[1], 7, 'xp', libtcod.lightest_blue, always_visible=True,
                                  description='xp', on_step=pick_up_xp))
        tiles.remove(random_pos)
        if len(tiles) == 0:
            return


def check_boss(level):
    global spawned_bosses

    for (k,v) in dungeon.bosses.items():
        chance = v.get(level)
        if chance is not None and spawned_bosses.get(k) is None:
            if chance >= libtcod.random_get_int(0,0,100):
                spawned_bosses[k] = True
                return k
    return None


def get_dungeon_level():
    global dungeon_level
    return "dungeon_{}".format(dungeon_level)


def player_move_or_attack(dx, dy, ctrl=False):

    if ctrl:
        weapon = get_equipped_in_slot(player.fighter.inventory, 'right hand')
        if weapon and weapon.ctrl_attack:
            if weapon.quality != 'broken':
                success = weapon.ctrl_attack(dx, dy) != 'failed'
            else:
                ui.message('Your ' + weapon.owner.name + ' cannot do that in its current state!')
                return False
        else:
            success = player_bash_attack(dx, dy) != 'failed'
    else:
        target = get_monster_at_tile(player.x + dx, player.y + dy)
        if target is not None:
            success = player.fighter.attack(target) != 'failed'
            if success and target.fighter:
                ui.select_monster(target)
        else:
            value = player.move(dx, dy)
            return value

    return success


def player_dig(dx, dy):
    global changed_tiles

    dig_x = player.x + dx
    dig_y = player.y + dy
    if dungeon_map[dig_x][dig_y].diggable:
        dungeon_map[dig_x][dig_y].tile_type = 'stone floor'
        changed_tiles.append((dig_x, dig_y))
        if pathfinding.map:
            pathfinding.map.mark_passable((dig_x, dig_y))
        fov.set_fov_properties(dig_x, dig_y, False, dungeon_map[dig_x][dig_y].elevation)
        check_breakage(get_equipped_in_slot(player.fighter.inventory, 'right hand'))
        return 'success'
    else:
        ui.message('You cannot dig there.', libtcod.lightest_gray)
        return 'failed'


def player_reach_attack(dx, dy):

    target_space = player.x + 2 * dx, player.y + 2 * dy
    target = get_monster_at_tile(target_space[0], target_space[1])
    if target is not None:
        result = player.fighter.attack_ex(target, player.fighter.calculate_attack_stamina_cost(), player.fighter.accuracy,
                             player.fighter.attack_damage * 1.5, player.fighter.damage_variance, None, 'reach-attacks',
                             player.fighter.attack_shred, player.fighter.attack_guaranteed_shred, player.fighter.attack_pierce)
        if result != 'failed' and target.fighter:
            ui.select_monster(target)
        return result
    else:
        target = get_monster_at_tile(player.x + dx, player.y + dy)
        if target is not None:
            result = player.fighter.attack(target)
            if result != 'failed' and target.fighter:
                ui.select_monster(target)
        else:
            value = player.move(dx, dy)
            if value:
                return 'moved'
    return 'failed'


def player_cleave_attack(dx, dy):
    # attack all adjacent creatures
    adjacent = adjacent_tiles_diagonal(player.x, player.y)
    if adjacent and len(adjacent) > 0:
        stamina_cost = player.fighter.calculate_attack_stamina_cost() * 2
        if player.fighter.stamina < stamina_cost:
            ui.message("You don't have the stamina to perform a cleave attack!", libtcod.light_yellow)
            return 'failed'
        player.fighter.adjust_stamina(-stamina_cost)
        for tile in adjacent:
            target = get_monster_at_tile(tile[0], tile[1])
            if target and target.fighter:
                player.fighter.attack_ex(target, 0, player.fighter.accuracy, player.fighter.attack_damage,
                                 player.fighter.damage_variance, None, 'cleaves', player.fighter.attack_shred,
                                 player.fighter.attack_guaranteed_shred + 1, player.fighter.attack_pierce)
        return 'cleaved'
    else:
        value = player.move(dx, dy)
        if value:
            return 'moved'
    return 'failed'


def player_bash_attack(dx, dy):

    target = get_monster_at_tile(player.x + dx, player.y + dy)
    if target is not None:
        result = player.fighter.attack_ex(target, consts.BASH_STAMINA_COST, player.fighter.accuracy * consts.BASH_ACC_MOD,
                                 player.fighter.attack_damage * consts.BASH_DMG_MOD, player.fighter.damage_variance,
                                 None, 'bashes', player.fighter.attack_shred + 1, player.fighter.attack_guaranteed_shred,
                                 player.fighter.attack_pierce)
        if result == 'hit' and target.fighter:
            ui.select_monster(target)
            # knock the target back one space. Stun it if it cannot move.
            direction = target.x - player.x, target.y - player.y  # assumes the player is adjacent
            stun = False
            against = ''
            against_tile = dungeon_map[target.x + direction[0]][target.y + direction[1]]
            if against_tile.blocks:
                stun = True
                against = dungeon_map[target.x + direction[0]][target.y + direction[1]].name
            elif against_tile.elevation != target.elevation and against_tile.tile_type != 'ramp' and dungeon_map[target.x][target.y] != 'ramp':
                stun = True
                against = 'cliff'
            else:
                for obj in objects:
                    if obj.x == target.x + direction[0] and obj.y == target.y + direction[1] and obj.blocks:
                        stun = True
                        against = obj.name
                        break

            if stun:
                #  stun the target
                if target.fighter.apply_status_effect(effects.StatusEffect('stunned', time_limit=2, color=libtcod.light_yellow)):
                    ui.message('The ' + target.name + ' collides with the ' + against + ', stunning it!', libtcod.gold)
            else:
                ui.message('The ' + target.name + ' is knocked backwards.', libtcod.gray)
                target.set_position(target.x + direction[0], target.y + direction[1])
                render_map()
                libtcod.console_flush()

        return result
    else:
        value = player.move(dx, dy)
        if value:
            return 'moved'
    return 'failed'


def get_loot(monster):
    loot_table = monster.loot_table
    drop = loot_table[libtcod.random_get_int(0,0,len(loot_table) - 1)]
    if drop:
        proto = loot.proto[drop]
        item = Item(category=proto['category'], use_function=proto['on_use'], type=proto['type'])
        return GameObject(monster.owner.x, monster.owner.y, proto['char'], proto['name'], proto['color'], item=item)


def do_queued_action(action):
    if action == 'finish-meditate':
        manatype = 'normal'
        #if dungeon_map[player.x][player.y].tile_type == 'grass floor':  # Temporary - used for testing
        #    manatype = 'life'

        if len(player.mana) < player.player_stats.max_mana:
            player.mana.append(manatype)
            ui.message('You have finished meditating. You are infused with magical power.', libtcod.dark_cyan)
            return
        elif manatype != 'normal':
            for i in range(len(player.mana)):
                if player.mana[i] == 'normal':
                    player.mana[i] = manatype
                    ui.message('You have finished meditating. You are infused with magical power.', libtcod.dark_cyan)
                    return
        ui.message('You have finished meditating. You were unable to gain any more power than you already have.', libtcod.dark_cyan)
        return


def show_ability_screen():
    opts = []
    for a in abilities.default_abilities:
        opts.append(a)
    for i in player.fighter.inventory:
        if i.item.ability is not None:
            opts.append(i.item.ability)
    index = ui.menu('Abilities',[opt.name for opt in opts],20)
    if index is not None:
        choice = opts[index]
        if choice is not None:
            return choice.use(player)
    return 'didnt-take-turn'


def handle_keys():

    global game_state, stairs
    global key, mouse

    # key = libtcod.console_check_for_keypress()  #real-time
    # key = libtcod.console_wait_for_keypress(True)  #turn-based

    ui.mouse_select_monster()

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game

    if game_state == 'playing':

        if player.fighter and player.fighter.has_status('stunned'):
            return 'stunned'

        if player.action_queue is not None and len(player.action_queue) > 0:
            action = player.action_queue[0]
            player.action_queue.remove(action)
            do_queued_action(action)
            return action


        key_char = chr(key.c)
        moved = False
        ctrl = key.lctrl or key.rctrl
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            moved = player_move_or_attack(0, -1, ctrl)
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            moved = player_move_or_attack(0, 1, ctrl)
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            moved = player_move_or_attack(-1, 0, ctrl)
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            moved = player_move_or_attack(1, 0, ctrl)
        elif key.vk == libtcod.KEY_KP7:
            moved = player_move_or_attack(-1, -1, ctrl)
        elif key.vk == libtcod.KEY_KP9:
            moved = player_move_or_attack(1, -1, ctrl)
        elif key.vk == libtcod.KEY_KP1:
            moved = player_move_or_attack(-1, 1, ctrl)
        elif key.vk == libtcod.KEY_KP3:
            moved = player_move_or_attack(1, 1, ctrl)
        elif key.vk == libtcod.KEY_KP5 or key_char == 's':
            player.fighter.adjust_stamina(consts.STAMINA_REGEN_WAIT) # gain stamina for standing still
            moved = True  # so that this counts as a turn passing
            pass
        else:
            if key_char == 'g':
                return pick_up_item()
            if key_char == 'i':
                return ui.inspect_inventory()
            if key_char == 'u':
                chosen_item = ui.inventory_menu('Use which item?')
                if chosen_item is not None:
                    use_result = chosen_item.use()
                    if use_result == 'cancelled':
                       return 'didnt-take-turn'
                    else:
                       return 'used-item'
            if key_char == 'd':
                chosen_item = ui.inventory_menu('Drop which item?')
                if chosen_item is not None:
                    chosen_item.drop()
                    return 'dropped-item'
            if key_char == ',' and key.shift:
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()
            if key_char == 'c':
                ui.msgbox('Character Information\n\nLevel: ' + str(player.level) + '\n\nMaximum HP: ' +
                       str(player.fighter.max_hp),
                       consts.CHARACTER_SCREEN_WIDTH)
            if key_char == 'z':
                return cast_spell_new()
                #if key.shift:
                #    return cast_spell_new()
                #else:
                #    if len(memory) == 0:
                #        ui.message('You have no spells in your memory to cast.', libtcod.purple)
                #    elif dungeon_map[player.x][player.y].tile_type == 'deep water':
                #        ui.message('You cannot cast spells underwater.', libtcod.purple)
                #    else:
                #        cast_spell()
                #        return 'casted-spell'
            if key_char == 'j':
                return jump()
            if key_char == 'e':
                examine()
            if key.vk == libtcod.KEY_TAB:
                ui.target_next_monster()
            if key_char == 'm':
                return meditate()
            if key_char == 'a':
                return show_ability_screen()
            if key_char == 'l': # TEMPORARY
                ui.skill_menu()
                return 'didnt-take-turn'
            if mouse.rbutton_pressed:
                offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2, player.y - consts.MAP_VIEWPORT_HEIGHT / 2
                mouse_pos = mouse.cx + offsetx - consts.MAP_VIEWPORT_X, mouse.cy + offsety - consts.MAP_VIEWPORT_Y
                if in_bounds(mouse_pos[0], mouse_pos[1]):
                    examine(mouse_pos[0], mouse_pos[1])
            return 'didnt-take-turn'
        if not moved:
            return 'didnt-take-turn'

def cast_spell_new():
    if len(player.known_spells) <= 0:
        ui.message("You don't know any spells.", libtcod.light_blue)
        return 'didnt-take-turn'
    else:
        names = []
        for s in player.known_spells:
            names.append(s.name + ' ' + s.cost_string)
        selection = ui.menu('Cast which spell?', names, 30)
        if selection is not None:
            if player.known_spells[selection].check_mana():
                if player.known_spells[selection].cast():
                    return 'cast-spell'
                else:
                    return 'didnt-take-turn'
            else:
                ui.message("You don't have enough mana to cast that spell.", libtcod.light_blue)
                return 'didnt-take-turn'
    return 'didnt-take-turn'


def pick_up_item():
    items_here = get_objects(player.x, player.y, condition=lambda o: o.item)
    if len(items_here) > 0:
        if len(items_here) == 1:
            items_here[0].item.pick_up()
            return 'picked-up-item'
        options = []
        options.append('All')
        for item in items_here:
            options.append(item.name)

        selection = ui.menu('Pick up which item?', options, 30)
        if selection is not None:
            if selection == 0:
                for i in items_here:
                    i.item.pick_up()
            else:
                items_here[selection - 1].item.pick_up()
            return 'picked-up-item'
    else:
        interactable_here = get_objects(player.x, player.y, condition=lambda o:o.interact, distance=1) #get stuff that's adjacent too
        if len(interactable_here) > 0:
            interactable_here[0].interact(interactable_here[0])
            return 'interacted'
    return 'didnt-take-turn'


def get_objects(x, y, condition=None, distance=0):
    found = []
    for obj in objects:
        if max(abs(obj.x - x), abs(obj.y - y)) <= distance:
            if condition is not None:
                if condition(obj):
                    found.append(obj)
            else:
                found.append(obj)
    return found

def meditate():
    ui.message('You tap into the magic of the world around you...', libtcod.dark_cyan)
    for i in range(consts.MEDITATE_CHANNEL_TIME - 1):
        player.action_queue.append('channel-meditate')
    player.action_queue.append('finish-meditate')
    return 'start-meditate'


def get_description(obj):
    if obj and hasattr(obj, 'description') and obj.description is not None:
        return obj.description
    else:
        return ""


def examine(x=None, y=None):
    if x is None or y is None:
        x, y = ui.target_tile()
    if x is not None and y is not None:
        obj = object_at_coords(x, y)
        if obj is not None:
            if isinstance(obj, GameObject):
                desc = obj.name.capitalize()# + '\n' + get_description(obj)
                if hasattr(obj, 'fighter') and obj.fighter is not None and \
                        hasattr(obj.fighter, 'inventory') and obj.fighter.inventory is not None and len(obj.fighter.inventory) > 0:
                    desc = desc + '\nInventory: '
                    for item in obj.fighter.inventory:
                        desc = desc + item.name + ', '
                ui.menu(desc, ['back'], 50, render_func=obj.print_description)
            else:
                desc = obj.name.capitalize() + '\n' + get_description(obj)
                ui.menu(desc, ['back'], 50)


def jump(actor=None):

    if not dungeon_map[player.x][player.y].jumpable:
        ui.message('You cannot jump from this terrain!', libtcod.light_yellow)
        return 'didnt-take-turn'

    web = object_at_tile(player.x, player.y, 'spiderweb')
    if web is not None:
        ui.message('You struggle against the web.')
        web.destroy()
        return 'webbed'

    if player.fighter.stamina < consts.JUMP_STAMINA_COST:
        ui.message("You don't have the stamina to jump!", libtcod.light_yellow)
        return 'didnt-take-turn'

    ui.message('Jump to where?', libtcod.white)

    ui.render_message_panel()
    libtcod.console_flush()
    (x, y) = ui.target_tile(consts.BASE_JUMP_RANGE, 'pick', consts.JUMP_ATTACK_ACC_MOD)
    if x is not None and y is not None:
        if dungeon_map[x][y].blocks:
            ui.message('There is something in the way.', libtcod.light_yellow)
            return 'didnt-take-turn'
        elif is_blocked(x, y, player.elevation) and dungeon_map[x][y].elevation > player.elevation:
            ui.message("You can't jump that high!", libtcod.light_yellow)
            return 'didnt-take-turn'
        else:
            jump_attack_target = None
            for obj in objects:
                if obj.x == x and obj.y == y and obj.blocks:
                    jump_attack_target = obj
                    break
            if jump_attack_target is not None:
                # Jump attack
                land = land_next_to_target(jump_attack_target.x, jump_attack_target.y, player.x, player.y)
                if land is not None:
                    player.set_position(land[0], land[1])
                    player.fighter.adjust_stamina(-consts.JUMP_STAMINA_COST)

                    player.fighter.attack_ex(jump_attack_target, 0, player.fighter.accuracy * consts.JUMP_ATTACK_ACC_MOD,
                                             player.fighter.attack_damage * consts.JUMP_ATTACK_DMG_MOD,
                                             player.fighter.damage_variance, player.fighter.on_hit, 'jump-attacks',
                                             player.fighter.attack_shred, player.fighter.attack_guaranteed_shred,
                                             player.fighter.attack_pierce)

                    return 'jump-attacked'
                else:
                    ui.message('There is something in the way.', libtcod.white)
                    return 'didnt-take-turn'
            else:
                #jump to open space
                player.set_position(x, y)
                player.fighter.adjust_stamina(-consts.JUMP_STAMINA_COST)
                return 'jumped'


    ui.message('Out of range.', libtcod.white)
    return 'didnt-take-turn'


def land_next_to_target(target_x, target_y, source_x, source_y):
    if abs(target_x - source_x) <= 1 and abs(target_y - source_y) <= 1:
        return source_x, source_y  # trivial case - if we are adjacent we don't need to move
    b = beam(source_x, source_y, target_x, target_y)
    land_x = b[len(b) - 2][0]
    land_y = b[len(b) - 2][1]
    if not is_blocked(land_x, land_y):
        return land_x, land_y
    return None


def cast_spell():
    ui.message('Cast which spell?', libtcod.purple)

    render_all()
    libtcod.console_flush()

    choice = libtcod.console_wait_for_keypress(True).c - 48

    if choice > 0 and choice < len(memory) + 1:
        memory[choice - 1].item.use()
    else:
        ui.message('No such spell.', libtcod.purple)


def clear_map():
    libtcod.console_set_default_background(map_con, libtcod.black)
    libtcod.console_set_default_foreground(map_con, libtcod.black)
    libtcod.console_clear(map_con)


def render_map():
    global changed_tiles, visible_tiles

    if fov.fov_recompute:
        fov.fov_recompute = False
        libtcod.map_compute_fov(fov.fov_player, player.x, player.y, consts.TORCH_RADIUS, consts.FOV_LIGHT_WALLS, consts.FOV_ALGO)
        fov.player_fov_calculated = True
        new_visible = []
        for y in range(consts.MAP_HEIGHT):
            for x in range(consts.MAP_WIDTH):
                if libtcod.map_is_in_fov(fov.fov_player, x, y):
                    new_visible.append((x, y))
        for tile in new_visible:
            if tile not in visible_tiles:
                changed_tiles.append(tile)
        for tile in visible_tiles:
            if tile not in new_visible:
                changed_tiles.append(tile)
        visible_tiles = new_visible

    for tile in changed_tiles:
        x = tile[0]
        y = tile[1]
        visible = libtcod.map_is_in_fov(fov.fov_player, x, y)
        color_fg = libtcod.Color(dungeon_map[x][y].color_fg[0], dungeon_map[x][y].color_fg[1],
                                 dungeon_map[x][y].color_fg[2])
        color_bg = libtcod.Color(dungeon_map[x][y].color_bg[0], dungeon_map[x][y].color_bg[1],
                                 dungeon_map[x][y].color_bg[2])
        tint = clamp(1.0 + 0.25 * float(dungeon_map[x][y].elevation), 0.1, 2.0)
        libtcod.color_scale_HSV(color_fg, 1.0, tint)
        libtcod.color_scale_HSV(color_bg, 1.0, tint)
        if not visible:
            if dungeon_map[x][y].explored:
                libtcod.color_scale_HSV(color_fg, 0.1, 0.4)
                libtcod.color_scale_HSV(color_bg, 0.1, 0.4)
                libtcod.console_put_char_ex(map_con, x, y, dungeon_map[x][y].tile_char, color_fg, color_bg)
            else:
                libtcod.console_put_char_ex(map_con, x, y, ' ', libtcod.black, libtcod.black)
        else:
            libtcod.console_put_char_ex(map_con, x, y, dungeon_map[x][y].tile_char, color_fg, color_bg)
            dungeon_map[x][y].explored = True

    changed_tiles = []

    for obj in objects:
        if obj is not player:
            obj.draw(map_con)
    player.draw(map_con)

    libtcod.console_blit(map_con, player.x - consts.MAP_VIEWPORT_WIDTH / 2, player.y - consts.MAP_VIEWPORT_HEIGHT / 2,
                consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT, 0, consts.MAP_VIEWPORT_X, consts.MAP_VIEWPORT_Y)
    ui.draw_border(0, consts.MAP_VIEWPORT_X, consts.MAP_VIEWPORT_Y, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT)




def render_all():

    if not in_game:
        return

    libtcod.console_set_default_background(0, libtcod.black)
    libtcod.console_clear(0)

    render_map()

    ui.render_side_panel()

    ui.render_message_panel()

    ui.render_ui_overlay()

def generate_level():
    global dungeon_map, objects, stairs, spawned_bosses
    mapgen.make_map()
    fov.initialize_fov()


#############################################
# Initialization & Main Loop
#############################################

def main_menu():
    mapgen.load_features_from_file('features.txt')
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        libtcod.console_set_default_background(0, libtcod.black)
        libtcod.console_clear(0)
        libtcod.image_blit_2x(img, 0, 0, 0)
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT /2 - 8, libtcod.BKGND_NONE, libtcod.CENTER,
            'MAGIC-ROGUELIKE')
        libtcod.console_print_ex(0, consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER,
            'by Tyler Soberanis and Adrien Young')

        choice = ui.menu('', ['NEW GAME', 'CONTINUE', 'QUIT'], 24, x_center=consts.SCREEN_WIDTH / 2)
        
        if choice == 0: #new game
            new_game()
            play_game()
        elif choice == 1:
            try:
                load_game()
            except:
                ui.msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2:
            break
    

def new_game():
    global player, game_state, dungeon_level, memory, in_game, changed_tiles, learned_skills

    in_game = True

    #create object representing the player
    fighter_component = Fighter(hp=100, xp=0, stamina=100, death_function=player_death)
    player = GameObject(25, 23, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component, player_stats=PlayerStats(), description='You, the fearless adventurer!')
    player.level = 1
    
    #generate map
    dungeon_level = 1
    generate_level()
    #initialize_fov()
    game_state = 'playing'

    #item = GameObject(0, 0, '#', 'scroll of bullshit', libtcod.yellow, item=Item(use_function=spells.cast_fireball), description='the sword you started with')
    #waterbreathing = GameObject(0, 0, '!', 'potion of waterbreathing', libtcod.yellow, item=Item(use_function=spells.cast_waterbreathing), description='This potion allows the drinker to breath underwater for a short time.')
    #inventory.append(item)
    #inventory.append(waterbreathing)

    memory = []
    player.mana = []
    player.known_spells = [] #[spells.cast_manabolt]
    learned_skills = []
    player.action_queue = []
    # spell = GameObject(0, 0, '?', 'mystery spell', libtcod.yellow, item=Item(use_function=spells.cast_lightning, type="spell"))
    # memory.append(spell)

    #spawn_item('tome_manabolt', player.x, player.y)
    #spawn_item('tome_mend', player.x, player.y)
    #spawn_item('scroll_fireball', player.x, player.y)
    #spawn_item('equipment_pickaxe', player.x, player.y, material='iron', quality='')

    leather_armor = create_item('equipment_leather_armor')
    player.fighter.inventory.append(leather_armor)
    leather_armor.equipment.equip()
    dagger = create_item('equipment_dagger', material='iron', quality='')
    player.fighter.inventory.append(dagger)
    dagger.equipment.equip()

    if consts.DEBUG_STARTING_ITEM is not None:
        test = create_item(consts.DEBUG_STARTING_ITEM)
        player.fighter.inventory.append(test)

    selected_monster = None

    ui.message('Welcome to the dungeon...', libtcod.gold)

    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            changed_tiles.append((x, y))


def save_game():
    file = shelve.open('savegame', 'n')
    file['map'] = dungeon_map
    file['objects'] = objects
    file['player_index'] = objects.index(player)
    file['stairs_index'] = objects.index(stairs)
    file['memory'] = memory
    file['game_msgs'] = ui.game_msgs
    file['game_state'] = game_state
    file['dungeon_level'] = dungeon_level
    file['learned_skills'] = learned_skills
    file.close()


def load_game():
    global dungeon_map, objects, player, memory, game_state, dungeon_level, stairs, in_game, selected_monster, learned_skills

    in_game = True

    file = shelve.open('savegame', 'r')
    dungeon_map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]
    stairs = objects[file['stairs_index']]
    memory = file['memory']
    ui.game_msgs = file['game_msgs']
    game_state = file['game_state']
    dungeon_level = file['dungeon_level']
    selected_monster = None
    learned_skills = file['learned_skills']
    file.close()

    pathfinding.map.initialize(dungeon_map)
    fov.initialize_fov()

    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            changed_tiles.append((x, y))


def play_game():
    global key, mouse, game_state, in_game
    player_action = None
    
    mouse = libtcod.Mouse()
    key = libtcod.Key()
    while not libtcod.console_is_window_closed():

        # render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()
        libtcod.console_flush()
    
        # erase the map so it can be redrawn next frame
        #clear_map()

        # handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            in_game = False
            break

        if consts.RENDER_EVERY_TURN:
            render_all()
            libtcod.console_flush()

        # Let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            player.on_tick(object=player)
            for object in objects:
                if object.ai:
                    object.ai.take_turn()
                if object is not player:
                    object.on_tick(object=object)

        # Handle auto-targeting
        ui.auto_target_monster()


# my modules
import loot
import spells
import monsters
import dungeon
import mapgen
import abilities
import effects
import pathfinding
import fov
import ui
from ai import *

# Globals

# Libtcod initialization
libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT, 'Magic Roguelike', False)
libtcod.sys_set_fps(consts.LIMIT_FPS)

# Consoles
con = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
map_con = libtcod.console_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)

# Flags
in_game = False

# Graphics
changed_tiles = []
visible_tiles = []

# Level
dungeon_map = None