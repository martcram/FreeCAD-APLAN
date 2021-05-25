from freecad.aplan_workbench import ICONPATH
from PySide import QtCore, QtGui
from .version import __version__
from itertools import chain
import FreeCADGui as Gui
import os


class APLANWorkbench(Gui.Workbench):
    MenuText = "APLAN"
    ToolTip = "Assembly Planning"
    Icon = os.path.join(ICONPATH, "workbench_icon.svg")
    commands = [["ToggleTransparency"], ["ExtractConnectionGraph", "ExtractObstructionGraphs"]]


    def GetClassName(self):
        return "Gui::PythonWorkbench"


    def Initialize(self):
        self.asked_feedback = False

        from .commands import ExtractConnectionGraph, ExtractObstructionGraphs
        self.appendToolbar("General", self.commands[0])
        self.appendToolbar("APLAN", self.commands[1])
        self.appendMenu("APLAN", list(chain.from_iterable(self.commands)))


    def Activated(self):
        '''
        code which should be computed when a user switch to this workbench
        '''
        pass


    def Deactivated(self):
        if not self.asked_feedback:
            diag = QtGui.QMessageBox(QtGui.QMessageBox.Question, "How was your experience?", f'Thank you for using the APLAN {__version__} workbench!\n\nWe are always interested in receiving your comments and feedback: martijn.cramer@kuleuven.be')
            diag.setWindowModality(QtCore.Qt.ApplicationModal)
            diag.exec_()

            self.asked_feedback = True


Gui.addWorkbench(APLANWorkbench())