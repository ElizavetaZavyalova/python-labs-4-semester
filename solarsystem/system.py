import sys
from pyqtgraph.Qt import QtCore, QtWidgets
import pyqtgraph.opengl as gl
import numpy as np
import math


class Rotate:
    def __init__(self, _R: int, _w: gl.GLViewWidget):
        self.w = _w
        self.R = _R / 2
        self.orbit = None
        self.list_of_plots = []
        self.list_of_plots_pos = []
        self.phi = 0

    def set_orbit(self, _orbit):
        self.orbit = _orbit

    def draw(self):
        for plots in self.list_of_plots:
            self.w.addItem(plots)

    def set_list_of_plots(self):
        for i in range(3):
            cordinates = [[self.orbit['x'], self.orbit['y'], self.orbit['z']],
                          [self.orbit['x'], self.orbit['y'], self.orbit['z']]]
            cordinates[0][i] += self.R
            cordinates[1][i] -= self.R
            self.set_list(cordinates)

    def set_list(self, cordinates):
        pts3 = np.array(cordinates)
        plt3 = gl.GLScatterPlotItem(pos=pts3, color=(255, 0, 255, 1), size=0.12 * self.R, pxMode=False)
        self.list_of_plots.append(plt3)
        self.list_of_plots_pos.append(plt3.pos)
        plt3 = gl.GLLinePlotItem(pos=pts3, color=(1, 1, 0, 1))
        plt3.setData(width=2.8 * self.R)
        self.list_of_plots.append(plt3)
        self.list_of_plots_pos.append(plt3.pos)

    def set_color2(self, _r, _g, _b):
        self.list_of_plots[1].setData(color=(_r, _g, _b, 1))

    def set_color1(self, _r, _g, _b):
        self.list_of_plots[0].setData(color=(_r, _g, _b, 1))

    def move(self, time):
        phi = (time * math.pi) / 180
        Mr_z = [[math.cos(phi), math.sin(phi), 0],
                [-math.sin(phi), math.cos(phi), 0],
                [0, 0, 1]]
        Mr_x = [[1, 0, 0],
                [0, math.cos(phi), math.sin(phi)],
                [0, -math.sin(phi), math.cos(phi)]]
        Mr_y = [[math.cos(phi), 0, math.sin(phi)],
                [0, 1, 0],
                [-math.sin(phi), 0, math.cos(phi)]]
        Mr_xyz = np.dot(Mr_x, Mr_y)
        Mr_xyz = np.dot(Mr_xyz, Mr_z)

        for plt, plt_pos in zip(self.list_of_plots, self.list_of_plots_pos):
            pos_new = np.dot(plt_pos, Mr_xyz)
            for i in range(2):
                pos_new[i][0] += self.orbit['x']
                pos_new[i][1] += self.orbit['y']
                pos_new[i][2] += self.orbit['z']

            plt.setData(pos=pos_new)


class Formulas:
    @staticmethod
    def get_rot_matrix(_axis, _angle_rad):
        if _axis == 'x':
            return np.array([[1, 0, 0],
                             [0, math.cos(_angle_rad), math.sin(_angle_rad)],
                             [0, -math.sin(_angle_rad), math.cos(_angle_rad)]])
        if _axis == 'y':
            return np.array([[math.cos(_angle_rad), 0, math.sin(_angle_rad)], [0, 1, 0],
                             [-math.sin(_angle_rad), 0, math.cos(_angle_rad)]])
        if _axis == 'z':
            return np.array(
                [[math.cos(_angle_rad), math.sin(_angle_rad), 0], [-math.sin(_angle_rad), math.cos(_angle_rad), 0],
                 [0, 0, 1]])

    @staticmethod
    def get_3d_rot_matrix(_psi_rad: float = 0, _phi_rad: float = 0, _theta_rad: float = 0) -> np.ndarray:
        rot_z_1 = Formulas.get_rot_matrix('z', _psi_rad)
        rot_x = Formulas.get_rot_matrix('x', _theta_rad)
        rot_z_2 = Formulas.get_rot_matrix('z', _phi_rad)
        rot_matrix = rot_z_1
        rot_matrix = rot_matrix.dot(rot_x)
        rot_matrix = rot_matrix.dot(rot_z_2)
        return rot_matrix

    @staticmethod
    def get_ellipse_pts(a: float, b: float) -> np.ndarray:
        pts = []
        angle_rng = np.linspace(0, 2 * math.pi, 180, endpoint=True)
        for angle in angle_rng:
            x = a * math.sin(angle)
            y = b * math.cos(angle)
            pts.append([x, y, 0])

        return np.array(pts)


class Orbit:
    def __init__(self, a, e, _w: gl.GLViewWidget):
        self.w = _w
        self.pos = None
        self.orbit = {'a': a, 'b': a * math.sqrt(1 - e ** 2)}
        self.plt = None
        self.pts = None
        self.central_body = None
        self.angle = {'phi': 0, 'psi': 0, 'theta': 0}

    def get_center(self):
        return self.pos

    def set_color(self, _r, _g, _b):
        self.plt.setData(color=(_r, _g, _b, 0.6))

    def set_plot(self):
        pts = Formulas.get_ellipse_pts(self.orbit['a'], self.orbit['b'])
        pts = np.dot(pts,
                     Formulas.get_3d_rot_matrix(_psi_rad=np.radians(self.angle['psi']),
                                                _theta_rad=np.radians(self.angle['theta']),
                                                _phi_rad=np.radians(self.angle['phi'])))
        pts += np.array([self.pos['x'], self.pos['y'], self.pos['z']])
        return pts

    def draw(self):
        self.pts = self.set_plot()
        self.plt = gl.GLLinePlotItem(pos=np.array(self.pts), color=(0, 255, 0, 0.6), width=5)
        self.w.addItem(self.plt)

    def move(self):
        self.pts = self.set_plot()
        self.plt.setData(pos=np.array(self.pts))

    def set_body_pos(self, body_pos):
        self.pos = body_pos


class CelestialObject:
    def __init__(self, r, w: gl.GLViewWidget):
        self.pos = {'x': 0, 'y': 0, 'z': 0}
        self.angle = {'phi': 0, 'psi': 0, 'theta': 0}
        self.w = w
        self.radius = r
        self.body = self.set_body()
        self.orbit = None
        self.orb = None
        self.orbit_a = None
        self.orbit_b = None
        self.rotate = Rotate(r, w)

    def set_rotate(self):
        self.rotate.set_orbit(self.get_center())
        self.rotate.set_list_of_plots()

    def set_body(self):
        return gl.GLScatterPlotItem(
            pos=np.array([self.pos['x'], self.pos['y'], self.pos['z']]),
            size=self.radius,
            color=(255, 255, 0, 0.6),
            pxMode=False)

    def set_body_color(self, _r: int, _g: int, _b: int):
        self.body.setData(color=(_r, _g, _b, 0.6))

    def draw(self):
        self.w.addItem(self.body)
        if self.rotate is not None:
            self.rotate.draw()

    def set_orbit(self, orbit: Orbit):
        self.orb = orbit
        self.orbit = orbit.get_center()
        self.orbit_a = orbit.orbit['a']
        self.orbit_b = orbit.orbit['b']
        self.angle = orbit.angle

    def move(self, time):
        self.rotate.set_orbit(self.get_center())
        self.rotate.move(time)
        if self.orbit is None:
            return
        self.recount_pos(time)
        self.plt_sphere.setData(pos=np.array([self.pos['x'], self.pos['y'], self.pos['z']]))

    def recount_pos(self, time):
        rad = np.radians(time)
        self.pos['x'] = self.orbit_a * math.cos(rad)
        self.pos['y'] = self.orbit_b * math.sin(rad)
        self.pos['z'] = 0
        pos = [self.pos['x'], self.pos['y'], self.pos['z']]
        new_pos = np.dot(pos, Formulas.get_3d_rot_matrix(_psi_rad=np.radians(self.angle['psi']),
                                                         _theta_rad=np.radians(self.angle['theta']),
                                                         _phi_rad=np.radians(self.angle['phi'])))
        self.pos['x'] = new_pos[0] + self.orbit['x']
        self.pos['y'] = new_pos[1] + self.orbit['y']
        self.pos['z'] = new_pos[2] + self.orbit['z']

    def get_center(self):
        return self.pos


class Planet(CelestialObject):
    def __init__(self, w):
        super().__init__(3, w)
        self.set_body_color(0, 0, 255)

    def move(self, time):
        if self.orbit is None:
            return
        self.recount_pos(2 * time)
        self.body.setData(pos=np.array([self.pos['x'], self.pos['y'], self.pos['z']]))
        self.rotate.set_orbit(self.get_center())
        self.rotate.move(time)


class Sputnik(CelestialObject):
    def __init__(self, w):
        super().__init__(1, w)
        self.set_body_color(255, 0, 0)

    def move(self, time):
        if self.orbit is None:
            return
        self.recount_pos(3 * time)
        self.body.setData(pos=np.array([self.pos['x'], self.pos['y'], self.pos['z']]))
        self.rotate.set_orbit(self.get_center())
        self.rotate.move(time)


class Sun(CelestialObject):
    def __init__(self, w):
        super().__init__(5, w)


class SolarSystem:
    def __init__(self):
        self.celestial_objects = []
        self.w = gl.GLViewWidget()
        self.draw()
        self.setup()
        self.time = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(70)

    def update(self):
        self.time = (self.time + 1.5) % 360
        for celestial_object in self.celestial_objects:
            celestial_object.move(self.time)
            if celestial_object.orbit is not None:
                celestial_object.orb.move()

    def get_wid(self):
        return self.w

    def draw(self):
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.w.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.w.addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        self.w.addItem(gz)

    def create(self):
        sun = Sun(self.get_wid())
        sun.set_rotate()
        sun.draw()

        planet = Planet(self.get_wid())

        sputnik = Sputnik(self.get_wid())

        planet_orb = Orbit(14, 0.2, self.get_wid())
        planet_orb.set_body_pos(sun.get_center())
        planet.set_orbit(planet_orb)
        planet.set_rotate()
        planet.draw()
        planet_orb.draw()

        sputnik_orb = Orbit(5, 0.9, self.get_wid())
        sputnik_orb.set_body_pos(planet.get_center())
        sputnik.set_orbit(sputnik_orb)
        sputnik.set_rotate()
        sputnik_orb.draw()
        sputnik.draw()

        self.celestial_objects.append(sun)
        self.celestial_objects.append(planet)
        self.celestial_objects.append(sputnik)

    def setup(self):
        self.w.setCameraPosition(distance=50)
        self.w.showMaximized()

    def add_celestial_object(self, celestial_object):
        self.celestial_objects.append(celestial_object)


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseDesktopOpenGL)
    app = QtWidgets.QApplication(sys.argv)
    solar_system = SolarSystem()
    solar_system.create()
    sys.exit(app.exec_())
