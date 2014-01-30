import cbpos
from cbpos.modules import BaseModuleLoader

class ModuleLoader(BaseModuleLoader):
    def menu(self):
        from cbpos.interface import MenuItem
        from cbmod.installer.views import ModulesPage
            
        return [[],
                [MenuItem('modules', parent='system',
                          label=cbpos.tr.installer_('Modules'),
                          icon=cbpos.res.installer('images/menu-modules.png'),
                          page=ModulesPage
                          )
                 ]
                ]

    def load_argparsers(self):
        parser1 = cbpos.subparsers.add_parser('modules', description="Modules operations")
        parser1.set_defaults(handle=self.arg_handler)

    def init(self):
        # TODO: Check for updates
        return True

    def arg_handler(self, args):
        for wrap in cbpos.modules.all_wrappers():
            if wrap.disabled:
                sep = '--'
            else:
                sep = '>>'
            
            if wrap.metadata is None:
                print '{} {:10}'.format(
                    sep,
                    wrap.base_name,
                )
            else:
                print '{} {:10}\t\t|{}'.format(
                    sep,
                    wrap.base_name,
                    '|'.join(' {:12} '.format(a+'-'+b) for (a,b) in \
                             wrap.metadata.dependencies)
                )
        return False