import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import numpy as np
import sys

app = QtWidgets.QApplication([]) #Create Qt application

win = pg.GraphicsLayoutWidget(title="Test Display") #creates main oscilloscope window
win.setWindowFlags(win.windowFlags())

plot = win.addPlot() #Create plot inside the window

#Configure axis labels
plot.setLabel('left', 'Voltage(V)')
plot.setLabel('bottom', 'Time (samples)')
plot.showGrid(x=True, y=True, alpha=0.2) # Enable grid for readability
plot.setTitle("Digital OScilloIscope", color="w", size="12pt") #Set plot title

plot.setContentsMargins(0, 0, 0, 0)# Remove extra padding so plot fills window better

legend = plot.addLegend(offset=(10, 10)) # Add legend for channel indetification

# Create 3 wafeform channels
# Each curve represents one oscilliscope input
curve1 = plot.plot(pen='g', name='CH1')
curve2 = plot.plot(pen='r', name='CH2')
curve3 = plot.plot(pen='b', name='CH3')

#Initializes time variable 
#Used to generate waveforms
t = 0

#Buffer size or number of displayed values
N = 1000

#Initializes waveform storage buffer
#Each channel stires last N samples
data1 = np.zeros(N)
data2 = np.zeros(N)
data3 = np.zeros(N)

#Update function
#Runs repeadetly via timer
def update():
    global data1, data2, data3, t
    
    t += 0.5 # increment time step

    v1 = np.sin(2 * np.pi * t / 100) # Ch1: Sine wave
    v2 = np.cos(2 * np.pi * t / 100) # CH2: Cosine wave
    v3 = 1 if (t % 50) < 25 else -1  # CH3: Square wave

    #Shift data left creates the scrolling oscilliscope effect
    data1 = np.roll(data1, -1) 
    data2 = np.roll(data2, -1)
    data3 = np.roll(data3, -1)

    #Insert newest sample at end of buffer
    data1[-1] = v1 #np.sin(np.random.randn() * 10)
    data2[-1] = v2 #np.sin(np.random.randn() * 10)
    data3[-1] = v3 #np.sin(np.random.randn() * 10)

    #Updat plots with new data
    curve1.setData(data1)
    curve2.setData(data2)
    curve3.setData(data3)

#Timer setup
# 20 ms update intervals ~ real time display of around 50 frames per second
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(5) # This timer start function operates at 5 ms


win.show() #Start window
sys.exit(app.exec()) # Start Qt event loop 
