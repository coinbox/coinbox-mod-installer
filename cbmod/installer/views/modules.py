from PySide import QtGui

import cbpos

from cbmod.base.views import BasePage

from cbmod.installer.controllers import ModuleManager

class ModulesPage(BasePage):
    def __init__(self):
        super(ModulesPage, self).__init__()
        
        self.manager = ModuleManager()
        self.headers = ['Module', 'Name', 'Dependencies', 'State']
        
        self.modules = QtGui.QTreeWidget()
        self.modules.setColumnCount(len(self.headers))
        self.modules.setHeaderLabels(self.headers)
        self.modules.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.modules.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.modules.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.modules.setUniformRowHeights(True);
        self.modules.setRootIsDecorated(False);
        
        self.modules.itemSelectionChanged.connect(self.onModuleItemSelected)
        self.modules.itemActivated.connect(lambda: self._enableModules(None))
        
        self.exportBtn = QtGui.QPushButton('Export...')
        self.exportBtn.clicked.connect(self.onExportButton)
        
        self.enableBtn = QtGui.QPushButton('Enable')
        self.enableBtn.clicked.connect(lambda: self._enableModules(True))
        
        self.disableBtn = QtGui.QPushButton('Disable')
        self.disableBtn.clicked.connect(lambda: self._enableModules(False))
        
        self.installBtn = QtGui.QPushButton('Install...')
        self.installBtn.clicked.connect(self.onInstallButton)
        
        self.uninstallBtn = QtGui.QPushButton('Uninstall')
        self.uninstallBtn.clicked.connect(self.onUninstallButton)
        
        buttons = QtGui.QHBoxLayout()
        buttons.setSpacing(10)
        
        [buttons.addWidget(btn) for btn in \
                (self.exportBtn, self.enableBtn, self.disableBtn, self.installBtn, self.uninstallBtn)]
        
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(10)
        
        layout.addWidget(self.modules)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
        
        self.populate(update=False)
        self.onModuleItemSelected()
    
    def populate(self, update=False):
        disabled = self.manager.get_disabled_names()
        
        modules = self.manager.get_wrappers()
        
        def fillitem(mod, item):
            item.setText(0, mod.base_name)
            item.setText(1, mod.metadata.display_name if mod.metadata else 'N/A')
            item.setText(2, ', '.join(a+'-'+b for (a,b) in mod.metadata.dependencies) \
                         if mod.metadata else 'N/A')
            if mod.disabled:
                [item.setBackground(c, QtGui.QColor(255, 0, 0)) for c in range(4)]
                item.setText(3, 'Disabled' if mod.base_name in disabled else 'Conflict')
            else:
                item.setText(3, 'Enabled')
            return item
        
        if not update:
            self.modules.clear()
            self._items = []
            for i, mod in enumerate(modules):
                item = QtGui.QTreeWidgetItem(self.modules)
                fillitem(mod, item)
                self._items.append(item)
        else:
            for i, mod in enumerate(modules):
                fillitem(mod, self._items[i])
        
        for c in xrange(self.modules.columnCount()):
            self.modules.resizeColumnToContents(c)
    
    def _enableModules(self, enable=None):
        selected_items = self.modules.selectedItems()
        mod_names = [item.text(0) for item in selected_items]
        self.manager.enable(mod_names, enable)
        self.populate(update=True)
    
    def onModuleItemSelected(self):
        selected_items = self.modules.selectedItems()
        self.exportBtn.setEnabled(len(selected_items) == 1)
        self.enableBtn.setEnabled(len(selected_items)>0)
        self.disableBtn.setEnabled(len(selected_items)>0)
        self.uninstallBtn.setEnabled(len(selected_items)>0)

    def onExportButton(self):
        selected_items = self.modules.selectedItems()
        
        wildcard = "Zip file (*.zip);;All files (*.*)"
        target, _ = QtGui.QFileDialog.getSaveFileName(self, "Select the destination installer", "", wildcard)
        
        name = selected_items[0].text(0)

        reply = QtGui.QMessageBox.question(self, 'Export Module',
                                'Export source also for %s?' % (name,),
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Cancel:
            return
        else:
            export_source = (reply == QtGui.QMessageBox.Yes)

        mod = self.modules_dict[name]
        self.manager.export(mod, target, export_source=export_source)
    
    def onInstallButton(self):
        wildcard = "Zip file (*.zip);;All files (*.*)"
        target, _ = QtGui.QFileDialog.getOpenFileName(self, "Select the installer", "", wildcard)
        
        info = self.manager.installer_info(target)
        if not info:
            QtGui.QMessageBox.information(self, 'Install Module', 'Invalid module installer.', QtGui.QMessageBox.Ok)
            return
        else:
            base_name, name, version = info
        
        reply = QtGui.QMessageBox.question(self, 'Install Module',
                            'Install %s version %s?\n%s' % (base_name, version, name),
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply != QtGui.QMessageBox.Yes:
            return
        
        if cbpos.modules.is_installed(base_name):
            reply = QtGui.QMessageBox.question(self, 'Install Module',
                            '%s is already installed. Do you want to replace it?' % (base_name,),
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                return
            else:
                replace = (reply == QtGui.QMessageBox.Yes)
            self.manager.install(target, info=info, replace=replace)
        else:
            self.manager.install(target, info=info, replace=False)
        self.populate()
    
    def onUninstallButton(self):
        selected_items = self.modules.selectedItems()
        reply = QtGui.QMessageBox.question(self, 'Uninstall module',
                        'Uninstall %d selected module(s)? This cannot be undone.' % (len(selected_items)),
                        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        if reply != QtGui.QMessageBox.Ok:
            return
        
        reply = QtGui.QMessageBox.question(self, 'Uninstall module',
                        'Remove resources also? This cannot be undone.',
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No |QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Cancel:
            return
        else:
            remove_res = (reply == QtGui.QMessageBox.Yes)
        
        for item in selected_items:
            name = item.text(0)
            self.manager.uninstall(name, remove_res)
        self.populate()
