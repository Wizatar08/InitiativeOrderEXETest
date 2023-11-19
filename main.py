import PySimpleGUI as gui

class Entity:

    def __init__(self, name, initiative, iModifier = 0):
        self.name = name
        self.initiative = initiative + iModifier
        self.iModifier = iModifier

    def __str__(self) -> str:
        return f"{self.name}: {self.initiative}"
    
    def forListboxString(self):
        return f"[{self.initiative:02d} ({self.iModifier:+2d})] - {self.name}"

def isInt(inp):
    if inp.replace("-", "").isdigit():
        return True
    return False

def optionalIntParam(inp):
    if inp.replace("-", "").isdigit():
        return int(inp)
    return 0

def main():
    entities = getEntities()

def getEntities():
    bStr = ["Add to initiative order"]
    entities = []
    namebox = gui.Listbox([], size = (40, 10), horizontal_scroll = True, key = "nameBox")
    layout = [
        [gui.Text("Enter name")],
        [gui.Input(do_not_clear = False, size = (50, 1))],
        [gui.Text("Enter initiative and initiative modifier")],
        [gui.Input(do_not_clear = False, size = (35, 1)), gui.Input(size = (13, 1), do_not_clear = False)],
        [gui.Button(bStr[0])],
        [namebox]]
    window = gui.Window("DND Initiative Tracker", layout)
    flag = False
    while not flag:
        event, values = window.read()
        if event == gui.WIN_CLOSED:
            terminate(window)
        if event == bStr[0] and isInt(values[1]) and (isInt(values[2]) or values[2] == ''):
            print(values)
            e = Entity(values[0], int(values[1]), optionalIntParam(values[2]))
            entities.append(e)
            entities = order(entities)
            window['nameBox'].update([entities[i].forListboxString() for i in range(
                len(getData(entities)[0])
            )])
        print(event)
    window.close()
    return entities

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