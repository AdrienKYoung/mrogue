import game as main
import libtcodpy as libtcod
import consts
import textwrap
import fov
import loot
import spells
import abilities

def msgbox(text, width=50):
    menu(text, [], width)


def menu(header, options, width, x_center=None, render_func=None):

    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    no_header = False
    header_height = libtcod.console_get_height_rect(main.con, 0, 0, width - 2, consts.SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
        no_header = True

    height = len(options) + header_height + 2
    if not no_header:
        height += 1
    width += 2

    libtcod.console_clear(window)
    main.render_all()
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

def inventory_menu(header):

    player = main.player

    libtcod.console_clear(window)
    main.render_all()
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
                                     loot.item_categories[item_category]['plural'].title())
            y += 1
            for item in player.fighter.inventory:
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
    if 0 <= index < len(player.fighter.inventory):
        return menu_items[index].item
    return None


def auto_target_monster():
    global selected_monster

    if selected_monster is None:
        monster = main.closest_monster(consts.TORCH_RADIUS)
        if monster is not None:
            select_monster(monster)
    elif not fov.player_can_see(selected_monster.x, selected_monster.y):
        main.changed_tiles.append((selected_monster.x, selected_monster.y))
        selected_monster = None


def target_next_monster():
    global selected_monster

    if selected_monster is not None:
        main.changed_tiles.append((selected_monster.x, selected_monster.y))

    nearby = []
    for obj in main.objects:
        if fov.player_can_see(obj.x, obj.y) and obj.fighter and obj is not main.player:
            nearby.append((obj.distance_to(main.player), obj))
    nearby.sort(key=lambda m: m[0])

    if len(nearby) == 0:
        selected_monster = None
        return
    else:
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

    player = main.player
    mouse = main.mouse

    if mouse.lbutton_pressed:
        offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2 - consts.MAP_VIEWPORT_X, \
                           player.y - consts.MAP_VIEWPORT_HEIGHT / 2 - consts.MAP_VIEWPORT_Y
        (x, y) = (mouse.cx + offsetx, mouse.cy + offsety)

        monster = None
        for obj in main.objects:
            if obj.x == x and obj.y == y and (
                fov.player_can_see(obj.x, obj.y) or (obj.always_visible and main.dungeon_map[obj.x][obj.y].explored)):
                if hasattr(obj, 'fighter') and obj.fighter and not obj is player:
                    monster = obj
                    break
        if monster is not None:
            select_monster(monster)


def get_names_under_mouse():
    mouse = main.mouse

    offsetx, offsety = main.player.x - consts.MAP_VIEWPORT_WIDTH / 2 - consts.MAP_VIEWPORT_X, \
                       main.player.y - consts.MAP_VIEWPORT_HEIGHT / 2 - consts.MAP_VIEWPORT_Y
    (x, y) = (mouse.cx + offsetx, mouse.cy + offsety)

    names = [obj.name for obj in main.objects if (obj.x == x and obj.y == y and (fov.player_can_see(obj.x, obj.y)
                                                                            or (
                                                                            obj.always_visible and main.dungeon_map[obj.x][
                                                                                obj.y].explored)))]
    names = ', '.join(names)

    return names.capitalize()


def message(new_msg, color=libtcod.white):
    global game_msgs
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
    global selected_monster

    player = main.player

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

    drawHeight = 17

    # Weapon
    libtcod.console_print(side_panel, 2, drawHeight, 'Weapon:')
    drawHeight += 1
    weapon = main.get_equipped_in_slot(player.fighter.inventory, 'right hand')
    if weapon is None:
        weapon_string = 'Fists'
        weapon_color = libtcod.gray
    else:
        weapon_string = weapon.owner.name.title()
        weapon_color = loot.weapon_qualities[weapon.quality]['color']
    weapon_string_height = libtcod.console_get_height_rect(side_panel, 2, drawHeight, consts.SIDE_PANEL_WIDTH - 3, 5, weapon_string)
    libtcod.console_set_default_foreground(side_panel, weapon_color)
    libtcod.console_print_rect_ex(side_panel, 2, drawHeight, consts.SIDE_PANEL_WIDTH - 3, weapon_string_height, libtcod.BKGND_DEFAULT, libtcod.LEFT, weapon_string)
    libtcod.console_set_default_foreground(side_panel, libtcod.white)
    drawHeight += weapon_string_height + 1

    seperator_height = drawHeight
    drawHeight += 2

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
    objects_here = main.get_objects(player.x, player.y, lambda o: o is not player)
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
    libtcod.console_print(side_panel, 4, drawHeight, main.dungeon_map[player.x][player.y].name)
    drawHeight += 2
    libtcod.console_set_default_foreground(side_panel, libtcod.white)

    # Selected Monster
    if selected_monster is not None and selected_monster.fighter is not None:
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
        s = 'Your Accuracy: %d%%' % int(100.0 * main.get_chance_to_hit(selected_monster, player.fighter.accuracy * acc_mod))
        s += '%'  # Yeah I know I suck with string formatting. Whatever, this works.  -T
        libtcod.console_print(side_panel, 2, drawHeight, s)
        drawHeight += 1
        if selected_monster.fighter.accuracy > 0:
            s = "Its Accuracy : %d%%" % int(100.0 * main.get_chance_to_hit(player, selected_monster.fighter.accuracy))
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
        libtcod.console_put_char(side_panel, x, seperator_height, libtcod.CHAR_HLINE)
    libtcod.console_put_char(side_panel, 0, seperator_height, 199)
    libtcod.console_put_char(side_panel, consts.SIDE_PANEL_WIDTH - 1, seperator_height, 182)

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


def target_tile(max_range=None, targeting_type='pick', acc_mod=1.0, default_target=None):
    global selected_monster

    player = main.player
    mouse = main.mouse
    key = main.key

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
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        main.render_map()
        render_side_panel(acc_mod=acc_mod)

        # Render range shading
        libtcod.console_clear(overlay)
        libtcod.console_set_key_color(overlay, libtcod.magenta)
        if max_range is not None:
            for draw_x in range(consts.MAP_WIDTH):
                for draw_y in range(consts.MAP_HEIGHT):
                    if round((player.distance(draw_x + offsetx, draw_y + offsety))) > max_range:
                        libtcod.console_put_char_ex(overlay, draw_x, draw_y, ' ', libtcod.light_yellow, libtcod.black)
                    else:
                        libtcod.console_put_char_ex(overlay, draw_x, draw_y, ' ', libtcod.light_yellow, libtcod.magenta)
            libtcod.console_blit(overlay, 0, 0, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT, 0,
                                 consts.MAP_VIEWPORT_X, consts.MAP_VIEWPORT_Y, 0, 0.2)
        # Render cursor
        libtcod.console_set_default_background(overlay, libtcod.magenta)
        libtcod.console_clear(overlay)
        if targeting_type == 'beam' or targeting_type == 'beam_interrupt':
            libtcod.line_init(player.x, player.y, cursor_x, cursor_y)
            line_x, line_y = libtcod.line_step()
            while (not line_x is None):
                libtcod.console_put_char_ex(overlay, line_x - offsetx, line_y - offsety, ' ', libtcod.white, libtcod.yellow)
                line_x, line_y = libtcod.line_step()
        libtcod.console_put_char_ex(overlay, selected_x - offsetx, selected_y - offsety, ' ', libtcod.light_yellow,
                                    libtcod.white)

        libtcod.console_blit(overlay, 0, 0, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT, 0, consts.MAP_VIEWPORT_X,
                             consts.MAP_VIEWPORT_Y, 0, 0.5)

        if main.key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
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
            selected_x, selected_y = main.beam_interrupt(player.x, player.y, cursor_x, cursor_y)
        elif targeting_type == 'beam':
            beam_values = main.beam(player.x, player.y, cursor_x, cursor_y)
            selected_x, selected_y = beam_values[len(beam_values) - 1]

        if (mouse.lbutton_pressed or key.vk == libtcod.KEY_ENTER) and fov.player_can_see(x, y):
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

def inspect_inventory():
    chosen_item = ui.inventory_menu('Select which item?')
    if chosen_item is not None:
        options = chosen_item.get_options_list()
        menu_choice = ui.menu(chosen_item.owner.name, options, 50, render_func=chosen_item.owner.print_description)
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

def skill_menu(add_skill=False):

    scroll_height = 0
    selected_index = 1

    libtcod.console_clear(window)
    main.render_all()
    libtcod.console_flush()

    skill_categories = []
    menu_lines = []

    mouse = main.mouse
    key = main.key


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
        if add_skill:
            title_text = 'Your skills have increased. Choose a skill to learn:'
        else:
            title_text = 'Browsing skills...'
        libtcod.console_print(window, 1, 1, title_text)
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
                        if skill.meets_requirements():
                            libtcod.console_set_default_foreground(sub_window, libtcod.white)
                        else:
                            libtcod.console_set_default_foreground(sub_window, libtcod.gray)

                    libtcod.console_print_ex(sub_window, 5, y, libtcod.BKGND_SET, libtcod.LEFT, skill.name.capitalize())
                    for s in main.learned_skills:
                        if s.name == skill.name:
                            libtcod.console_set_default_foreground(sub_window, libtcod.dark_blue)
                            libtcod.console_print_ex(sub_window, 6 + len(skill.name), y, libtcod.BKGND_SET, libtcod.LEFT, ' [LEARNED]')
                            break
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
        elif key.vk == libtcod.KEY_ENTER and add_skill:
            if menu_lines[selected_index].meets_requirements() and menu_lines[selected_index] not in main.learned_skills:
                return menu_lines[selected_index] # returns a Perk object
        # Down arrow increments selection index
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2 or key.vk == libtcod.KEY_KP6:
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
        elif key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8 or key.vk == libtcod.KEY_KP4:
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


overlay = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
panel = libtcod.console_new(consts.PANEL_WIDTH, consts.PANEL_HEIGHT)
side_panel = libtcod.console_new(consts.SIDE_PANEL_WIDTH, consts.SIDE_PANEL_HEIGHT)
window = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
selected_monster = None
game_msgs = []