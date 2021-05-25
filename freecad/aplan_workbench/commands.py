from freecad.aplan_workbench import ICONPATH
from .graphs import MotionDirection
from .assembly import Assembly
import FreeCADGui as Gui
import FreeCAD as App
import time
import os


class ExtractConnectionGraph():
    def GetResources(self):
        return {'Pixmap'  : os.path.join(ICONPATH, "connection.svg"),
                'MenuText': "Compute connection graph",
                'ToolTip' : "Compute connection graph"}


    def Activated(self):
        asm_name = App.ActiveDocument.Label
        parts = App.ActiveDocument.findObjects("Part::Feature")
        file_loc = f'{"/".join(App.ActiveDocument.FileName.split("/")[0:-1])}/APLAN'

        assembly = Assembly(asm_name, parts)
        time_start = time.time()
        connection_graph = assembly.get_connections(swell_dist=3)
        time_end = time.time()
        print(f'Total runtime [s]: {round(time_end-time_start,3)}\n')

        connection_graph.save(file_loc=file_loc)


    def IsActive(self):
        if App.ActiveDocument is None:
            return False
        else:
            return True


class ExtractObstructionGraphs():
    def GetResources(self):
        return {'Pixmap'  : os.path.join(ICONPATH, "obstruction.svg"),
                'MenuText': "Compute obstruction graphs",
                'ToolTip' : "Compute obstruction graphs"}


    def Activated(self):
        asm_name = App.ActiveDocument.Label
        parts = App.ActiveDocument.findObjects("Part::Feature")
        file_loc = f'{"/".join(App.ActiveDocument.FileName.split("/")[0:-1])}/APLAN'
        motion_directions = [MotionDirection.POS_X, MotionDirection.POS_Y, MotionDirection.POS_Z]

        assembly = Assembly(asm_name, parts)
        time_start = time.time()
        obstruction_graphs = assembly.get_obstructions(motion_directions=motion_directions, min_step_size=2.5)
        time_end = time.time()
        print(f'Total runtime [s]: {round(time_end-time_start,3)}\n')

        for obstruction_graph in obstruction_graphs:    
            obstruction_graph.save(file_loc=file_loc)


    def IsActive(self):
        if App.ActiveDocument is None:
            return False
        else:
            return True


class ToggleTransparency():
    def GetResources(self):
        return {'Pixmap'  : os.path.join(ICONPATH, "transparency.svg"),
                'MenuText': "Toggle transparency",
                'ToolTip' : "Toggle transparency"}


    def Activated(self):
        parts = App.ActiveDocument.findObjects("Part::Feature")
        
        if sum([True for part in parts if part.ViewObject.Transparency > 0]) >= len(parts)/2:
            for part in parts: part.ViewObject.Transparency = 0
        else:
            for part in parts: part.ViewObject.Transparency = 80


    def IsActive(self):
        if App.ActiveDocument is None:
            return False
        else:
            return True


Gui.addCommand('ExtractConnectionGraph', ExtractConnectionGraph())
Gui.addCommand('ExtractObstructionGraphs', ExtractObstructionGraphs())
Gui.addCommand('ToggleTransparency', ToggleTransparency())