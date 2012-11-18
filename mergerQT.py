from PyQt4 import QtGui, QtCore
import merger
import sys
import re
import time

class MergeQt(QtGui.QMainWindow):
	def __init__(self):
		super(MergeQt, self).__init__()
		self.galleryWall = merger.GalleryWall()
		self.values = {}
		self.realpath = {}
		self.fileModel = QtGui.QStringListModel()
		self.initUI()

	def initUI(self):
		width = 480
		height = 332

		leftpanel = QtGui.QFrame()
		rightpanel = QtGui.QFrame()

		leftpanel = self.createLeftPanel()
		rightpanel = self.createRightPanel()

		hbox = QtGui.QHBoxLayout()
		hbox.addWidget(leftpanel)
		hbox.addWidget(rightpanel)

		self.panel = QtGui.QFrame()
		self.panel.setLayout(hbox)
		self.setCentralWidget(self.panel)

		self.setGeometry(300, 300, width, height)
		self.statusBar().addWidget(self.createStatusBar())
		self.statusBar().showMessage("Something")
		self.setWindowTitle('Statusbar')
		self.show()

	def createStatusBar(self):
		panel = QtGui.QFrame()

		self.progressBar = QtGui.QProgressBar()
		messageLabel = QtGui.QLabel("Ready")

		layout = QtGui.QHBoxLayout()
		layout.addWidget(self.progressBar)
		layout.addWidget(messageLabel)

		def showMessage(message):
			messageLabel.setText(message)

		self.statusBar().showMessage = showMessage

		panel.setLayout(layout)
		layout.setContentsMargins(0, 0, 0, 0)

		return panel


	def createLeftPanel(self):
		panel = QtGui.QFrame()

		listView = QtGui.QListView()
		listView.setModel(self.fileModel)

		button = QtGui.QPushButton("파일 선택")
		QtCore.QObject.connect(button,
			QtCore.SIGNAL("clicked()"), self.fileSelect)

		QtCore.QObject.connect(listView,
			QtCore.SIGNAL("clicked(QModelIndex)"), lambda index : self.setClickedIndex(index))

		self.setValue("filenames", set())

		layout = QtGui.QVBoxLayout()
		layout.addWidget(listView)
		layout.addWidget(button)

		panel.setLayout(layout)

		return panel

	def setClickedIndex(self, index):
		self.clickedIndex = index

	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key_Delete:
			self.removeData()

	def removeData(self):
		if not hasattr(self, "clickedIndex"):
			return
		data = self.clickedIndex.data()
		self.values["filenames"].remove(self.realpath[data])
		self.updateFileList()

	def fileSelect(self):
		files = set(QtGui.QFileDialog().getOpenFileNames())
		files = files.union(self.values["filenames"])
		self.setValue("filenames", files)
		self.updateFileList()

	def updateFileList(self):
		pat = re.compile(r"\\([^\\]+)$")
		names = list(map(lambda s : re.search(pat, s).group(1), self.values["filenames"]))
		self.fileModel.setStringList(names)
		for name in self.values["filenames"]:
			self.realpath[re.search(pat, name).group(1)] = name

	def createRightPanel(self):
		panel = QtGui.QFrame()
		
		optionPanel = self.createOptionPanel()

		createImageButton = QtGui.QPushButton("생성하기")
		QtCore.QObject.connect(createImageButton,
			QtCore.SIGNAL("clicked()"), lambda : self.createImage())

		layout = QtGui.QVBoxLayout()
		layout.addWidget(optionPanel)
		layout.addWidget(createImageButton)

		panel.setLayout(layout)

		return panel

	def createOptionPanel(self):
		panel = QtGui.QFrame()

		cellWidthSpinBox = QtGui.QSpinBox()
		cellHeightSpinBox = QtGui.QSpinBox()
		paddingXSpinBox = QtGui.QSpinBox()
		paddingYSpinBox = QtGui.QSpinBox()
		columnSpinBox = QtGui.QSpinBox()
		upperCurveSpinBox = QtGui.QSpinBox()
		lowerCurveSpinBox = QtGui.QSpinBox()
		meshNumberSpinBox = QtGui.QSpinBox()
		interpolationComboBox = QtGui.QComboBox()

		con = QtCore.QObject.connect
		sig = QtCore.SIGNAL
		sv = self.setValue

		# This context should locate before setValue() code
		con(cellWidthSpinBox, sig("valueChanged(int)"), lambda val: sv("cellWidth", val))
		con(cellHeightSpinBox, sig("valueChanged(int)"), lambda val: sv("cellHeight", val))
		con(paddingXSpinBox, sig("valueChanged(int)"), lambda val: sv("paddingX", val))
		con(paddingYSpinBox, sig("valueChanged(int)"), lambda val: sv("paddingY", val))
		con(columnSpinBox, sig("valueChanged(int)"), lambda val: sv("column", val))
		con(upperCurveSpinBox, sig("valueChanged(int)"), lambda val: sv("upperCurve", val))
		con(lowerCurveSpinBox, sig("valueChanged(int)"), lambda val: sv("lowerCurve", val))
		con(meshNumberSpinBox, sig("valueChanged(int)"), lambda val: sv("meshNumber", val))
		con(interpolationComboBox, sig("currentIndexChanged(QString)"), lambda val: sv("interpolation", val))

		cellWidthSpinBox.setMaximum(9999)
		cellHeightSpinBox.setMaximum(9999)
		paddingXSpinBox.setMaximum(9999)
		paddingYSpinBox.setMaximum(9999)
		columnSpinBox.setMaximum(999)
		upperCurveSpinBox.setMaximum(999)
		lowerCurveSpinBox.setMaximum(999)
		meshNumberSpinBox.setMaximum(99)

		cellWidthSpinBox.setValue(705)
		cellHeightSpinBox.setValue(344)
		paddingXSpinBox.setValue(40)
		paddingYSpinBox.setValue(200)
		columnSpinBox.setValue(4)
		upperCurveSpinBox.setValue(16)
		lowerCurveSpinBox.setValue(12)
		meshNumberSpinBox.setValue(12)
		meshNumberSpinBox.setToolTip("숫자가 크면 이미지가 부드러워지지만 연산이 오래 걸립니다.")

		interpolationComboBox.addItem("NEAREST")
		interpolationComboBox.addItem("BILINEAR")
		interpolationComboBox.addItem("BICUBIC")
		interpolationComboBox.setCurrentIndex(0)

		layout = QtGui.QGridLayout()
		QLabel = QtGui.QLabel

		layout.addWidget(QLabel("넓이:"), 0 , 0)
		layout.addWidget(QLabel("가로 여백:"), 1 , 0)
		layout.addWidget(QLabel("윗쪽 곡률:"), 2 , 0)
		layout.addWidget(QLabel("열:"), 3 , 0)
		layout.addWidget(cellWidthSpinBox, 0 , 1)
		layout.addWidget(paddingXSpinBox, 1, 1)
		layout.addWidget(upperCurveSpinBox, 2, 1)
		layout.addWidget(columnSpinBox, 3, 1)

		layout.addWidget(QLabel("높이:"), 0 , 2)
		layout.addWidget(QLabel("세로 여백:"), 1 , 2)
		layout.addWidget(QLabel("아래 곡률:"), 2 , 2)
		layout.addWidget(QLabel("분할 면:"), 3 , 2)
		layout.addWidget(cellHeightSpinBox, 0, 3)
		layout.addWidget(paddingYSpinBox, 1, 3)
		layout.addWidget(lowerCurveSpinBox, 2, 3)
		layout.addWidget(meshNumberSpinBox, 3, 3)

		layout.addWidget(QLabel("필터:"), 4 , 0)
		layout.addWidget(interpolationComboBox, 4, 1, 1, 2)

		panel.setLayout(layout)

		# AvoidName 옵션을 추가할까 말까?
		self.setValue("avoidName", [])

		return panel

	def setValue(self, key, value):
		self.values[key] = value

	def createImage(self):
		values = self.values
		galleryWall = self.galleryWall
		galleryWall.setAvoidName(values["avoidName"])
		galleryWall.setCellWidth(values["cellWidth"])
		galleryWall.setCellHeight(values["cellHeight"])
		galleryWall.setPaddingX(values["paddingX"])
		galleryWall.setPaddingY(values["paddingY"])
		galleryWall.setPaddingY(values["paddingY"])
		galleryWall.setColumn(values["column"])
		galleryWall.setMeshNumber(values["meshNumber"])
		galleryWall.setInterpolation(values["interpolation"])
		galleryWall.setFilenames(values["filenames"])

		def upperFunc(x, width):
		    hw = width / 2
		    y = (x-hw)**2
		    y *= values["upperCurve"] / 192000
		    return (int)(y)

		def lowerFunc(x, width):
		    hw = width / 2
		    y = (x-hw)**2
		    y *= values["lowerCurve"] / 192000
		    return (int)(y)

		galleryWall.upperFunc = upperFunc
		galleryWall.lowerFunc = lowerFunc

		progressThread = Progress(self, self.progressBar, galleryWall)

		galleryWall.setProgress(0)
		progressThread.start()

		galleryWall.createImage()
		self.progressBar.setValue(100)

		progressThread.quit()

		galleryWall.showImage()

		name = QtGui.QFileDialog().getSaveFileName()

		if name == "":
			return

		if name.find(".jpg") == -1 or name.find(".png") == -1:
			name += ".jpg"

		galleryWall.saveImage(name)

class Progress(QtCore.QThread):
	def __init__(self, parent, progressBar, work):
		QtCore.QThread.__init__(self, parent)
		self.progressBar = progressBar
		self.work = work

	def run(self):
		while self.work.progress != 100:
			self.progressBar.setValue(self.work.progress)
			time.sleep(0.01)

def main():
	app = QtGui.QApplication(sys.argv)
	qt = MergeQt()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
