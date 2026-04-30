import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import numpy as np
import sys

app = QtWidgets.QApplication([])

win = pg.GraphicsLayoutWidget(title="Test Display")
win.setWindowFlags(win.windowFlags())

plot = win.addPlot()

plot.setLabel('left', 'Voltage(V)')
plot.setLabel('bottom', 'Time (samples)')
plot.showGrid(x=True, y=True, alpha=0.2)
plot.setTitle("Digital OScilloIscope", color="w", size="12pt")

plot.setContentsMargins(0, 0, 0, 0)

legend = plot.addLegend(offset=(10, 10))

curve1 = plot.plot(pen='g', name='CH1')
curve2 = plot.plot(pen='r', name='CH2')
curve3 = plot.plot(pen='b', name='CH3')

t = 0

N = 1000
data1 = np.zeros(N)
data2 = np.zeros(N)
data3 = np.zeros(N)


def update():
    global data1, data2, data3, t
    
    t += 0.5

    v1 = np.sin(2 * np.pi * t / 100)
    v2 = np.cos(2 * np.pi * t / 100)
    v3 = 1 if (t % 50) < 25 else -1

    data1 = np.roll(data1, -1) 
    data2 = np.roll(data2, -1)
    data3 = np.roll(data3, -1)

    data1[-1] = v1 #np.sin(np.random.randn() * 10)
    data2[-1] = v2 #np.sin(np.random.randn() * 10)
    data3[-1] = v3 #np.sin(np.random.randn() * 10)

    curve1.setData(data1)
    curve2.setData(data2)
    curve3.setData(data3)


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(20)


win.show()
sys.exit(app.exec())
