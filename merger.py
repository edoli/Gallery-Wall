from PIL import Image
import os
import imghdr

class GalleryWall:
    def __init__(self, init = True):
        if not init:
            return
        self.paddingX = 40
        self.paddingY = 200
        self.cellWidth = 705
        self.cellHeight = 344
        self.column = 4
        self.setMeshNumber(12)

        self.interpolation = "NEAREST"

        self.avoidName = ['merge_result', 'result', 'gallery']
        self.directory = ""
        self.mergedImage = None
        self.isMirror = False
        self.filenames = os.listdir()
        self.setProgress(0)

    def setPaddingX(self, paddingX):
        self.paddingX = paddingX

    def setPaddingY(self, paddingY):
        self.paddingY = paddingY

    def setWidth(self, width):
        self.cellWidth = width / self.column

    def setHidth(self, height):
        self.cellHeight = height / self.row

    def setCellWidth(self, cellWidth):
        self.cellWidth = cellWidth

    def setCellHeight(self, cellHeight):
        self.cellHeight = cellHeight

    def setColumn(self, column):
        self.column = column

    def setRow(self, row):
        self.row = row

    def setFilenames(self, filenames):
        self.filenames = filenames

    def setAvoidName(self, avoidName):
        self.avoidName = avoidName

    def setInterpolation(self, interpolation):
        self.interpolation = interpolation

    def setMeshNumber(self, nIter):
        self.nIter = nIter

    def setProgress(self, progress):
        self.progress = progress
        
    def createImage(self):
        self.setProgress(0)
        # 파일 이름 걸러내기
        self.filenames = list(filter(self.isValidFile, self.filenames))

        self.row = (int)((len(self.filenames) + self.column - 1) / (self.column))
        self.width = (int)(self.cellWidth * self.column + self.paddingX * 2)
        self.height = (int)(self.cellHeight * self.row + self.paddingY * 2)
        self.cw = (int)(self.width / self.nIter)

        self.mergeImages()

        interpolation = getattr(Image, self.interpolation)

        mesh = self.createMesh(self.upperFunc, self.lowerFunc)
        mirrorMesh = self.createMirrorMesh(self.upperFunc, self.lowerFunc)

        img = self.mergedImage
        result = img.transform(img.size, Image.MESH, mesh, interpolation)
        self.setProgress(61)

        blank = Image.new("RGBA", (self.width, self.height))
        reflect = img.copy()
        reflect = img.transpose(Image.FLIP_TOP_BOTTOM)
        self.setProgress(81)
        reflect = reflect.transform(img.size, Image.MESH, mirrorMesh, interpolation)
        self.setProgress(92)
        reflect = Image.blend(reflect, blank, 0.5)
        y = int(self.paddingY * 2.9)
        result.paste(reflect, (0, self.height - y, 
            self.width, self.height * 2 - y), reflect)

        self.setProgress(100)

        self.result = result

    def createMesh(self, func1, func2):
        trans = []
        cw = self.cw
        px = self.paddingX
        height = self.height
        for i in range(self.nIter):
            x1 = cw * i + px
            y1 = 0
            x2 = cw * (i+1) + px
            y2 = height
            cyl1 = func1(x1, self.width)   
            cyl2 = height - func2(x1, self.width)
            cyr1 = func1(x2, self.width)
            cyr2 = height - func2(x2, self.width)
            target = (x1, y1, x2, y2)
            source = (x1, cyl1, x1, cyl2, x2, cyr2, x2, cyr1)
            trans.append((target, source))
        return trans

    def createMirrorMesh(self, func1, func2):
        trans = []
        cw = self.cw
        px = self.paddingX
        height = self.height
        for i in range(self.nIter):
            x1 = cw * i + px
            y1 = 0
            x2 = cw * (i+1) + px
            y2 = height
            cyl1 = - func1(x1, self.width)   
            cyl2 = height - func2(x1, self.width) + func1(x1, self.width)  
            cyr1 = - func1(x2, self.width)
            cyr2 = height - func2(x2, self.width) + func1(x2, self.width)
            target = (x1, y1, x2, y2)
            source = (x1, cyl1, x1, cyl2, x2, cyr2, x2, cyr1)
            trans.append((target, source))
        return trans

    # 합쳐진 이미지 만들기
    def mergeImages(self):
        self.mergedImage = Image.new("RGBA", (self.width, self.height))
        img = self.mergedImage
        initProgress = 0
        self.setProgress(initProgress)
        length = len(self.filenames)
        for i, filename in enumerate(self.filenames):
            cn = (i % self.column)
            rn = (int)(i / self.column)

            src = Image.open(filename)
            rSrc = src.resize((self.cellWidth, self.cellHeight))

            # 특정 부분 Grayscale
            if self.grayscaleFunc(cn, rn):
                rSrc = rSrc.convert('L')

            x = (int)(self.cellWidth * cn + self.paddingX)
            y = (int)(self.cellHeight * rn + self.paddingY * 0.5)
            img.paste(rSrc, (x, y, x + self.cellWidth, y+ self.cellHeight))
            i += 1
            self.setProgress(initProgress + (i / length) * 50)
            del src, rSrc
        self.setProgress(50)

    def isValidFile(self, filename):
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return False
        for name in self.avoidName:
            if filename.find(name) != -1:
                return False
        if imghdr.what(filename) == None:
            return False
        return True

    # Default Functions
    def upperFunc(self, x, width):
        hw = width / 2
        y = (x-hw)**2
        y /= 12000
        return (int)(y)

    def lowerFunc(self, x, width):
        hw = width / 2
        y = (x-hw)**2
        y /= 16000
        return (int)(y)

    def grayscaleFunc(self, cn, rn):
        return False

    def showImage(self):
        self.result.show()

    def saveImage(self, name = "result.jpg"):
        self.result.save(name)


if __name__ == "__main__":
    gw = GalleryWall()
    gw.createImage()
    gw.saveImage()