import sys
import PyQt5.QtWidgets as QtWidgets

class C_QFileTree(QtWidgets.QWidget):

    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.windowLayout = QtWidgets.QGridLayout()
        self.windowLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.windowLayout)
        self.createInputs()
    
    def createInputs(self):

        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath('')
        self.tree = QtWidgets.QTreeView()
        self.tree.setModel(self.model)
        self.tree.setColumnHidden(1,True)
        self.tree.setColumnHidden(2,True)
        self.tree.setColumnHidden(3,True)
        self.tree.setHeaderHidden(True)
        
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        
        # self.tree.setWindowTitle("Dir View")
        # self.tree.resize(640, 480)
        
        self.windowLayout.addWidget(self.tree,0,0)
        
        