import cbpos
from cbpos.modules import BaseModuleLoader

class ModuleLoader(BaseModuleLoader):
    dependencies = ('base',)
    name = 'Module Installer and Manager'

    def menu(self):
        from cbpos.mod.installer.views import ModulesPage
            
        return [[],
                [{'parent': 'System', 'label': 'Modules', 'page': ModulesPage, 'image': cbpos.res.installer('images/menu-modules.png')}]]

    def argparser(self):
        parser1 = cbpos.subparsers.add_parser('modules', description="Modules operations")
        parser1.set_defaults(handle=self.arg_handler)

    def init(self):
        # Check for updates
        return True

    def arg_handler(self, args):
        for mod in cbpos.modules.all_loaders():
            print '>>', mod, mod.name
            print '\t', ', '.join(mod.dependencies)
        return False