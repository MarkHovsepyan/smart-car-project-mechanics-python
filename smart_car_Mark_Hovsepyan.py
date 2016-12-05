import sys
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui
from pyqtgraph.Qt import QtWidgets, QtCore


class Graph(pg.PlotWidget):
    def __init__(self):
        super(Graph, self).__init__()

        pg.setConfigOptions(antialias=True)

        self.setTitle('Acceleration - Distance Relationships')
        self.enableAutoRange('y', 1)
        self.enableAutoRange('x', 1)
        self.showGrid(x=True, y=True)

        # getting the position of the mouse pointer
        self.coords = QtWidgets.QLabel()
        self.proxy = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        self.l1 = self.getPlotItem().addLine(x=0, movable=False, pen={'color': "w"})
        self.l1 = self.getPlotItem().addLine(y=0, movable=False, pen={'color': "w"})
        self.l2 = self.plot()
        self.l3 = self.plot()
        self.l4 = self.plot()
        self.l5 = self.plot()

        # Let's initialize our variables
        self.distance = 0
        self.length = 0
        self.time_yellow = 0
        self.v_current = 0
        self.v_max = 0
        self.a_max = 0
        self.a_min = 0

        self.getPlotItem().setLabel('left', text='Distance (m)')
        self.getPlotItem().setLabel('bottom', text='Acceleration (m/s^2)')

    def set_distance(self, distance):
        self.distance = float(distance)

    def set_length(self, length):
        self.length = float(length)

    def set_t_yellow(self, time_yellow):
        self.time_yellow = float(time_yellow)

    def set_v_current(self, car_vel):
        self.v_current = float(car_vel) * 1000 / float(3600)

    def set_v_max(self, v_max):
        self.v_max = float(v_max) * 1000 / float(3600)

    def set_a_max(self, acc):
        self.a_max = float(acc)

    def set_a_min(self, acc):
        if (float(acc) < 0):
            self.a_min = float(acc)
        else:
            self.a_min = -float(acc)


    # function for updating the plot in real time
    def plot_real_time(self):

        # let's create our initial axes (a, d)
        l0 = self.getPlotItem().addLine(x=0, movable=False, pen={'color': "w"})
        l1 = self.getPlotItem().addLine(y=0, movable=False, pen={'color': "w"})

        if self.distance != 0:
            l2 = self.getPlotItem().addLine(y=self.distance, movable=True, pen={'color': "c"})
        else:
            pass

        if self.length != 0:
            l3 = self.getPlotItem().addLine(y=self.length + self.distance, movable=True, pen={'color': "m"})
        else:
            pass

        if self.a_min != 0:
            l4 = self.getPlotItem().addLine(x=self.a_min, movable=False, pen={'color': "r"})
        else:
            pass

        if self.a_max != 0:
            l5 = self.getPlotItem().addLine(x=self.a_max, movable=False, pen={'color': "g"})
        else:
            pass

        # Let's separtely cover the case when the car accelerates and plot it
        case_1 = int(100 * self.a_max) + 1
        a_max_temp = np.empty([case_1, ])
        a_dist_max = np.empty([case_1, ])
        a_max = 0
        for i in range(0, case_1):
            a_max_temp[i] = a_max
            if a_max == 0:
                a_dist_max[0] = self.v_current * self.time_yellow
            else:
                if self.v_current > self.v_max:
                    a_dist_max[i] = self.v_current * self.time_yellow
                else:
                    self.time_limit = (self.v_max - self.v_current) / float(a_max)
                    if self.time_limit < self.time_yellow:
                        a_dist_max[i] = self.v_current * self.time_limit + a_max * self.time_limit * self.time_limit / float(2) + self.v_max * (self.time_yellow - self.time_limit)
                    else:
                        a_dist_max[i] = self.v_current * self.time_yellow + a_max * self.time_yellow * self.time_yellow / float(2)
            a_max = a_max + 1 / 100

        self.plot(x=a_max_temp, y=a_dist_max, pen='b')

        # Let's also cover the case when the car decelerates and plot it
        if self.a_min != 0:
            case_2 = int(self.a_min * 100)
            a_min_temp = np.empty([-self.a_min * 100, ])
            a_dist_min = np.empty([-self.a_min * 100, ])
            a_min = 0
            for i in range(case_2, 0):
                a_min = a_min - 1 / 100
                a_min_temp[i] = a_min
                a_dist_min[i] = -self.v_current * self.v_current / float(2 * a_min)
        else:
            pass

        try:
            p2 = self.plot(x=a_min_temp, y=a_dist_min, pen='y')
        except:
            pass

        # changing the auto range of graphing
        self.enableAutoRange('y', 0.1)
        self.enableAutoRange('x', 1)

    def set_coordinates_indicate(self, coor_ind):
        self.coords = coor_ind

    def mouseMoved(self, event):
        mousePoint = self.getPlotItem().vb.mapSceneToView(event[0])
        self.coords.setText(
            "<span style='font-size: 15pt'> Coordinates: Acceleration = %0.2f (m/s^2), <span style='font-size: 15pt'> Distance = %0.2f (m)</span>" % (
                mousePoint.x(), mousePoint.y()))


class Window(QtWidgets.QPushButton):
    def __init__(self):
        super(Window, self).__init__()

        self.setWindowTitle('Smart Car Project')
        self.setWindowIcon(QtGui.QIcon('logo.png'))

        plot = Graph()

        exit_button = QtWidgets.QPushButton("Exit", self)
        exit_button.clicked.connect(self.close_application)

        yellow_t_input = QtWidgets.QLineEdit(self)
        yellow_t_input.setPlaceholderText('Duration of yellow traffic light, Ty (2s – 4s)')
        yellow_t_input.setValidator(QtGui.QDoubleValidator(2.00, 4.00, 2))
        yellow_t_input.textChanged.connect(lambda: plot.clear())
        yellow_t_input.textChanged.connect(lambda: plot.set_t_yellow(yellow_t_input.text()))
        yellow_t_input.textChanged.connect(plot.plot_real_time)
        yellow_t_input.textChanged.connect(plot.show)

        a_max_input = QtWidgets.QLineEdit(self)
        a_max_input.setPlaceholderText('Maximum acceleration of the car (m/s^2)')
        a_max_input.setValidator(QtGui.QDoubleValidator(0.00, 3.00, 2))
        a_max_input.textChanged.connect(lambda: plot.clear())
        a_max_input.textChanged.connect(lambda: plot.set_a_max(a_max_input.text()))
        a_max_input.textChanged.connect(plot.plot_real_time)
        a_max_input.textChanged.connect(plot.show)

        a_min_input = QtWidgets.QLineEdit(self)
        a_min_input.setPlaceholderText('Minimum acceleration of the car (m/s^2)')
        a_min_input.setValidator(QtGui.QDoubleValidator(-3.00, 0.00, 2))
        a_min_input.textChanged.connect(lambda: plot.clear())
        a_min_input.textChanged.connect(lambda: plot.set_a_min(a_min_input.text()))
        a_min_input.textChanged.connect(plot.plot_real_time)
        a_min_input.textChanged.connect(plot.show)

        v_current_input = QtWidgets.QLineEdit(self)
        v_current_input.setPlaceholderText('Vehicle’s current speed, V0 (20 km/h – 80 km/h)')
        v_current_input.setValidator(QtGui.QDoubleValidator(20.00, 80.00, 2))
        v_current_input.textChanged.connect(lambda: plot.clear())
        v_current_input.textChanged.connect(lambda: plot.set_v_current(v_current_input.text()))
        v_current_input.textChanged.connect(plot.plot_real_time)
        v_current_input.textChanged.connect(plot.show)

        distance_input = QtWidgets.QLineEdit(self)
        distance_input.setPlaceholderText('Distance to the intersection, D (7m – 50m)');
        distance_input.setValidator(QtGui.QDoubleValidator(7.00, 50.00, 2))
        distance_input.textChanged.connect(lambda: plot.clear())
        distance_input.textChanged.connect(lambda: plot.set_distance(distance_input.text()))
        distance_input.textChanged.connect(plot.plot_real_time)
        distance_input.textChanged.connect(plot.show)

        length_input = QtWidgets.QLineEdit(self)
        length_input.setPlaceholderText('Length of the intersection, L (7m – 20m)');
        length_input.setValidator(QtGui.QDoubleValidator(7.00, 20.00, 2))
        length_input.textChanged.connect(lambda: plot.clear())
        length_input.textChanged.connect(lambda: plot.set_length(length_input.text()))
        length_input.textChanged.connect(plot.plot_real_time)
        length_input.textChanged.connect(plot.show)

        v_max_input = QtWidgets.QLineEdit(self)
        v_max_input.setPlaceholderText('Speed Limit (km/h)')
        v_max_input.setValidator(QtGui.QDoubleValidator(40.00, 90.00, 2))
        v_max_input.textChanged.connect(lambda: plot.clear())
        v_max_input.textChanged.connect(lambda: plot.set_v_max(v_max_input.text()))
        v_max_input.textChanged.connect(plot.plot_real_time)
        v_max_input.textChanged.connect(plot.show)

        position_indicator = QtWidgets.QLabel()
        position_indicator.setText(
            "<span style='font-size: 13pt, '> Coordinates: a = 0 (m/s^2), <span style='', 'font-size: 13pt'> d = 0 (m)</span>")
        plot.set_coordinates_indicate(position_indicator)

        descriptlabel = QtWidgets.QLabel(
            '\nPlease input the variables to plot our graph'
            '\n\nMouse should be used to navigate the graph'
            '\n\nRight click on the graph to show the options'
            '\n\n\nNote: do not completely remove the entered variables to escape'
            '\nthe crashing of the app (the program is in the beta version)')

        authorlabel = QtWidgets.QLabel(
            '\n\nMark Hovsepyan\nAmerican University of Armenia\nClass: Mechanics\nInstructor: Arsen Tonoyan\nProject Title: Smart Car Project')

        layout = QtWidgets.QGridLayout(self)

        layout.addWidget(distance_input, 1, 3)
        layout.addWidget(length_input, 2, 3)
        layout.addWidget(a_max_input, 3, 3)
        layout.addWidget(a_min_input, 4, 3)
        layout.addWidget(yellow_t_input, 5, 3)
        layout.addWidget(v_current_input, 6, 3)
        layout.addWidget(v_max_input, 7, 3)
        layout.addWidget(exit_button, 11, 2, 1, 2)

        layout.addWidget(position_indicator, 11, 1)
        layout.addWidget(plot, 1, 1, 10, 1)

        layout.addWidget(descriptlabel, 8, 2, 1, 2)
        layout.addWidget(authorlabel, 10, 2, 1, 2)
        authorlabel.setAlignment(QtCore.Qt.AlignRight)
        descriptlabel.setAlignment(QtCore.Qt.AlignCenter)

        self.resize(1000, 600)
        self.show()

    def close_application(self):
        response = QtWidgets.QMessageBox.question(self, 'Exiting', "Do you really want to exit?",
                                                  QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if response == QtWidgets.QMessageBox.Ok:
            sys.exit()
        else:
            pass


app = QtWidgets.QApplication(sys.argv)
window = Window()
# sys.exit(app.exec_())
app.exec_()
