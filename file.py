#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, 
        QLabel, QSpinBox, QRadioButton, QFileDialog)
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt

from json import dumps, loads
from pydub import AudioSegment
from pydub.playback import play

import os
import sys
import wave
import array



class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # CONSTANTS
        self.S_WIDTH = 300  # DRAWING SCREEN DIMENTIONS 
        self.S_HEIGHT = 300
        
        self.A_WIDTH = 550  # APP DIMENTIONS
        self.A_HEIGHT = 350

        self.BG_COLOR = (0, 0, 30)    # Back- and Fore- ground colors
        self.FG_COLOR = (80, 80, 200)
        self.BGL_COlOR = (30, 30, 75) # Background lines color

        # MUSIC CONSTANTS
        self.NCHANNELS = 1
        self.SAMPWIDTH = 2 
        self.FRAMERATE = 44100
        self.SAMPLENGTH = 200
        self.NFRAMES = self.FRAMERATE * self.SAMPLENGTH

        # OTHER STUFF
        self.text = "HI" 
        self.wave = [-1] * self.S_WIDTH
        self.queue = list()
        self.lastp = 0
        self.firstp = (0, 0)
        self.secondp = (0, 0)

        self.resize(self.A_WIDTH, self.A_HEIGHT)
        self.setWindowTitle('WINDOW TITLE')

        # BUTTONS AND STUFF
        self.BASE_FREQ = 440
        self.PLAY_BUTTON = QPushButton("PLAY", self)
        self.PLAY_BUTTON.clicked.connect(self.play)
        self.PLAY_BUTTON.setGeometry(self.S_WIDTH + 1, 0,
                self.A_WIDTH - self.S_WIDTH, self.S_HEIGHT // 5)

        self.FREQ_LABEL= QLabel(self)
        self.FREQ_LABEL.setText("Frequency, Hz")
        self.FREQ_LABEL.move(self.S_WIDTH + 1, self.S_HEIGHT // 5 + 3)
        self.FREQ_BOX = QSpinBox(self)
        self.FREQ_BOX.setRange(1, 4410)
        self.FREQ_BOX.setGeometry(self.S_WIDTH + 1, self.S_HEIGHT // 5 + 15,
                (self.A_WIDTH - self.S_WIDTH) // 2, self.S_HEIGHT // 5 - 10)
        self.FREQ_BOX.setValue(self.BASE_FREQ)

        self.CLEAR_BUTTON = QPushButton("CLEAR", self)
        self.CLEAR_BUTTON.clicked.connect(self.clear)
        self.CLEAR_BUTTON.setGeometry((self.A_WIDTH + self.S_WIDTH) // 2,
                self.S_HEIGHT // 5, (self.A_WIDTH - self.S_WIDTH) // 2,
                self.S_HEIGHT // 5 + 4)

        self.SAVE_BUTTON = QPushButton("SAVE THIS GRAPH", self)
        self.SAVE_BUTTON.clicked.connect(self.save)
        self.SAVE_BUTTON.setGeometry(0, self.S_HEIGHT + 1, 
                self.S_WIDTH + 1, self.A_HEIGHT - self.S_HEIGHT)

        self.OPEN_BUTTON = QPushButton("OPEN FILE", self)
        self.OPEN_BUTTON.clicked.connect(self.show_dialog)
        self.OPEN_BUTTON.setGeometry(self.S_WIDTH + 1, self.S_HEIGHT + 1,
                self.A_WIDTH - self.S_WIDTH, self.A_HEIGHT - self.S_HEIGHT)


        # --- Part with presets ---
        PRESETS_LABEL = QLabel(self)
        PRESETS_LABEL.setText("Presets")
        PRESETS_LABEL.move(self.S_WIDTH + 3, 2 * self.S_HEIGHT // 5 + 5)
        a = 1
        for file in sorted(os.listdir( "Presets" )):
            b = str(a)
            exec(f"""
self.PRESET{b} = QRadioButton(self)
self.PRESET{b}.setText(file)
self.PRESET{b}.toggled.connect(lambda x, self=self: self.radio(self.PRESET{b}) )
if (2 * self.S_HEIGHT // 5 + 20 * a > self.S_HEIGHT - 20):
    self.PRESET{b}.move((self.S_WIDTH + self.A_WIDTH) // 2 + 3, 
            2 * self.S_HEIGHT // 5 + 20 * a 
            - 3 * self.S_HEIGHT // 5 + 20)
else:
    self.PRESET{b}.move(self.S_WIDTH + 3, 
            2 * self.S_HEIGHT // 5 + 20 * a)
""")
            a += 1


    def show_dialog(self):
        filename = QFileDialog.getOpenFileName(self, 'Open file', 
                                               'SavedGraphs')[0]
        if filename:
            file = open(filename, "rb").read()
            self.wave = loads(file)["Data"]
    
    def radio(self, button):
        filename = button.text()
        file = open("Presets/" + filename, "rb").read()
        self.wave = loads(file)["Data"]

    def save(self):
        lastfile = sorted(os.listdir("SavedGraphs"))[-1]
        lastfile = int(lastfile.rstrip(".json").lstrip("file_"))
        file = open("SavedGraphs/file_" + str(lastfile + 1) + ".json", "w")
        file.write(dumps({"Data": self.wave}))
        file.close()

    def clear(self):
        self.wave = [-1] * self.S_WIDTH
    
    def play(self):
        FREQ = self.FREQ_BOX.value()
        koef = self.FRAMERATE / FREQ
        koef /= self.S_WIDTH
        data = array.array("h")
        file = wave.open("_.wav", "w")
        file.setnchannels( self.NCHANNELS )
        file.setsampwidth( self.SAMPWIDTH )
        file.setframerate( self.FRAMERATE )
        file.setnframes( self.NFRAMES )
        file.setcomptype("NONE", "Uncompressed")

        for times in range(FREQ * 5):
            for i in range(len(self.wave)):
                sample = self.wave[i] / self.S_HEIGHT
                sample *= -30000
                data.extend([int(sample)] * len(range(int(i * koef), 
                                                  int((i + 1) * koef))))
        file.writeframes(data.tobytes())
        file.close()
        song = AudioSegment.from_wav("_.wav")
        play(song)

        

    def draw_point(self, event, qp, coords, color):
        pen = QPen( QColor(color[0], color[1], color[2]), 5, Qt.SolidLine )
        qp.setPen(pen)
        qp.drawPoint(coords[0], coords[1])
    
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        
        dx = self.secondp[0] - self.firstp[0]
        dy = self.secondp[1] - self.firstp[1]
        for x in range(min(self.firstp[0], self.secondp[0]),
                       max(self.firstp[0], self.secondp[0])):
            y = self.firstp[1] + dy * (x - self.firstp[0]) / dx
            self.wave[x] = y

        # --- Drawing background and coordinate grid ---
        qp.setBrush( QColor(self.BG_COLOR[0], self.BG_COLOR[1], 
                           self.BG_COLOR[2]) )
        qp.drawRect(0, 0, self.S_WIDTH, self.S_HEIGHT)
        pen = QPen( QColor(self.BGL_COlOR[0], self.BGL_COlOR[1],
                           self.BGL_COlOR[2]), 1, Qt.SolidLine )
        qp.setPen(pen)
        for i in range(10):
            qp.drawLine((self.S_HEIGHT / 10) * i, 0, 
                        (self.S_HEIGHT / 10) * i, self.S_WIDTH)
            qp.drawLine(0, (self.S_WIDTH / 10) * i, 
                        self.S_HEIGHT, (self.S_WIDTH / 10) * i)

        # --- Drawing the graph from self.wave list ---
        pen = QPen( QColor(self.FG_COLOR[0], self.FG_COLOR[1], 
                           self.FG_COLOR[2]), 2, Qt.SolidLine )
        qp.setPen(pen)
        for i in range(len(self.wave)):
            qp.drawPoint(i, self.wave[i] + self.S_HEIGHT / 2)
        self.firstp = self.secondp

        
        qp.end()
        self.update()

    def mousePressEvent(self, event):
        if (0 < event.x() < self.S_WIDTH and 0 < event.y() < self.S_HEIGHT):
            self.firstp = (event.x(), event.y() - self.S_HEIGHT / 2)
   


    def mouseMoveEvent(self, event):
        if (0 < event.x() < self.S_WIDTH and 
                0 < event.y() < self.S_HEIGHT and event.buttons()):
            self.secondp = (event.x(), event.y() - self.S_HEIGHT / 2)
    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
