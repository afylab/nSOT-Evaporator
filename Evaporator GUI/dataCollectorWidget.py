from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks
import numpy as np
import dataCollectorUI
import time
import exceptions

""" The following section defines the data collector object, which is used to prompt various
    equipment for data and sending them to a relevant data vault fies. """  
    
class dataCollectorWidget(QtGui.QWidget, dataCollectorUI.Ui_Form):
    def __init__(self, parent = None):
        super(dataCollectorWidget, self).__init__(parent)
        #self.connect(sub_directory)    
        #self.textEdit = textEdit
        #Initalize all the timers. 
        self.prs_rate = 1000
        self.thk_rate = 1000
        self.rate_rate = 1000
        self.volt_rate = 1000
        
        self.prs_timer = QtCore.QTimer(self)
        self.prs_timer.timeout.connect(self.update_prs)
        
        self.thk_timer = QtCore.QTimer(self)
        self.thk_timer.timeout.connect(self.update_thk)
        
        self.rate_timer = QtCore.QTimer(self)
        self.rate_timer.timeout.connect(self.update_rate)
        
        self.volt_timer = QtCore.QTimer(self)
        self.volt_timer.timeout.connect(self.update_volt)
        
        #Initalize zero time
        self.zero_prs = time.clock()
        self.zero_thk = time.clock()
        self.zero_rate = time.clock()
        self.zero_volt = time.clock()
        
        #Initialize UI
        self.setupUi(self)
        
        #Connect buttons in UI to appropriate functions
        self.pressureButton.clicked.connect(self.setPressureRate)
        self.thicknessButton.clicked.connect(self.setThicknessRate)
        self.rateButton.clicked.connect(self.setRateRate)
        self.voltButton.clicked.connect(self.setVoltRate)
        
        self.pressureStartButton.clicked.connect(self.startSamplingPressure)
        self.thicknessStartButton.clicked.connect(self.startSamplingThickness)
        self.rateStartButton.clicked.connect(self.startSamplingRate)
        self.voltStartButton.clicked.connect(self.startSamplingVolt)
        self.allStartButton.clicked.connect(self.startSamplingAll)
        
    @inlineCallbacks
    def connect(self):
        try: 
            from labrad.wrappers import connectAsync
            #Need a data vault connection for each file being run. 
            self.cxn_prs = yield connectAsync(name = 'Data Collector: Pressure')
            self.dv_prs = self.cxn_prs.data_vault
            self.rvc = self.cxn_prs.rvc_server
            yield self.rvc.select_device()
            
            self.ftm = self.cxn_prs.ftm_server
            yield self.ftm.select_device()
            
            self.tdk = self.cxn_prs.power_supply_server
            yield self.tdk.select_device()
        
            self.cxn_thk = yield connectAsync(name = 'Data Collector: Thickness')
            self.dv_thk = self.cxn_thk.data_vault
            
            self.cxn_rate = yield connectAsync(name = 'Data Collector: Deposition Rate')
            self.dv_rate = self.cxn_rate.data_vault
            
            self.cxn_volt = yield connectAsync(name = 'Data Collector: Voltage')
            self.dv_volt = self.cxn_volt.data_vault

        except:
            print 'Didn\'t work!'
            raise
            
    @inlineCallbacks
    def setDirectory(self, directory_path):
        #Wait until the experiment subdirectory is created
        #while True:
        try: 
            yield self.dv_prs.cd(directory_path)
            yield self.dv_thk.cd(directory_path)   
            yield self.dv_rate.cd(directory_path)
            yield self.dv_volt.cd(directory_path)              
                
            self.textEdit.setPlainText('Data collector successfully initialized')
               
        except:
            self.textEdit.setPlainText('Subdirectory not yet created. Try again after setting subdirectory.')
     
#----------------------------------------------------------------------------------------------#   
    """ The following section has functions for setting rates."""   
     
    def setPressureRate(self):
        try:
            self.textEdit.clear()
            self.prs_rate = int(self.pressureInput.text())
            self.pressureRate.setText(self.pressureInput.text())
            #If the timer is already running, restart it with the new rate
            if self.prs_timer.isActive():
                print "Reset timer!"
                self.prs_timer.start(self.prs_rate)
        except:
            print self.prs_timer.isActive()
            self.textEdit.setPlainText("Man, that aint a number")
        
        self.pressureInput.clear()
        
    def setThicknessRate(self):
        try:
            self.textEdit.clear()
            self.thk_rate = int(self.thicknessInput.text())
            self.thicknessRate.setText(self.thicknessInput.text())
            #If the timer is already running, restart it with the new rate
            if self.thk_timer.isActive():
                self.thk_timer.start(self.thk_rate)
        except:
            self.textEdit.setPlainText("Man, that aint a number")
        
        self.thicknessInput.clear()
        
    def setRateRate(self):
        try:
            self.textEdit.clear()
            self.rate_rate = int(self.rateInput.text())
            self.rateRate.setText(self.rateInput.text())
            #If the timer is already running, restart it with the new rate
            if self.rate_timer.isActive():
                self.rate_timer.start(self.thk_rate)
        except:
            self.textEdit.setPlainText("Man, that aint a number")
        
        self.rateInput.clear()
        
    def setVoltRate(self):
        try:
            self.textEdit.clear()
            self.volt_rate = int(self.voltInput.text())
            self.voltRate.setText(self.voltInput.text())
            #If the timer is already running, restart it with the new rate
            if self.volt_timer.isActive():
                self.volt_timer.start(self.volt_rate)
        except:
            self.textEdit.setPlainText("Man, that aint a number")
        
        self.voltInput.clear()
        
#----------------------------------------------------------------------------------------------#   
    """ The following section has functions for starting/stopping timers. Each time a timer is
    started, a new file is created to which the values are updated."""   
     
    @inlineCallbacks
    def startSamplingPressure(self, cntx):
        if self.pressureStatus.text() == 'N/A':
            self.pressureStatus.setText("Sampling")
            self.pressureStartButton.setText("Stop Sampling Pressure")
            
            yield self.dv_prs.new('Pressure vs. Time','x','y')
            
            self.zero_prs = time.clock()
            self.prs_timer.start(self.prs_rate)
 
        else: 
            self.pressureStatus.setText("N/A")
            self.pressureStartButton.setText("Start Sampling Pressure")
            self.prs_timer.stop()
    
    @inlineCallbacks
    def startSamplingThickness(self, cntx):
        if self.thicknessStatus.text() == 'N/A':
            self.thicknessStatus.setText("Sampling")
            self.thicknessStartButton.setText("Stop Sampling Thickness")
            
            yield self.dv_thk.new('Thickness vs. Time','x','y')
            
            self.zero_thk = time.clock()
            self.thk_timer.start(self.thk_rate)
        else: 
            self.thicknessStatus.setText("N/A")
            self.thicknessStartButton.setText("Start Sampling Thickness")
            self.thk_timer.stop()
    
    @inlineCallbacks
    def startSamplingRate(self, cntx):
        if self.rateStatus.text() == 'N/A':
            self.rateStatus.setText("Sampling")
            self.rateStartButton.setText("Stop Sampling Rate")
            
            yield self.dv_rate.new('Deposition Rate vs. Time','x','y')
            
            self.zero_rate = time.clock()
            self.rate_timer.start(self.thk_rate)
        else: 
            self.rateStatus.setText("N/A")
            self.rateStartButton.setText("Start Sampling Rate")
            self.rate_timer.stop()
    
    @inlineCallbacks
    def startSamplingVolt(self, cntx):
        if self.voltStatus.text() == 'N/A':
            self.voltStatus.setText("Sampling")
            self.voltStartButton.setText("Stop Sampling Voltage")
            
            yield self.dv_volt.new('Voltage vs. Time','x','y')
            
            self.zero_volt = time.clock()
            self.volt_timer.start(self.volt_rate)
            
        else: 
            self.voltStatus.setText("N/A")
            self.voltStartButton.setText("Start Sampling Voltage")
            self.volt_timer.stop()
    
    def startSamplingAll(self):
        if self.allStartButton.text() == 'Start Sampling Everything':
            if self.pressureStatus.text() == 'N/A':
                self.startSamplingPressure(None)
            if self.thicknessStatus.text() == 'N/A':
                self.startSamplingThickness(None)
            if self.rateStatus.text() == 'N/A':  
                self.startSamplingRate(None)
            if self.voltStatus.text() == 'N/A':  
                self.startSamplingVolt(None)
            self.allStartButton.setText('Stop Sampling Everything')
        else: 
            if self.pressureStatus.text() == 'Sampling':
                self.startSamplingPressure(None)
            if self.thicknessStatus.text() == 'Sampling':
                self.startSamplingThickness(None)
            if self.rateStatus.text() == 'Sampling':  
                self.startSamplingRate(None)
            if self.voltStatus.text() == 'Sampling':  
                self.startSamplingVolt(None)
            self.allStartButton.setText('Start Sampling Everything')
     
#----------------------------------------------------------------------------------------------#   
    """ The following section has functions for prompting data points."""   
     
    @inlineCallbacks    
    def update_prs(self):        
        prs = yield self.rvc.get_prs()
        num = float(prs[4:8])*(10**float(prs[9:12]))
        yield self.dv_prs.add(time.clock() - self.zero_prs, num)
        
    @inlineCallbacks    
    def update_thk(self):
        thk = yield self.ftm.get_sensor_thickness(1)
        thk = 1000*float(thk)
        yield self.dv_thk.add(time.clock() - self.zero_thk, thk)
        
    @inlineCallbacks
    def update_rate(self):
        rate = yield self.ftm.get_sensor_rate(1)
        rate = float(rate)
        yield self.dv_rate.add(time.clock() - self.zero_rate, rate)
        
    @inlineCallbacks
    def update_volt(self):
        volt = yield self.tdk.volt_read()
        volt = float(volt)
        #tzero = time.clock()
        yield self.dv_volt.add(time.clock() - self.zero_volt, volt)
        #tadd = time.clock()-tzero
        #print 'Time to add data point: ' + str(tadd)
        
#----------------------------------------------------------------------------------------------#   
    """ The following section has functions for stopping everything."""  
    
    def lock_buttons(self):   
        self.pressureButton.setEnabled(False)
        self.thicknessButton.setEnabled(False)
        self.rateButton.setEnabled(False)
        self.voltButton.setEnabled(False)
        
        self.pressureStartButton.setEnabled(False)
        self.thicknessStartButton.setEnabled(False)
        self.rateStartButton.setEnabled(False)
        self.voltStartButton.setEnabled(False)
        self.allStartButton.setEnabled(False)
        
    def unlock_buttons(self):
        self.pressureButton.setEnabled(True)
        self.thicknessButton.setEnabled(True)
        self.rateButton.setEnabled(True)
        self.voltButton.setEnabled(True)
        
        self.pressureStartButton.setEnabled(True)
        self.thicknessStartButton.setEnabled(True)
        self.rateStartButton.setEnabled(True)
        self.voltStartButton.setEnabled(True)
        self.allStartButton.setEnabled(True)
        
    def stop_timers(self):
        self.prs_timer.stop()
        self.thk_timer.stop()
        self.rate_timer.stop()
        self.volt_timer.stop()
    
    @inlineCallbacks
    def disconnect(self):
        self.stop_timers()
        print 'Data Collector Widget timers being stopped.'
        yield self.cxn_prs.disconnect()
        self.cxn_prs = None
        yield self.cxn_rate.disconnect()
        self.cxn_rate = None
        yield self.cxn_thk.disconnect()
        self.cxn_thk = None
        yield self.cxn_volt.disconnect()
        self.cxn_volt = None
        print 'Data Collector Widget connections are closed.'
        