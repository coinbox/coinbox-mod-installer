import cbpos
from cbpos.modules import BaseModuleLoader

class ModuleLoader(BaseModuleLoader):
    dependencies = ('base',)
    name = 'Module Installer and Manager'

    def menu(self):
        from cbpos.interface import MenuItem
        from cbpos.mod.installer.views import ModulesPage
            
        return [[],
                [MenuItem('modules', parent='system',
                          label=cbpos.tr.installer._('Modules'),
                          icon=cbpos.res.installer('images/menu-modules.png'),
                          page=ModulesPage
                          )
                 ]
                ]

    def argparser(self):
        parser1 = cbpos.subparsers.add_parser('modules', description="Modules operations")
        parser1.set_defaults(handle=self.arg_handler)

    def init(self):
        # TODO: Check for updates
        return True

    def arg_handler(self, args):
        for mod in cbpos.modules.all_loaders():
            print '>>', mod, mod.name
            print '\t', ', '.join(mod.dependencies)
        return False