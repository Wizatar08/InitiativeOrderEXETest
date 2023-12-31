import PySimpleGUI as gui
import random

MENU_OPTIONS = ["Add Entity", "Run Combat"]
ENTITY_MENU_OPTIONS = ["Initiative and Base Stats", "Health", "Spells (NPC setting)"]
DICE_RANGE = [""] + [i for i in range(1, 21)]
MODIFIER_RANGE = [i for i in range(-10, 11)]
GENERAL_NUMBER_SCROLL = [""] + [i for i in range(0, 1001)]
SPELL_MAX_LENGTH_TIME_DICT = {"Action": "action", "Second": "second", "Minute": "minute", "Day": "day"}
SPELL_MAX_LENGTH_TIME_OPTIONS = list(SPELL_MAX_LENGTH_TIME_DICT.keys())
LEFT_SIDE_SIZE = (350, 500)
SPELL_LEVEL_RANGE = [i for i in range(0, 10)]
SPELL_AMOUNT_RANGE = [i for i in range(0, 11)]

class Entity:

    def __init__(self, name, initiative, iModifier = 0, isNPC = False, health = None, trackDeathSavingThrows = False, conditions=[], spells=[]):
        self.name = name
        self.initiative = initiative + iModifier
        self.iModifier = iModifier
        self.isNPC = isNPC
        self.health = health
        self.trackDeathSavingThrows = trackDeathSavingThrows
        self.conditions = conditions
        self.spells = spells

        self.removable = False

    def __str__(self) -> str:
        return f"{self.name}: {self.initiative}"
    
    def forListboxString(self):
        return [f"[{self.initiative:02d} ({self.iModifier:+2d})]", f"[{'NPC' if self.isNPC else 'Player'}] {self.name}", "" if self.health == None else self.health, self.trackDeathSavingThrows]
    
class Spell:

    def __init__(self, name, minLevel, concentration = False, time = 0, timeType = "action"):
        self.name = name
        self.minLevel = minLevel
        self.concentration = concentration
        self.time = int(time) if int(time) > 0 else None
        self.timeType = timeType

    def makePlural(self, value, word):
        if value != 1:
            return word + "s"
        return word

    def forTableString(self):
        if self.time == None:
            s = "Instantaneous"
        else:
            s = f"{self.time} {self.makePlural(self.time, self.timeType)}"
        return [self.name, self.minLevel, "Yes" if self.concentration else "No", s]

# TEST METHODS

def isInt(inp):
    if inp.replace("-", "").isdigit():
        return True
    return False

def isPositiveInt(inp):
    if isInt(str(inp)) and int(inp) > 0:
        return True
    return False

def setZeroInt(inp):
    if str(inp).replace("-", "").isdigit():
        return inp
    return 0

def numberOrBlank(inp):
    if inp == "" or isInt(str(inp)):
        return True
    return False

# RUN

def main():
    window = setUp()
    run(window)

def collapsable(layout, key, size=(None, None), visible=True, element_justification=None, background_color=None, justification=None, vertical_alignment=None, padding=None, scrollable=None):
    return gui.pin(gui.Column(layout, size=size, visible=visible, key=key, element_justification=element_justification, background_color=background_color, justification=justification, pad=padding, scrollable=scrollable))

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
    

    
    # -----------------------
    # LEFT SIDE SETUP
    # -----------------------

    initiativeMenu = [
        [gui.Checkbox("Is NPC?", key="-NPC_CHECK-")],
        [gui.Text("Enter name"), gui.Input(size = (25, 1), key="-ADD_ENTITY_NAME-")],
        [gui.Text("Enter initiative + modifier"), gui.Spin(DICE_RANGE, initial_value="", size = (5, 1), key="-ADD_ENTITY_BASE_INIT-"), gui.Text("+", pad=(0, 0)), gui.Spin(MODIFIER_RANGE, initial_value="", size = (5, 1), key="-ADD_ENTITY_MOD_INIT-")],
        [gui.Text("First box is base roll, second box is modifier.", pad=(5, 0), text_color="grey80")],
        [gui.Text("Leave first box blank for random base roll.", pad=(5, 0), text_color="grey80")],
        [gui.Text("Leave second box blank for +0 modifier.", pad=(5, 0), text_color="grey80")]
    ]

    healthMenu = [
        [gui.Text("HP"), gui.Spin(GENERAL_NUMBER_SCROLL, initial_value="", size=(10, 1), key="-NPC_HEALTH-")],
        [gui.Text("Leave health blank to not track", text_color="grey80")],
        [gui.HorizontalSeparator()],
        [gui.Checkbox("Track death saving throws", key="-NPC_DEATH_SAVING_THROWS-", enable_events=True, pad=(5, 0))],
        [gui.Checkbox("Do not remove at 0HP", key="-NPC_AT_DEATH_TRACK-", pad=(5, 0))],
        [gui.Text("Initial conditions: "), gui.Input(size = (18, 1), key="-CONDITIONS_TEXT-"), gui.Button("+", size=(2,1), key="-CONDITIONS_ADD-"), gui.Button("-", size=(2,1), key="-CONDITIONS_REMOVE-")],
            [gui.Listbox([], size=(38, 5), key="-CONDITIONS_LISTBOX-")]
    ]

    spellsMenu = [
        [gui.Text("0th:"), gui.Spin(SPELL_AMOUNT_RANGE, initial_value=0, readonly=True, size=[3, 1], key="-ADD_SPELLS_0-"), gui.Text("1st:"), gui.Spin(SPELL_AMOUNT_RANGE, initial_value=0, readonly=True, size=[3, 1], key="-ADD_SPELLS_1-"), gui.Text("2nd:"), gui.Spin(SPELL_AMOUNT_RANGE, initial_value=0, readonly=True, size=[3, 1], key="-ADD_SPELLS_2-"), gui.Text("3rd:"), gui.Spin(SPELL_AMOUNT_RANGE, initial_value=0, readonly=True, size=[3, 1], key="-ADD_SPELLS_3-")],
        [gui.Text("4th:"), gui.Spin(SPELL_AMOUNT_RANGE, initial_value=0, readonly=True, size=[3, 1], key="-ADD_SPELLS_4-"), gui.Text("5th:"), gui.Spin(SPELL_AMOUNT_RANGE, initial_value=0, readonly=True, size=[3, 1], key="-ADD_SPELLS_5-"), gui.Text("6th:"), gui.Spin(SPELL_AMOUNT_RANGE, initial_value=0, readonly=True, size=[3, 1], key="-ADD_SPELLS_6-"), gui.Text("7th:"), gui.Spin(SPELL_AMOUNT_RANGE, initial_value=0, readonly=True, size=[3, 1], key="-ADD_SPELLS_7-")],
        [gui.Text("8th:"), gui.Spin(SPELL_AMOUNT_RANGE, initial_value=0, readonly=True, size=[3, 1], key="-ADD_SPELLS_8-"), gui.Text("9th:"), gui.Spin(SPELL_AMOUNT_RANGE, initial_value=0, readonly=True, size=[3, 1], key="-ADD_SPELLS_9-")],
        [gui.HorizontalSeparator()],
        [gui.Text("Spell:"), gui.Input(size=[20, 1], key="-SPELL_NAME-"), gui.Text("Level:"), gui.Spin(SPELL_LEVEL_RANGE, initial_value=0, readonly=True, size=[2, 1], key="-SPELL_LEVEL_INPUT-")],
        [gui.Checkbox("Has Duration?", key="-DURATION_CHECK-", enable_events=True), collapsable([[gui.Spin(GENERAL_NUMBER_SCROLL, initial_value=0, size=[4,1], key="-DURATION_TIME_INPUT-"),
            gui.Combo(SPELL_MAX_LENGTH_TIME_OPTIONS, default_value=SPELL_MAX_LENGTH_TIME_OPTIONS[0], size=[10,1], key="-CONCENTRATION_TIME_TYPE-", readonly=True)]]
            , "-SPELL_TIME_MENU-", visible=False)],
        [gui.Checkbox("Requires Concentration?", key="-CONCENTRATION_CHECK-")],
        [gui.Button("ADD", key="-ADD_SPELL_BUTTON-"), gui.Button("REMOVE", key="-REMOVE_SPELL_BUTTON-")],
        [gui.Table([[]], headings=["Name", "Lvl", "Conc", "Duration"], justification="left", auto_size_columns=False, col_widths=[17, 4, 4, 10], enable_click_events=True, key="-SPELLS_TABLE-")]
    ]


    addEntityLayout = [
            [gui.Combo(ENTITY_MENU_OPTIONS, readonly=True, default_value=ENTITY_MENU_OPTIONS[0], size=(23, 1), key="-ADD_ENTITY_MENU_COMBO-", enable_events=True)],
            [gui.Button("Add to initiative order", key="-ADD_TO_INIT-"), gui.Checkbox("Clear after adding", key="-CLEAR_AFTER_ADDING_CHECK-")],
            [gui.HorizontalSeparator()],
            [collapsable(initiativeMenu, "-ENTITY_INITIATIVE_MENU-")],
            [collapsable(healthMenu, "-ENTITY_HEALTH_MENU-", visible=False)],
            [collapsable(spellsMenu, "-ENTITY_SPELLS_MENU-", visible=False)]
    ]

    # ---------------------------
    # COMBAT LAYOUT
    # --------------------------

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
            [gui.Column(leftLayout, size=(350, 500), vertical_alignment="top", key="-LEFT_MENU-", pad=(0,0)),
             gui.VSeparator(),
             gui.Column(nameboxLayout)]
    ]
    return gui.Window("DND Initiative Tracker", layout)
    

def run(window):
    entities = []
    currEntityIndex = None
    currSelectedEntityIndex = None
    flag = False

    # SET UP VARIABLES
    conditions = []
    spells = []

    while not flag:
        event, values = window.read()
        
        if event == gui.WIN_CLOSED:
            terminate(window)

        elif event == "-ADD_ENTITY_MENU_COMBO-":
            if values["-ADD_ENTITY_MENU_COMBO-"] == ENTITY_MENU_OPTIONS[0]:
                window["-ENTITY_INITIATIVE_MENU-"].update(visible=True)
                window["-ENTITY_HEALTH_MENU-"].update(visible=False)
                window["-ENTITY_SPELLS_MENU-"].update(visible=False)
            elif values["-ADD_ENTITY_MENU_COMBO-"] == ENTITY_MENU_OPTIONS[1]:
                window["-ENTITY_INITIATIVE_MENU-"].update(visible=False)
                window["-ENTITY_HEALTH_MENU-"].update(visible=True)
                window["-ENTITY_SPELLS_MENU-"].update(visible=False)
            elif values["-ADD_ENTITY_MENU_COMBO-"] == ENTITY_MENU_OPTIONS[2]:
                window["-ENTITY_INITIATIVE_MENU-"].update(visible=False)
                window["-ENTITY_HEALTH_MENU-"].update(visible=False)
                window["-ENTITY_SPELLS_MENU-"].update(visible=True)



        # INITIAITIVE:
        elif event == "-ADD_TO_INIT-" and values["-ADD_ENTITY_NAME-"] != "" and numberOrBlank(values["-ADD_ENTITY_BASE_INIT-"]) and numberOrBlank(values["-ADD_ENTITY_MOD_INIT-"]):
            entities = addEntity(window, entities, name=values["-ADD_ENTITY_NAME-"], bI=values["-ADD_ENTITY_BASE_INIT-"], iM=values["-ADD_ENTITY_MOD_INIT-"], conditions=conditions, isNPC= values["-NPC_CHECK-"], health=values["-NPC_HEALTH-"], dst=values["-NPC_DEATH_SAVING_THROWS-"], spells=spells)
            if values["-CLEAR_AFTER_ADDING_CHECK-"]:
                clearAddEntityInputs(window)
                conditions = []
        elif event == "-NPC_DEATH_SAVING_THROWS-":
            window["-NPC_AT_DEATH_TRACK-"].update(text = "Do not remove on death" if values[event] else "Do not remove at 0HP")

        # HEALTH
        elif event == "-CONDITIONS_ADD-":
            conditions += [values["-CONDITIONS_TEXT-"]]
            window["-CONDITIONS_LISTBOX-"].update(conditions)

        elif event == "-DURATION_CHECK-":
            window["-SPELL_TIME_MENU-"].update(visible=values["-DURATION_CHECK-"])

        # SPELLS
        elif event == "-ADD_SPELL_BUTTON-":
            s = Spell(values["-SPELL_NAME-"], values["-SPELL_LEVEL_INPUT-"], values["-CONCENTRATION_CHECK-"], setZeroInt(values["-DURATION_TIME_INPUT-"]) if values["-DURATION_CHECK-"] else 0, values["-CONCENTRATION_TIME_TYPE-"])
            spells.append(s)
            window["-SPELLS_TABLE-"].update([spells[i].forTableString() for i in range(len(spells))])
            window["-SPELL_NAME-"].update("")
            window["-SPELL_LEVEL_INPUT-"].update(0)
            window["-CONCENTRATION_CHECK-"].update(False)
            window["-DURATION_CHECK-"].update(False)
            window["-DURATION_TIME_INPUT-"].update(0)
            window["-CONCENTRATION_TIME_TYPE-"].update(SPELL_MAX_LENGTH_TIME_OPTIONS[0])
        elif event == "-REMOVE_SPELL_BUTTON-" and len(values["-SPELLS_TABLE-"]) > 0:
            spells.pop(values["-SPELLS_TABLE-"][0])
            

        # MANAGE COMBAT
        elif event == "-START_COMBAT_BUTTON-":
            window["-START_COMBAT_CONFIRM-"].update(visible=False)
            window["-RUN_COMBAT_BOX-"].update(visible=True)
            currEntityIndex = 0
            currSelectedEntityIndex = 0
            window["-NAMEBOX-"].update(row_colors=[[currEntityIndex,'green']], select_rows=[currSelectedEntityIndex])

        
        elif event == "-MENU_COMBO-":
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

    window.close()

def addEntity(window, en, name, bI, iM, conditions, isNPC, health, dst, spells):
    e = Entity(name, random.randint(1, 20) if bI == "" else int(bI), iModifier = setZeroInt(iM), conditions=conditions,
        isNPC = isNPC,
        health = health if isPositiveInt(health) else None,
        trackDeathSavingThrows = dst,
        spells=spells
    )
    en.append(e)
    en = order(en)
    window['-NAMEBOX-'].update([en[i].forListboxString() for i in range(
        len(getData(en)[0])
    )])
    return en

def clearAddEntityInputs(w):
    w["-ADD_ENTITY_NAME-"].update("")
    w["-ADD_ENTITY_BASE_INIT-"].update("")
    w["-ADD_ENTITY_MOD_INIT-"].update("")
    w["-NPC_HEALTH-"].update("")
    w["-CONDITIONS_LISTBOX-"].update([])
    w["-CONDITIONS_TEXT-"].update("")
    for i in range(10):
        w[f"-ADD_SPELLS_{i}-"].update(0)
    w["-SPELL_LEVEL_INPUT-"].update("")

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