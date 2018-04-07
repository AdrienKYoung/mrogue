
_item_table_cache = None

def table():
    global _item_table_cache
    if _item_table_cache is None:
        import armor
        import consumables
        import items_charms
        import summoned_weapons
        import tomes
        import weapons
        import rings
        import shoulders
        import boots
        import gloves
        import helms
        _item_table_cache = dict(armor.table.items() + consumables.table.items() + items_charms.table.items() +
                                 summoned_weapons.table.items() + tomes.table.items() + weapons.table.items() +
                                 rings.table.items() + shoulders.table.items() + boots.table.items() +
                                 gloves.table.items() + helms.table.items())
    return _item_table_cache