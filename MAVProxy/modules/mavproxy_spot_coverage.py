from modules.lib import mp_module
import mavproxy_logging
import modules.lib.mp_geometry as mp_geo
import sys
import os
import json
from LatLon23 import LatLon
import shapely.geometry as sg
from modules.lib.mp_geometry import Segment, Point, Convert


logger = mavproxy_logging.create_logger("spotcoverage")
GRAVITY = 9.80665  # Gravity in meters/second on earth


class GridCell(object):
    def __init__(self, min_x, min_y, max_x, max_y):
        self.covered_percent = 0
        self.box = sg.box(min_x, min_y, max_x, max_y)

    def __str__(self):
        return str(round(self.covered_percent, 2))

    def __repr__(self):
        return str(round(self.covered_percent, 2))


class Grid(object):
    def __init__(self, min_lat, min_lon, max_lat, max_lon, granularity):
        self.convert = Convert(min_lat, min_lon)
        min_x, min_y = self.convert.ll2m(min_lat, min_lon)
        max_x, max_y = self.convert.ll2m(max_lat, max_lon)

        self.arr = []  # x, y
        for y in frange(min_y, max_y, granularity):
            row = []
            for x in frange(min_x, max_x, granularity):
                row.append(GridCell(x, y, x + granularity, y + granularity))
            self.arr.append(row)

    def __str__(self):
        output = ""
        for row in self.arr[::-1]:
            output += str(row) + "\n"
        return output

    def __repr__(self):
        output = ""
        for row in self.arr[::-1]:
            output += str(row) + "\n"
        return output

    def __getitem__(self, i):
        return self.arr[i]

    def __len__(self):
        return len(self.arr)

    def get(self, point):
        return self.arr[point.y][point.x]

    def in_bounds(self, point):
        if point.x < 0 or point.y < 0:
            return False
        try:
            self.get(point)
            return True
        except IndexError:
            return False


class Position:

    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def __repr__(self):
        return "Position: {}, {}, {}, {}".format(self.x, self.y, self.vx, self.vy)


def frange(x, y, jump):
    while x < y:
        yield x
        x += jump


class SpotCoverageModule(mp_module.MPModule):

    def __init__(self, mpstate):
        super(SpotCoverageModule, self).__init__(mpstate, "SpotModule", description="An illustrative example of module", public=True)
        self.add_command('sp_get_segments', self._get_segments, "get segments to fly")
        self.add_command('sp_set_search', self._set_searchgrid, "set search grid file")
        self.add_command('sp_set_ext_dist', self._set_ext_dist, "set extension distance")
        self.add_command('sp_set_max_bank', self._set_max_bank, "set maximum bank angle")
        self.add_command('sp_set_min_cov', self._set_min_coverage, "set minimum coverage fraction")
        self.add_command('sp_set_granularity', self._set_granularity, "set grid granularity")
        self.add_command('sp_set_height', self._set_flight_height, "set flight waypoint height")

        self.image_coords = None
        self.search_grid = None

        self.extension_distance = 20.
        self.max_bank = 30.
        self.min_coverage = 0.7
        self.granularity = 20.
        self.flight_height = 60.
        self.read_settings()

    def set_searchgrid_data(self, data):
        lat_lons = [[float(ll['lat']), float(ll['lon'])] for ll in data]
        self.search_grid = lat_lons

        dir_prefix = os.path.dirname(os.path.realpath(__file__)) + "/"
        storage_file_name = dir_prefix + 'coverage_area.gf'
        file_text = '\n'.join(['{} {}'.format(ll[0], ll[1]) for ll in lat_lons])
        try:
            with open(storage_file_name, 'w') as storage_file:
                storage_file.write(file_text)
        except IOError:
            logger.error('Unable to write coverage area file')

    def get_segments_with_settings(self, settings):
        self.extension_distance = float(settings['extension_distance']) if 'extension_distance' in settings else self.extension_distance
        self.max_bank = float(settings['max_bank']) if 'max_bank' in settings else self.max_bank
        self.min_coverage = float(settings['min_coverage']) if 'min_coverage' in settings else self.min_coverage
        self.granularity = float(settings['granularity']) if 'granularity' in settings else self.granularity
        self.write_settings()
        return self._get_segments([])

    def _set_searchgrid(self, args):
        dir_prefix = os.path.dirname(os.path.realpath(__file__)) + "/"
        storage_file_name = dir_prefix + 'coverage_area.gf'
        file_name = storage_file_name if len(args) == 0 else args[0]

        try:
            with open(file_name, 'r') as file:
                file_text = file.read()
                if file_text == "":
                    logger.error('Empty File')
                    return
                lines = file_text.split('\n')
                lat_lons = [map(float, line.rstrip().split(' ')) for line in lines]
            self.search_grid = lat_lons
        except IOError:
            pass

        self.read_settings()

    def get_settings(self):
        settings_obj = {
            'extension_distance': self.extension_distance,
            'max_bank': self.max_bank,
            'min_coverage': self.min_coverage,
            'granularity': self.granularity,
            'flight_height': self.flight_height
        }
        return settings_obj

    def get_searchgrid(self):
        self._set_searchgrid([])
        return self.search_grid

    def _get_segments(self, args):
        fill_lines = self._get_fill_lines()
        if fill_lines is None:
            return None

        db = self.mpstate.public_modules['database']
        gps = db.get_gps()
        vfr_hud = db.get_vfr_hud()
        initial_position = Position(gps['lat'], gps['lon'], vfr_hud['airvx'], vfr_hud['airvy'])
        points = self.ordered_segments_to_points(fill_lines, initial_position)
        waypoints = []
        for point in points:
            wp = {}
            wp['index'] = -1
            wp['lat'] = point.x
            wp['lon'] = point.y
            wp['alt'] = self.flight_height
            wp['sda'] = False
            wp['command'] = 16
            waypoints.append(wp)
        return waypoints

    def _set_ext_dist(self, args):
        try:
            self.extension_distance = float(args[0])
        except IndexError:
            logger.error('No distance provided')
        except ValueError:
            logger.error('Invalid number provided')
        self.write_settings()

    def _set_max_bank(self, args):
        try:
            self.max_bank = float(args[0])
        except IndexError:
            logger.error('No angle provided')
        except ValueError:
            logger.error('Invalid number provided')
        self.write_settings()

    def _set_min_coverage(self, args):
        try:
            self.min_coverage = float(args[0])
        except IndexError:
            logger.error('No fraction provided')
        except ValueError:
            logger.error('Invalid number provided')
        self.write_settings()

    def _set_granularity(self, args):
        try:
            self.granularity = float(args[0])
        except IndexError:
            logger.error('No granularity provided')
        except ValueError:
            logger.error('Invalid number provided')
        self.write_settings()

    def _set_flight_height(self, args):
        try:
            self.flight_height = float(args[0])
        except IndexError:
            logger.error('No flight height provided')
        except ValueError:
            logger.error('Invalid number provided')
        self.write_settings()

    def read_settings(self):
        dir_prefix = os.path.dirname(os.path.realpath(__file__)) + "/"
        storage_file_name = dir_prefix + 'coverage_settings.json'
        try:
            with open(storage_file_name, 'r') as storage_file:
                jsn = json.loads(storage_file.read())
                self.extension_distance = jsn['extension_distance']
                self.max_bank = jsn['max_bank']
                self.min_coverage = jsn['min_coverage']
                self.granularity = jsn['granularity']
                self.flight_height = jsn['flight_height']
        except IOError:
            logger.error('Invalid settings read file')
            self.write_settings()
        except ValueError:
            logger.error('Invalid JSON')
            self.write_settings()
        except KeyError:
            logger.error('Missing property')
            self.write_settings()

    def write_settings(self):
        dir_prefix = os.path.dirname(os.path.realpath(__file__)) + "/"
        storage_file_name = dir_prefix + 'coverage_settings.json'
        try:
            with open(storage_file_name, 'w') as storage_file:
                settings_obj = {
                    'extension_distance': self.extension_distance,
                    'max_bank': self.max_bank,
                    'min_coverage': self.min_coverage,
                    'granularity': self.granularity,
                    'flight_height': self.flight_height
                }
                storage_file.write(json.dumps(settings_obj))
        except IOError:
            logger.error('Invalid settings write file')

    def generate_polygons(self):
        image_data = self.mpstate.public_modules['distributed'].get_image_data()
        if image_data is None:
            logger.info('No image data available')
            return
        image_coords = []
        for image in image_data:
            image_obj = []
            for name in ['topLeft', 'topRight', 'bottomLeft', 'bottomRight']:
                image_obj.append((image[name]['lat'], image[name]['lon']))
            image_coords.append(image_obj)
        self.image_coords = image_coords

    def _get_fill_lines(self):
        self.generate_polygons()
        self._set_searchgrid([])
        if self.image_coords is None or self.search_grid is None:
            logger.error('Missing image coordinates or search grid')
            return None
        gps = self.mpstate.public_modules['database'].get_gps()
        fill_lines = self.get_fill_lines(self.search_grid, self.image_coords, gps['lat'], gps['lon'], gps['heading'])
        return fill_lines

    def ordered_segments_to_points(self, list_of_segments, initial_position):
        ordered_segments = self.find_segments_in_order(list_of_segments, initial_position)
        points = []
        for i, segment in enumerate(ordered_segments):
            future_segment = ordered_segments[i + 1] if i + 1 < len(ordered_segments) else None
            points.append(self.get_pre_point(segment.p1, segment.p2))
            points.append(segment.p1)
            points.append(segment.p2)
            points.append(self.get_pre_point(segment.p2, segment.p1, future_segment))
        return points

    def find_segments_in_order(self, list_of_segments, current_position):
        ordered_segments = []
        # greedy approach
        while len(list_of_segments) > 0:
            best_segment, p1_better = self.find_best_segment(list_of_segments, current_position)
            new_segment = mp_geo.Segment(best_segment.p1, best_segment.p2) if p1_better else mp_geo.Segment(best_segment.p2, best_segment.p1)
            ordered_segments.append(new_segment)
            list_of_segments.remove(best_segment)

            conv = mp_geo.Convert(new_segment.p1.x, new_segment.p1.y)
            new_p1_m = mp_geo.Point(*conv.ll2m(new_segment.p1.x, new_segment.p1.y))
            new_p2_m = mp_geo.Point(*conv.ll2m(new_segment.p2.x, new_segment.p2.y))
            new_v = new_p2_m - new_p1_m
            # normalize new_v
            if new_v.x != 0 or new_v.y != 0:
                magnitude = (new_v.x ** 2 + new_v.y ** 2) ** 0.5
                new_v = new_v.mult(1 / magnitude)
            current_position = Position(new_segment.p2.x, new_segment.p2.y, new_v.x, new_v.y)
        return ordered_segments

    # Lower is better
    def point_score(self, point, next_point, end_segment, current_attitude):
        conv = mp_geo.Convert(current_attitude.x, current_attitude.y)
        here_m = mp_geo.Point(*conv.ll2m(current_attitude.x, current_attitude.y))
        point_m = mp_geo.Point(*conv.ll2m(point.x, point.y))
        next_point_m = mp_geo.Point(*conv.ll2m(next_point.x, next_point.y))
        end_segment_m = mp_geo.Point(*conv.ll2m(end_segment.x, end_segment.y))

        distance = here_m.distance(point_m)
        length = next_point_m.distance(end_segment_m)

        return distance - length

    def get_pre_point(self, point1, point2, future_point=None):
        diff_point = point2 - point1
        angle = atan2(diff_point.y, diff_point.x) * 180 / pi
        heading = 360 - angle
        point1_latlon = LatLon(point1.x, point1.y)

        if future_point is None:
            future_point = point1
        else:
            future_point = future_point.p1

        conv = mp_geo.Convert(point1.x, point1.y)
        point1_m = mp_geo.Point(*conv.ll2m(point1.x, point1.y))
        future_point_m = mp_geo.Point(*conv.ll2m(future_point.x, future_point.y))

        extension = min(future_point_m.distance(point1_m) / 5, 15)
        new_latlon = point1_latlon.offset(heading, (self.extension_distance + extension) / 1000)
        new_point = mp_geo.Point(float(new_latlon.lat), float(new_latlon.lon))
        return new_point

    def find_best_segment(self, list_of_segments, current_position):
        best_segment = None
        best_p1_better = True
        best_score = sys.maxint
        for segment in list_of_segments:
            p1_score = self.point_score(self.get_pre_point(segment.p1, segment.p2), segment.p1, segment.p2, current_position)
            p2_score = self.point_score(self.get_pre_point(segment.p2, segment.p1), segment.p2, segment.p1, current_position)
            p1_better = p1_score < p2_score
            lower_score = min(p1_score, p2_score)
            if lower_score < best_score:
                best_segment = segment
                best_score = lower_score
                best_p1_better = p1_better
        return best_segment, best_p1_better

    # Splits the search polygon into a grid of size granularity * granularity
    # Each cell contains the percent of the cell that has been covered.
    # search polygon: [[lat, lon],...]
    # coverage_polygons: [polygon, polygon]
    # granularity is in meters
    def create_grid(self, search_polygon_arr, coverage_polygons_arr):
        grid = Grid(*sg.Polygon(search_polygon_arr).bounds, granularity=self.granularity)

        coverage_polygons_arr_xy = [[grid.convert.ll2m(lat, lon) for lat, lon in polygon] for polygon in coverage_polygons_arr]
        coverage_polygons = map(sg.Polygon, coverage_polygons_arr_xy)

        for row in grid.arr:
            for grid_cell in row:
                for p in coverage_polygons:
                    grid_cell.covered_percent += grid_cell.box.intersection(p).area / grid_cell.box.area
        return grid

    def find_unfilled_area(self, start_point, frontier, visited, grid):
        to_fill = set()
        fill_frontier = set([start_point])
        while fill_frontier:
            curr = fill_frontier.pop()
            if curr in visited or not grid.in_bounds(curr):
                continue
            # If it's covered, add it to the general search frontier, but not this current flood fill
            if grid.get(curr).covered_percent >= self.min_coverage:
                frontier.add(curr)
                continue
            # We both need to fill it in this iteration, and we can count it as visited
            to_fill.add(curr)
            visited.add(curr)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                fill_frontier.add(Point(curr.x + dx, curr.y + dy))

        return to_fill

    def fill_blob(self, start_point, frontier, visited, grid):
        lines = []
        to_fill = self.find_unfilled_area(start_point, frontier, visited, grid)

        while to_fill:
            max_y = max(f.y for f in to_fill)
            max_x = max(f.x for f in to_fill)
            min_y = min(f.y for f in to_fill)
            min_x = min(f.x for f in to_fill)

            best_start = None
            best_end = None
            best_length = 0

            curr_start = None

            # Vertical sweep
            for x in xrange(min_x, max_x + 1):
                curr_start = None
                for y in xrange(min_y, max_y + 1):
                    curr = Point(x, y)
                    if curr in to_fill and not curr_start:
                        curr_start = curr
                    if (curr not in to_fill or y == max_y) and curr_start:
                        end = Point(x, y - 1 if curr not in to_fill else y)
                        if (end.y - curr_start.y) + 1 > best_length:
                            best_start = curr_start
                            best_end = end
                            best_length = (end.y - curr_start.y) + 1
                        curr_start = None

            # Horizontal sweep
            for y in xrange(min_y, max_y + 1):
                for x in xrange(min_x, max_x + 1):
                    curr = Point(x, y)
                    if curr in to_fill and not curr_start:
                        curr_start = curr
                    if (curr not in to_fill or x == max_x) and curr_start:
                        end = Point(x - 1 if curr not in to_fill else x, y)
                        if end.x - curr_start.x > best_length:
                            best_start = curr_start
                            best_end = end
                            best_length = end.x - curr_start.x
                        curr_start = None

            start_coords = grid.get(best_start).box.centroid.coords[0]
            end_coords = grid.get(best_end).box.centroid.coords[0]

            lines.append([grid.convert.m2ll(*start_coords), grid.convert.m2ll(*end_coords)])

            for x in range(best_start.x, best_end.x + 1):
                for y in range(best_start.y, best_end.y + 1):
                    to_fill.remove(Point(x, y))

        return lines

    def get_fill_lines(self, search_polygon_arr, coverage_polygons_arr, start_lat, start_lon, heading):
        grid = self.create_grid(search_polygon_arr, coverage_polygons_arr)

        lines = []
        visited = set()
        frontier = set([Point(0, 0)])
        while frontier:
            curr = frontier.pop()
            if curr in visited or not grid.in_bounds(curr):
                continue
            curr_cell = grid.get(curr)
            if curr_cell.covered_percent < self.min_coverage:
                lines.extend(self.fill_blob(curr, frontier, visited, grid))

            visited.add(curr)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                frontier.add(Point(curr.x + dx, curr.y + dy))

        # Convert to segments
        segments = []
        for line in lines:
            seg = Segment(Point(line[0]['lat'], line[0]['lon']), Point(line[1]['lat'], line[1]['lon']))
            segments.append(seg)
        return segments


instance = None
def get_spot_coverage_mod():
    global instance
    if (instance is None):
        raise Exception("SpotCoverageModule Not Initialized")
    return instance


def init(mpstate):
    '''initialize module'''
    global instance
    instance = SpotCoverageModule(mpstate)
    return instance
