import sys, os, importlib, importlib.util

sys.dont_write_bytecode = True

from main import moss, App

contextCurrent = None
exitSuccess, exitError = range(2)

def setContextCurrent(context):
    global contextCurrent
    if contextCurrent != None: return False
    contextCurrent = context
    return True

def getContextCurrent():
    if contextCurrent == None:
        moss.logger.log(moss.ERROR, "no active context found.")

    return contextCurrent

def submitDescriptor(desc):
    getContextCurrent().modDescriptors[desc.name] = desc

def importModule(path):
    name = os.path.splitext(os.path.split(path)[1])[0]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class ModBase:
    def __init__(self, context):
        self.context = context
        self.bind(self.context, ["window", "renderer", "shader", "world", "player"])
        
    def bind(self, object, keys):
        for i in keys:
            setattr(self, i, getattr(object, i))

class ModDescriptor:
    def __init__(self, name, version, modClass):
        self.name, self.version, self.modClass = name, version, modClass

class ModLoader:
    def __init__(self, modsFolder = "mods", mods = {}):
        self.modsFolder, self.mods = modsFolder, mods

        for modName in os.listdir(self.modsFolder):
            modFolder = os.path.join(self.modsFolder, modName)
            if not os.path.isdir(modFolder):
                moss.logger.log(moss.ERROR, f"file found in mod folder: '{modName}'")
                continue

            modEntry = os.path.join(modFolder, "entry.py")
            if not os.path.isfile(modEntry):
                moss.logger.log(moss.ERROR, f"entry not found in folder: '{modName}'")
                continue

            moss.logger.log(moss.INFO, f"loading mod: '{modName}'.")
            modSpec = importlib.util.spec_from_file_location(modName, modEntry)
            mod = importlib.util.module_from_spec(modSpec)
            modSpec.loader.exec_module(mod)
            self.mods[modName] = mod
            moss.logger.log(moss.INFO, f"mod '{modName}' successfully loaded.")

class Domain:
    def __init__(self):
        if setContextCurrent(self):
            moss.logger.log(moss.INFO, "domain loader initialized.")

        else:
            moss.logger.log(moss.ERROR, "domain loader already initialized.")
            sys.exit(1)

        self.app = App()
        self.bind(self.app, ["window"])
        self.window.event(self.setup)
        self.window.event(self.update)
        self.window.event(self.exit)
        self.modsFolder  = os.path.join(os.path.split(__file__)[0], "mods")
        self.mods, self.modDescriptors = {}, {}
        self.modLoader = ModLoader(self.modsFolder, self.mods)
        self.clear = self.window.clear
        self.window.clear = lambda: None

    def setup(self, window):
        self.app.setup(window)
        self.bind(self.app, ["renderer", "shader", "world", "player"])
        self.proccessInputs = self.player.proccessInputs
        self.updatePhysics = self.player.updatePhysics

        for i in self.mods.copy():
            errorCode = self.mods[i].entry(self)

            if errorCode != exitSuccess:
                moss.logger.log(moss.ERROR, f"the entry of the '{i}' mod returned error code: '{errorCode}'")

            if i not in self.modDescriptors:
                moss.logger.log(moss.ERROR, f"mod descriptor not found: '{i}'")
                del self.mods[i]

        for i in self.modDescriptors:
            self.modDescriptors[i].modClass.setup()

    def setInputState(self, state):
        if state: self.player.proccessInputs = self.proccessInputs
        else: self.player.proccessInputs = lambda: self.window.input.setCursorVisible(True)

    def setPhysicsState(self, state):
        if state: self.player.updatePhysics = self.updatePhysics
        else: self.player.updatePhysics = lambda: None

    def update(self, window):
        self.clear()

        for i in self.modDescriptors:
            self.modDescriptors[i].modClass.update()

        self.app.update(window)

    def exit(self, window):
        for i in self.modDescriptors:
            self.modDescriptors[i].modClass.exit()

        self.app.exit(window)
        setContextCurrent(None)

    def bind(self, object, keys):
        for i in keys:
            setattr(self, i, getattr(object, i))

    def run(self):
        self.app.run()

def main(argv):
    domain = Domain()
    domain.run()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))