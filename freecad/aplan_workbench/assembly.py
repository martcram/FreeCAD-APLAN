from .graphs import ConnectionGraph, ObstructionGraph, MotionDirection
from itertools import combinations, chain
import FreeCAD as App
import numpy as np
import time


class Assembly:
    def __init__(self, id, parts):
        self.id = id
        self.parts = parts
        self.part_names = [part.Label for part in parts]
        self.connections = None
        self.obstructions = None


    def get_connections(self, swell_dist=1):
        part_boundbox_dict = {part.Name: App.BoundBox((part.Shape.BoundBox.XMin-swell_dist/2), (part.Shape.BoundBox.YMin-swell_dist/2), (part.Shape.BoundBox.ZMin-swell_dist/2), (part.Shape.BoundBox.XMax+swell_dist/2), (part.Shape.BoundBox.YMax+swell_dist/2), (part.Shape.BoundBox.ZMax+swell_dist/2)) for part in self.parts}

        refined_combinations = [comb for comb in combinations(self.parts, 2) if part_boundbox_dict[comb[0].Name].intersect(comb[1].Shape.BoundBox)]

        connections = {tuple(sorted([comb[0].Label, comb[1].Label])) for comb in refined_combinations if comb[0].Shape.distToShape(comb[1].Shape)[0] < 0.01}
        
        connection_graph = ConnectionGraph(name=self.id)
        connection_graph.add_nodes_from(self.part_names)
        connection_graph.add_edges_from(connections)

        self.connections = connection_graph
        return connection_graph

    
    def get_obstructions(self, motion_directions, min_step_size=1):
        overall_boundbox = App.BoundBox()
        for part in self.parts: 
            overall_boundbox.add(part.Shape.BoundBox)

        edge_dict = {}
        for motion_direction in motion_directions:

            edge_list = []
            for target in self.parts:
                start_time = time.time()
                target_start_pos = target.Placement
                intersection_objects, intervals = self.find_obstacles(target, [part for part in self.parts if part is not target], overall_boundbox, motion_direction)

                if motion_direction == MotionDirection.POS_X:
                    diff = target.Placement.Base[0]-target.Shape.BoundBox.XMin
                elif motion_direction == MotionDirection.POS_Y:
                    diff = target.Placement.Base[1]-target.Shape.BoundBox.YMin
                elif motion_direction == MotionDirection.POS_Z:
                    diff = target.Placement.Base[2]-target.Shape.BoundBox.ZMin

                colliding_objects = []
                for index, interval in enumerate(intervals):
                    step_size = max(((interval[1]-interval[0])/10), min_step_size)

                    target_pos = interval[0]
                    if motion_direction == MotionDirection.POS_X:
                        target.Placement = App.Placement(App.Vector(interval[0]+diff, target_start_pos.Base[1], target_start_pos.Base[2]), target_start_pos.Rotation)
                    elif motion_direction == MotionDirection.POS_Y:
                        target.Placement = App.Placement(App.Vector(target_start_pos.Base[0], interval[0]+diff, target_start_pos.Base[2]), target_start_pos.Rotation)
                    elif motion_direction == MotionDirection.POS_Z:
                        target.Placement = App.Placement(App.Vector(target_start_pos.Base[0], target_start_pos.Base[1], interval[0]+diff), target_start_pos.Rotation)

                    potential_obstacles = intersection_objects[index]
                    target_pos = interval[0]
                    while target_pos < interval[1]:
                        if sum([True for obj in potential_obstacles if obj in colliding_objects]) == len(potential_obstacles):
                            break

                        self.move_target(target, step_size, motion_direction)
                        obstacles = [obst for obst in potential_obstacles if obst not in colliding_objects]
                        colliding_objects = self.detect_collisions(target, obstacles, colliding_objects)

                        if motion_direction == MotionDirection.POS_X:
                            target_pos = target.Shape.BoundBox.XMin
                        elif motion_direction == MotionDirection.POS_Y:
                            target_pos = target.Shape.BoundBox.YMin
                        elif motion_direction == MotionDirection.POS_Z:
                            target_pos = target.Shape.BoundBox.ZMin

                target.Placement = target_start_pos
                end_time = time.time()
                print(f'Motion: {motion_direction.name}, Target: {target.Label}, Obstacles: {[obj.Label for obj in colliding_objects]}, Time: {round(end_time-start_time,3)}')

                edge_list.append([(target.Label, obj.Label) for obj in colliding_objects])

            edge_dict[motion_direction] = list(chain.from_iterable(edge_list))

        obstruction_graphs = []
        for motion_direction, obstruction_list in edge_dict.items():
            obstruction_graph = ObstructionGraph(name=self.id, motion_direction=motion_direction)
            obstruction_graph.add_nodes_from(self.part_names)
            obstruction_graph.add_edges_from(obstruction_list)
            obstruction_graphs.append(obstruction_graph)

        self.obstructions = obstruction_graphs
        return obstruction_graphs


    def find_obstacles(self, target, objects, overall_boundbox, motion_direction):
        av = target.Shape.BoundBox

        if motion_direction == MotionDirection.POS_X:
            targetBB = App.BoundBox(av.XMin, av.YMin, av.ZMin, overall_boundbox.XMax, av.YMax, av.ZMax)
        elif motion_direction == MotionDirection.POS_Y:
            targetBB = App.BoundBox(av.XMin, av.YMin, av.ZMin, av.XMax, overall_boundbox.YMax, av.ZMax)
        elif motion_direction == MotionDirection.POS_Z:
            targetBB = App.BoundBox(av.XMin, av.YMin, av.ZMin, av.XMax, av.YMax, overall_boundbox.ZMax)

        obstacles = []
        intersections = []
        for obj in objects:
            if targetBB.intersect(obj.Shape.BoundBox):
                intersection = targetBB.intersected(obj.Shape.BoundBox)
                if intersection.XLength > 0.01 and intersection.YLength > 0.01 and intersection.ZLength > 0.01:
                    obstacles.append(obj)
                    
                    if motion_direction == MotionDirection.POS_X:
                        intersections.append([intersection.XMin, intersection.XMax])
                        target_boundary = target.Shape.BoundBox.XMin
                        target_size = target.Shape.BoundBox.XLength
                    elif motion_direction == MotionDirection.POS_Y:
                        intersections.append([intersection.YMin, intersection.YMax])
                        target_boundary = target.Shape.BoundBox.YMin
                        target_size = target.Shape.BoundBox.YLength
                    elif motion_direction == MotionDirection.POS_Z:
                        intersections.append([intersection.ZMin, intersection.ZMax])
                        target_boundary = target.Shape.BoundBox.ZMin
                        target_size = target.Shape.BoundBox.ZLength

        intersection_objects = []
        intervals = []
        if obstacles and intersections:
            sorted_intersections, sorted_obstacles = zip(*sorted(zip(intersections, obstacles)))

            new_intersections = [[max(target_boundary, (intersection[0]-target_size)), intersection[1]] for intersection in sorted_intersections]

            interval_boundaries = sorted(np.unique(list(chain.from_iterable(new_intersections))))
            intervals = [[first, second] for first, second in zip(interval_boundaries, interval_boundaries[1:])]
    
            intersection_objects = [[sorted_obstacles[index] for index, intersection in enumerate(new_intersections) if interval[0] < intersection[1] and intersection[0] < interval[1]] for interval in intervals]

            intersection_objects, intervals = zip(*[(obstacles, interval) for obstacles, interval in zip(intersection_objects, intervals) if obstacles])

        return intersection_objects, intervals


    def detect_collisions(self, target, obstacles, colliding_objects):
        av = target.Shape.BoundBox
        for obl in obstacles:
            ov = obl.Shape.BoundBox
            if av.intersect(ov):
                intersection = av.intersected(ov)
                if intersection.XLength > 0.01 or intersection.YLength > 0.01 or intersection.ZLength > 0.01:
                    dist, points, _ = target.Shape.distToShape(obl.Shape)
                    if dist < 0.01:
                        if sum([target.Shape.isInside(p,10**-6, False) for point in points for p in point]) >= 1 or sum([obl.Shape.isInside(p,10**-6, False) for point in points for p in point]) >= 1:   
                            colliding_objects.append(obl)

        return colliding_objects


    def move_target(self, target, step_size, motion_direction):
        if motion_direction == MotionDirection.POS_X:
            target.Placement.move(App.Vector(step_size, 0, 0))
        elif motion_direction == MotionDirection.POS_Y:
            target.Placement.move(App.Vector(0, step_size, 0))
        elif motion_direction == MotionDirection.POS_Z:
            target.Placement.move(App.Vector(0, 0, step_size))