from modulefinder import ModuleFinder

finder = ModuleFinder()
finder.run_script('CreateMC.py')

print('Loaded modules:')
#print(finder.modules)
for name, module in finder.modules.items():
    print(name)
    print(module, '\n')
    #print(','.join(mod.globalnames.keys()[:3]))

print('-'*50)
print('Modules not imported')
print(finder.badmodules)
