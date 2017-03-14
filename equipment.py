import libtcodpy as libtcod
import game as main
import consts
import player
import spells
import ui
import collections

class Equipment:
    def __init__(self, slot, category, max_hp_bonus=0, strength_dice_bonus=0,
                 armor_bonus=0, evasion_bonus=0, spell_power_bonus=0, stamina_cost=0, str_requirement=0, shred_bonus=0,
                 guaranteed_shred_bonus=0, pierce=0, accuracy=0, ctrl_attack=None, ctrl_attack_desc=None,
                 break_chance=0.0, weapon_dice=None, str_dice=None, on_hit=None, damage_type=None, attack_speed_bonus=0,
                 attack_delay=0, essence=None, spell_list=None, level_progression=None, level_costs=None,
                 resistances=[], modifiers = {}, base_id=None,
                 crit_bonus=1.0, subtype=None, spell_resist_bonus=0, starting_level=0, weight=0):
        self.is_equipped = False
        self.slot = slot
        self.base_id = base_id
        self.category = category
        self.subtype = subtype

        self.ctrl_attack = ctrl_attack
        self.ctrl_attack_desc = ctrl_attack_desc

        self.modifiers = dict(modifiers) #list of references to dictionaries

        self._stamina_cost = stamina_cost
        self._str_requirement = str_requirement
        self._weight = weight
        self._break_chance = break_chance

        self._max_hp_bonus = max_hp_bonus
        self._armor_bonus = armor_bonus
        self._evasion_bonus = evasion_bonus
        self._resistances = list(resistances)

        self.damage_type = damage_type
        self.weapon_dice = weapon_dice
        self._strength_dice_bonus = strength_dice_bonus
        self._on_hit = on_hit  # expects list
        self._attack_delay = attack_delay
        self._str_dice = str_dice
        self._shred_bonus = shred_bonus
        self._guaranteed_shred_bonus = guaranteed_shred_bonus
        self._pierce_bonus = pierce

        self._accuracy_bonus = accuracy
        self._crit_bonus = crit_bonus
        self._attack_speed_bonus = attack_speed_bonus

        self._spell_power_bonus = spell_power_bonus
        self._spell_resist_bonus = spell_resist_bonus

        self.essence = essence
        self.level = 0
        if level_progression is not None:
            self.max_level = len(level_progression)
        self.level_progression = level_progression
        if spell_list is not None:
            default_level = 0
            if level_progression is None:
                default_level = 1
            self.spell_list = {s: default_level for s in spell_list}
            self.flat_spell_list = spell_list
            self.level_costs = level_costs
            self.spell_charges = {}
            self.refill_spell_charges()
        for i in range(starting_level):
            self.level_up(True)

    def get_bonus(self,stat):
        return sum([v.get(stat,0) for v in self.modifiers.values()])

    def get_scalar(self,stat):
        return reduce(lambda a,b: a * b,[v.get(stat,1) for v in self.modifiers.values()],1)

    @property
    def stamina_cost(self):
        return self._stamina_cost * self.get_scalar('stamina_cost_scalar')

    @property
    def str_requirement(self):
        return self._str_requirement + self.get_bonus('str_requirement_bonus')

    @property
    def weight(self):
        return max(self._weight + self.get_bonus('weight_bonus'),0)

    @property
    def break_chance(self):
        return self._break_chance + self.get_bonus('break_chance_bonus')

    @property
    def max_hp_bonus(self):
        return self._max_hp_bonus + self.get_bonus('max_hp_bonus')

    @property
    def armor_bonus(self):
        return self._armor_bonus + self.get_bonus('armor_bonus')

    @property
    def evasion_bonus(self):
        return self._evasion_bonus + self.get_bonus('evasion_bonus')

    @property
    def accuracy_bonus(self):
        return self._accuracy_bonus + self.get_bonus('accuracy_bonus')

    @property
    def resistances(self):
        return self._resistances + [mod.get('resistance') for mod in self.modifiers.values() if mod.get('resistance') is not None]

    @property
    def strength_dice_bonus(self):
        return self._strength_dice_bonus + self.get_bonus('strength_dice_bonus')

    @property
    def on_hit(self):
        return self._on_hit + [mod.get('on_hit') for mod in self.modifiers.values() if mod.get('on_hit') is not None]

    @property
    def attack_delay(self):
        return self._attack_delay + self.get_bonus('attack_delay_bonus')

    @property
    def str_dice(self):
        return self._str_dice + self.get_bonus('str_dice_bonus')

    @property
    def shred_bonus(self):
        return self._shred_bonus + self.get_bonus('shred_bonus')

    @property
    def guaranteed_shred_bonus(self):
        return self._guaranteed_shred_bonus + self.get_bonus('guaranteed_shred_bonus')

    @property
    def pierce_bonus(self):
        return self._pierce_bonus + self.get_bonus('pierce_bonus')

    @property
    def accuracy(self):
        return self._accuracy_bonus + self.get_bonus('accuracy')

    @property
    def crit_bonus(self):
        return self._crit_bonus + self.get_bonus('crit_bonus')

    @property
    def attack_speed_bonus(self):
        return self._attack_speed_bonus + self.get_bonus('attack_speed_bonus')

    @property
    def spell_power_bonus(self):
        return self._spell_power_bonus + self.get_bonus('spell_power_bonus')

    @property
    def spell_resist_bonus(self):
        return self._spell_resist_bonus + self.get_bonus('spell_resist_bonus')

    @property
    def holder(self):
        return self.owner.item.holder

    def toggle(self):
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        # First check weight
        if self.holder is player.instance:
            if self.holder.fighter.equip_weight + self.weight > self.holder.fighter.max_equip_weight:
                ui.message('That is too heavy.', libtcod.orange)
                return

        if self.slot == 'both hands':
            rh = main.get_equipped_in_slot(self.holder.fighter.inventory, 'right hand')
            lh = main.get_equipped_in_slot(self.holder.fighter.inventory, 'left hand')
            if rh is not None: rh.dequip()
            if lh is not None: lh.dequip()
        else:
            old_equipment = main.get_equipped_in_slot(self.holder.fighter.inventory, self.slot)
            if old_equipment is not None:
                old_equipment.dequip(self.holder)
        self.is_equipped = True
        if self.holder is player.instance:
            ui.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.orange)

    def dequip(self, no_message=False):
        self.is_equipped = False
        if not no_message and self.holder is player.instance:
            ui.message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.orange)

    def print_description(self, console, x, y, width):
        print_height = 1
        if self.str_requirement != 0:
            if player.instance.player_stats.str < self.str_requirement:
                libtcod.console_set_default_foreground(console, libtcod.red)
            else:
                libtcod.console_set_default_foreground(console, libtcod.dark_green)
            libtcod.console_print(console, x, y + print_height, 'Strength Required: ' + str(self.str_requirement))
            print_height += 1
            libtcod.console_set_default_foreground(console, libtcod.white)
        libtcod.console_print(console, x, y + print_height, 'Slot: ' + self.slot)
        print_height += 2
        if self.level_progression is not None and self.level_progression != 0:
            libtcod.console_print(console, x, y + print_height, 'Level: ' + str(self.level) + '/' + str(self.max_level))
            print_height += 1
        if self.armor_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Armor: ' + str(self.armor_bonus))
            print_height += 1
        if self.weapon_dice is not None and self.weapon_dice != '0d0':
            r = main.dice_range(self.weapon_dice, normalize_size=4)
            libtcod.console_print(console, x, y + print_height, 'Damage: ' + str(r[0]) + '-' + str(r[1]))
            print_height += 1
        if self.str_dice is not None and self.str_dice > 0:
            r = main.dice_range(str(self.str_dice) + 'd' + str(player.instance.player_stats.str), normalize_size=4)
            libtcod.console_print(console, x, y + print_height, 'Strength Bonus: ' + str(r[0]) + '-' + str(r[1]))
            print_height += 1
        if self.accuracy_bonus != 0:
            acc_str = 'Accuracy: '
            if self.accuracy_bonus > 0:
                acc_str += '+'
            libtcod.console_print(console, x, y + print_height, acc_str + str(self.accuracy_bonus))
            print_height += 1
        if self.crit_bonus != 0:
            acc_str = 'Crit: x'
            libtcod.console_print(console, x, y + print_height, acc_str + str(self.crit_bonus))
            print_height += 1
        if self.attack_delay != 0:
            attacks = max(round(float(player.instance.fighter.attack_speed) / float(self.attack_delay), 1), 1.0)
            libtcod.console_print(console, x, y + print_height, 'Attack Speed: ' + str(attacks))
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
        if self.spell_resist_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Spell Resist: ' + str(self.spell_resist_bonus))
            print_height += 1
        if self.weight > 0:
            libtcod.console_print(console, x, y + print_height, 'Weight: ' + str(self.weight))
            print_height += 1
        if self.break_chance > 0:
            libtcod.console_print(console, x, y + print_height,
                                  'It has a ' + str(self.break_chance) + '%%' + ' chance to break when used.')
            print_height += 1
        for r in self.resistances:
            libtcod.console_print(console, x, y + print_height, 'Resist %s' % r)
            print_height += 1
        if self.ctrl_attack_desc:
            libtcod.console_set_default_foreground(console, libtcod.azure)
            text = 'Ctrl+attack: ' + self.ctrl_attack_desc
            h = libtcod.console_get_height_rect(console, x, y + print_height, width, consts.SCREEN_HEIGHT, text)
            libtcod.console_print_rect(console, x, y + print_height + 1, width, h, text)
            print_height += h + 1
            libtcod.console_set_default_foreground(console, libtcod.white)
        if hasattr(self, 'spell_list') and self.spell_list is not None:
            libtcod.console_set_default_foreground(console, libtcod.azure)
            libtcod.console_print(console, x, y + print_height, 'Spells:')
            libtcod.console_set_default_foreground(console, libtcod.white)
            for spell in self.flat_spell_list:
                level = self.spell_list[spell]  # dictionaries don't preserve order - flat lists do
                spell_data = spells.library[spell]
                if level == 0:
                    libtcod.console_set_default_foreground(console, libtcod.gray)
                libtcod.console_print(console, x, y + print_height,
                                      "- " + spell_data.name.title() + " " + str(level) + "/" + str(
                                          spell_data.max_level))
                libtcod.console_set_default_foreground(console, libtcod.white)
                print_height += 1

        return print_height

    def get_active_spells(self):
        return {s: l for (s, l) in self.spell_list.items() if l > 0}

    def can_cast(self, spell_name, actor):
        sl = self.spell_list[spell_name]
        if actor is player.instance:
            if player.instance.player_stats.int < spells.library[spell_name].int_requirement - main.skill_value('scholar'):
                ui.message("This spell is too difficult for you to understand.", libtcod.blue)
                return False
        level = spells.library[spell_name].levels[sl - 1]

        if spell_name not in self.spell_list:
            ui.message("You don't have that spell.")
            return False
        elif sl <= 0:
            ui.message('That spell has not been learned!', libtcod.blue)
            return False
        elif self.spell_charges[spell_name] <= 0:
            ui.message('That spell is out of charges.', libtcod.blue)
            return False
        elif actor.fighter.stamina < level['stamina_cost']:
            ui.message("You don't have the stamina to cast that spell.", libtcod.light_yellow)
            return False
        return True

    def level_up(self, force=False):
        if self.level >= self.max_level:
            ui.message('{} is already max level!'.format(self.owner.name))

        if self.essence not in player.instance.essence and not force:
            ui.message("You don't have any " + self.essence + " essence.", libtcod.blue)
            return 'didnt-take-turn'

        cost = self.level_costs[self.level]  # next level cost, no level-1

        if collections.Counter(player.instance.essence)[self.essence] < cost and not force:
            ui.message("You don't have enough " + self.essence + " essence.", libtcod.blue)
            return 'didnt-take-turn'

        if self.spell_list is not None:
            spell = self.level_progression[self.level]
            self.spell_list[spell] += 1
            # refill spell charges for that spell
            self.spell_charges[spell] = spells.library[spell].max_spell_charges(self.spell_list[spell])
            if not force:
                if self.spell_list[spell] == 1:
                    ui.message('Learned spell ' + spells.library[spell].name.title(), libtcod.white)
                else:
                    ui.message('Upgraded spell ' + spells.library[spell].name.title() + " to level " + str(
                        self.spell_list[spell]), libtcod.white)
        for i in range(cost):
            if self.essence in player.instance.essence:
                player.instance.essence.remove(self.essence)
        self.level += 1
        return 'leveled-up'

    def refill_spell_charges(self):
        # on medidate, item create, and potions(?)
        for spell, level in self.get_active_spells().items():
            self.spell_charges[spell] = spells.library[spell].max_spell_charges(level)

    def add_spell(self, spell, level):
        self.spell_list[spell] = level
        self.flat_spell_list.append(spell)
        self.spell_charges[spell] = spells.library[spell].max_spell_charges(self.spell_list[spell])