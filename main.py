import PySimpleGUI as gui
import random



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

def collapsable(layout, k, size=(None, None), visible=True):
    return gui.pin(gui.Column(layout, size=size, visible=visible, key=k))

def setUp():
    nameboxLayout = [
        [gui.Table([[]],
            key = "-NAMEBOX-",
            size = (40, 25), col_widths=[7, 22],
            auto_size_columns=False,
            headings=["Initiative", "Entity Name", "Health", "DST"],
            justification="left",
            enable_click_events=True
        )]
    ]
    
    # LEFT SIDE SETUP
    addEntityLayout = [[gui.Column([
            [gui.Text("Enter name", background_color="firebrick4"), gui.Input(do_not_clear = False, size = (25, 1), key="-ADD_ENTITY_NAME-")],
            [gui.Text("Enter initiative + modifier", background_color="firebrick4")],
                [gui.Text("First box is base roll, second box is modifier.", text_color = 'grey70', background_color="firebrick4", pad=(5, 0))],
                [gui.Text("Leave first box blank for random base roll.", text_color = 'grey70', background_color="firebrick4", pad=(5, 0))],
                [gui.Text("Leave second box blank for +0 modifier.", text_color = 'grey70', background_color="firebrick4", pad=(5, 0))],
                [gui.Input(do_not_clear = False, size = (10, 1), key="-ADD_ENTITY_BASE_INIT-"), gui.Input(size = (10, 1), do_not_clear = False, key="-ADD_ENTITY_MOD_INIT-")],
            [gui.Checkbox("Is NPC?", background_color="firebrick4", key="-NPC_CHECK-", enable_events=True)],
            [collapsable(
                [
                    [gui.Text("NPC Settings:")],
                    [gui.HorizontalSeparator()],
                    [gui.Text("HP"), gui.Input(do_not_clear=False, size=(10, 1), key="-NPC_HEALTH-")],
                    [gui.HorizontalSeparator()],
                    [gui.Checkbox("Track death saving throws", key="-NPC_DEATH_SAVING_THROWS-", pad=(5, 0))],
                    [gui.Checkbox("Do not remove at 0HP", key="-NPC_AT_DEATH_TRACK-", pad=(5, 0))]
                ], "-ENTITY_SETTINGS-", size=(280, 240), visible=False
            )],
            [gui.Button("Add to initiative order", button_color="orange red", key="-ADD_TO_INIT-")]
        ], size=(500, 800), background_color="black")
    ]]
    
    leftLayout = changeLeftSide(addEntityLayout)
    

    layout = [
            [gui.Column(leftLayout, background_color="firebrick4", scrollable=False, size=(300, 500), vertical_alignment="top", key="-LEFT_MENU-"),
             gui.VSeparator(),
             gui.Column(nameboxLayout, background_color="firebrick4")]
    ]
    return gui.Window("DND Initiative Tracker", layout, background_color="firebrick4")
    

def run(window):
    entities = []
    flag = False
    while not flag:
        event, values = window.read()
        print(values)
        if event == gui.WIN_CLOSED:
            terminate(window)
        elif event == "-ADD_TO_INIT-" and values["-ADD_ENTITY_NAME-"] != "" and testIsIntOptional(values["-ADD_ENTITY_BASE_INIT-"]) and testIsIntOptional(values["-ADD_ENTITY_MOD_INIT-"]):
            entities = addEntity(window, entities, values["-ADD_ENTITY_NAME-"], values["-ADD_ENTITY_BASE_INIT-"], values["-ADD_ENTITY_MOD_INIT-"], None if not values["-NPC_CHECK-"] else (
                values["-NPC_HEALTH-"], values["-NPC_DEATH_SAVING_THROWS-"]
            ))
            print("HI")
        elif event == "-NPC_CHECK-":
            window["-ENTITY_SETTINGS-"].update(visible = values["-NPC_CHECK-"])
            window["-ADD_TO_INIT-"].update()
        elif type(event) == tuple and event[0] == "-NAMEBOX-":
            print("HI")
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

def changeLeftSide(settings):
    topBar = [
        [gui.Text("Current Mode:", background_color="firebrick4"), gui.Combo(["Add entity", "Run Combat"], readonly=True, default_value="Add entity", size=(23, 1), background_color="indian red", text_color="black", key="-MENU_COMBO-", enable_events=True)],
        [gui.HorizontalSeparator()]
    ]
    return topBar + settings

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