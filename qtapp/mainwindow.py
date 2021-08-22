import __global__,os

import PyQt5.QtCore    as QtCore
import PyQt5.QtGui     as QtGui
import PyQt5.QtWidgets as QtWidgets

# Get App specific widgets
from qtapp.widgets.C_QNavigator         import C_QNavigatorDock,C_QNavigator
from qtapp.widgets.C_QFileTree          import C_QFileTree
from qtapp.widgets.C_QWindowCntl        import C_QExitBtn, C_QMaxMinBtn, C_QMinimizeBtn
from qtapp.widgets.C_QScrollWidgets     import C_QRenderArea, C_QScrollArea, C_QMultiScrollArea, C_QScrollItem
from . import subwindows

class Action(QtWidgets.QAction):
    def __init__(self,*args,shortcut=None):
        super(Action,self).__init__(*args)
        if not shortcut is None:
            self.setShortcut(shortcut) 
    
    def connect(self,fn):
        self.triggered.connect(fn)
        return self


class mainWindow(QtWidgets.QMainWindow):
    def __init__(self,application,sysargs = None):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(os.path.join(__global__.MEDIA_DIR,"window.svg")))
        #Widget Layout
        self.setGeometry(100,100,1000,500)
        self.centralWidget = QtWidgets.QWidget(self)
        self.__docklayout = QtWidgets.QGridLayout(self.centralWidget)
        self.__docklayout.setSpacing(0)
        self.__docklayout.setContentsMargins(0,0,0,0)
        self.layout = QtWidgets.QGridLayout()
        self.__docklayout.addLayout(self.layout,1,1)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.setContentsMargins(0,0,0,0)

        self.setCentralWidget(self.centralWidget)

        # TODO: Add Drag function
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
  
        # Internal Memory
        self.mainWidgetMap = {}
        self.currentMainWidget = None

        # Grips
        self.grips = []
        self.gripSize = 16
        
        # Build the gui
        self.createMenu()
        self.createInputs()
        self.buildInteractions()
        
        #Private States
        # Objects
        self.__qtapplication = application
        self.__oneshotTimer  = QtCore.QTimer()
        # States
        self.__isMaximized = False
        self.__disableDrag = False
        self.__lastHeight = 0
        self.__lastWidth  = 0
        self.__lastXPos   = 0
        self.__lastYPos   = 0

     
    def createMenu(self):
        self.mainMenu = self.menuBar()

        self.mainMenu.installEventFilter(self)
        # self.mainMenu.setIconSize(self.mainMenu.height(),self.mainMenu.height())
        #
        ## ICON
        #
        self.__mainIcon = self.mainMenu.addMenu( QtGui.QIcon(os.path.join(__global__.MEDIA_DIR,"pie.svg")) , "")
        self.__mainIcon.setEnabled(False)
        #|====================
        #|   Start Menus
        #|===================
        
        #
        ## File Menu
        #
        fileMenu = self.mainMenu.addMenu('&File')

        # Actions
        fileMenu.addAction(Action("load",self).connect(self.dummy)) 
        fileMenu.addAction(Action("save",self).connect(self.dummy)) 
        
        #exit
        fileMenu.addSeparator()
        exitAct = Action("Exit",self).connect(self.close)
        fileMenu.addAction(exitAct)

        #
        ## Edit Menu
        #
        editMenu = self.mainMenu.addMenu('&Edit')

        # Actions
        editMenu.addAction(Action("settings",self).connect(self.dummy))

        #
        ## Help Menu
        #
        helpMenu = self.mainMenu.addMenu('&Help')

        # Actions
        helpMenu.addAction(Action("help",self).connect(self.dummy)) 


        #|====================
        #|  Finished Menus
        #|===================

        # Setup Window Control Buttons 
        self._menuLayout = QtWidgets.QHBoxLayout(self.mainMenu)
        self._menuLayout.setContentsMargins(0,0,0,0)
        self._menuLayout.setSpacing(0)
        self._menuLayout.addStretch()
        
        self.minwinButton = C_QMinimizeBtn(self)
        self.minwinButton.clicked.connect(self.showMinimized)
        self._menuLayout.addWidget(self.minwinButton)

        self.maxwinButton = C_QMaxMinBtn(self)
        self.maxwinButton.clicked.connect(self.toggleMaximized)
        self._menuLayout.addWidget(self.maxwinButton)

        self.exitButton = C_QExitBtn(self)
        self.exitButton.clicked.connect(self.close)
        self._menuLayout.addWidget(self.exitButton)
        
        # Add Final Spacer To Correct for any layout issues
        # self._menuLayout.addItem(QtWidgets.QSpacerItem(10,0))
        pass

    def buildInteractions(self):
        for i in range(3):
            grip = QtWidgets.QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            self.grips.append(grip)
    
    def resizeEvent(self,event):
        rect = self.rect()
        self.__isMaximized = False
        # top left grip doesn't need to be moved...
        # top right
        # self.grips[1].move(rect.right() - self.gripSize, 0)
        # bottom right
        self.grips[1].move(
            rect.right() - self.gripSize, rect.bottom() - self.gripSize)
        # bottom left
        self.grips[2].move(0, rect.bottom() - self.gripSize)

    def createInputs(self):
        self.createWidgets()
        # Left Side
        self.leftNavigator = C_QNavigator(self)
        for name,widget in self.mainWidgetMap.items(): self.leftNavigator.addButton(name,widget)
        
        self.__docklayout.addWidget(self.leftNavigator,1,0)
        self.leftNavigator.onPress.connect(self.mainWidgetChanged)
        
        self.leftNavigator.setWidget("tree")
        
        pass

        
    def eventFilter(self,watched,event):
        if(watched == self.mainMenu):
            if (event.type() == QtCore.QEvent.MouseButtonPress):
                if (event.button() == QtCore.Qt.LeftButton):
                    self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
                    return False
            elif (event.type() == QtCore.QEvent.MouseButtonDblClick):
                self.toggleMaximized()
            elif (event.type() == QtCore.QEvent.MouseMove):
                if (event.buttons() & QtCore.Qt.LeftButton) and not self.__disableDrag:
                    if self.__isMaximized:
                        if (event.globalPos().y() < 20): return False
                        self.toggleMaximized()
                    self.move(event.globalPos() - self.dragPosition)
                    if (event.globalPos().y() < 10): self.toggleMaximized(Maxonly=True)
                    return False
        return super(mainWindow, self).eventFilter(watched, event)
    
    def toggleMaximized(self,Maxonly=False):
        if self.__isMaximized:
            if Maxonly: return
            # self.showNormal()
            self.__disableDrag = True
            self.setGeometry(
                self.__lastXPos,
                self.__lastYPos,
                self.__lastWidth,
                self.__lastHeight)
            self.__isMaximized = False
            self.__oneshotTimer.singleShot(100,lambda : self.setDrag(True))
        else:
            self.__lastHeight = self.height()
            self.__lastWidth  = self.width()
            self.__lastXPos   = self.pos().x()
            self.__lastYPos   = self.pos().y()
            self.move(0,0)
            self.resize(self.__qtapplication.primaryScreen().size())
            # self.showMaximized()
            self.__isMaximized = True
            self.__disableDrag = True
            self.__oneshotTimer.singleShot(100,lambda : self.setDrag(True))

    def setDrag(self,en):
        self.__disableDrag = not en

    def mainWidgetChanged(self,widgetName):
        if not self.currentMainWidget is None: 
            self.layout.removeWidget(self.currentMainWidget)
            self.currentMainWidget.setVisible(False)
        self.currentMainWidget = self.mainWidgetMap[widgetName]
        self.layout.addWidget(self.currentMainWidget,0,1)
        self.currentMainWidget.setVisible(True)
    
    #|==================================================================================
    #|                              User Functions 
    #|==================================================================================
    def createWidgets(self):
        self.mainWidgetMap['tree'] = C_QFileTree(self)
        self.mainWidgetMap['tree'].setVisible(False)

        self.mainWidgetMap['scroll'] = C_QMultiScrollArea(self)
        self.mainWidgetMap['scroll'].setVisible(False)

        self.mainWidgetMap['scroll'].addScrollArea("left" ,C_QScrollArea(self.mainWidgetMap['scroll'],"left",C_QRenderArea(self)))
        self.mainWidgetMap['scroll'].addScrollArea("right",C_QScrollArea(self.mainWidgetMap['scroll'],"right",C_QRenderArea(self)))
        
        widget = self.mainWidgetMap['scroll'].getWidget("left")
        
        widget.addWidget('1',C_QScrollItem(self))
        widget.addWidget('2',C_QScrollItem(self))
        widget.addWidget('3',C_QScrollItem(self))
        widget.addWidget('4',C_QScrollItem(self))
        widget.addWidget('5',C_QScrollItem(self))
        pass

    def dummy(self):
        print("Dummy Function Called")
