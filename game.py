import libtcodpy as libtcod
import math
import textwrap
import shelve
import consts
import terrain

#############################################
# Classes
#############################################

class Equipment:
    def __init__(self, slot, category, max_hp_bonus=0, attack_damage_bonus=0,
                 armor_bonus=0, evasion_bonus=0, spell_power_bonus=0, stamina_cost=0, str_requirement=0, shred_bonus=0,
                 guaranteed_shred_bonus=0, pierce=0):
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
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.orange)
        
    def dequip(self):
        self.is_equipped = False
        message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.orange)

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


        return print_height

class ConfusedMonster:
    def __init__(self, old_ai, num_turns=consts.CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns
        
    def act(self):
        if self.num_turns > 0:
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else:
            self.owner.ai.behavior = self.old_ai
            if libtcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y):
                message('The ' + self.owner.name + ' is no longer confused.', libtcod.light_grey)


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
                message('Your inventory is too full to pick up ' + self.owner.name)
            else:
                player.fighter.inventory.append(self.owner)
                self.owner.destroy()
                message('You picked up a ' + self.owner.name + '!', libtcod.light_grey)
                equipment = self.owner.equipment
                if equipment and get_equipped_in_slot(player.fighter.inventory,equipment.slot) is None:
                    equipment.equip()
        elif self.type == 'spell':
            if len(memory) >= player.player_stats.max_memory:
                message('You cannot hold any more spells in your memory!', libtcod.purple)
            else:
                memory.append(self.owner)
                self.owner.destroy()
                message(str(self.owner.name) + ' has been added to your memory.', libtcod.purple)
            
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
                message('You already know this spell.', libtcod.light_blue)
                return 'cancelled'
            else:
                player.known_spells.append(spell)
                message('You have mastered ' + spell.name + '!', libtcod.light_blue)
                player.fighter.inventory.remove(self.owner)
        else:
            message('The ' + self.owner.name + ' cannot be used.')

                
    def drop(self):
        if self.owner.equipment:
            self.owner.equipment.dequip();
        objects.append(self.owner)
        player.fighter.inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', libtcod.white)

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

    def __init__(self, hp=1, defense=0, power=0, xp=0, stamina=0, armor=0, evasion=0, accuracy=1.0, attack_damage=1,
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
            libtcod.console_print(window, x + 10, y + print_height, '(%d)' % (self.armor + self.shred))
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
        if hasattr(self.owner, 'mana') and self is not player:
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

    def attack(self, target):
        stamina_cost = 0
        if self.owner is player:
            stamina_cost = consts.UNARMED_STAMINA_COST / (self.owner.player_stats.str / consts.UNARMED_STAMINA_COST)
            if get_equipped_in_slot(self.inventory, 'right hand') is not None:
                stamina_cost = int((float(get_equipped_in_slot(self.inventory, 'right hand').stamina_cost) /
                                    (float(self.owner.player_stats.str) / float(get_equipped_in_slot(self.inventory, 'right hand').str_requirement))))
        return self.attack_ex(target, stamina_cost, self.accuracy, self.attack_damage, self.damage_variance, self.on_hit,
                       'attacks', self.attack_shred, self.attack_guaranteed_shred, self.attack_pierce)

    def attack_ex(self, target, stamina_cost, accuracy, attack_damage, damage_variance, on_hit, verb, shred, guaranteed_shred, pierce):
        # check stamina
        if self.owner.name == 'player':
            if self.stamina < stamina_cost:
                message("You can't find the strength to swing your weapon!", libtcod.light_yellow)
                return 'failed'
            else:
                self.adjust_stamina(-stamina_cost)

        if roll_to_hit(target, accuracy):
            # Target was hit
            damage = attack_damage * (1.0 - damage_variance + libtcod.random_get_float(0, 0, 2 * damage_variance))
            # calculate damage reduction
            effective_armor = target.fighter.armor - pierce
            # without armor, targets receive no damage reduction!
            if effective_armor > 0:
                # Damage is reduced by 25% + 5% for every point of armor up to 5 armor (50% reduction)
                reduction_factor = consts.ARMOR_REDUCTION_BASE + consts.ARMOR_REDUCTION_STEP * min(effective_armor, consts.ARMOR_REDUCTION_DROPOFF)
                # For every point of armor after 5, damage is further reduced by 2.5%
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
                    if libtcod.random_get_int(0, 0, 2) == 0 and target.fighter.shred < target.fighter.armor:
                        target.fighter.shred += 1
                target.fighter.shred = min(target.fighter.shred + guaranteed_shred, target.fighter.armor)
                # Take damage
                message(self.owner.name.capitalize() + ' ' + verb + ' ' + target.name + ' for ' + str(damage) + ' damage!', libtcod.grey)
                target.fighter.take_damage(damage)
                return 'hit'
            else:
                message(self.owner.name.capitalize() + ' ' + verb + ' ' + target.name + ', but the attack is deflected!', libtcod.grey)
                return 'blocked'
        else:
            message(self.owner.name.capitalize() + ' ' + verb + ' ' + target.name + ', but misses!', libtcod.grey)
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
                message('You repair your armor')

        # Manage breath/drowning
        if dungeon_map[self.owner.x][self.owner.y].tile_type == 'deep water':
            if not (self.can_breath_underwater or self.has_status('waterbreathing')):
                if self.breath > 0:
                    self.breath -= 1
                else:
                    drown_damage = int(self.max_hp / 4)
                    message('The ' + self.owner.name + ' drowns, suffering ' + str(drown_damage) + ' damage!',
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

    def apply_status_effect(self, new_effect):
        # check for immunity
        for resist in self.resistances:
            if resist == new_effect.name:
                if libtcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y):
                    message('The ' + self.owner.name + ' resists.', libtcod.gray)
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
            message(new_effect.message,new_effect.color)
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
        return self.base_accuracy

    @property
    def damage_variance(self):
        return self.base_damage_variance

    @property
    def attack_damage(self):
        bonus = sum(equipment.attack_damage_bonus for equipment in get_all_equipped(self.inventory))
        if self.owner.player_stats:
            return self.base_attack_damage + self.owner.player_stats.str + bonus
        else:
            return self.base_attack_damage + bonus

    @property
    def armor(self):
        bonus = sum(equipment.armor_bonus for equipment in get_all_equipped(self.inventory))
        return self.base_armor + bonus - self.shred

    @property
    def attack_shred(self):
        bonus = sum(equipment.shred_bonus for equipment in get_all_equipped(self.inventory))
        return self.base_shred + bonus

    @property
    def attack_guaranteed_shred(self):
        bonus = sum(equipment.guaranteed_shred_bonus for equipment in get_all_equipped(self.inventory))
        return self.base_guaranteed_shred + bonus

    @property
    def attack_pierce(self):
        bonus = sum(equipment.pierce_bonus for equipment in get_all_equipped(self.inventory))
        return self.base_pierce + bonus

    @property
    def evasion(self):
        bonus = sum(equipment.evasion_bonus for equipment in get_all_equipped(self.inventory))
        if self.owner.player_stats:
            return self.base_evasion + self.owner.player_stats.agi + bonus
        else:
            return self.base_evasion + bonus

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

class AI_Default:

    def __init__(self):
        self.last_seen_position = None

    def act(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            #Handle default ability use behavior
            for a in self.owner.fighter.abilities:
                if a.current_cd <= 0:
                    #Use abilities when they're up
                    a.use(self.owner)
                    return


            #Handle moving
            if not is_adjacent_diagonal(monster.x, monster.y, player.x, player.y):
                monster.move_astar(player.x, player.y)

            #Handle attacking
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)
            self.last_seen_position = (player.x, player.y)
        elif self.last_seen_position is not None and not\
                (self.last_seen_position[0] == monster.x and self.last_seen_position[1] == monster.y):
            monster.move_astar(self.last_seen_position[0], self.last_seen_position[1])


class ReekerGasBehavior:
    def __init__(self):
        self.ticks = consts.REEKER_PUFF_DURATION

    def on_tick(self, object=None):
        self.ticks -= 1
        if self.ticks == consts.REEKER_PUFF_DURATION * 2 / 3:
            self.owner.char = libtcod.CHAR_BLOCK2
        elif self.ticks == consts.REEKER_PUFF_DURATION / 3:
            self.owner.char = libtcod.CHAR_BLOCK1
        elif self.ticks <= 0:
            self.owner.destroy()
            return
        #self.owner.char = str(self.ticks)
        for obj in objects:
            if obj.x == self.owner.x and obj.y == self.owner.y and obj.fighter:
                if obj.name != 'reeker':
                    if self.ticks >= consts.REEKER_PUFF_DURATION - 1:
                        if libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
                            message('A foul-smelling cloud of gas begins to form around the ' + obj.name, libtcod.fuchsia)
                    else:
                        obj.fighter.take_damage(consts.REEKER_PUFF_DAMAGE)
                        if libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
                            message('The ' + obj.name + ' chokes on the foul gas.', libtcod.fuchsia)

class FireBehavior:
    def __init__(self,temp):
        self.temperature = temp

    def on_tick(self, object=None):
        if self.temperature > 8:
            self.owner.color = libtcod.Color(255,244,247)
        elif self.temperature > 6:
            self.owner.color = libtcod.Color(255,219,20)
        elif self.temperature > 4:
            self.owner.color = libtcod.Color(250,145,20)
        elif self.temperature > 2:
            self.owner.color = libtcod.Color(232,35,0)
        else:
            self.owner.color = libtcod.Color(100,100,100)

        self.temperature -= 1
        if self.temperature == 0:
            self.owner.destroy()
        else:
            for obj in objects:
                if obj.x == self.owner.x and obj.y == self.owner.y and obj.fighter:
                    obj.fighter.apply_status_effect(effects.burning())
            # Spread to adjacent tiles
            if self.temperature < 9: # don't spread on the first turn
                for tile in adjacent_tiles_diagonal(self.owner.x, self.owner.y):
                    if dungeon_map[tile[0]][tile[1]].flammable:
                        if libtcod.random_get_int(0, 0, 8) == 0:
                            create_fire(tile[0], tile[1], 10)

class AI_Reeker:

    def act(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            for i in range(consts.REEKER_PUFF_MAX):
                if libtcod.random_get_int(0, 0, 10) < 3:
                    # create puff
                    position = random_position_in_circle(consts.REEKER_PUFF_RADIUS)
                    puff_pos = (clamp(monster.x + position[0], 1, consts.MAP_WIDTH - 2),
                                clamp(monster.y + position[1], 1, consts.MAP_HEIGHT - 2))
                    if not dungeon_map[puff_pos[0]][puff_pos[1]].blocks and object_at_tile(puff_pos[0], puff_pos[1], 'reeker gas') is None:
                        puff = GameObject(monster.x + position[0], monster.y + position[1], libtcod.CHAR_BLOCK3,
                                          'reeker gas', libtcod.dark_fuchsia, description='a puff of reeker gas',
                                          misc=ReekerGasBehavior())
                        objects.append(puff)

class AI_TunnelSpider:

    def __init__(self):
        self.closest_web = None
        self.state = 'resting'
        self.last_seen_position = None

    def act(self):
        monster = self.owner
        if self.state == 'resting':
            if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
                self.state = 'hunting'
                self.act()
            elif object_at_tile(monster.x, monster.y, 'spiderweb') is None:
                self.state = 'retreating'
                self.act()
        elif self.state == 'retreating':
            self.closest_web = self.find_closest_web()
            if self.closest_web is None:
                self.state = 'hunting'
                self.act()
            else:
                monster.move_astar(self.closest_web.x, self.closest_web.y)
                if object_at_tile(monster.x, monster.y, 'spiderweb') is not None:
                    self.state = 'resting'
        elif self.state == 'hunting':
            if is_adjacent_diagonal(monster.x, monster.y, player.x, player.y) and player.fighter.hp > 0:
                monster.fighter.attack(player)
                return
            self.closest_web = self.find_closest_web()
            if self.closest_web is not None and monster.distance_to(self.closest_web) > consts.TUNNEL_SPIDER_MAX_WEB_DIST:
                self.state = 'retreating'
                self.act()
            elif libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
                    monster.move_astar(player.x, player.y)
                    self.last_seen_position = (player.x, player.y)
            elif self.last_seen_position is not None and not \
                    (self.last_seen_position[0] == monster.x and self.last_seen_position[1] == monster.y):
                monster.move_astar(self.last_seen_position[0], self.last_seen_position[1])

    def find_closest_web(self):
        closest_web = None
        closest_dist = consts.TUNNEL_SPIDER_MAX_WEB_DIST
        for obj in objects:
            if obj.name == 'spiderweb':
                if closest_web is None or self.owner.distance_to(obj) < closest_dist:
                    closest_web = obj
                    closest_dist = self.owner.distance_to(obj)
        return closest_web


class AI_General:
    def __init__(self, speed=1.0, behavior=AI_Default()):
        self.turn_ticker = 0.0
        self.speed = speed
        self.behavior = behavior

    def take_turn(self):
        self.turn_ticker += self.speed
        while self.turn_ticker > 1.0:
            if not (self.owner.fighter and (self.owner.fighter.has_status('stunned') or self.owner.fighter.has_status('frozen'))):
                self.behavior.act()
            self.turn_ticker -= 1.0


class GameObject:

    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None, equipment=None,
                 player_stats=None, always_visible=False, interact=None, description=None, on_create=None,
                 update_speed=1.0, misc=None, blocks_sight=False, on_step=None, burns=False, on_tick=None):
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
            libtcod.map_set_properties(fov_map, self.x, self.y, not self.blocks_sight, True)

    def set_position(self, x, y):
        global changed_tiles
        changed_tiles.append((self.x, self.y))
        if self.blocks_sight:
            libtcod.map_set_properties(fov_map, self.x, self.y, not dungeon_map[self.x][self.y].blocks_sight, True)
            libtcod.map_set_properties(fov_map, x, y, False, True)
            fov_recompute_fn()
        self.x = x
        self.y = y
        stepped_on = get_objects(self.x, self.y, lambda o: o.on_step)
        if len(stepped_on) > 0:
            for obj in stepped_on:
                obj.on_step(obj, self)

    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):
            if self.fighter is not None:
                if self.fighter.has_status('immobilized'):
                    return True
                web = object_at_tile(self.x, self.y, 'spiderweb')
                if web is not None and not self.name == 'tunnel spider':
                    message('The ' + self.name + ' struggles against the web.')
                    web.destroy()
                    return True
                cost = dungeon_map[self.x][self.y].stamina_cost
                if cost > 0 and self is player: # only the player cares about stamina costs (at least for now. I kind of like it this way) -T
                    if self.fighter.stamina >= cost:
                        self.fighter.adjust_stamina(-cost)
                    else:
                        message("You don't have the stamina leave this space!", libtcod.light_yellow)
                        return False
                else:
                    self.fighter.adjust_stamina(consts.STAMINA_REGEN_MOVE)     # gain stamina for moving across normal terrain

            self.set_position(self.x + dx, self.y + dy)
            return True

    # Unused
    def draw_old(self):
        offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2, player.y - consts.MAP_VIEWPORT_HEIGHT / 2
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            if selected_monster is self:
                libtcod.console_put_char_ex(map_con, self.x - offsetx, self.y - offsety, self.char, libtcod.black, self.color)
            else:
                libtcod.console_set_default_foreground(map_con, self.color)
                libtcod.console_put_char(map_con, self.x - offsetx, self.y - offsety, self.char, libtcod.BKGND_NONE)
        elif self.always_visible and dungeon_map[self.x][self.y].explored:
            shaded_color = libtcod.Color(self.color[0], self.color[1], self.color[2])
            libtcod.color_scale_HSV(shaded_color, 0.1, 0.4)
            libtcod.console_set_default_foreground(map_con, shaded_color)
            libtcod.console_put_char(map_con, self.x - offsetx, self.y - offsety, self.char, libtcod.BKGND_NONE)

    def draw(self, console):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            if selected_monster is self:
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
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)
        
    def move_astar(self, target_x, target_y):

        if self.x == target_x and self.y == target_y:
            return

        fov = libtcod.map_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)
        
        # Scan the map and set all walls to unwalkable
        for y1 in range(consts.MAP_HEIGHT):
            for x1 in range(consts.MAP_WIDTH):
                libtcod.map_set_properties(fov, x1, y1, not dungeon_map[x1][y1].blocks_sight, not dungeon_map[x1][y1].blocks)
        
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
            libtcod.map_set_properties(fov_map, self.x, self.y, not dungeon_map[self.x][self.y].blocks_sight, True)
            fov_recompute_fn()
        changed_tiles.append((self.x, self.y))
        objects.remove(self)


class Tile:
    
    def __init__(self, tile_type='stone floor'):
        self.explored = False
        self.tile_type = tile_type

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

                
#############################################
# General Functions
#############################################

def expire_out_of_vision(obj):
    if not libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
        obj.destroy()

def pick_up_mana(mana, obj):
    if obj is player and len(player.mana) < player.player_stats.max_mana:
        player.mana.append(mana.mana_type)
        message('You are infused with magical power.', mana.color)
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
    global selected_monster

    blastcap.fighter = None
    message('The blastcap explodes with a BANG, stunning nearby creatures!', libtcod.gold)
    for obj in objects:
        if obj.fighter and is_adjacent_orthogonal(blastcap.x, blastcap.y, obj.x, obj.y):
            if obj.fighter.apply_status_effect(effects.StatusEffect('stunned', consts.BLASTCAP_STUN_DURATION, libtcod.light_yellow)):
                message('The ' + obj.name + ' is stunned!', libtcod.gold)

    if selected_monster is blastcap:
        selected_monster = None
        auto_target_monster()

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

# This function exists so files outside game.py can modify this global variable.
# Hopefully there's a better way to do this    -T
def fov_recompute_fn():
    global fov_recompute
    fov_recompute = True


def roll_to_hit(target,  accuracy):
    return libtcod.random_get_float(0, 0, 1) < get_chance_to_hit(target, accuracy)

def get_chance_to_hit(target, accuracy):
    if target.fighter.has_status('stunned'):
        return 1.0
    return max(min((consts.EVADE_FACTOR / (consts.EVADE_FACTOR + target.fighter.evasion)) * accuracy, 1.0), 0)

def random_position_in_circle(radius):
    r = libtcod.random_get_float(0, 0.0, float(radius))
    theta = libtcod.random_get_float(0, 0.0, 2.0 * math.pi)
    return (int(round(r * math.cos(theta))), int(round(r * math.sin(theta))))

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
    player.level += 1
    message('You grow stronger! You have reached level ' + str(player.level) + '!', libtcod.green)
    choice = None
    while choice == None:
        choice = menu('Level up! Choose a stat to raise:\n',
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

    if altar:
        altar.destroy()


def next_level():
    global dungeon_level, changed_tiles

    message('You descend...', libtcod.white)
    dungeon_level += 1
    generate_level()
    initialize_fov()

    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            changed_tiles.append((x, y))


def player_death(player):
    global game_state
    message('You\'re dead, sucka.', libtcod.grey)
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
        message('The bomb beetle corpse explodes!', libtcod.orange)
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
    global selected_monster

    if beetle.fighter.loot_table is not None:
        drop = get_loot(beetle.fighter)
        if drop:
            objects.append(drop)
            drop.send_to_back()

    message(beetle.name.capitalize() + ' is dead!', libtcod.red)
    beetle.char = 149
    beetle.color = libtcod.black
    beetle.blocks = True
    beetle.fighter = None
    beetle.ai = None
    beetle.name = 'beetle bomb'
    beetle.description = 'The explosive carapace of a blast beetle. In a few turns, it will explode!'
    beetle.bomb_timer = 3
    beetle.on_tick = bomb_beetle_corpse_tick

    if selected_monster is beetle:
        selected_monster = None
        auto_target_monster()


def monster_death(monster):
    global selected_monster, changed_tiles

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


    message(monster.name.capitalize() + ' is dead!', libtcod.red)
    monster.char = '%'
    monster.color = libtcod.darker_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()

    if selected_monster is monster:
        changed_tiles.append((monster.x, monster.y))
        selected_monster = None
        auto_target_monster()


def target_monster(max_range=None):
    while True:
        (x, y) = target_tile(max_range)
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
        menu_choice = menu("Which object?", [o.name for o in ops], 40)
        if menu_choice is not None:
            return ops[menu_choice]
        else:
            return None
    elif len(ops) == 0:
        return dungeon_map[x][y]
    else:
        return ops[0]


def target_tile(max_range=None, targeting_type='pick', acc_mod=1.0, default_target=None):
    global key, mouse, selected_monster

    if default_target is None:
        x = player.x
        y = player.y
    else:
        x = default_target[0]
        y = default_target[1]
    cursor_x = x
    cursor_y = y
    oldMouseX = mouse.cx
    oldMouseY = mouse.cy
    offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2, player.y - consts.MAP_VIEWPORT_HEIGHT / 2
    selected_x = x
    selected_y = y

    while True:
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_map()
        render_side_panel(acc_mod=acc_mod)

        # Render range shading
        libtcod.console_clear(ui)
        libtcod.console_set_key_color(ui, libtcod.magenta)
        if max_range is not None:
            for draw_x in range(consts.MAP_WIDTH):
                for draw_y in range(consts.MAP_HEIGHT):
                    if round((player.distance(draw_x + offsetx, draw_y + offsety))) > max_range:
                        libtcod.console_put_char_ex(ui, draw_x, draw_y, ' ', libtcod.light_yellow, libtcod.black)
                    else:
                        libtcod.console_put_char_ex(ui, draw_x, draw_y, ' ', libtcod.light_yellow, libtcod.magenta)
            libtcod.console_blit(ui, 0, 0, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT, 0, consts.MAP_VIEWPORT_X, consts.MAP_VIEWPORT_Y, 0, 0.2)
        # Render cursor
        libtcod.console_set_default_background(ui, libtcod.magenta)
        libtcod.console_clear(ui)
        if targeting_type == 'beam' or targeting_type == 'beam_interrupt':
            libtcod.line_init(player.x, player.y, cursor_x, cursor_y)
            line_x, line_y = libtcod.line_step()
            while (not line_x is None):
                libtcod.console_put_char_ex(ui, line_x - offsetx, line_y - offsety, ' ', libtcod.white, libtcod.yellow)
                line_x, line_y = libtcod.line_step()
        libtcod.console_put_char_ex(ui, selected_x - offsetx, selected_y - offsety, ' ', libtcod.light_yellow, libtcod.white)

        libtcod.console_blit(ui, 0, 0, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT, 0, consts.MAP_VIEWPORT_X, consts.MAP_VIEWPORT_Y, 0, 0.5)


        if key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            x -= 1
        if key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            x += 1
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            y -= 1
        if key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            y += 1
        if key.vk == libtcod.KEY_KP7:
            x -= 1
            y -= 1
        if key.vk == libtcod.KEY_KP9:
            x += 1
            y -= 1
        if key.vk == libtcod.KEY_KP1:
            x -= 1
            y += 1
        if key.vk == libtcod.KEY_KP3:
            x += 1
            y += 1

        if oldMouseX != mouse.cx or oldMouseY != mouse.cy:
            x, y = mouse.cx + offsetx - consts.MAP_VIEWPORT_X, mouse.cy + offsety - consts.MAP_VIEWPORT_Y

        cursor_x = x
        cursor_y = y

        monster_at_tile = get_monster_at_tile(cursor_x, cursor_y)
        if monster_at_tile is not None:
            selected_monster = monster_at_tile

        selected_x = cursor_x
        selected_y = cursor_y
        beam_values = []

        if targeting_type == 'beam_interrupt':
            selected_x, selected_y = beam_interrupt(player.x, player.y, cursor_x, cursor_y)
        elif targeting_type == 'beam':
            beam_values = beam(player.x, player.y, cursor_x, cursor_y)
            selected_x, selected_y = beam_values[len(beam_values) - 1]

        if (mouse.lbutton_pressed or key.vk == libtcod.KEY_ENTER) and libtcod.map_is_in_fov(fov_map, x, y):
            if max_range is None or round((player.distance(x, y))) <= max_range:
                if targeting_type == 'beam':
                    return beam_values
                else:
                    return selected_x, selected_y
            else:
                return None, None  # out of range
            
        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return None, None  # cancelled

        oldMouseX = mouse.cx
        oldMouseY = mouse.cy


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
        if is_blocked(line_x, line_y):  # beam interrupt scans until it hits something
            return line_x, line_y
        line_x, line_y = libtcod.line_step()
    return destx, desty


def closest_monster(max_range):
    closest_enemy = None
    closest_dist = max_range + 1

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            dist = player.distance_to(object)
            if dist < closest_dist:
                closest_dist = dist
                closest_enemy = object
    return closest_enemy


def inventory_menu(header):

    libtcod.console_clear(window)
    render_all()
    libtcod.console_flush()

    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print(window, 1, 1, header)
    y = 3
    letter_index = ord('a')
    menu_items = []
    item_categories = []

    if len(player.fighter.inventory) == 0:
        height = 5
        draw_border(window, 0, 0, consts.INVENTORY_WIDTH, height)
        libtcod.console_set_default_foreground(window, libtcod.dark_grey)
        libtcod.console_print(window, 1, 3, 'Inventory is empty.')
    else:
        for item in player.fighter.inventory:
            if not item.item.category in item_categories:
                item_categories.append(item.item.category)
        height = 4 + len(item_categories) + len(player.fighter.inventory)
        draw_border(window, 0, 0, consts.INVENTORY_WIDTH, height)

        for item_category in loot.item_categories:
            if not item_category in item_categories:
                continue
            libtcod.console_set_default_foreground(window, libtcod.gray)
            for i in range(consts.INVENTORY_WIDTH):
                libtcod.console_put_char(window, i, y, libtcod.CHAR_HLINE)
            libtcod.console_put_char(window, 0, y, 199)
            libtcod.console_put_char(window, consts.INVENTORY_WIDTH - 1, y, 182)
            libtcod.console_print_ex(window, consts.INVENTORY_WIDTH / 2, y, libtcod.BKGND_DEFAULT, libtcod.CENTER,
                                     loot.item_categories[item_category]['plural'].capitalize())
            y += 1
            for item in player.fighter.inventory:
                if item.item.category == item_category:
                    menu_items.append(item)

                    libtcod.console_set_default_foreground(window, libtcod.white)
                    libtcod.console_print(window, 1, y, '(' + chr(letter_index) + ') ')
                    libtcod.console_put_char_ex(window, 5, y, item.char, item.color, libtcod.black)
                    libtcod.console_print(window, 7, y, item.name.capitalize())

                    if item.equipment and item.equipment.is_equipped:
                        libtcod.console_set_default_foreground(window, libtcod.orange)
                        libtcod.console_print_ex(window, consts.INVENTORY_WIDTH - 2, y, libtcod.BKGND_DEFAULT,
                                                 libtcod.RIGHT, '[E]')
                    y += 1
                    letter_index += 1

    x = consts.MAP_VIEWPORT_X + 1
    y = consts.MAP_VIEWPORT_Y + 1
    libtcod.console_blit(window, 0, 0, consts.INVENTORY_WIDTH, height, 0, x, y, 1.0, 1.0)
    libtcod.console_flush()

    key = libtcod.console_wait_for_keypress(True)
    index = key.c - ord('a')
    if 0 <= index < len(player.fighter.inventory):
        return menu_items[index].item
    return None


def msgbox(text, width=50):
    menu(text, [], width)


def menu(header, options, width, x_center=None, render_func=None):
    global window

    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    no_header = False
    header_height = libtcod.console_get_height_rect(con, 0, 0, width - 2, consts.SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
        no_header = True

    height = len(options) + header_height + 2
    if not no_header:
        height += 1
    width += 2

    libtcod.console_clear(window)
    render_all()
    libtcod.console_flush()


    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 1, 1, width - 2, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    y = header_height + 1
    if not no_header:
        y += 1

    if render_func is not None:
        h = render_func(window, 1, y, width)
        y += h + 1
        height += h + 1


    letter_index = ord('a')
    
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    draw_border(window, 0, 0, width, height)

    if x_center is None:
        x = consts.MAP_VIEWPORT_X + consts.MAP_VIEWPORT_WIDTH / 2 - width / 2
    else:
        x = x_center - width / 2
    y = consts.SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 1.0)
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)
    
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None


def auto_target_monster():
    global selected_monster

    if selected_monster is None:
        monster = closest_monster(consts.TORCH_RADIUS)
        if monster is not None:
            selected_monster = monster
    elif not libtcod.map_is_in_fov(fov_map, selected_monster.x, selected_monster.y):
        selected_monster = None


def target_next_monster():
    global selected_monster, changed_tiles

    if selected_monster is not None:
        changed_tiles.append((selected_monster.x, selected_monster.y))

    nearby = []
    for obj in objects:
        if libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and obj.fighter and obj is not player:
            nearby.append((obj.distance_to(player), obj))
    nearby.sort(key=lambda m: m[0])

    if len(nearby) == 0:
        selected_monster = None
        return
    else:
        i = 0
        while nearby[i][1] is not selected_monster:
            i += 1
        if i + 1 == len(nearby):
            selected_monster = nearby[0][1]
            return
        else:
            selected_monster = nearby[i + 1][1]
            return


def mouse_select_monster():
    global mouse, selected_monster

    if mouse.lbutton_pressed:
        offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2 - consts.MAP_VIEWPORT_X, \
                           player.y - consts.MAP_VIEWPORT_HEIGHT / 2 - consts.MAP_VIEWPORT_Y
        (x, y) = (mouse.cx + offsetx, mouse.cy + offsety)

        monster = None
        for obj in objects:
            if obj.x == x and obj.y == y and (libtcod.map_is_in_fov(fov_map, obj.x, obj.y) or (obj.always_visible and dungeon_map[obj.x][obj.y].explored)):
                if hasattr(obj, 'fighter') and obj.fighter and not obj is player:
                    monster = obj
                    break
        selected_monster = monster


def get_names_under_mouse():

    global mouse, selected_monster

    offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2 - consts.MAP_VIEWPORT_X,\
                       player.y - consts.MAP_VIEWPORT_HEIGHT / 2 - consts.MAP_VIEWPORT_Y
    (x, y) = (mouse.cx + offsetx, mouse.cy + offsety)

    names = [obj.name for obj in objects if (obj.x == x and obj.y == y and (libtcod.map_is_in_fov(fov_map, obj.x, obj.y)
                            or (obj.always_visible and dungeon_map[obj.x][obj.y].explored)))]
    names = ', '.join(names)

    return names.capitalize()


def message(new_msg, color = libtcod.white):
    new_msg_lines = textwrap.wrap(new_msg, consts.MSG_WIDTH)
    
    for line in new_msg_lines:
        if len(game_msgs) == consts.MSG_HEIGHT:
            del game_msgs[0]
        game_msgs.append((line, color))


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color, align=libtcod.CENTER):
    bar_width = int(float(value) / maximum * total_width)
    
    libtcod.console_set_default_background(side_panel, back_color)
    libtcod.console_rect(side_panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(side_panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(side_panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
        
    libtcod.console_set_default_foreground(side_panel, libtcod.white)
    pos = x + 1
    if align == libtcod.LEFT:
        pos = x + 1
    elif align == libtcod.CENTER:
        pos = x + total_width / 2
    elif align == libtcod.RIGHT:
        pos = x + total_width - 1
    libtcod.console_print_ex(side_panel, pos, y, libtcod.BKGND_NONE, align,
                             name + ': ' + str(value) + '/' + str(maximum))


def is_blocked(x, y):
    if dungeon_map[x][y].blocks:
        return True
        
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
            
    return False


def get_room_spawns(room):
    return [[k, libtcod.random_get_int(0, v[0], v[1])] for (k, v) in room['spawns'].items()]


def spawn_monster(name, x, y):
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
        objects.append(monster)
        return monster
    return None

def spawn_monster_inventory(proto):
    result = []
    if proto:
        for slot in proto:
            equip = random_choice(slot)
            if equip != 'none':
                result.append(create_item(equip))
    return result

def create_ability(name):
    if name in abilities.data:
        a = abilities.data[name]
        return abilities.Ability(a.get('name'), a.get('description'), a['function'], a.get('cooldown'))
    else:
        return None

def create_item(name):
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
            pierce=p.get('pierce', 0)
        )
    go = GameObject(0, 0, p['char'], p['name'], p.get('color', libtcod.white), item=item_component,
                      equipment=equipment_component, always_visible=True, description=p.get('description'))
    if ability is not None:
        go.item.ability = ability
    return go

def spawn_item(name, x, y):
        item = create_item(name)
        item.x = x
        item.y = y
        objects.append(item)
        item.send_to_back()

def create_fire(x,y,temp):
    global changed_tiles

    if dungeon_map[x][y].tile_type == 'shallow water' or \
                    dungeon_map[x][y].tile_type == 'deep water' or is_blocked(x, y):
        return
    component = FireBehavior(temp)
    obj = GameObject(x,y,'^','Fire',libtcod.red,misc=component)
    objects.append(obj)
    if temp > 4:
        dungeon_map[x][y] = Tile('scorched floor')
    for obj in get_objects(x, y, condition=lambda o: o.burns):
        obj.destroy()
    changed_tiles.append((x, y))

def place_objects(tiles):
    if len(tiles) == 0:
        return
    max_items = from_dungeon_level([[1, 1], [2, 4], [4, 7]])
    item_chances = {'potion_healing':70, 'scroll_lightning':10, 'scroll_confusion':10, 'scroll_fireball':10 }
    item_chances['equipment_longsword'] = 25
    item_chances['equipment_shield'] = 25

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
            choice = random_choice(item_chances)
            spawn_item(choice, random_pos[0], random_pos[1])
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


def player_move_or_attack(dx, dy, bash=False):
    global selected_monster, changed_tiles

    x = player.x + dx
    y = player.y + dy
    
    target = None
    for object in objects:
        if object.x == x and object.y == y and object.fighter is not None:
            target = object
            break
            
    if target is not None:
        if bash:
            success = player_bash_attack(target) != 'failed'
        else:
            success = player.fighter.attack(target) != 'failed'
        if success and target.fighter and target is not selected_monster:
            changed_tiles.append((target.x, target.y))
            selected_monster = target
        return success
    else:
        value = player.move(dx, dy)
        fov_recompute_fn()
        return value


def player_bash_attack(target):
    result = player.fighter.attack_ex(target, consts.BASH_STAMINA_COST, player.fighter.accuracy * consts.BASH_ACC_MOD,
                             player.fighter.attack_damage * consts.BASH_DMG_MOD, player.fighter.damage_variance,
                             None, 'bashes', player.fighter.attack_shred + 1, player.fighter.attack_guaranteed_shred,
                             player.fighter.attack_pierce)
    if result == 'hit' and target.fighter:
        # knock the target back one space. Stun it if it cannot move.
        direction = target.x - player.x, target.y - player.y  # assumes the player is adjacent
        stun = False
        against = ''
        if dungeon_map[target.x + direction[0]][target.y + direction[1]].blocks:
            stun = True
            against = dungeon_map[target.x + direction[0]][target.y + direction[1]].name
        else:
            for obj in objects:
                if obj.x == target.x + direction[0] and obj.y == target.y + direction[1] and obj.blocks:
                    stun = True
                    against = obj.name
                    break

        if stun:
            #  stun the target
            if target.fighter.apply_status_effect(effects.StatusEffect('stunned', time_limit=2, color=libtcod.light_yellow)):
                message('The ' + target.name + ' collides with the ' + against + ', stunning it!', libtcod.gold)
        else:
            message('The ' + target.name + ' is knocked backwards.', libtcod.gray)
            target.set_position(target.x + direction[0], target.y + direction[1])
            render_map()
            libtcod.console_flush()

    return result


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
            message('You have finished meditating. You are infused with magical power.', libtcod.dark_cyan)
            return
        elif manatype != 'normal':
            for i in range(len(player.mana)):
                if player.mana[i] == 'normal':
                    player.mana[i] = manatype
                    message('You have finished meditating. You are infused with magical power.', libtcod.dark_cyan)
                    return
        message('You have finished meditating. You were unable to gain any more power than you already have.', libtcod.dark_cyan)
        return

def show_ability_screen():
    opts = []
    for a in abilities.default_abilities:
        opts.append(a)
    for i in player.fighter.inventory:
        if i.item.ability is not None:
            opts.append(i.item.ability)
    index = menu('Abilities',[opt.name for opt in opts],20)
    if index is not None:
        choice = opts[index]
        if choice is not None:
            return choice.use(player)
    return 'didnt-take-turn'

def handle_keys():
 
    global game_state, stairs, selected_monster
    global key
    
    # key = libtcod.console_check_for_keypress()  #real-time
    # key = libtcod.console_wait_for_keypress(True)  #turn-based

    mouse_select_monster()

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
                return inspect_inventory()
            if key_char == 'u':
                chosen_item = inventory_menu('Use which item?')
                if chosen_item is not None:
                    use_result = chosen_item.use()
                    if use_result == 'cancelled':
                       return 'didnt-take-turn'
                    else:
                       return 'used-item'
            if key_char == 'd':
                chosen_item = inventory_menu('Drop which item?')
                if chosen_item is not None:
                    chosen_item.drop()
                    return 'dropped-item'
            if key_char == ',' and key.shift:
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()
            if key_char == 'c':
                msgbox('Character Information\n\nLevel: ' + str(player.level) + '\n\nMaximum HP: ' +
                       str(player.fighter.max_hp) + '\nAttack: ' + str(player.fighter.power) + '\nDefense: ' +
                       str(player.fighter.defense),
                       consts.CHARACTER_SCREEN_WIDTH)
            if key_char == 'z':
                return cast_spell_new()
                #if key.shift:
                #    return cast_spell_new()
                #else:
                #    if len(memory) == 0:
                #        message('You have no spells in your memory to cast.', libtcod.purple)
                #    elif dungeon_map[player.x][player.y].tile_type == 'deep water':
                #        message('You cannot cast spells underwater.', libtcod.purple)
                #    else:
                #        cast_spell()
                #        return 'casted-spell'
            if key_char == 'j':
                return jump()
            if key_char == 'e':
                examine()
            if key.vk == libtcod.KEY_TAB:
                target_next_monster()
            if key_char == 'm':
                return meditate()
            if key_char == 'a':
                return show_ability_screen()
            if key_char == 'l': # TEMPORARY
                skill_menu()
                return 'didnt-take-turn'
            return 'didnt-take-turn'
        if not moved:
            return 'didnt-take-turn'


def skill_menu():
    global key, mouse

    scroll_height = 0
    selected_index = 1

    libtcod.console_clear(window)
    render_all()
    libtcod.console_flush()

    skill_categories = []
    menu_lines = []

    for skill in abilities.skill_list:
        if not skill.category in skill_categories:
            skill_categories.append(skill.category)
            menu_lines.append(None)
        menu_lines.append(skill)
    sub_height = len(skill_categories) + len(abilities.skill_list)
    scroll_limit = sub_height - (consts.MAP_VIEWPORT_HEIGHT - 10)

    sub_window = libtcod.console_new(consts.MAP_VIEWPORT_WIDTH, sub_height)
    libtcod.console_set_key_color(sub_window, libtcod.magenta)

    while True:
        # Check for input
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        # Reset 'window' console
        libtcod.console_set_default_background(window, libtcod.black)
        libtcod.console_clear(window)
        # Reset 'sub_window' console (magenta backgrounds are ignored when blitting)
        libtcod.console_set_default_background(sub_window, libtcod.magenta)
        libtcod.console_clear(sub_window)
        libtcod.console_set_default_background(sub_window, libtcod.black)

        # RENDER

        # Print header and borders
        libtcod.console_set_default_foreground(window, libtcod.white)
        libtcod.console_print(window, 1, 1, 'Your skills have increased. Choose a skill to learn:')
        y = 0
        draw_border(window, 0, 0, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT - 5)
        draw_border(window, 0, consts.MAP_VIEWPORT_HEIGHT - 6, consts.MAP_VIEWPORT_WIDTH, 6)

        # Draw scrollable menu
        for skill_category in skill_categories:
            # Draw category dividers
            libtcod.console_set_default_foreground(sub_window, libtcod.gray)
            for i in range(consts.MAP_VIEWPORT_WIDTH):
                libtcod.console_put_char_ex(sub_window, i, y, libtcod.CHAR_HLINE, libtcod.gray, libtcod.black)
            libtcod.console_put_char_ex(sub_window, 0, y, 199, libtcod.gray, libtcod.black)
            libtcod.console_put_char_ex(sub_window, consts.MAP_VIEWPORT_WIDTH - 1, y, 182, libtcod.gray, libtcod.black)
            libtcod.console_print_ex(sub_window, 3, y, libtcod.black, libtcod.LEFT, skill_category.title())
            y += 1
            # Draw all skills in category
            for i in range(len(abilities.skill_list)):
                skill = abilities.skill_list[i]
                if skill.category == skill_category:

                    if y == selected_index:
                        libtcod.console_set_default_background(sub_window, libtcod.white)
                        libtcod.console_set_default_foreground(sub_window, libtcod.black)
                        for j in range(1, consts.MAP_VIEWPORT_WIDTH - 1):
                            libtcod.console_put_char_ex(sub_window, j, y, ' ', libtcod.black, libtcod.white)
                    else:
                        libtcod.console_set_default_background(sub_window, libtcod.black)
                        libtcod.console_set_default_foreground(sub_window, libtcod.white)

                    libtcod.console_print_ex(sub_window, 5, y, libtcod.BKGND_SET, libtcod.LEFT, skill.name.capitalize())
                    y += 1
        # Blit sub_window to window. Select based on scroll height
        libtcod.console_blit(sub_window, 0, scroll_height, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT - 10, window, 0, 4, 1.0, 1.0)

        # print description
        libtcod.console_set_default_foreground(window, libtcod.white)
        libtcod.console_print_rect(window, 1, consts.MAP_VIEWPORT_HEIGHT - 5, consts.MAP_VIEWPORT_WIDTH - 2, 5, menu_lines[selected_index].description)

        # print scroll bar
        libtcod.console_set_default_foreground(window, libtcod.gray)
        libtcod.console_put_char(window, consts.MAP_VIEWPORT_WIDTH - 2, 4, 30)
        libtcod.console_put_char(window, consts.MAP_VIEWPORT_WIDTH - 2, consts.MAP_VIEWPORT_HEIGHT - 7, 31)
        for i in range(consts.MAP_VIEWPORT_HEIGHT - 12):
            libtcod.console_put_char(window, consts.MAP_VIEWPORT_WIDTH - 2, 5 + i, libtcod.CHAR_VLINE)
        bar_height = int(float((consts.MAP_VIEWPORT_HEIGHT - 12) ** 2) / float(sub_height))
        bar_height = clamp(bar_height, 1, consts.MAP_VIEWPORT_HEIGHT - 12)
        bar_y = int(float(consts.MAP_VIEWPORT_HEIGHT - 12 - bar_height) * (float(scroll_height) / float(scroll_limit)))
        for i in range(bar_height):
            libtcod.console_put_char(window, consts.MAP_VIEWPORT_WIDTH - 2, bar_y + 5 + i, 219)

        # Blit to main screen and flush
        libtcod.console_blit(window, 0, 0, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT, 0,
                             consts.MAP_VIEWPORT_X, consts.MAP_VIEWPORT_Y, 1.0, 1.0)
        libtcod.console_flush()

        # HANDLE INPUT

        # Mouse select
        if mouse.lbutton_pressed:
            mouse_item = mouse.cy - consts.MAP_VIEWPORT_Y - 4 + scroll_height
            if 0 <= mouse_item < len(menu_lines) and menu_lines[mouse_item] is not None:
                selected_index = mouse_item
        # ESC back
        if key.vk == libtcod.KEY_ESCAPE:
            return None
        # Enter select
        elif key.vk == libtcod.KEY_ENTER:
            return menu_lines[selected_index] # returns a Perk object
        # Down arrow increments selection index
        elif key.vk == libtcod.KEY_DOWN:
            #selected_index = min(selected_index + 1, len(menu_lines) - 1)
            new_index = None
            while new_index is None:
                selected_index += 1
                if selected_index >= len(menu_lines):
                    selected_index = 0
                new_index = menu_lines[selected_index]
            if selected_index < scroll_height + 1:
                scroll_height = selected_index - 1
            elif selected_index > scroll_height + (consts.MAP_VIEWPORT_HEIGHT - 12):
                scroll_height = selected_index - (consts.MAP_VIEWPORT_HEIGHT - 12)
        # Up arrow decrements selection index
        elif key.vk == libtcod.KEY_UP:
            #selected_index = max(selected_index - 1, 0)
            new_index = None
            while new_index is None:
                selected_index -= 1
                if selected_index < 0:
                    selected_index = len(menu_lines) - 1
                new_index = menu_lines[selected_index]
            if selected_index < scroll_height + 1:
                scroll_height = selected_index - 1
            elif selected_index > scroll_height + (consts.MAP_VIEWPORT_HEIGHT - 12):
                scroll_height = selected_index - (consts.MAP_VIEWPORT_HEIGHT - 12)
        # Scroll wheel & pageup/pagedown adjust scroll height
        elif key.vk == libtcod.KEY_PAGEDOWN or mouse.wheel_down:
            scroll_height = min(scroll_height + 3, scroll_limit)
        elif key.vk == libtcod.KEY_PAGEUP or mouse.wheel_up:
            scroll_height = max(scroll_height - 3, 0)

def cast_spell_new():
    if len(player.known_spells) <= 0:
        message("You don't know any spells.", libtcod.light_blue)
        return 'didnt-take-turn'
    else:
        names = []
        for s in player.known_spells:
            names.append(s.name + ' ' + s.cost_string)
        selection = menu('Cast which spell?', names, 30)
        if selection is not None:
            if player.known_spells[selection].check_mana():
                if player.known_spells[selection].cast():
                    return 'cast-spell'
                else:
                    return 'didnt-take-turn'
            else:
                message("You don't have enough mana to cast that spell.", libtcod.light_blue)
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

        selection = menu('Pick up which item?', options, 30)
        if selection is not None:
            if selection == 0:
                for i in items_here:
                    i.item.pick_up()
            else:
                items_here[selection - 1].item.pick_up()
            return 'picked-up-item'
    else:
        interactable_here = get_objects(player.x, player.y, condition=lambda o:o.interact)
        if len(interactable_here) > 0:
            interactable_here[0].interact(interactable_here[0])
            return 'interacted'
    return 'didnt-take-turn'


def get_objects(x, y, condition=None):
    found = []
    for obj in objects:
        if obj.x == x and obj.y == y:
            if condition is not None:
                if condition(obj):
                    found.append(obj)
            else:
                found.append(obj)
    return found


def inspect_inventory():
    chosen_item = inventory_menu('Select which item?')
    if chosen_item is not None:
        options = chosen_item.get_options_list()
        menu_choice = menu(chosen_item.owner.name, options, 30, render_func=chosen_item.owner.print_description)
        if menu_choice is not None:
            if options[menu_choice] == 'Use':
                chosen_item.use()
                return 'used-item'
            elif options[menu_choice] == 'Drop':
                chosen_item.drop()
                return 'dropped-item'
            elif options[menu_choice] == 'Equip' or options[menu_choice] == 'Unequip':
                chosen_item.owner.equipment.toggle()
                return 'equipped-item'
            else:
                return inspect_inventory()
        else:
            return inspect_inventory()
    return 'didnt-take-turn'


def meditate():
    message('You tap into the magic of the world around you...', libtcod.dark_cyan)
    for i in range(consts.MEDITATE_CHANNEL_TIME - 1):
        player.action_queue.append('channel-meditate')
    player.action_queue.append('finish-meditate')
    return 'start-meditate'


def get_description(obj):
    if obj and hasattr(obj, 'description') and obj.description is not None:
        return obj.description
    else:
        return ""


def examine():
    x, y = target_tile()
    if x is not None and y is not None:
        obj = object_at_coords(x, y)
        desc = ""
        if obj is not None:
            desc = obj.name.capitalize()# + '\n' + get_description(obj)
            if hasattr(obj, 'fighter') and obj.fighter is not None and \
                    hasattr(obj.fighter, 'inventory') and obj.fighter.inventory is not None and len(obj.fighter.inventory) > 0:
                desc = desc + '\nInventory: '
                for item in obj.fighter.inventory:
                    desc = desc + item.name + ', '
            menu(desc, ['back'], 50, render_func=obj.print_description)


def jump():
    global player

    if not dungeon_map[player.x][player.y].jumpable:
        message('You cannot jump from this terrain!', libtcod.light_yellow)
        return 'didnt-take-turn'

    web = object_at_tile(player.x, player.y, 'spiderweb')
    if web is not None:
        message('You struggle against the web.')
        web.destroy()
        return 'webbed'

    if player.fighter.stamina < consts.JUMP_STAMINA_COST:
        message("You don't have the stamina to jump!", libtcod.light_yellow)
        return 'didnt-take-turn'

    message('Jump to where?', libtcod.white)

    render_message_panel()
    libtcod.console_flush()
    (x, y) = target_tile(consts.BASE_JUMP_RANGE, 'pick', consts.JUMP_ATTACK_ACC_MOD)
    if x is not None and y is not None:
        if dungeon_map[x][y].blocks:
            message('There is something in the way.', libtcod.white)
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
                    fov_recompute_fn()
                    player.fighter.adjust_stamina(-consts.JUMP_STAMINA_COST)

                    player.fighter.attack_ex(jump_attack_target, 0, player.fighter.accuracy * consts.JUMP_ATTACK_ACC_MOD,
                                             player.fighter.attack_damage * consts.JUMP_ATTACK_DMG_MOD,
                                             player.fighter.damage_variance, player.fighter.on_hit, 'jump-attacks',
                                             player.fighter.attack_shred, player.fighter.attack_guaranteed_shred,
                                             player.fighter.attack_pierce)

                    return 'jump-attacked'
                else:
                    message('There is something in the way.', libtcod.white)
                    return 'didnt-take-turn'
            else:
                #jump to open space
                player.set_position(x, y)
                fov_recompute_fn()
                player.fighter.adjust_stamina(-consts.JUMP_STAMINA_COST)
                return 'jumped'


    message('Out of range.', libtcod.white)
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
    message('Cast which spell?', libtcod.purple)

    render_all()
    libtcod.console_flush()

    choice = libtcod.console_wait_for_keypress(True).c - 48

    if choice > 0 and choice < len(memory) + 1:
        memory[choice - 1].item.use()
    else:
        message('No such spell.', libtcod.purple)


def clear_map():
    libtcod.console_set_default_background(map_con, libtcod.black)
    libtcod.console_set_default_foreground(map_con, libtcod.black)
    libtcod.console_clear(map_con)


def render_map():
    global changed_tiles, fov_recompute

    if fov_recompute:
        fov_recompute = False
        old_map = libtcod.map_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)
        libtcod.map_copy(fov_map, old_map)
        libtcod.map_compute_fov(fov_map, player.x, player.y, consts.TORCH_RADIUS, consts.FOV_LIGHT_WALLS,
                                consts.FOV_ALGO)
        for y in range(consts.MAP_HEIGHT):
            for x in range(consts.MAP_WIDTH):
                if libtcod.map_is_in_fov(old_map, x, y) != libtcod.map_is_in_fov(fov_map, x, y):
                    changed_tiles.append((x, y))

    for tile in changed_tiles:
        x = tile[0]
        y = tile[1]
        visible = libtcod.map_is_in_fov(fov_map, x, y)
        color_fg = libtcod.Color(dungeon_map[x][y].color_fg[0], dungeon_map[x][y].color_fg[1],
                                 dungeon_map[x][y].color_fg[2])
        color_bg = libtcod.Color(dungeon_map[x][y].color_bg[0], dungeon_map[x][y].color_bg[1],
                                 dungeon_map[x][y].color_bg[2])
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
    draw_border(0, consts.MAP_VIEWPORT_X, consts.MAP_VIEWPORT_Y, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT)

# No longer used, but I'm not willing to delete it from the code base just yet in case problems arise with the new system
def render_map_old():

    global fov_recompute

    libtcod.console_set_default_foreground(map_con, libtcod.white)
    offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2, player.y - consts.MAP_VIEWPORT_HEIGHT / 2

    if fov_recompute:
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, consts.TORCH_RADIUS, consts.FOV_LIGHT_WALLS,
                                consts.FOV_ALGO)

    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            # culling
            if x - offsetx < 0 or x - offsetx > consts.MAP_VIEWPORT_WIDTH or \
                                    y - offsety < 0 or y - offsety > consts.MAP_VIEWPORT_HEIGHT:
                continue

            visible = libtcod.map_is_in_fov(fov_map, x, y)
            color_fg = libtcod.Color(dungeon_map[x][y].color_fg[0], dungeon_map[x][y].color_fg[1],
                                     dungeon_map[x][y].color_fg[2])
            color_bg = libtcod.Color(dungeon_map[x][y].color_bg[0], dungeon_map[x][y].color_bg[1],
                                     dungeon_map[x][y].color_bg[2])
            if not visible:
                if dungeon_map[x][y].explored:
                    libtcod.color_scale_HSV(color_fg, 0.1, 0.4)
                    libtcod.color_scale_HSV(color_bg, 0.1, 0.4)
                    libtcod.console_put_char_ex(map_con, x - offsetx, y - offsety, dungeon_map[x][y].tile_char, color_fg,
                                                color_bg)
            else:
                libtcod.console_put_char_ex(map_con, x - offsetx, y - offsety, dungeon_map[x][y].tile_char, color_fg,
                                            color_bg)
                dungeon_map[x][y].explored = True

    # draw all objects in the list
    for object in objects:
        if object != player:
            object.draw_old()
    player.draw_old()

    draw_border(map_con, 0, 0, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT)

    libtcod.console_blit(map_con, 0, 0, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT, 0, consts.MAP_VIEWPORT_X,
                         consts.MAP_VIEWPORT_Y)


def render_side_panel(acc_mod=1.0):

    libtcod.console_set_default_background(side_panel, libtcod.black)
    libtcod.console_clear(side_panel)

    render_bar(2, 2, consts.BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.dark_red, libtcod.darker_red, align=libtcod.LEFT)
    # Display armor/shred
    armor_string = 'AR:' + str(player.fighter.armor)
    if player.fighter.shred > 0:
        libtcod.console_set_default_foreground(side_panel, libtcod.yellow)
    libtcod.console_print_ex(side_panel, consts.SIDE_PANEL_WIDTH - 4, 2, libtcod.BKGND_DEFAULT, libtcod.RIGHT, armor_string)

    render_bar(2, 3, consts.BAR_WIDTH, 'Stamina', player.fighter.stamina, player.fighter.max_stamina,
               libtcod.dark_green, libtcod.darker_green)

    # Breath
    if player.fighter.breath < player.fighter.max_breath:
        breath_text = ''
        for num in range(0, player.fighter.breath):
            breath_text += 'O '
        libtcod.console_set_default_foreground(side_panel, libtcod.dark_blue)
        libtcod.console_print(side_panel, 2, 4, breath_text)
        libtcod.console_set_default_foreground(side_panel, libtcod.white)

    # Base stats
    libtcod.console_print(side_panel, 2, 6, 'INT: ' + str(player.player_stats.int))
    libtcod.console_print(side_panel, 2, 7, 'WIZ: ' + str(player.player_stats.wiz))
    libtcod.console_print(side_panel, 2, 8, 'STR: ' + str(player.player_stats.str))
    libtcod.console_print(side_panel, 2, 9, 'AGI: ' + str(player.player_stats.agi))

    # Level/XP
    libtcod.console_print(side_panel, 2, 11, 'Lvl: ' + str(player.level))
    libtcod.console_print(side_panel, 2, 12, 'XP:  ' + str(player.fighter.xp))

    # Mana
    libtcod.console_print(side_panel, 2, 14, 'Mana:')
    libtcod.console_put_char(side_panel, 2, 15, '[')
    x = 4
    for m in range(len(player.mana)):
        libtcod.console_set_default_foreground(side_panel, spells.mana_colors[player.mana[m]])
        libtcod.console_put_char(side_panel, x, 15, '*')
        x += 2
    for m in range(player.player_stats.max_mana - len(player.mana)):
        libtcod.console_set_default_foreground(side_panel, libtcod.dark_grey)
        libtcod.console_put_char(side_panel, x, 15, '.')
        x += 2
    libtcod.console_set_default_foreground(side_panel, libtcod.white)
    libtcod.console_put_char(side_panel, x, 15, ']')

    drawHeight = 19

    # Status effects
    if len(player.fighter.status_effects) > 0:
        for effect in player.fighter.status_effects:
            libtcod.console_set_default_foreground(side_panel, effect.color)
            libtcod.console_print(side_panel, 2, drawHeight, effect.name + ' (' + str(effect.time_limit) + ')')
            drawHeight += 1
        drawHeight += 1
        libtcod.console_set_default_foreground(side_panel, libtcod.white)

    # Objects here
    libtcod.console_print(side_panel, 2, drawHeight, 'Objects here:')
    drawHeight += 1
    objects_here = get_objects(player.x, player.y, lambda o: o is not player)
    if len(objects_here) > 0:
        end = min(len(objects_here), 7)
        if len(objects_here) == 8:
            end = 8
        for i in range(end):
            line = objects_here[i].name
            line = (line[:consts.SIDE_PANEL_WIDTH - 8] + '...') if len(line) > consts.SIDE_PANEL_WIDTH - 5 else line
            if objects_here[i].item:
                libtcod.console_set_default_foreground(side_panel, libtcod.yellow)
            else:
                libtcod.console_set_default_foreground(side_panel, libtcod.gray)
            libtcod.console_print(side_panel, 4, drawHeight, line)
            drawHeight += 1
        libtcod.console_set_default_foreground(side_panel, libtcod.gray)
        if end < len(objects_here) - 1:
            libtcod.console_print(side_panel, 4, drawHeight, '...' + str(len(objects_here) - 7) + ' more...')
            drawHeight += 1
    libtcod.console_print(side_panel, 4, drawHeight, dungeon_map[player.x][player.y].name)
    drawHeight += 2
    libtcod.console_set_default_foreground(side_panel, libtcod.white)

    # Spells in memory
    #libtcod.console_print(side_panel, 2, drawHeight, 'Spells in memory:')
    #drawHeight += 1
    #y = 1
    #for spell in memory:
    #    libtcod.console_print(side_panel, 2, drawHeight, str(y) + ') ' + spell.name)
    #    drawHeight += 1
    #    y += 1

    # Selected Monster
    if selected_monster is not None:
        drawHeight = consts.SIDE_PANEL_HEIGHT - 16
        libtcod.console_print(side_panel, 2, drawHeight, selected_monster.name)
        drawHeight += 2
        render_bar(2, drawHeight, consts.BAR_WIDTH, 'HP', selected_monster.fighter.hp, selected_monster.fighter.max_hp,
                   libtcod.dark_red, libtcod.darker_red, align=libtcod.LEFT)
        libtcod.console_set_default_foreground(side_panel, libtcod.white)
        armor_string = 'AR:' + str(selected_monster.fighter.armor)
        if selected_monster.fighter.shred > 0:
            libtcod.console_set_default_foreground(side_panel, libtcod.yellow)
        libtcod.console_print_ex(side_panel, consts.SIDE_PANEL_WIDTH - 4, drawHeight, libtcod.BKGND_DEFAULT, libtcod.RIGHT,
                                     armor_string)

        drawHeight += 1
        libtcod.console_set_default_foreground(side_panel, libtcod.gray)
        s = 'Your Accuracy: %d%%' % int(100.0 * get_chance_to_hit(selected_monster, player.fighter.accuracy * acc_mod))
        s += '%'  # Yeah I know I suck with string formatting. Whatever, this works.  -T
        libtcod.console_print(side_panel, 2, drawHeight, s)
        drawHeight += 1
        if selected_monster.fighter.accuracy > 0:
            s = "Its Accuracy : %d%%" % int(100.0 * get_chance_to_hit(player, selected_monster.fighter.accuracy))
            s += '%'
            libtcod.console_print(side_panel, 2, drawHeight, s)
        else:
            libtcod.console_print(side_panel, 2, drawHeight, 'Does not attack')

        drawHeight += 2
        for effect in selected_monster.fighter.status_effects:
            libtcod.console_set_default_foreground(side_panel, effect.color)
            libtcod.console_print(side_panel, 2, drawHeight, effect.name + ' (' + str(effect.time_limit) + ')')
            drawHeight += 1

    draw_border(side_panel, 0, 0, consts.SIDE_PANEL_WIDTH, consts.SIDE_PANEL_HEIGHT)
    for x in range(1, consts.SIDE_PANEL_WIDTH - 1):
        libtcod.console_put_char(side_panel, x, 17, libtcod.CHAR_HLINE)
    libtcod.console_put_char(side_panel, 0, 17, 199)
    libtcod.console_put_char(side_panel, consts.SIDE_PANEL_WIDTH - 1, 17, 182)

    libtcod.console_blit(side_panel, 0, 0, consts.SIDE_PANEL_WIDTH, consts.SIDE_PANEL_HEIGHT, 0, consts.SIDE_PANEL_X,
                         consts.SIDE_PANEL_Y)


def render_message_panel():
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, consts.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    libtcod.console_set_default_foreground(panel, libtcod.light_grey)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    draw_border(panel, 0, 0, consts.PANEL_WIDTH, consts.PANEL_HEIGHT)

    libtcod.console_blit(panel, 0, 0, consts.PANEL_WIDTH, consts.PANEL_HEIGHT, 0, consts.PANEL_X, consts.PANEL_Y)


def render_ui_overlay():
    libtcod.console_set_default_background(ui, libtcod.black)
    libtcod.console_clear(ui)

    under = get_names_under_mouse()

    if under != '':
        unders = under.split(', ')
        y = 1
        max_width = 0
        for line in unders:
            libtcod.console_print(ui, mouse.cx, mouse.cy + y, line.capitalize())
            if len(line) > max_width: max_width = len(line)
            y += 1
        libtcod.console_blit(ui, mouse.cx, mouse.cy + 1, max_width, y - 1, 0, mouse.cx, mouse.cy + 1, 1.0, 0.5)


def render_all():

    if not in_game:
        return

    libtcod.console_set_default_background(0, libtcod.black)
    libtcod.console_clear(0)

    render_map()

    render_side_panel()

    render_message_panel()

    render_ui_overlay()


def draw_border(console, x0, y0, width, height, foreground=libtcod.gray, background=libtcod.black):

    libtcod.console_set_default_foreground(console, foreground)
    libtcod.console_set_default_background(console, background)
    for x in range(1, width - 1):
        libtcod.console_put_char(console, x0 + x, y0, libtcod.CHAR_DHLINE, libtcod.BKGND_SET)
        libtcod.console_put_char(console, x0 + x, y0 + height - 1, libtcod.CHAR_DHLINE, libtcod.BKGND_SET)
    for y in range(1, height - 1):
        libtcod.console_put_char(console, x0, y0 + y, libtcod.CHAR_DVLINE, libtcod.BKGND_SET)
        libtcod.console_put_char(console, x0 + width - 1, y0 + y, libtcod.CHAR_DVLINE, libtcod.BKGND_SET)
    libtcod.console_put_char(console, x0, y0, 4, libtcod.BKGND_SET)
    libtcod.console_put_char(console, x0 + width - 1, y0, 4, libtcod.BKGND_SET)
    libtcod.console_put_char(console, x0 + width - 1, y0 + height - 1, 4, libtcod.BKGND_SET)
    libtcod.console_put_char(console, x0, y0 + height - 1, 4, libtcod.BKGND_SET)


def generate_level():
    global dungeon_map, objects, stairs, spawned_bosses
    mapgen.make_map()
 
#############################################
# Initialization & Main Loop
#############################################

def main_menu():
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
        
        choice = menu('', ['NEW GAME', 'CONTINUE', 'QUIT'], 24, x_center=consts.SCREEN_WIDTH / 2)
        
        if choice == 0: #new game
            new_game()
            play_game()
        elif choice == 1:
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2:
            break
    

def new_game():
    global player, game_msgs, game_state, dungeon_level, memory, in_game, selected_monster, changed_tiles

    in_game = True

    #create object representing the player
    fighter_component = Fighter(hp=100, xp=0, stamina=100, death_function=player_death)
    player = GameObject(25, 23, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component, player_stats=PlayerStats(), description='You, the fearless adventurer!')
    player.level = 1
    
    #generate map
    dungeon_level = 1
    generate_level()
    initialize_fov()
    game_state = 'playing'

    #item = GameObject(0, 0, '#', 'scroll of bullshit', libtcod.yellow, item=Item(use_function=spells.cast_fireball), description='the sword you started with')
    #waterbreathing = GameObject(0, 0, '!', 'potion of waterbreathing', libtcod.yellow, item=Item(use_function=spells.cast_waterbreathing), description='This potion allows the drinker to breath underwater for a short time.')
    #inventory.append(item)
    #inventory.append(waterbreathing)

    memory = []
    player.mana = []
    player.known_spells = [] #[spells.cast_manabolt]
    player.action_queue = []
    # spell = GameObject(0, 0, '?', 'mystery spell', libtcod.yellow, item=Item(use_function=spells.cast_lightning, type="spell"))
    # memory.append(spell)

    #Welcome message
    game_msgs = []

    spawn_item('tome_manabolt', player.x, player.y)
    spawn_item('tome_mend', player.x, player.y)
    spawn_item('scroll_fireball', player.x, player.y)
    spawn_item('equipment_spear', player.x, player.y)

    leather_armor = create_item('equipment_leather_armor')
    player.fighter.inventory.append(leather_armor)
    leather_armor.equipment.equip()
    dagger = create_item('equipment_dagger')
    player.fighter.inventory.append(dagger)
    dagger.equipment.equip()

    #spawn_monster('monster_blastcap', player.x, player.y - 1)

    selected_monster = None

    message('Welcome to the dungeon...', libtcod.gold)

    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            changed_tiles.append((x, y))


def initialize_fov():
    global fov_recompute, fov_map
    
    libtcod.console_clear(con)
    
    fov_recompute = True
    
    fov_map = libtcod.map_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            sight_blockers = get_objects(x, y, lambda o: o.blocks_sight)
            libtcod.map_set_properties(fov_map, x, y, len(sight_blockers) == 0 and not dungeon_map[x][y].blocks_sight, not dungeon_map[x][y].blocks)
            #dungeon_map[x][y].explored = True


def save_game():
    file = shelve.open('savegame', 'n')
    file['map'] = dungeon_map
    file['objects'] = objects
    file['player_index'] = objects.index(player)
    file['stairs_index'] = objects.index(stairs)
    file['memory'] = memory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['dungeon_level'] = dungeon_level
    file.close()


def load_game():
    global dungeon_map, objects, player, memory, game_msgs, game_state, dungeon_level, stairs, in_game, selected_monster

    in_game = True

    file = shelve.open('savegame', 'r')
    dungeon_map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]
    stairs = objects[file['stairs_index']]
    memory = file['memory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    dungeon_level = file['dungeon_level']
    selected_monster = None
    file.close()
    
    initialize_fov()

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

        # Let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            player.on_tick(object=player)
            for object in objects:
                if object.ai:
                    object.ai.take_turn()
                if object is not player:
                    object.on_tick(object=object)

        # Handle auto-targeting
        auto_target_monster()


# my modules
import spells
import loot
import monsters
import dungeon
import mapgen
import abilities
import effects

in_game = False
libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT, 'Magic Roguelike', False)
libtcod.sys_set_fps(consts.LIMIT_FPS)
con = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
window = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
#map_con = libtcod.console_new(consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT)
map_con = libtcod.console_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)
ui = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
panel = libtcod.console_new(consts.PANEL_WIDTH, consts.PANEL_HEIGHT)
side_panel = libtcod.console_new(consts.SIDE_PANEL_WIDTH, consts.SIDE_PANEL_HEIGHT)
changed_tiles = []