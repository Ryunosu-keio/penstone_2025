
def transform_condition(room, figure):
    if room == "1" :
        room_condition = "roomBright"
    else:
        room_condition = "roomDark"
    if figure == "1":
        figure_condition = "figureBright"
    else:
        figure_condition = "figureDark"
    return room_condition + "_" + figure_condition
