import game as main
import libtcodpy as libtcod
import consts
import textwrap
import fov
import player
import combat
import perks
import spells
import collections
import math

def msgbox(text, width=50):
    menu(text, [], width)


def menu(header, options, width=30, x_center=None, render_func=None):

    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    options_ex = collections.OrderedDict()
    letter_index = ord('a')
    for option in options:
        options_ex[chr(letter_index)] = [{
            'text' : option
        }]
        letter_index += 1

    return menu_ex(header, options_ex, width, x_center, render_func)

def menu_y_n(header, width=30, x_center=None):
    options_ex = collections.OrderedDict()
    options_ex['y'] = [{'text' : 'Yes'}]
    options_ex['n'] = [{'text' : 'No'}]
    #options_ex = {
    #    'y' : [{'text' : 'Yes'}],
    #    'n' : [{'text' : 'No'}]
    #}
    return menu_ex(header, options_ex, width, x_center, None, True) == 'y'

# Example menu options data:
#
#menu_options = {
#       'a' : [  #<= indexed by key, value is a list of dictionaries
#           {
#               'category' : 'name',  #<= The column for this item
#               'text' : 'fire brand',  #<= The text for this item
#               'color' : libtcod.grey,  #<= The color of this item
#           },
#           {
#               'category' : 'essence cost',
#               'text' : '**',
#               'color' : libtcod.red,
#           }
#        ]
#    }
def menu_ex(header, options, width, x_center=None, render_func=None, return_as_char=False):
    # Prepare header spacing
    if header is None:
        header = ''
    no_header = False
    header_height = libtcod.console_get_height_rect(main.con, 0, 0, width - 2, consts.SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
        no_header = True

    height = len(options.keys()) + header_height + 2
    if not no_header:
        height += 1

    libtcod.console_clear(window)
    main.render_all()
    libtcod.console_flush()

    # Print header
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 1, 1, width - 2, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    draw_height = header_height + 1
    if not no_header:
        draw_height += 1

    # Run Render Function if there is one (used for descriptions)
    if render_func is not None:
        h = render_func(window, 1, draw_height, width - 2)
        draw_height += h + 1
        height += h + 1

    categories = []
    col_widths = {}
    for option in options.values():
        for item in option:
            if 'category' in item.keys() and item['category'] not in categories:
                categories.append(item['category'])
    if len(categories) > 1:
        # If there is more than one category, we need to print column headers and decide column width
        for category in categories:
            col_widths[category] = len(category) + 2
            for option in options.values():
                for item in option:
                    if 'category' in item.keys() and \
                                    item['category'] == category and \
                                    len(item['text']) + 2 > col_widths[category]:
                        col_widths[category] = len(item['text']) + 2
        # column widths have been established - print column headers
        libtcod.console_set_default_foreground(window, libtcod.white)
        x = 0
        for category in categories:
            libtcod.console_print(window, 5 + x, draw_height, category.title())
            x += col_widths[category]
        draw_height += 1
        libtcod.console_set_default_foreground(window, libtcod.gray)
        for i in range(4 + sum(col_widths.values())):
            libtcod.console_put_char(window, 1 + i, draw_height, 196)
        draw_height += 1
        height += 2

    # Print options list
    for index in options.keys():
        if options[index] is None or len(options[index]) == 0:
            continue
        # Print letter index
        libtcod.console_set_default_foreground(window, libtcod.white)
        libtcod.console_print(window, 1, draw_height, '(%s)' % index)
        # Print category items
        if len(options[index]) > 1:
            for item in options[index]:
                if 'text' not in item.keys():
                    continue
                x = 0
                for category in categories:
                    if 'category' in item.keys() and item['category'] == category:
                        if 'color' in item.keys():
                            libtcod.console_set_default_foreground(window, item['color'])
                        else:
                            libtcod.console_set_default_foreground(window, libtcod.white)
                        libtcod.console_print(window, 5 + x, draw_height, item['text'])
                    x += col_widths[category]
        elif 'text' in options[index][0]:
            if 'color' in options[index][0].keys():
                libtcod.console_set_default_foreground(window, options[index][0]['color'])
            else:
                libtcod.console_set_default_foreground(window, libtcod.white)
            libtcod.console_print(window, 5, draw_height, options[index][0]['text'])

        draw_height += 1

    # Draw Border
    draw_border(window, 0, 0, width, height)

    # Blit the window to the screen
    if x_center is None:
        x = consts.MAP_VIEWPORT_X + consts.MAP_VIEWPORT_WIDTH / 2 - width / 2
    else:
        x = x_center - width / 2
    y = consts.SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 1.0)
    libtcod.console_flush()

    # Handle input and return index
    key = libtcod.console_wait_for_keypress(True)
    if chr(key.c) in options.keys():
        if return_as_char:
            return chr(key.c)
        else:
            index = key.c - ord('a')
            if 0 <= index < len(options): return index
            else: return None
    else:
        return None


def inventory_menu(header):
    import loot
    libtcod.console_clear(window)
    main.render_all()
    libtcod.console_flush()

    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print(window, 1, 1, header)
    y = 3
    letter_index = ord('a')
    menu_items = []
    item_categories = []

    if len(player.instance.fighter.inventory) == 0:
        height = 5
        draw_border(window, 0, 0, consts.INVENTORY_WIDTH, height)
        libtcod.console_set_default_foreground(window, libtcod.dark_grey)
        libtcod.console_print(window, 1, 3, 'Inventory is empty.')
    else:
        for item in player.instance.fighter.inventory:
            if not item.item.category in item_categories:
                item_categories.append(item.item.category)
        height = 4 + len(item_categories) + len(player.instance.fighter.inventory)
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
                                     loot.item_categories[item_category]['plural'].title())
            y += 1
            for item in player.instance.fighter.inventory:
                if item.item.category == item_category:
                    menu_items.append(item)

                    libtcod.console_set_default_foreground(window, libtcod.white)
                    libtcod.console_print(window, 1, y, '(' + chr(letter_index) + ') ')
                    libtcod.console_put_char_ex(window, 5, y, item.char, item.color, libtcod.black)
                    libtcod.console_print(window, 7, y, item.name.title())

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
    if 0 <= index < len(player.instance.fighter.inventory):
        return menu_items[index].item
    return None


def auto_target_monster():
    global selected_monster

    if selected_monster is None:
        monster = main.closest_monster(consts.TORCH_RADIUS)
        if monster is not None:
            select_monster(monster)
    elif not selected_monster.player_can_see():
        main.changed_tiles.append((selected_monster.x, selected_monster.y))
        selected_monster = None


def target_next_monster():
    global selected_monster

    if selected_monster is not None:
        main.changed_tiles.append((selected_monster.x, selected_monster.y))

    nearby = []
    for obj in main.current_map.fighters:
        if fov.player_can_see(obj.x, obj.y) and obj is not player.instance:
            nearby.append((obj.distance_to(player.instance), obj))
    nearby.sort(key=lambda m: m[0])

    if len(nearby) == 0:
        selected_monster = None
        return
    else:
        if selected_monster not in main.current_map.fighters:
            select_monster(nearby[0][1])
            return
        i = 0
        while nearby[i][1] is not selected_monster:
            i += 1
        if i + 1 == len(nearby):
            select_monster(nearby[0][1])
            return
        else:
            select_monster(nearby[i + 1][1])
            return


def select_monster(monster):
    global selected_monster

    if fov.player_can_see(monster.x, monster.y) and monster is not selected_monster:
        main.changed_tiles.append((monster.x, monster.y))
        if selected_monster is not None:
            main.changed_tiles.append((selected_monster.x, selected_monster.y))
        selected_monster = monster


def mouse_select_monster():
    global selected_monster

    mouse = main.mouse

    if mouse.lbutton_pressed:
        offsetx, offsety = player.instance.x - consts.MAP_VIEWPORT_WIDTH / 2 - consts.MAP_VIEWPORT_X, \
                           player.instance.y - consts.MAP_VIEWPORT_HEIGHT / 2 - consts.MAP_VIEWPORT_Y
        (x, y) = (mouse.cx + offsetx, mouse.cy + offsety)

        monster = None
        for obj in main.current_map.fighters:
            if obj.x == x and obj.y == y and (fov.player_can_see(obj.x, obj.y) or (obj.always_visible and
                                       main.current_map.tiles[obj.x][obj.y].explored)) and obj is not player.instance:
                monster = obj
                break
        if monster is not None:
            select_monster(monster)


def get_names_under_mouse():
    mouse = main.mouse

    offsetx, offsety = player.instance.x - consts.MAP_VIEWPORT_WIDTH / 2 - consts.MAP_VIEWPORT_X, \
                       player.instance.y - consts.MAP_VIEWPORT_HEIGHT / 2 - consts.MAP_VIEWPORT_Y
    (x, y) = (mouse.cx + offsetx, mouse.cy + offsety)

    names = []
    for obj in main.get_objects(x, y, lambda o: fov.player_can_see(o.x, o.y) or (o.always_visible and main.current_map.tiles[o.x][o.y].explored)):
        if obj.name == 'player':
            names.append('you')
        else:
            names.append(obj.name)

    names = ', '.join(names)

    return names.title()


def message(new_msg, color=libtcod.white):
    global game_msgs, msg_render_height
    new_msg_lines = textwrap.wrap(new_msg, consts.MSG_WIDTH)

    for line in new_msg_lines:
        if len(game_msgs) == 100:
            del game_msgs[0]
        game_msgs.append((line, color))
    msg_render_height = 0

def message_flush(new_msg, color=libtcod.white):
    message(new_msg,color)
    render_message_panel()
    libtcod.console_flush()

def scroll_message(amount):
    global msg_render_height
    msg_render_height = main.clamp(msg_render_height + amount, 0, len(game_msgs) - consts.MSG_HEIGHT - 1)

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

def render_side_panel(acc_mod=1.0):
    import loot
    import spells
    global selected_monster

    libtcod.console_set_default_background(side_panel, libtcod.black)
    libtcod.console_clear(side_panel)

    render_bar(2, 2, consts.BAR_WIDTH, 'HP', player.instance.fighter.hp, player.instance.fighter.max_hp,
               libtcod.dark_red, libtcod.darker_red, align=libtcod.LEFT)
    # Display armor/shred
    armor_string = 'AR:' + str(player.instance.fighter.armor)
    if player.instance.fighter.shred > 0:
        libtcod.console_set_default_foreground(side_panel, libtcod.yellow)
    libtcod.console_print_ex(side_panel, consts.SIDE_PANEL_WIDTH - 4, 2, libtcod.BKGND_DEFAULT, libtcod.RIGHT, armor_string)

    render_bar(2, 3, consts.BAR_WIDTH, 'Stamina', player.instance.fighter.stamina, player.instance.fighter.max_stamina,
               libtcod.dark_green, libtcod.darker_green)

    # Breath
    if player.instance.fighter.breath < player.instance.fighter.max_breath:
        breath_text = ''
        for num in range(0, player.instance.fighter.breath):
            breath_text += 'O '
        libtcod.console_set_default_foreground(side_panel, libtcod.dark_blue)
        libtcod.console_print(side_panel, 2, 4, breath_text)
        libtcod.console_set_default_foreground(side_panel, libtcod.white)

    # Base stats
    libtcod.console_print(side_panel, 2, 6, 'INT: ' + str(player.instance.player_stats.int))
    libtcod.console_print(side_panel, 2, 7, 'WIS: ' + str(player.instance.player_stats.wiz))
    libtcod.console_print(side_panel, 2, 8, 'STR: ' + str(player.instance.player_stats.str))
    libtcod.console_print(side_panel, 2, 9, 'AGI: ' + str(player.instance.player_stats.agi))

    # Level/XP
    libtcod.console_print(side_panel, 2, 11, 'Lvl: ' + str(player.instance.level))
    libtcod.console_print(side_panel, 2, 12, 'XP:  ' + str(player.instance.fighter.xp))
    libtcod.console_print(side_panel, 2, 13, 'SP:  ' + str(player.instance.skill_points))

    # Mana
    libtcod.console_print(side_panel, 2, 14, 'Essence:')
    libtcod.console_put_char(side_panel, 2, 15, '[')
    x = 4
    for m in range(len(player.instance.essence)):
        libtcod.console_set_default_foreground(side_panel, spells.essence_colors[player.instance.essence[m]])
        libtcod.console_put_char(side_panel, x, 15, '*')
        x += 2
    for m in range(player.instance.player_stats.max_essence - len(player.instance.essence)):
        libtcod.console_set_default_foreground(side_panel, libtcod.dark_grey)
        libtcod.console_put_char(side_panel, x, 15, '.')
        x += 2
    libtcod.console_set_default_foreground(side_panel, libtcod.white)
    libtcod.console_put_char(side_panel, x, 15, ']')

    drawHeight = 17

    # Equip Load
    libtcod.console_print(side_panel, 2, drawHeight, 'Equip Load: %d/%d' % (player.instance.fighter.equip_weight, player.instance.fighter.max_equip_weight))
    drawHeight += 2

    # Weapon
    libtcod.console_print(side_panel, 2, drawHeight, 'Weapon:')
    drawHeight += 1
    weapon = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
    if weapon is None:
        weapon_string = 'Fists'
        weapon_color = libtcod.gray
    else:
        weapon_string = weapon.owner.name.title()
        weapon_color = loot.qualities[weapon.quality]['color']
    weapon_string_height = libtcod.console_get_height_rect(side_panel, 2, drawHeight, consts.SIDE_PANEL_WIDTH - 3, 5, weapon_string)
    libtcod.console_set_default_foreground(side_panel, weapon_color)
    libtcod.console_print_rect_ex(side_panel, 2, drawHeight, consts.SIDE_PANEL_WIDTH - 3, weapon_string_height, libtcod.BKGND_DEFAULT, libtcod.LEFT, weapon_string)
    libtcod.console_set_default_foreground(side_panel, libtcod.white)
    drawHeight += weapon_string_height + 1

    seperator_height = drawHeight
    drawHeight += 2

    # Status effects
    if len(player.instance.fighter.status_effects) > 0:
        for effect in player.instance.fighter.status_effects:
            libtcod.console_set_default_foreground(side_panel, effect.color)
            effect_str = effect.name
            if effect.stacks > 1:
                effect_str += ' x' + str(effect.stacks)
            if effect.time_limit is not None:
                effect_str += ' (' + str(effect.time_limit) + ')'
            libtcod.console_print(side_panel, 2, drawHeight, effect_str.capitalize())
            drawHeight += 1
        drawHeight += 1
        libtcod.console_set_default_foreground(side_panel, libtcod.white)

    # Objects here
    libtcod.console_print(side_panel, 2, drawHeight, 'Objects here:')
    drawHeight += 1
    objects_here = main.get_objects(player.instance.x, player.instance.y, lambda o: o is not player.instance)
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
            libtcod.console_print(side_panel, 4, drawHeight, line.title())
            drawHeight += 1
        libtcod.console_set_default_foreground(side_panel, libtcod.gray)
        if end < len(objects_here) - 1:
            libtcod.console_print(side_panel, 4, drawHeight, '...' + str(len(objects_here) - 7) + ' more...')
            drawHeight += 1
    libtcod.console_set_default_foreground(side_panel, libtcod.gray)
    libtcod.console_print(side_panel, 4, drawHeight, main.current_map.tiles[player.instance.x][player.instance.y].name.title())
    drawHeight += 2
    libtcod.console_set_default_foreground(side_panel, libtcod.white)

    # Selected Monster
    if selected_monster is not None and selected_monster.fighter is not None:
        drawHeight = consts.SIDE_PANEL_HEIGHT - 16
        libtcod.console_print(side_panel, 2, drawHeight, selected_monster.name.title())
        drawHeight += 1
        libtcod.console_set_default_foreground(side_panel, libtcod.gray)
        if selected_monster.behavior:
            if selected_monster.fighter.team == 'ally':
                ai_state_text = 'Ally'
            else:
                ai_state_text = selected_monster.behavior.ai_state.capitalize()
            libtcod.console_print(side_panel, 2, drawHeight, ai_state_text)
        drawHeight += 2
        if selected_monster.fighter.team == 'ally':
            health_bar_color = libtcod.darker_blue
            health_bar_bkgnd_color = libtcod.darkest_blue
        else:
            health_bar_color = libtcod.dark_red
            health_bar_bkgnd_color = libtcod.darker_red
        render_bar(2, drawHeight, consts.BAR_WIDTH, 'HP', selected_monster.fighter.hp, selected_monster.fighter.max_hp,
                   health_bar_color, health_bar_bkgnd_color, align=libtcod.LEFT)
        libtcod.console_set_default_foreground(side_panel, libtcod.white)
        armor_string = 'AR:' + str(selected_monster.fighter.armor)
        if selected_monster.fighter.shred > 0:
            libtcod.console_set_default_foreground(side_panel, libtcod.yellow)
        libtcod.console_print_ex(side_panel, consts.SIDE_PANEL_WIDTH - 4, drawHeight, libtcod.BKGND_DEFAULT, libtcod.RIGHT,
                                     armor_string)

        drawHeight += 1
        libtcod.console_set_default_foreground(side_panel, libtcod.gray)
        s = 'Your Accuracy: %d%%' % int(100.0 * combat.get_chance_to_hit(selected_monster, player.instance.fighter.accuracy * acc_mod))
        s += '%'  # Yeah I know I suck with string formatting. Whatever, this works.  -T
        libtcod.console_print(side_panel, 2, drawHeight, s)
        drawHeight += 1
        if selected_monster.fighter.accuracy > 0:
            s = "Its Accuracy : %d%%" % int(100.0 * combat.get_chance_to_hit(player.instance, selected_monster.fighter.accuracy))
            s += '%'
            libtcod.console_print(side_panel, 2, drawHeight, s)
        else:
            libtcod.console_print(side_panel, 2, drawHeight, 'Does not attack')

        drawHeight += 2
        for effect in selected_monster.fighter.status_effects:
            libtcod.console_set_default_foreground(side_panel, effect.color)
            effect_str = effect.name
            if effect.time_limit is not None:
                effect_str += ' (' + str(effect.time_limit) + ')'
            libtcod.console_print(side_panel, 2, drawHeight, effect_str.capitalize())
            drawHeight += 1

    draw_border(side_panel, 0, 0, consts.SIDE_PANEL_WIDTH, consts.SIDE_PANEL_HEIGHT)
    for x in range(1, consts.SIDE_PANEL_WIDTH - 1):
        libtcod.console_put_char(side_panel, x, seperator_height, libtcod.CHAR_HLINE)
    libtcod.console_put_char(side_panel, 0, seperator_height, 199)
    libtcod.console_put_char(side_panel, consts.SIDE_PANEL_WIDTH - 1, seperator_height, 182)
    libtcod.console_put_char(side_panel, consts.SIDE_PANEL_WIDTH - 1, consts.PANEL_HEIGHT, 4)

    libtcod.console_blit(side_panel, 0, 0, consts.SIDE_PANEL_WIDTH, consts.SIDE_PANEL_HEIGHT, 0, consts.SIDE_PANEL_X,
                         consts.SIDE_PANEL_Y)


def render_message_panel():
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    y = 1
    start = -(consts.MSG_HEIGHT + msg_render_height + 1)
    if start + consts.MSG_HEIGHT + 1 >= 0:
        render_msgs = game_msgs[start:]
    else:
        render_msgs = game_msgs[start:start + consts.MSG_HEIGHT + 1]
    for (line, color) in render_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, consts.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    libtcod.console_set_default_foreground(panel, libtcod.light_grey)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    draw_border(panel, 0, 0, consts.PANEL_WIDTH, consts.PANEL_HEIGHT + 1)

    libtcod.console_blit(panel, 0, 0, consts.PANEL_WIDTH, consts.PANEL_HEIGHT, 0, consts.PANEL_X, consts.PANEL_Y)


def render_action_panel():
    libtcod.console_set_default_background(action_panel, libtcod.black)
    libtcod.console_clear(action_panel)

    if show_action_panel:

        draw_height = 1
        libtcod.console_set_default_foreground(action_panel, libtcod.white)

        # Header
        libtcod.console_print(action_panel, 1, draw_height, 'ACTIONS')
        draw_height += 2
        # Actions
        libtcod.console_print(action_panel, 1, draw_height, '(a) Abilities')
        draw_height += 2
        libtcod.console_print(action_panel, 1, draw_height, '(i) Inventory')
        draw_height += 2
        libtcod.console_print(action_panel, 1, draw_height, '(e) Use Item')
        draw_height += 2
        libtcod.console_print(action_panel, 1, draw_height, '(d) Drop Item')
        draw_height += 2
        libtcod.console_print(action_panel, 1, draw_height, '(P) Perks')
        draw_height += 2
        libtcod.console_print(action_panel, 1, draw_height, '(v) Jump')
        draw_height += 2
        libtcod.console_print(action_panel, 1, draw_height, '(x) Examine')
        draw_height += 2
        libtcod.console_print(action_panel, 1, draw_height, '(TAB) Toggle\n    Selection')
        draw_height += 3
        libtcod.console_print(action_panel, 1, draw_height, '(M) Map')
        draw_height += 2
        # Get/Interact
        items_here = main.get_objects(player.instance.x, player.instance.y, condition=lambda o: o.item)
        if len(items_here) > 0:
            libtcod.console_print(action_panel, 1, draw_height, '(g) Pick Up Item')
            draw_height += 2
        else:
            essence_here = main.get_objects(player.instance.x, player.instance.y,
                                            condition=lambda o: hasattr(o, 'essence_type'))
            if len(essence_here) > 0:
                libtcod.console_print(action_panel, 1, draw_height, '(g) Pick Up Essence')
                draw_height += 2
            else:
                interactable_here = main.get_objects(player.instance.x, player.instance.y,
                                                     condition=lambda o: o.interact, distance=1)
                if len(interactable_here) > 0:
                    libtcod.console_print(action_panel, 1, draw_height, '(g) ')
                    text = 'Use %s' % interactable_here[0].name.title()
                    h = libtcod.console_get_height_rect(action_panel, 5, 0, consts.ACTION_MENU_WIDTH - 6, 3, text)
                    libtcod.console_print_rect(action_panel, 5, draw_height, consts.ACTION_MENU_WIDTH - 6, h, text)
                    draw_height += h + 1
        # Spells
        left_hand = main.get_equipped_in_slot(player.instance.fighter.inventory, 'left hand')
        if hasattr(left_hand, 'spell_list') and len(left_hand.spell_list) > 0:
            libtcod.console_print(action_panel, 1, draw_height, '(z) Cast Spell')
            draw_height += 2
            libtcod.console_print(action_panel, 1, draw_height, '(m) Meditate')
            draw_height += 2
        # Character Info
        libtcod.console_print(action_panel, 1, draw_height, '(c) Character \n    Info')
        draw_height += 3
        # Hide Panel
        libtcod.console_print(action_panel, 1, draw_height, '(A) Hide Panel')
        draw_height += 2


        draw_border(action_panel, 0, 0, consts.ACTION_MENU_WIDTH, consts.ACTION_MENU_HEIGHT)

        libtcod.console_blit(action_panel, 0, 0, consts.ACTION_MENU_WIDTH, consts.ACTION_MENU_HEIGHT, 0, consts.ACTION_MENU_X, consts.ACTION_MENU_Y)

    else:
        draw_border(action_panel, 0, consts.ACTION_MENU_HEIGHT - 3, consts.ACTION_MENU_WIDTH, 3)

        libtcod.console_set_default_foreground(action_panel, libtcod.white)
        libtcod.console_print_ex(action_panel, consts.ACTION_MENU_WIDTH / 2 - 2, consts.ACTION_MENU_HEIGHT - 2, libtcod.BKGND_DEFAULT, libtcod.CENTER, '(A) Actions')

        libtcod.console_blit(action_panel, 0, consts.ACTION_MENU_HEIGHT - 3, consts.ACTION_MENU_WIDTH, 3, 0,
                             consts.ACTION_MENU_X, consts.ACTION_MENU_Y + consts.ACTION_MENU_HEIGHT - 3)


def render_ui_overlay():
    global display_ticker, overlay_text

    mouse = main.mouse

    libtcod.console_set_default_background(overlay, libtcod.black)
    libtcod.console_clear(overlay)

    under = get_names_under_mouse()

    if under != '':
        unders = under.split(', ')
        y = 1
        max_width = 0
        for line in unders:
            libtcod.console_print(overlay, mouse.cx, mouse.cy + y, line.capitalize())
            if len(line) > max_width: max_width = len(line)
            y += 1
        libtcod.console_blit(overlay, mouse.cx, mouse.cy + 1, max_width, y - 1, 0, mouse.cx, mouse.cy + 1, 1.0, 0.5)

    if overlay_text is not None:
        libtcod.console_set_default_foreground(overlay, libtcod.black)
        libtcod.console_set_default_background(overlay, libtcod.black)
        libtcod.console_clear(overlay)
        libtcod.console_set_default_foreground(overlay, libtcod.white)
        text_width = len(overlay_text)
        libtcod.console_print(overlay, 0, 0, overlay_text)
        if display_ticker > fade_value:
            fade_factor = 1.0
        else:
            fade_factor = 1.0 - float(fade_value - display_ticker) / float(fade_value)
        libtcod.console_blit(overlay, 0, 0, text_width, 1, 0, consts.MAP_VIEWPORT_X + consts.MAP_VIEWPORT_WIDTH / 2 -
                             text_width / 2, consts.MAP_VIEWPORT_Y + 20, fade_factor, 0.0)
        display_ticker -= 1
        if display_ticker == 0:
            overlay_text = None


def target_tile(max_range=None, targeting_type='pick', acc_mod=1.0, default_target=None):
    global selected_monster
    mouse = main.mouse
    key = main.key

    if default_target is None:
        x = player.instance.x
        y = player.instance.y
    else:
        x = default_target[0]
        y = default_target[1]
    cursor_x = x
    cursor_y = y
    oldMouseX = mouse.cx
    oldMouseY = mouse.cy
    offsetx, offsety = player.instance.x - consts.MAP_VIEWPORT_WIDTH / 2, player.instance.y - consts.MAP_VIEWPORT_HEIGHT / 2
    selected_x = x
    selected_y = y
    libtcod.console_set_default_background(0, libtcod.black)
    libtcod.console_clear(0)
    main.render_map()
    render_side_panel()
    render_message_panel()
    affected_tiles = []

    while True:
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_side_panel(acc_mod=acc_mod)
        main.render_map()

        # Render range shading
        libtcod.console_clear(overlay)
        libtcod.console_set_key_color(overlay, libtcod.magenta)
        if max_range is not None:
            for draw_x in range(consts.MAP_WIDTH):
                for draw_y in range(consts.MAP_HEIGHT):
                    if round((player.instance.distance(draw_x, draw_y))) > max_range:
                        libtcod.console_put_char_ex(overlay, draw_x, draw_y, ' ', libtcod.light_yellow, libtcod.black)
                    else:
                        libtcod.console_put_char_ex(overlay, draw_x, draw_y, ' ', libtcod.light_yellow, libtcod.magenta)
            libtcod.console_blit(overlay, player.instance.x - consts.MAP_VIEWPORT_WIDTH / 2,
                                 player.instance.y - consts.MAP_VIEWPORT_HEIGHT / 2,
                                 consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT, 0,
                                 consts.MAP_VIEWPORT_X, consts.MAP_VIEWPORT_Y, 0.0, 0.2)

        # Render cursor
        libtcod.console_set_default_background(overlay, libtcod.magenta)
        libtcod.console_clear(overlay)
        if targeting_type == 'beam' or targeting_type == 'beam_interrupt':
            libtcod.line_init(player.instance.x, player.instance.y, cursor_x, cursor_y)
            line_x, line_y = libtcod.line_step()
            while (not line_x is None):
                libtcod.console_put_char_ex(overlay, line_x - offsetx, line_y - offsety, ' ', libtcod.white, libtcod.yellow)
                line_x, line_y = libtcod.line_step()
        libtcod.console_put_char_ex(overlay, selected_x - offsetx, selected_y - offsety, ' ', libtcod.light_yellow,
                                    libtcod.white)
        if targeting_type == 'cone':
            affected_tiles = []
            selected_angle = math.atan2(-(selected_y - player.instance.y), selected_x - player.instance.x)
            if selected_angle < 0: selected_angle += math.pi * 2
            for draw_x in range(max(player.instance.x - max_range, 0), min(player.instance.x + max_range, consts.MAP_WIDTH - 1) + 1):
                for draw_y in range(max(player.instance.y - max_range, 0), min(player.instance.y + max_range, consts.MAP_HEIGHT - 1) + 1):
                    if draw_x == player.instance.x and draw_y == player.instance.y:
                        continue
                    if not fov.player_can_see(draw_x, draw_y):
                        continue
                    this_angle = math.atan2(-(draw_y - player.instance.y), draw_x - player.instance.x)
                    if this_angle < 0: this_angle += math.pi * 2
                    phi = abs(this_angle - selected_angle)
                    if phi > math.pi:
                        phi = 2 * math.pi - phi

                    if phi <= math.pi / 4 and round(player.instance.distance(draw_x, draw_y)) <= max_range:
                        affected_tiles.append((draw_x, draw_y))
                        libtcod.console_put_char_ex(overlay, draw_x - offsetx, draw_y - offsety, ' ', libtcod.white, libtcod.yellow)

        libtcod.console_put_char_ex(overlay, selected_x - offsetx, selected_y - offsety, ' ',
                                    libtcod.light_yellow,
                                    libtcod.white)

        libtcod.console_blit(overlay, 0, 0, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT, 0, consts.MAP_VIEWPORT_X,
                             consts.MAP_VIEWPORT_Y, 0, 0.5)

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
            mouse_pos = mouse.cx + offsetx - consts.MAP_VIEWPORT_X, mouse.cy + offsety - consts.MAP_VIEWPORT_Y
            if main.in_bounds(mouse_pos[0], mouse_pos[1]):
                x = mouse_pos[0]
                y = mouse_pos[1]

        cursor_x = x
        cursor_y = y

        monster_at_tile = main.get_monster_at_tile(cursor_x, cursor_y)
        if monster_at_tile is not None:
            select_monster(monster_at_tile)

        selected_x = cursor_x
        selected_y = cursor_y
        beam_values = []

        if targeting_type == 'beam_interrupt':
            selected_x, selected_y = main.beam_interrupt(player.instance.x, player.instance.y, cursor_x, cursor_y)
        elif targeting_type == 'beam':
            beam_values = main.beam(player.instance.x, player.instance.y, cursor_x, cursor_y)
            selected_x, selected_y = beam_values[len(beam_values) - 1]

        if (mouse.lbutton_pressed or key.vk == libtcod.KEY_ENTER) and fov.player_can_see(x, y):
            if max_range is None or round((player.instance.distance(x, y))) <= max_range:
                if targeting_type == 'beam':
                    return beam_values
                elif targeting_type == 'cone':
                    return affected_tiles
                else:
                    return selected_x, selected_y
            else:
                return None, None  # out of range

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return None, None  # cancelled

        oldMouseX = mouse.cx
        oldMouseY = mouse.cy

def inspect_inventory():
    chosen_item = inventory_menu('Select which item?')
    if chosen_item is not None:
        options = chosen_item.get_options_list()
        menu_choice = menu(chosen_item.owner.name, options, 50, render_func=chosen_item.owner.print_description)
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
            elif 'Imbue' in options[menu_choice]: #has some extra text about the level cost, so use in
                chosen_item.owner.equipment.level_up()
            else:
                return inspect_inventory()
        else:
            return inspect_inventory()
    return 'didnt-take-turn'

def skill_menu():

    scroll_height = 0
    selected_index = 1

    libtcod.console_clear(window)
    main.render_all()
    libtcod.console_flush()

    skill_categories = []
    menu_lines = []

    mouse = main.mouse
    key = main.key

    show_available = False

    for k in perks.perk_keys:
        skill = perks.perk_list[k]
        if not skill['category'] in skill_categories:
            skill_categories.append(skill['category'])
            menu_lines.append(None)
        menu_lines.append(k)
    sub_height = len(skill_categories) + len(perks.perk_keys)
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
        title_text = 'Browsing skills... [%d points available]' % player.instance.skill_points
        libtcod.console_print(window, 1, 1, title_text)
        if show_available:
            libtcod.console_print(window, 1, 3, '[TAB] - Show All')
        else:
            libtcod.console_print(window, 1, 3, '[TAB] - Show Available')
        y = 0
        draw_border(window, 0, 0, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT - 5)
        draw_border(window, 0, consts.MAP_VIEWPORT_HEIGHT - 6, consts.MAP_VIEWPORT_WIDTH, 6)

        # Draw scrollable menu
        if len(skill_categories) <= 0:
            libtcod.console_set_default_foreground(window, libtcod.light_gray)
            libtcod.console_print(window, 2, 6, 'No skills available.')
        else:

            for skill_category in skill_categories:
                # Draw category dividers
                libtcod.console_set_default_foreground(sub_window, libtcod.light_gray)
                for i in range(consts.MAP_VIEWPORT_WIDTH):
                    libtcod.console_put_char_ex(sub_window, i, y, libtcod.CHAR_HLINE, libtcod.gray, libtcod.black)
                libtcod.console_put_char_ex(sub_window, 0, y, 199, libtcod.gray, libtcod.black)
                libtcod.console_put_char_ex(sub_window, consts.MAP_VIEWPORT_WIDTH - 1, y, 182, libtcod.gray, libtcod.black)
                libtcod.console_print_ex(sub_window, 3, y, libtcod.black, libtcod.LEFT, skill_category.upper())
                y += 1
                # Draw all skills in category
                for i in range(len(perks.perk_keys)):
                    k = perks.perk_keys[i]
                    skill = perks.perk_list[k]
                    if k not in menu_lines:
                        continue
                    if skill['category'] == skill_category:

                        if y == selected_index:
                            libtcod.console_set_default_background(sub_window, libtcod.white)
                            libtcod.console_set_default_foreground(sub_window, libtcod.black)
                            for j in range(1, consts.MAP_VIEWPORT_WIDTH - 1):
                                libtcod.console_put_char_ex(sub_window, j, y, ' ', libtcod.black, libtcod.white)
                        else:
                            libtcod.console_set_default_background(sub_window, libtcod.black)
                            if k in main.learned_skills.keys():
                                libtcod.console_set_default_foreground(sub_window, libtcod.white)
                            elif skill['sp_cost'] <= player.instance.skill_points and perks.meets_requirements(k):
                                libtcod.console_set_default_foreground(sub_window, libtcod.dark_gray)
                            else:
                                libtcod.console_set_default_foreground(sub_window, libtcod.darker_red)

                        name_string = "({}) {}".format(skill['sp_cost'],skill['name'].title())
                        libtcod.console_print_ex(sub_window, 5, y, libtcod.BKGND_SET, libtcod.LEFT, name_string)
                        for s in main.learned_skills.keys():
                            if s == k:
                                rank = main.learned_skills[s]
                                libtcod.console_set_default_foreground(sub_window, libtcod.dark_blue)
                                if perks.perk_list[s]['max_rank'] > 1:
                                    if rank == perks.perk_list[s]['max_rank']:
                                        tag_text = ' [MASTERED]'
                                    else:
                                        tag_text = ' [RANK %s]' % str(rank)
                                else:
                                    tag_text = ' [LEARNED]'
                                libtcod.console_print_ex(sub_window, 6 + len(name_string), y, libtcod.BKGND_SET, libtcod.LEFT, tag_text)
                                break
                        y += 1
            # Blit sub_window to window. Select based on scroll height
            libtcod.console_blit(sub_window, 0, scroll_height, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT - 10, window, 0, 4, 1.0, 1.0)

            # print description
            selected_skill = menu_lines[selected_index]
            can_purchase = perks.meets_requirements(selected_skill) and player.instance.skill_points >= perks.perk_list[selected_skill]['sp_cost']
            if can_purchase:
                libtcod.console_set_default_foreground(window, libtcod.dark_green)
            else:
                libtcod.console_set_default_foreground(window, libtcod.darker_red)

            require_string = ''
            req = perks.perk_list[selected_skill].get('requires')
            if req is not None:
                req = req.split(' ')
                lvl = ''
                if len(req) > 1:
                    lvl = req[1]
                require_string = ', Requires: %s %s' % (perks.perk_list[req[0]]['name'], lvl)

            libtcod.console_print(window, 2, consts.MAP_VIEWPORT_HEIGHT - 5, 'Cost: %dSP%s' % (perks.perk_list[selected_skill]['sp_cost'], require_string))

            libtcod.console_set_default_foreground(window, libtcod.white)
            rank = main.has_skill(selected_skill)
            max_rank = perks.perk_list[selected_skill]['max_rank']
            if rank == max_rank:
                desc_index = max_rank - 1
            else:
                desc_index = rank
            desc = perks.perk_list[selected_skill]['description'][desc_index]

            libtcod.console_print_rect(window, 1, consts.MAP_VIEWPORT_HEIGHT - 4, consts.MAP_VIEWPORT_WIDTH - 2, 5, desc)

            # print scroll bar
            libtcod.console_set_default_foreground(window, libtcod.gray)
            libtcod.console_put_char(window, consts.MAP_VIEWPORT_WIDTH - 2, 4, 30)
            libtcod.console_put_char(window, consts.MAP_VIEWPORT_WIDTH - 2, consts.MAP_VIEWPORT_HEIGHT - 7, 31)
            for i in range(consts.MAP_VIEWPORT_HEIGHT - 12):
                libtcod.console_put_char(window, consts.MAP_VIEWPORT_WIDTH - 2, 5 + i, libtcod.CHAR_VLINE)
            bar_height = int(float((consts.MAP_VIEWPORT_HEIGHT - 12) ** 2) / float(sub_height))
            bar_height = main.clamp(bar_height, 1, consts.MAP_VIEWPORT_HEIGHT - 12)
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
            if perks.meets_requirements(menu_lines[selected_index]) and \
                            main.has_skill(menu_lines[selected_index]) < perks.perk_list[menu_lines[selected_index]]['max_rank']:
                return menu_lines[selected_index] # returns a Perk name
        # Down arrow increments selection index
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP2 or key.vk == libtcod.KEY_KP6:
            #selected_index = min(selected_index + 1, len(menu_lines) - 1)
            if len(menu_lines) > 0:
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
        elif key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP8 or key.vk == libtcod.KEY_KP4:
            #selected_index = max(selected_index - 1, 0)
            if len(menu_lines) > 0:
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
        elif key.vk == libtcod.KEY_TAB:
            show_available = not show_available
            scroll_height = 0
            selected_index = 1
            menu_lines = []
            skill_categories = []
            for k in perks.perk_keys:
                skill = perks.perk_list[k]
                if show_available and (player.instance.skill_points < skill['sp_cost'] or not perks.meets_requirements(k)):
                    continue
                if not skill['category'] in skill_categories:
                    skill_categories.append(skill['category'])
                    menu_lines.append(None)
                menu_lines.append(k)
            sub_height = len(skill_categories) + len(perks.perk_keys)
            scroll_limit = sub_height - (consts.MAP_VIEWPORT_HEIGHT - 10)

def examine(x=None, y=None):
    if x is None or y is None:
        x, y = target_tile()
    if x is not None and y is not None:
        obj = main.object_at_coords(x, y)
        if obj is not None:
            if isinstance(obj, main.GameObject):
                desc = obj.name.title()
                if obj.name == 'player':
                    desc = 'You'
                if hasattr(obj, 'fighter') and obj.fighter is not None and obj is not player.instance and \
                        hasattr(obj.fighter, 'inventory') and obj.fighter.inventory is not None and len(obj.fighter.inventory) > 0:
                    desc = desc + '\n\nInventory: '
                    for item in obj.fighter.inventory:
                        desc = desc + item.name + ', '
                menu(desc, ['back'], 50, render_func=obj.print_description)
            else:
                desc = obj.name.title() + '\n\n' + main.get_description(obj)
                menu(desc, ['back'], 50)

def show_ability_screen():
    import abilities
    opts = [abilities.default_abilities['attack']]
    # Weapon ability, or bash if none
    weapon = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')

    if weapon is not None and weapon.owner.item.ability is not None:
        opts.append(weapon.owner.item.ability)

    #if weapon is not None and weapon.ctrl_attack is not None:
    #    opts.append(weapon.ctrl_attack)
    else:
        opts.append(abilities.default_abilities['bash'])
    # Other equipment abilities
    for i in main.get_all_equipped(player.instance.fighter.inventory):
        if i is not weapon and i.owner.item.ability is not None:
            opts.append(i.owner.item.ability)
    opts += [v for k,v in abilities.default_abilities.items() if k not in ['attack','bash']]
    index = menu('Abilities',[opt.name for opt in opts],20)
    if index is not None:
        choice = opts[index]
        if choice is not None:
            return choice.use(player.instance)
    return 'didnt-take-turn'


map_offsets = {
    'north' : (0, -1, 0),
    'south' : (0, 1, 0),
    'east' : (1, 0, 0),
    'west' : (-1, 0, 0),
    'down' : (0, 0, 1),
    'up' : (0, 0, -1)
}

def show_map_screen():
    import world
    import dungeon

    console = libtcod.console_new(31, 31)
    canvas = libtcod.console_new(50, 50)

    # assemble map array (only horizontal for now)
    map_cells = {(0, 0, 0) : world.world_maps['beach']}
    q = [(0, 0, 0)]
    layers = [0]
    min_x = 0
    min_y = 0
    max_x = 0
    max_y = 0
    current_room_pos = (0, 0, 0)
    while len(q) > 0:
        current = q.pop(0)
        for l in map_cells[current].links:
            pos = (current[0] + map_offsets[l[0]][0], current[1] + map_offsets[l[0]][1], current[2] + map_offsets[l[0]][2])
            if pos in map_cells.keys():
                continue
            if pos[0] < min_x: min_x = pos[0]
            if pos[0] > max_x: max_x = pos[0]
            if pos[1] < min_y: min_y = pos[1]
            if pos[1] > max_y: max_y = pos[1]
            if pos[2] not in layers: layers.append(pos[2])
            map_cells[pos] = l[1]
            q.append(pos)
            if map_cells[pos] == main.current_map:
                current_room_pos = pos
    offset = (min_x * 4, min_y * 4)
    render_pos = 14 + offset[0] - 4 * current_room_pos[0], \
                 14 + offset[1] - 4 * current_room_pos[1]

    done = False
    draw_z = current_room_pos[2]

    while(not done):

        # draw the map
        libtcod.console_set_default_background(console, libtcod.black)
        libtcod.console_set_default_background(canvas, libtcod.black)
        libtcod.console_clear(canvas)
        libtcod.console_clear(console)
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if (x, y, draw_z) not in map_cells.keys() or not map_cells[(x, y, draw_z)].visited:
                    continue
                color = dungeon.branches[map_cells[(x,y,draw_z)].branch]['map_color']
                for d_y in range(4 * y, 4 * y + 3):
                    for d_x in range(4 * x, 4 * x + 3):
                        libtcod.console_put_char_ex(canvas, d_x - offset[0], d_y - offset[1], ' ', color, color)
                if x == current_room_pos[0] and y == current_room_pos[1] and draw_z == current_room_pos[2]:
                    libtcod.console_set_default_foreground(canvas, libtcod.white)
                    libtcod.console_put_char(canvas, 4 * x + 1 - offset[0], 4 * y + 1 - offset[1], '@')
                for l in map_cells[(x, y, draw_z)].links:
                    pos = (2 * map_offsets[l[0]][0], 2 * map_offsets[l[0]][1])
                    if l[0] == 'north' or l[0] == 'south':
                        link_char = libtcod.CHAR_DVLINE
                    elif l[0] == 'east' or l[0] == 'west':
                        link_char = libtcod.CHAR_DHLINE
                    elif l[0] == 'up':
                        link_char = '<'
                        pos = pos[0], pos[1] - 1
                    else:
                        link_char = '>'
                        pos = pos[0], pos[1] + 1
                    libtcod.console_put_char(canvas, 4 * x + 1 + pos[0] - offset[0], 4 * y + 1 + pos[1] - offset[1], link_char)

        libtcod.console_blit(canvas, 0, 0, 50, 50, console, render_pos[0], render_pos[1])

        draw_border(console, 0, 0, 31, 31)
        libtcod.console_blit(console, 0, 0, 31, 31, 0,
                             consts.MAP_VIEWPORT_X + consts.MAP_VIEWPORT_WIDTH / 2 - 15,
                             consts.MAP_VIEWPORT_Y + consts.MAP_VIEWPORT_HEIGHT / 2 - 15)
        libtcod.console_flush()

        # Handle input and return index
        key = libtcod.console_wait_for_keypress(True)
        if key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            render_pos = render_pos[0] + 1, render_pos[1]
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            render_pos = render_pos[0] - 1, render_pos[1]
        elif key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            render_pos = render_pos[0], render_pos[1] + 1
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            render_pos = render_pos[0], render_pos[1] - 1
        elif key.vk == libtcod.KEY_KP7:
            render_pos = render_pos[0] + 1, render_pos[1] + 1
        elif key.vk == libtcod.KEY_KP9:
            render_pos = render_pos[0] - 1, render_pos[1] + 1
        elif key.vk == libtcod.KEY_KP1:
            render_pos = render_pos[0] + 1, render_pos[1] - 1
        elif key.vk == libtcod.KEY_KP3:
            render_pos = render_pos[0] - 1, render_pos[1] - 1
        elif chr(key.c) == '.':
            if draw_z + 1 in layers:
                draw_z += 1
        elif chr(key.c) == ',':
            if draw_z - 1 in layers:
                draw_z -= 1
        else:
            done = True

def display_fading_text(text, display_time, fade_time):
    global fade_value, display_ticker, overlay_text
    fade_value = fade_time
    display_ticker = display_time
    overlay_text = text


def render_projectile(start, end, color, character=None):

    if character is None: bolt_char = chr(7)
    else: bolt_char = character
    bolt = main.GameObject(start[0], start[1], bolt_char, 'bolt', color=color)

    line = main.beam(start[0], start[1], end[0], end[1])
    main.current_map.add_object(bolt)
    prev = line[0][0], line[0][1]

    for p in line:
        bolt.set_position(p[0], p[1])
        if character is None:
            if bolt.x == prev[0] and bolt.y == prev[1]:
                pass
            elif bolt.x == prev[0] and bolt.y != prev[1]:
                bolt.char = chr(179)  # vertical line
            elif bolt.x != prev[0] and bolt.y == prev[1]:
                bolt.char = chr(196)  # horizontal line
            elif (bolt.y - prev[1]) / (bolt.x - prev[0]) < 0:
                bolt.char = '/'
            else:
                bolt.char = '\\'
        main.render_map()
        libtcod.console_flush()
        prev = bolt.x, bolt.y
    bolt.destroy()

def choose_essence_from_pool(charm_data):
    options_ex = collections.OrderedDict()
    letter_index = ord('a')
    for essence in player.instance.essence:
        options_ex[chr(letter_index)] = [{
            'category': 'essence',
            'text': essence,
            'color': spells.essence_colors[essence],
        },
            {
                'category': 'effect',
                'text': charm_data[essence]['name'],
                'color': libtcod.white,
            }]
        letter_index += 1
    index = menu_ex('Select essence:', options_ex, 50)

    if index is None:
        return None
    else:
        return player.instance.essence[index]

show_action_panel = True
overlay = libtcod.console_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)
panel = libtcod.console_new(consts.PANEL_WIDTH, consts.PANEL_HEIGHT)
side_panel = libtcod.console_new(consts.SIDE_PANEL_WIDTH, consts.SIDE_PANEL_HEIGHT)
action_panel = libtcod.console_new(consts.ACTION_MENU_WIDTH, consts.ACTION_MENU_HEIGHT)
window = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
selected_monster = None
game_msgs = []
msg_render_height = 0
fade_value = 0
display_ticker = 0
overlay_text = None
