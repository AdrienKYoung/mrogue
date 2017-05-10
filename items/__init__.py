
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
        _item_table_cache = dict(armor.table.items() + consumables.table.items() + items_charms.table.items() +
                                 summoned_weapons.table.items() + tomes.table.items() + weapons.table.items())
    return _item_table_cache