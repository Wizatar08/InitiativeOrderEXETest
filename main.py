import PySimpleGUI as gui
import random

MENU_OPTIONS = ["Add Entity", "Run Combat"]
LEFT_SIDE_SIZE = (300, 500)

class Entity:

    def __init__(self, name, initiative, iModifier = 0, isNPC = False, health = None, trackDeathSavingThrows = False):
        self.name = name
        self.initiative = initiative + iModifier
        self.iModifier = iModifier
        self.isNPC = isNPC
        self.health = health
        self.trackDeathSavingThrows = trackDeathSavingThrows

    def __str__(self) -> str:
        return f"{self.name}: {self.initiative}"
    
    def forListboxString(self):
        return [f"[{self.initiative:02d} ({self.iModifier:+2d})]", f"[{'NPC' if self.isNPC else 'Player'}] {self.name}", "" if self.health == None else self.health, self.trackDeathSavingThrows]

# TEST METHODS

def isInt(inp):
    if inp.replace("-", "").isdigit():
        return True
    return False

def isPositiveInt(inp):
    if isInt(inp) and int(inp) > 0:
        return True
    return False

def setOptionalIntParam(inp):
    if inp.replace("-", "").isdigit():
        return int(inp)
    return 0

def testIsIntOptional(inp):
    if isInt(inp) or inp == "":
        return True
    return 00

# RUN

def main():
    window = setUp()
    run(window)

def collapsable(layout, key, size=(None, None), visible=True, element_justification=None, background_color=None, justification=None, vertical_alignment=None, padding=None):
    return gui.pin(gui.Column(layout, size=size, visible=visible, key=key, element_justification=element_justification, background_color=background_color, justification=justification, pad=padding))

def setUp():
    topBar = [
        [gui.Text("Current Mode:"), gui.Combo(MENU_OPTIONS, readonly=True, default_value="Add entity", size=(23, 1), key="-MENU_COMBO-", enable_events=True)],
        [gui.HorizontalSeparator()]
    ]

    nameboxLayout = [
        [gui.Table([[]],
            key = "-NAMEBOX-", 
            size = (40, 25), col_widths=[7, 22, 5, 5],
            auto_size_columns=False,
            headings=["Initiative", "Entity Name", "Health", "DST"],
            justification="left",
            enable_click_events=True,
            selected_row_colors=("red", "yellow")
            
        )]
    ]
    
    # LEFT SIDE SETUP
    addEntityLayout = [
            [gui.Text("Enter name"), gui.Input(do_not_clear = False, size = (25, 1), key="-ADD_ENTITY_NAME-")],
            [gui.Text("Enter initiative + modifier")],
                [gui.Text("First box is base roll, second box is modifier.", pad=(5, 0), text_color="grey80")],
                [gui.Text("Leave first box blank for random base roll.", pad=(5, 0), text_color="grey80")],
                [gui.Text("Leave second box blank for +0 modifier.", pad=(5, 0), text_color="grey80")],
                [gui.Input(do_not_clear = False, size = (10, 1), key="-ADD_ENTITY_BASE_INIT-"), gui.Input(size = (10, 1), do_not_clear = False, key="-ADD_ENTITY_MOD_INIT-")],
            [gui.Checkbox("Is NPC?", key="-NPC_CHECK-", enable_events=True)],
            [collapsable(
                [
                    [gui.Text("NPC Settings:")],
                    [gui.HorizontalSeparator()],
                    [gui.Text("HP"), gui.Input(do_not_clear=False, size=(10, 1), key="-NPC_HEALTH-")],
                    [gui.HorizontalSeparator()],
                    [gui.Checkbox("Track death saving throws", key="-NPC_DEATH_SAVING_THROWS-", enable_events=True, pad=(5, 0))],
                    [gui.Checkbox("Do not remove at 0HP", key="-NPC_AT_DEATH_TRACK-", pad=(5, 0))]
                ], "-ENTITY_SETTINGS-", size=(280, 240), visible=False, padding=(0,0)
            )],
            [gui.Button("Add to initiative order", key="-ADD_TO_INIT-")]
    ]

    runCombatLayout = [
        [gui.Column([
            [collapsable([[gui.Text("Click button to start combat:"), gui.Button("Start Combat", key="-START_COMBAT_BUTTON-")]], "-START_COMBAT_CONFIRM-", padding=(0,0), visible=False)],
            [collapsable([[gui.Text("WARNING:")], [gui.Text("Must have at least 2 entities to start")]], "-START_COMBAT_ERROR-", visible=True, padding=(0,0))],
            [collapsable([
                [gui.Button("Finish Current Entity's Turn")]
            ], "-RUN_COMBAT_BOX-", visible=False, padding=(0,0))]
        ], vertical_alignment="center", element_justification="center", size=LEFT_SIDE_SIZE)]
    ]

    leftLayout = topBar + [[collapsable(addEntityLayout, "--ADD_ENTITY_LAYOUT--", size=LEFT_SIDE_SIZE, visible=True)]] + [[collapsable(runCombatLayout, "--RUN_COMBAT--", size=LEFT_SIDE_SIZE, visible=False, padding=(0,0))]]
    

    layout = [
            [gui.Column(leftLayout, scrollable=False, size=LEFT_SIDE_SIZE, vertical_alignment="top", key="-LEFT_MENU-", pad=(0,0)),
             gui.VSeparator(),
             gui.Column(nameboxLayout)]
    ]
    return gui.Window("DND Initiative Tracker", layout)
    

def run(window):
    entities = []
    currEntityIndex = None
    currSelectedEntityIndex = None
    flag = False
    while not flag:
        event, values = window.read()
        
        if event == gui.WIN_CLOSED:
            terminate(window)

        # ADD ENTITY TITLE:
        elif event == "-ADD_TO_INIT-" and values["-ADD_ENTITY_NAME-"] != "" and testIsIntOptional(values["-ADD_ENTITY_BASE_INIT-"]) and testIsIntOptional(values["-ADD_ENTITY_MOD_INIT-"]) and (not values["-NPC_CHECK-"] or isInt(values["-NPC_HEALTH-"])):
            entities = addEntity(window, entities, values["-ADD_ENTITY_NAME-"], values["-ADD_ENTITY_BASE_INIT-"], values["-ADD_ENTITY_MOD_INIT-"], None if not values["-NPC_CHECK-"] else (
                values["-NPC_HEALTH-"], values["-NPC_DEATH_SAVING_THROWS-"] 
            ))
        elif event == "-NPC_CHECK-":
            window["-ENTITY_SETTINGS-"].update(visible = values["-NPC_CHECK-"])
            window["-ADD_TO_INIT-"].update()
        elif event == "-NPC_DEATH_SAVING_THROWS-":
            window["-NPC_AT_DEATH_TRACK-"].update(text = "Do not remove on death" if values[event] else "Do not remove at 0HP")

        # MANAGE COMBAT
        elif event == "-START_COMBAT_BUTTON-":
            window["-START_COMBAT_CONFIRM-"].update(visible=False)
            window["-RUN_COMBAT_BOX-"].update(visible=True)
            currEntityIndex = 0
            currSelectedEntityIndex = 0
            window["-NAMEBOX-"].update(row_colors=[[currEntityIndex,'green']], select_rows=[currSelectedEntityIndex])
        
        elif event == "-MENU_COMBO-":
            print(event)
            if values["-MENU_COMBO-"] == MENU_OPTIONS[0]:
                window["--ADD_ENTITY_LAYOUT--"].update(visible=True)
                window["--RUN_COMBAT--"].update(visible=False)
            elif values["-MENU_COMBO-"] == MENU_OPTIONS[1]:
                window["--ADD_ENTITY_LAYOUT--"].update(visible=False)
                window["--RUN_COMBAT--"].update(visible=True)

        if currEntityIndex == None:
            if len(entities) >= 2:
                window["-START_COMBAT_ERROR-"].update(visible=False)
                window["-START_COMBAT_CONFIRM-"].update(visible=True)
            else:
                window["-START_COMBAT_ERROR-"].update(visible=True)
                window["-START_COMBAT_CONFIRM-"].update(visible=False)
        print(event, values)

    window.close()

def addEntity(window, en, name, bI, iM, npcData):
    if npcData == None:
        e = Entity(name, random.randint(1, 20) if bI == "" else int(bI), iModifier = setOptionalIntParam(iM))
    else:
        e = Entity(name, random.randint(1, 20) if bI == "" else int(bI), iModifier = setOptionalIntParam(iM),
            isNPC = True,
            health = int(npcData[0]) if isPositiveInt(npcData[0]) else None,
            trackDeathSavingThrows = npcData[1]
        )
    en.append(e)
    en = order(en)
    window['-NAMEBOX-'].update([en[i].forListboxString() for i in range(
        len(getData(en)[0])
    )])
    return en

def order(entities):
    i = 1
    while i < len(entities):
        a = entities[i].initiative
        b = entities[i - 1].initiative
        aI = entities[i].iModifier
        bI = entities[i - 1].iModifier
        if (b < a or (b == a and bI < aI)) and i > 0:
            entities[i - 1], entities[i] = entities[i], entities[i - 1]
            i -= 1
        else:
            i += 1
    return entities

def getData(entities):
    names = []
    initiatives = []
    for e in entities:
        names.append(e.name)
        initiatives.append(e.initiative)
    return names, initiatives

def terminate(window):
    window.close()
    exit()

main()