import PySimpleGUI as gui
import random



class Entity:

    def __init__(self, name, initiative, iModifier = 0):
        self.name = name
        self.initiative = initiative + iModifier
        self.iModifier = iModifier

    def __str__(self) -> str:
        return f"{self.name}: {self.initiative}"
    
    def forListboxString(self):
        return f"[{self.initiative:02d} ({self.iModifier:+2d})] - {self.name}"

# TEST METHODS

def isInt(inp):
    if inp.replace("-", "").isdigit():
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

def setUp():
    nameboxLayout = [
        [gui.Listbox([], size = (40, 25), horizontal_scroll = True, key = "nameBox")]
    ]
    
    # LEFT SIDE SETUP
    addEntityLayout = [
            [gui.Text("Enter name", background_color="firebrick4"), gui.Input(do_not_clear = False, size = (25, 1), key="-ADD_ENTITY_NAME-")],
            [gui.Text("Enter initiative + modifier", background_color="firebrick4")],
                [gui.Text("First box is base roll, second box is modifier.", text_color = 'grey70', background_color="firebrick4", pad=(5, 0))],
                [gui.Text("Leave first box blank for random base roll.", text_color = 'grey70', background_color="firebrick4", pad=(5, 0))],
                [gui.Text("Leave second box blank for +0 modifier.", text_color = 'grey70', background_color="firebrick4", pad=(5, 0))],
                [gui.Input(do_not_clear = False, size = (10, 1), key="-ADD_ENTITY_BASE_INIT-"), gui.Input(size = (10, 1), do_not_clear = False, key="-ADD_ENTITY_MOD_INIT-")],
            [gui.Button("Add to initiative order", button_color="orange red", key="-ADD_TO_INIT-")]
        ]
    
    leftLayout = changeLeftSide(addEntityLayout)
    

    layout = [
            [gui.Column(leftLayout, background_color="firebrick4", scrollable=False, size=(300, 500), vertical_alignment="top"),
             gui.VSeparator(),
             gui.Column(nameboxLayout, background_color="firebrick4")]
    ]
    return gui.Window("DND Initiative Tracker", layout, background_color="firebrick4")
    

def run(window):
    entities = []
    flag = False
    while not flag:
        event, values = window.read()
        if event == gui.WIN_CLOSED:
            terminate(window)
        elif event == "-ADD_TO_INIT-" and values["-ADD_ENTITY_NAME-"] != "" and testIsIntOptional(values["-ADD_ENTITY_BASE_INIT-"]) and testIsIntOptional(values["-ADD_ENTITY_MOD_INIT-"]):
            entities = addEntity(window, entities, values["-ADD_ENTITY_NAME-"], values["-ADD_ENTITY_BASE_INIT-"], values["-ADD_ENTITY_MOD_INIT-"])
    window.close()

def addEntity(window, en, name, bI, iM):
    e = Entity(name, random.randint(1, 20) if bI == "" else int(bI), setOptionalIntParam(iM))
    en.append(e)
    en = order(en)
    window['nameBox'].update([en[i].forListboxString() for i in range(
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