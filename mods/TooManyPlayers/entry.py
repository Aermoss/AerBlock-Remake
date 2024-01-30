import sys, os

domainAPI = __import__("domain")
currentFolder = os.path.split(__file__)[0]
main = domainAPI.importModule(os.path.join(currentFolder, "main.py"))

def entry(context):
    domainAPI.setContextCurrent(context)
    desc = domainAPI.ModDescriptor(name = "TooManyPlayers", version = "0.0.1", modClass = main.TooManyPlayers())
    domainAPI.submitDescriptor(desc)
    return domainAPI.exitSuccess