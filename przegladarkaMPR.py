"""Aplikacja
Aplikacja umozliwiająca prezentacje obrazu 3D CT w postaci rekonstrukcji multiplanarnej (MPR)
z możliwością nawigacji po wolumenie z wykorzystaniem przycisków myszy lub kółka myszy.

Aby aplikacja działała należy zaimportować następujące moduły:
* from PySide2.QtWidgets import *
* from PySide2.QtGui import *
* from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
* from matplotlib.figure import Figure
* import nibabel as nib 

Skrypt zawiera następujące klasy:
* class ImageDisplay(FigureCanvasQTAgg)
* class MainWindow(QMainWindow)

Skrypt zawiera następujące funkcje:
* drawlines(self)
* showimages(self)
* slicechange(self, event)
* slicechange2(self, event)
* slicechange3(self, event)
* openimages(self)
 
"""
# moduły umozliwiające utworzenie GUI
from PySide2.QtWidgets import *
from PySide2.QtGui import *

# moduły umożliwiające utworzenie wykresów 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# moduł umozliwiający odczytanie obrazów w formacie NIfTI (rozszerzenie nii.gz)
import nibabel as nib 
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import nibabel as nib


class ImageDisplay(FigureCanvasQTAgg):
    """Klasa, której obiekty są wykorzystywane do prezentacji poszczególnych 
    rzutów obrazu w MPR 
    """

    def __init__(self):
        """Konstruktor klasy ImageDisplay - odpowiada za stworzenie obiektu"""

        fig = Figure()
        self.axes = fig.add_subplot(1,1,1)

        super().__init__(fig)

class MainWindow(QMainWindow):
    """Klasa, której obiektem jest główne okno aplikacji"""

    def __init__(self):
        """Konstruktor klasy MainWindow - odpowiada za stworzenie obiektu"""

        super().__init__()
        self.setup()

    def setup(self):
        """Ustawia wszystkie parametry dotyczące głównego okna aplikacji"""

        self.xx = 0
        self.yy = 0
        self.zz = 0

        self.image = None
        self.setWindowTitle("MPR")
        # self.imgshape = [0,0,0]
        # self.imgdata = []
        label = QLabel("To change the slice use mouse wheel or mouse buttons (left - go one slice up, right - go one slice down)")
        label2 = QLabel("<--- Load your image here")

        self.lefttop = ImageDisplay()
        self.leftbottom = ImageDisplay()
        self.right = ImageDisplay()
        
        layout = QVBoxLayout()

        self.lefttop.axes.figure.canvas.mpl_connect('scroll_event',self.slicechange)
        self.lefttop.axes.figure.canvas.mpl_connect('button_press_event',self.slicechange)
        self.leftbottom.axes.figure.canvas.mpl_connect('scroll_event',self.slicechange2)
        self.leftbottom.axes.figure.canvas.mpl_connect('button_press_event',self.slicechange2)
        self.right.axes.figure.canvas.mpl_connect('scroll_event',self.slicechange3)
        self.right.axes.figure.canvas.mpl_connect('button_press_event',self.slicechange3)
        
       
        layout.addWidget(self.lefttop)
        layout.addWidget(self.leftbottom)

        layout4 = QVBoxLayout()
        layout4.addStretch(20)
        layout4.addWidget(self.right, Qt.AlignVCenter)
        layout4.addStretch(20)

        layout2 = QHBoxLayout()
        layout2.addLayout(layout)
        layout2.addLayout(layout4)

        layout3 = QVBoxLayout()
        button1 = QPushButton("Open image")
        button1.clicked.connect(self.openimages)

        layout_button = QHBoxLayout()
        layout_button.addWidget(button1)
        layout_button.addWidget(label2)
        layout_button.addStretch(10)
        layout3.addLayout(layout_button)
        layout3.addWidget(label, Qt.AlignHCenter)
        layout3.addLayout(layout2)

        widget = QWidget()
        widget.setLayout(layout3)
        self.setCentralWidget(widget)
        self.showMaximized()

    def drawlines(self):
        """Rysuje osie odpowiadające temu jak przemieszczamy się po konkretnych rzutach
        obrazu w MPR"""
        self.lefttop.axes.axvline(x = self.yy, color='#ff00f7', linestyle='--')
        self.lefttop.axes.axhline(y = self.zz, color='#001aff', linestyle='--')
        self.lefttop.draw()

        self.leftbottom.axes.axvline(x = self.xx, color='#fff700', linestyle='--')
        self.leftbottom.axes.axhline(y = self.yy, color='#ff00f7', linestyle='--')
        self.leftbottom.draw()

        self.right.axes.axvline(x = self.xx, color='#fff700', linestyle='--')
        self.right.axes.axhline(y = self.zz, color='#001aff', linestyle='--')
        self.right.draw()


    def showimages(self):
        """Wyświetla wybrany obraz w trzech rzutach w aplikacji"""
        self.lefttop.axes.clear()
        self.leftbottom.axes.clear()
        self.right.axes.clear()

        x_slice = self.imgdata[self.xx, :, :]
        y_slice = self.imgdata[:, self.yy, :]
        z_slice = self.imgdata[:, :, self.zz]

        self.lefttop.axes.imshow(x_slice.T, cmap="gray", origin="lower")
        self.lefttop.axes.set_title("Slice: " + str(self.xx+1) + "/" + str(self.imgshape[0]))
        self.lefttop.axes.set_aspect('auto')

        self.leftbottom.axes.imshow(z_slice.T, cmap="gray", origin="lower")
        self.leftbottom.axes.set_title("Slice: " + str(self.zz+1) + "/" + str(self.imgshape[2]))
        self.leftbottom.axes.set_aspect('auto')

        self.right.axes.imshow(y_slice.T , cmap="gray", origin="lower")
        self.right.axes.set_title("Slice: " + str(self.yy+1) + "/" + str(self.imgshape[1]))
        self.right.axes.set_aspect('auto')
        self.drawlines()

    def slicechange(self, event):
        """Odpowiada za zmienianie warstwy (slice), która jest aktualnie pokazywana
        w pierwszym rzucie

		Parameters
		---------
		event : obiekt
    		Pozwala na zauważenie, gdy dzieje się coś "nowego" w obrębie GUI
		"""

        if self.image:
            if event.button == 'up' or event.button == 1:
                if  self.xx < self.imgshape[0]-1:
                    self.xx = self.xx+1
                else:
                    self.xx = self.imgshape[0]-1
                self.showimages()
            if event.button == 'down' or event.button == 3:
                if  self.xx > 0:
                    self.xx = self.xx-1
                else:
                    self.xx = 0
                self.showimages()

    def slicechange2(self, event):
        """Odpowiada za zmienianie warstwy (slice), która jest aktualnie pokazywana
        w drugim rzucie

		Parameters
		---------
		event : obiekt
    		Pozwala na zauważenie, gdy dzieje się coś "nowego" w obrębie GUI
		"""

        if self.image:
            if event.button == 'up' or event.button == 1:
                if  self.zz < self.imgshape[2]-1:
                    self.zz = self.zz+1
                else:
                    self.zz = self.imgshape[2]-1
                self.showimages()
            if event.button == 'down' or event.button == 3:
                if  self.zz > 0:
                    self.zz = self.zz-1
                else:
                    self.zz = 0
                self.showimages()

    def slicechange3(self, event):
        """Odpowiada za zmienianie warstwy (slice), która jest aktualnie pokazywana
        w trzecim rzucie

		Parameters
		---------
		event : obiekt
    		Pozwala na zauważenie, gdy dzieje się coś "nowego" w obrębie GUI
		"""
        if self.image:
            if event.button == 'up' or event.button == 1:
                if  self.yy < self.imgshape[1]-1:
                    self.yy = self.yy+1
                else:
                    self.yy = self.imgshape[1]-1
                self.showimages()
            if event.button == 'down' or event.button == 3:
                if  self.yy > 0:
                    self.yy = self.yy-1
                else:
                    self.yy = 0
                self.showimages()
    
    
    def openimages(self):
        """Umożliwia otworzenie wybranego zdjęcia znajdującego się w folderze na komputerze"""

        path = QFileDialog.getOpenFileName(self,"Select file",filter="Nifti files (*.nii.gz)")
        if path[0]=="":
            return
        img = nib.load(path[0])
        if img is None:
            QMessageBox.warning(self,"Warning",f"Cannot open file {path}")
            return

        self.image = True
        self.imgdata = img.get_fdata()
        self.imgshape = img.shape
        self.xx = int(img.shape[0]/2-1)
        self.yy = int(img.shape[1]/2-1)
        self.zz = int(img.shape[2]/2-1)
        self.showimages()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec_()