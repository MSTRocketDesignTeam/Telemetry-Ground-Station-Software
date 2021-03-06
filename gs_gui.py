import csv
import os
import sys
import time
import keyboard
import pyqtgraph as pg
import imutils
import pytz
import cv2
import datetime
import math
from csv import writer
from pytz import timezone
from datetime import datetime, date, timezone
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap

from PyQt5.QtWidgets import *


class RDT_GS_GUI(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('rdtGsRaw.ui', self)

        dateL = date.today().strftime("%m / %d / %Y")
        self.date.setText(dateL)
        self.armBut.setStyleSheet("background-color:#37FF4F;")

        self.worker = WorkerThread()
        self.worker.start()

        self.armBut.setStyleSheet("background-color:#37FF4F;")
        if self.worker.armed:
            self.armBut.setStyleSheet("background-color:#FF3737;")
            self.armBut.setText("Disarm")
        else:
            self.armBut.setStyleSheet("background-color:#37FF4F;")
            self.armBut.setText("Arm")

        # Module Status updates
        self.worker.up_Module.connect(self.upModule)

        # Data updates
        self.worker.up_Data.connect(self.upData)
        self.worker.up_Data2.connect(self.upData2)

        # Avionics updates
        self.worker.up_Avionics.connect(self.upAvionics)

        # Telemetry updates
        self.worker.up_Telemetry.connect(self.upTelemetry)

        # Tracker updates
        # self.worker.up_Tracking.connect(self.upTracking)
        self.worker.up_TrackingTest.connect(self.upTrackingTest)
        self.armBut.clicked.connect(self.upArm)
        self.worker.up_Tracker.connect(self.upTracker)

        # Signal
        self.worker.up_sigIm.connect(self.upSignal)
        self.worker.up_signal.connect(self.upSigval)

        # Graphing
        self.worker.up_GraphData.connect(self.drawGraphs)
        self.velG.setLabel('bottom', 'Time (s)')
        self.velG.setLabel('left', 'Velocity (m/s)')
        self.velG.setTitle("Velocity", pen=pg.mkPen('k', width=2))
        self.velG.showGrid(x=True, y=True)
        self.velG.setBackground('DCDCDC')
        self.velG.getAxis('left').setTextPen('k')
        self.velG.getAxis('bottom').setTextPen('k')

        self.allaltG.setLabel('bottom', 'Time (s)')
        self.allaltG.setLabel('left', 'Altitude (m)')
        self.allaltG.setTitle("Altitude", pen=pg.mkPen('k', width=2))
        self.allaltG.showGrid(x=True, y=True)
        self.allaltG.setBackground('DCDCDC')
        self.allaltG.getAxis('left').setTextPen('k')
        self.allaltG.getAxis('bottom').setTextPen('k')
        self.allaltG.addLegend()

        self.allaccG.setLabel('bottom', 'Time (s)')
        self.allaccG.setLabel('left', 'Acceleration (m/s\u00b2)')
        self.allaccG.setTitle("Acceleration")
        self.allaccG.showGrid(x=True, y=True)
        self.allaccG.setBackground('DCDCDC')
        self.allaccG.getAxis('left').setTextPen('k')
        self.allaccG.getAxis('bottom').setTextPen('k')

        self.allorientG.setLabel('bottom', 'Time (s)')
        self.allorientG.setLabel('left', 'Roll Rate (\u00B0/s)')
        self.allorientG.setTitle("Roll Rate")
        self.allorientG.showGrid(x=True, y=True)
        self.allorientG.setBackground('DCDCDC')
        self.allorientG.getAxis('left').setTextPen('k')
        self.allorientG.getAxis('bottom').setTextPen('k')

        # Menu buttons
        self.actionData.triggered.connect(self.fileData)
        self.actionAvionics.triggered.connect(self.fileAvi)
        self.actionTelemetry.triggered.connect(self.fileTelem)
        self.actionTracking.triggered.connect(self.fileTrack)

    # Graphs
    def drawGraphs(self, timeD, yalt, yalt2, yaltav, yvel, yacc, yrollr):
        timeD = list(map(int, timeD))
        yalt = list(map(int, yalt))
        yalt2 = list(map(int, yalt2))
        yaltav = list(map(int, yaltav))
        yvel = list(map(int, yvel))
        yacc = list(map(int, yacc))
        yrollr = list(map(int, yrollr))

        self.velG.clear()
        self.velG.plot(timeD, yvel, pen=pg.mkPen('k', width=2))

        self.allaccG.clear()
        self.allaccG.plot(timeD, yacc, pen=pg.mkPen('k', width=2))

        self.allorientG.clear()
        self.allorientG.plot(timeD, yrollr, pen=pg.mkPen('k', width=2))

        self.allaltG.clear()
        self.allaltG.plot(timeD, yalt, pen=pg.mkPen('r', width=2), name='Barometer 1')
        self.allaltG.plot(timeD, yalt2, pen=pg.mkPen('b', width=2), name='Barometer 2')
        self.allaltG.plot(timeD, yaltav, pen=pg.mkPen('k', width=2), name='Average')

    # Module Status
    def upModule(self, dataacq, telemst, power, pyro):
        self.dataacqst.setText(dataacq)
        self.telemst.setText(telemst)
        self.powst.setText(power)
        self.pyrost.setText(pyro)

    # Data
    def upData(self, alt, vel, accel, rollr):
        self.altitude.setText(alt)
        self.velocity.setText(vel)
        self.acceleration.setText(accel)
        self.rollrate.setText(rollr)

    def upData2(self, timeL, UTC, MET):
        self.loctime.setText(timeL)
        self.utctime.setText(UTC)
        self.met.setText(MET)

    # Avionics
    def upAvionics(self, batv, batc, datar, dataer, onbds, chrg1, chrg2):
        self.batvolt.setText(batv)
        self.batemp.setText(batc)
        self.datarate.setText(datar)
        self.dataerror.setText(dataer)
        self.datastor.setText(onbds)
        self.charge1con.setText(chrg1)
        self.charge2con.setText(chrg2)

    # Telemetry
    def upTelemetry(self, gnss, posunc, velunc, sig, sentr, gnssst):
        self.gnsscount.setText(gnss)
        self.posunc.setText(posunc)
        self.velunc.setText(velunc)
        self.signal.setText(sig)
        self.sentrx.setText(sentr)
        self.gnssstatus.setText(gnssst)

    # Tracking
    def upTracking(self, lat, long):
        self.latcord.setText(lat)
        self.longcord.setText(long)

    def upTrackingTest(self, lat, long, dist, direc):
        self.latcord.setText(str("{:.4f}".format(lat)))
        self.longcord.setText(str("{:.4f}".format(long)))
        self.dist.setText(str(dist) + " m")
        self.direc.setText(direc)

    def upTracker(self, image):
        self.trackerimg.setPixmap(QPixmap.fromImage(image))

    # Signal Strength
    def upSignal(self, image):
        self.sigStrength.setPixmap(QPixmap.fromImage(image))

    def upSigval(self, val):
        self.sigVal.setText(val + " dB")

    def upArm(self):
        if self.worker.armed:
            self.armBut.setStyleSheet("background-color:#37FF4F;")
            self.armBut.setText("Arm")
            self.worker.armed = False
        else:
            self.armBut.setStyleSheet("background-color:#FF3737;")
            self.armBut.setText("Disarm")
            self.worker.armed = True

    # Obtain file source for all data values
    def fileData(self):
        global dataFile
        dataFile = QFileDialog.getOpenFileName(self, 'Open File: Data', '', 'CSV Files (*.csv)')[0]

    def fileAvi(self):
        global aviFile
        aviFile = QFileDialog.getOpenFileName(self, 'Open File: Avionics', '', 'CSV Files (*.csv)')[0]

    def fileTelem(self):
        global teleFile
        teleFile = QFileDialog.getOpenFileName(self, 'Open File: Telemetry', '', 'CSV Files (*.csv)')[0]

    def fileTrack(self):
        global trackFile
        trackFile = QFileDialog.getOpenFileName(self, 'Open File: Tracking', '', 'CSV Files (*.csv)')[0]


class WorkerThread(QThread):
    # Module Status
    up_Module = pyqtSignal(str, str, str, str)

    # Data
    up_Data = pyqtSignal(str, str, str, str)
    up_Data2 = pyqtSignal(str, str, str)

    # Avionics
    up_Avionics = pyqtSignal(str, str, str, str, str, str, str)

    # Telemetry
    up_Telemetry = pyqtSignal(str, str, str, str, str, str)

    # Tracker
    up_Tracking = pyqtSignal(str, str)
    up_TrackingTest = pyqtSignal(float, float, float, str)
    up_Arming = pyqtSignal(bool)

    up_Tracker = pyqtSignal(QImage)

    # Graphing
    up_GraphData = pyqtSignal(list, list, list, list, list, list, list)

    # Signal
    up_signal = pyqtSignal(str)
    up_sigIm = pyqtSignal(QImage)

    METstart = time.time()

    # Tracking
    topl = (37.2138385, -97.797595)
    botl = (37.1223676, -97.7968443)
    topr = (37.2117854, -97.6806518)
    botr = (37.122033, -97.6816494)
    lp = (37.1676624, -97.7399083)
    toplat = 37.212
    botlat = 37.122
    leftlon = -97.797
    rightlon = -97.681
    padx = 405
    pady = 405
    xmax = 810
    ymax = 810
    c = True
    armed = False
    blinkc = 0
    mrpix = [padx, pady]  # Recent pixel cords matrix
    mrcord = [round(lp[0], 4), round(lp[1], 4)]  # Recent cords matrix

    # Signal
    sigVal = 0

    def run(self):
        sat = cv2.imread("imgs/sat3.PNG")
        sig = cv2.imread("imgs/signalBar.jpg")
        while True:
            if self.armed:
                if keyboard.is_pressed('s'):
                    self.mrpix[1] += 3
                if keyboard.is_pressed('w'):
                    self.mrpix[1] -= 3
                if keyboard.is_pressed('a'):
                    self.mrpix[0] -= 3
                if keyboard.is_pressed('d'):
                    self.mrpix[0] += 3

            newsat = sat.copy()
            newsig = sig.copy()
            if keyboard.is_pressed('left'):
                self.sigVal -= 1
            if keyboard.is_pressed('right'):
                self.sigVal += 1
            sigX = int(round((self.sigVal - (-120))/140 * 600))
            cv2.line(newsig, (sigX, 0), (sigX, 80), (10, 10, 10), 3)
            image2 = imutils.resize(newsig, width=300, height=20)
            frame2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
            image2 = QImage(frame2, frame2.shape[1], frame2.shape[0], frame2.strides[0], QImage.Format_RGB888)
            self.up_sigIm.emit(image2)
            self.up_signal.emit(str(self.sigVal))

            # Draw Compass
            cv2.line(sat, (30, 750), (90, 750), (10, 10, 10), 3)  # Hori
            cv2.line(sat, (60, 720), (60, 780), (10, 10, 10), 3)  # Vert
            cv2.putText(sat, "N", (55, 714), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)
            cv2.putText(sat, "S", (54, 796), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)
            cv2.putText(sat, "E", (95, 754), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)
            cv2.putText(sat, "W", (14, 754), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)

            disx = self.mrpix[0] - self.padx
            disy = self.mrpix[1] - self.pady
            mrcordLA = round(abs((self.mrpix[1] / self.ymax) * (self.botlat - self.toplat) + self.toplat), 4)
            mrcordLO = round(((self.mrpix[0] / self.xmax) * (self.rightlon - self.leftlon) + self.leftlon), 4)

            try:
                deg = round((math.degrees(math.atan(disy / disx))))
            except ZeroDivisionError:
                deg = 0
            if disx < 0:  # West
                dir2 = "W"
            else:  # East
                dir2 = "E"
            if disy >= 0 and dir2 == "E":  # SE
                dir1 = "S"
                deg += 90
            elif disy >= 0 and dir2 == "W":  # SW
                dir1 = "S"
                deg += 270
            elif disy <= 0 and dir2 == "E":  # NE
                dir1 = "N"
                deg = 90 + deg
            elif disy <= 0 and dir2 == "W":  # NW
                dir1 = "N"
                deg += 270
            else:
                dir1 = "N"
            if disx == 0:
                if dir1 == "N":
                    deg = 0
                else:
                    deg = 180
                dir2 = ""
            if disy == 0:
                if dir2 == "E":
                    deg = 90
                else:
                    deg = 270
                dir1 = ""
            if disx == disy == 0:
                deg = 0
            direct = str(deg) + "\u00B0  " + dir1 + dir2
            dist = round(math.sqrt((disx ** 2) + (disy ** 2)), 2)
            dist2mile = round((dist / self.padx * 3.2), 2)
            dist2meters = round((dist2mile * 1609.34), 2)
            cv2.line(newsat, (self.padx, self.pady), self.mrpix, (0, 240, 255), 5)  # Distance line

            # Drawing location dot
            cv2.circle(sat, (405, 405), 3, (0, 255, 0), 5)  # Launch Pad Location
            cv2.circle(sat, self.mrpix, 2, (0, 120, 255), 5)  # Tracked path
            cv2.circle(newsat, self.mrpix, 3, (0, 0, 255), 5)  # Recent cords
            if self.armed:
                if self.blinkc % 10 < 5:  # Blinking dot border
                    cv2.circle(newsat, self.mrpix, 15, (30, 30, 255), 3)
                    cv2.circle(newsat, self.mrpix, 3, (30, 30, 255), 5)
            else:
                cv2.circle(newsat, self.mrpix, 15, (0, 0, 255), 3)
                cv2.circle(newsat, self.mrpix, 3, (0, 0, 255), 5)
            self.blinkc += 1
            self.up_TrackingTest.emit(mrcordLA, mrcordLO, dist2meters, direct)

            image = imutils.resize(newsat, width=432)
            frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            self.up_Tracker.emit(image)

            if self.c:
                dataacqst = "Active"
                telemst = "Active"
                power = "Active"
                pyro = "Active"
            else:
                dataacqst = "Inactive"
                telemst = "Inactive"
                power = "Inactive"
                pyro = "Inactive"

            self.up_Module.emit(dataacqst, telemst, power, pyro)

            try:
                with open(dataFile, "r") as file:
                    reader = csv.reader(file)
                    timeD = []
                    yAlt = []
                    yAlt2 = []
                    yAltAv = []
                    yVel = []
                    yAcc = []
                    yRollr = []
                    next(file)
                    for row in reader:
                        timeD.append(row[0])
                        yAlt.append(row[1])
                        yAlt2.append(row[2])
                        altav = round((int(row[1]) + int(row[2])) / 2)
                        yAltAv.append(str(altav))
                        yVel.append(row[3])
                        yAcc.append(row[4])
                        yRollr.append(row[5])
                        pass
                    self.up_Data.emit(yAltAv[-1] + " m",
                                      row[3] + " m/s",
                                      row[4] + " m/s\u00b2",
                                      row[5] + " \u00B0/s")
                    self.up_GraphData.emit(timeD, yAlt, yAlt2, yAltAv, yVel, yAcc, yRollr)
            except:
                pass

            try:
                with open(aviFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_Avionics.emit(row[1] + " V",
                                          row[2] + " \u00B0C",
                                          row[3] + " Hz",
                                          row[4] + " %",
                                          row[5] + " %",
                                          row[6],
                                          row[7])
            except:
                pass

            try:
                with open(teleFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_Telemetry.emit(row[1],
                                           row[2] + " m",
                                           row[3] + " m/s",
                                           row[4] + " dBm",
                                           row[5],
                                           row[6])
            except:
                pass

            try:
                with open(trackFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_Tracking.emit(str(round(float(row[1]), 6)),
                                          str(round(float(row[2]), 6)))
            except:
                pass

            timeNOW = datetime.now(pytz.timezone('US/Central'))
            timeL = timeNOW.strftime("%I:%M:%S %Z")

            utcNOW = datetime.now(timezone.utc)
            utcL = utcNOW.strftime("%I:%M:%S %Z")

            METnew = time.time()
            metdif = METnew - self.METstart
            mins = metdif // 60
            sec = round((metdif % 60))
            hours = mins // 60
            mins = mins % 60
            METl = "{:02d}:{:02d}:{:02d}".format(int(hours), int(mins), sec)

            self.up_Data2.emit(timeL, utcL, str(METl))

            self.c = not self.c
            time.sleep(0.1)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = RDT_GS_GUI()
    mainWindow.show()
    sys.exit(app.exec_())
