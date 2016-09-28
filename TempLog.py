#!/usr/bin/python
import tkinter as tk
import tkinter.ttk as ttk

import sys
import glob
import time
import os

try:
    import serial
except ImportError:
    print('Please install pyserial!')
    sys.exit()

import threading

try:
    import numpy as np
except ImportError:
    print('Please install numpy!')
    sys.exit()

try:
    import matplotlib
except ImportError:
    print('Please install matplotlib!')
    sys.exit()

#matplotlib.use("GTKAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from commu import Commu

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

class TempLog(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        # we use the grid type of aligning things
        self.grid()
        
        # initialize a numpy array for the values
        self.i = 0
        self.time = np.zeros([100000,1])
        self.time.fill(np.nan)
        self.values = np.zeros([100000,3])
        self.values.fill(np.nan)
        
        # empty object for the arduino
        self.ardu = None
        
        # variable for the connected port
        self.comport = tk.StringVar(master)
        self.portlist = serial_ports()
        
        # check for COM ports
        if len(self.portlist) == 0:
            sys.exit('No COM ports found!')
        
        self.frequency = tk.StringVar(master)
        self.frequencies = ['0.1 Hz', '0.5 Hz', '1 Hz', '2 Hz', '3 Hz',]
        
        self.create_widgets()

    def create_widgets(self):
        #configure the grid - the first line and row should expand
        self.grid_rowconfigure(0,weight=1)
        
        # create a drop down menu for the comport
        self.comportselector = ttk.OptionMenu(self.master, self.comport, self.portlist[0], *self.portlist)
        self.comportselector.grid(row = 2, column = 0, sticky='W')
        
        # create a drop down menu for the update frequency
        self.frequencyselector = ttk.OptionMenu(self.master, self.frequency, self.frequencies[2], *self.frequencies)
        self.frequencyselector.grid(row = 2, column = 2, sticky='W')
        
        # clear button
        self.clearb = ttk.Button(self.master, text="Clear", command=self.clearplot)
        self.clearb.grid(row = 2, column = 4, sticky='W')
        
        # connect button
        self.connectb = ttk.Button(self.master, text="Connect", command=self.connectcom)
        self.connectb.grid(row = 2, column = 1, sticky='W')

        # log button
        self.logbtn = ttk.Button(self.master, text="Save log", command=self.savelog)
        self.logbtn.grid(row = 2, column = 3, sticky='W')

        # start and stop button
        self.startb = ttk.Button(self.master, text="Start", command=self.start)
        self.startb.grid(row = 2, column = 5, sticky='W')
        
        self.stopb = ttk.Button(self.master, text="Stop", command=self.stop)
        self.stopb.grid(row = 2, column = 6, sticky='W')
        
        self.startb.config(state='disabled')
        self.stopb.config(state='disabled')
        self.logbtn.config(state='disabled')
        
        # label for the current value
        self.valuelabel1 = ttk.Label(self.master, text="0 °C", font = 'bold', foreground = "red")
        self.valuelabel1.grid(row=1, column = 4, sticky='W')
        self.valuelabel2 = ttk.Label(self.master, text="0 °C", font = 'bold', foreground = "green")
        self.valuelabel2.grid(row=1, column = 5, sticky='W')
        self.valuelabel3 = ttk.Label(self.master, text="0 °C", font = 'bold', foreground = "blue")
        self.valuelabel3.grid(row=1, column = 6, sticky='W')
        
        # make a figure and axes in the figure
        self.f = Figure(figsize=(10,5), dpi=100)
        self.f.set_facecolor('#f0f0ed')
        self.f.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        self.a = self.f.add_subplot(111)
        
        # already plot a "line" because we only want to update (not replot every time)
        self.line1, = self.a.plot(self.time[:], self.values[:,0],'r-')
        self.line2, = self.a.plot(self.time[:], self.values[:,1], 'g-')
        self.line3, = self.a.plot(self.time[:], self.values[:,2], 'b-')

        self.canvas = FigureCanvasTkAgg(self.f, self.master)
        self.canvas.get_tk_widget().grid(row = 0, columnspan=7)
        self.canvas.show()

        # add a toolbar
        self.toolbar_frame = ttk.Frame(self.master)
        toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbar_frame)
        toolbar.update()
        self.toolbar_frame.grid(row=1, columnspan = 4, sticky='W')
        
    def clearplot(self):
        # clear the axes of everything
        self.a.cla()
        self.canvas.draw()
        self.logbtn.config(state='disabled')
        
        # overwrite variables 
        self.i = 0
        self.time = np.zeros([100000,1])
        self.time.fill(np.nan)
        self.values = np.zeros([100000,3])
        self.values.fill(np.nan)
        
        # plot the line again, so we have something to update
        self.line1, = self.a.plot(self.time[:], self.values[:,0],'r-')
        self.line2, = self.a.plot(self.time[:], self.values[:,1], 'g-')
        self.line3, = self.a.plot(self.time[:], self.values[:,2], 'b-')

        
    def connectcom(self):
        # get the selected com port
        comoption = self.comport.get()
        # connect
        self.ardu = Commu(comoption)
        
        # adjust the GUI elements
        self.startb.config(state='normal')
        self.stopb.config(state='normal')
        self.connectb.config(state='disabled')
        self.comportselector.config(state='disabled')
        
    def printvalue(self):
        # only do this if we are running
        if self.running is True:
            # immediately schedule the next run of this function
            frequency = float(self.frequency.get().replace(' Hz', ''))
            delay = 1 / frequency
            threading.Timer(delay, self.printvalue).start ()
            
            # write the current time and value in the corresponding arrays
            # self.time = np.append(self.time, self.i)
            if self.i == 0:
                self.time[self.i, 0] = 0
            else:
                self.time[self.i,0] = self.time[self.i - 1, 0] + delay
                
            #self.values = np.append(self.values, self.ardu.read_value())
            value = self.ardu.read_value()
            self.valuelabel1['text'] = str(value[0]) + " °C"
            self.valuelabel2['text'] = str(value[1]) + " °C"
            self.valuelabel3['text'] = str(value[2]) + " °C"

            # plot - note that we don't use plt.plot, because it is horribly slow

            if 'N' not in value[0]:
                self.values[self.i, 0] = value[0]
                self.line1.set_ydata(self.values[~np.isnan(self.values[:, 0]), 0])
                self.line1.set_xdata(self.time[~np.isnan(self.time[:])])

            if 'N' not in value[1]:
                self.values[self.i, 1] = value[1]
                self.line2.set_ydata(self.values[~np.isnan(self.values[:, 1]), 1])
                self.line2.set_xdata(self.time[~np.isnan(self.time[:])])

            if 'N' not in value[2]:
                self.values[self.i, 2] = value[2]
                self.line3.set_ydata(self.values[~np.isnan(self.values[:, 2]), 2])
                self.line3.set_xdata(self.time[~np.isnan(self.time[:])])

            self.i = self.i + 1

            # rescale axes every fifth run
            if self.i %10 == 1:
                self.a.relim()
                self.a.autoscale_view(scalex=False)
                self.a.set_xlim(0, self.i + 20)

            # draw the new line
            self.canvas.draw()

    def start(self):
        # clear the plot before we start a new measurement
        self.running = True
        self.clearplot()
        self.printvalue()
        self.startb.config(state='disabled')
        self.stopb.config(state='normal')
        self.logbtn.config(state='disabled')
        # get current date and time and save into logname
        self.logname = time.strftime("%Y_%m_%d")+'_'+time.strftime("%H_%M_%S")+'_TMPLog'+'.txt'
        
    def stop(self):
        self.running = False
        self.stopb.config(state='disabled')
        self.startb.config(state='normal')
        # stack time and values array horizontally into log array and make btn available
        self.log = np.hstack((self.time,self.values))
        self.logbtn.config(state='normal')

    def savelog(self):
        # save measured TMPs to file, name = currentdate+currenttime.txt
        dir = tk.filedialog.askdirectory(initialdir = os.getcwd,title="Select directory for logfile!")
        logfinal = os.path.join(dir,self.logname)
        np.savetxt(logfinal,self.log,delimiter='\t',newline='\n',header='TemperatureLog '+self.logname.replace('_TMPLog.txt','')+
                   '\n\nTime\tT1\tT2\tT3\n')

        
    def on_closing(self):
        # we should disconnect before we close the program
        self.stop()
        if self.ardu is not None:
            self.ardu.close()
        self.master.destroy()
        
root = tk.Tk()
root.geometry("980x560")
app = TempLog(master=root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.wm_title("Temp Log")
app.mainloop()
