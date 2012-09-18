import cbpos
from cbpos.modules import BaseModuleLoader

class ModuleLoader(BaseModuleLoader):
    dependencies = ('base',)
    name = 'Module Installer and Manager'

    def menu(self):
        from cbpos.mod.installer.pages import ModulesPage
            
        return [[],
                [{'parent': 'System', 'label': 'Modules', 'page': ModulesPage, 'image': self.res('images/menu-modules.png')}]]

    def init(self):
        # Check for updates
        return True
