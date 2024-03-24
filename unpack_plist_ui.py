# -*- coding: utf-8 -*-
import os
import sys
import mainui
from PIL import Image
from xml.etree import ElementTree

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *

class StartRun(QThread):
    finished = pyqtSignal()
    outputWritten = pyqtSignal(str)  # 添加这一行定义信号
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pathname = ''
        self.dir_name = ''
        self.file_name = ''

    def setPathName(self,pathname= ''):
        self.pathname = pathname

    def tree_to_dict(self,tree):
        d = {}
        for index, item in enumerate(tree):
            if item.tag == 'key':
                if tree[index + 1].tag == 'string':
                    d[item.text] = tree[index + 1].text
                elif tree[index + 1].tag == 'true':
                    d[item.text] = True
                elif tree[index + 1].tag == 'false':
                    d[item.text] = False
                elif tree[index + 1].tag == 'integer':
                    d[item.text] = int(tree[index + 1].text);
                elif tree[index + 1].tag == 'dict':
                    d[item.text] = self.tree_to_dict(tree[index + 1])
        return d


    def frames_from_data(self,filename, ext):
        data_filename = filename + ext
        if ext == '.plist':
            root = ElementTree.fromstring(open(data_filename, 'r').read())
            plist_dict = self.tree_to_dict(root[0])
            to_list = lambda x: x.replace('{', '').replace('}', '').split(',')
            frames = plist_dict['frames'].items()
            for k, v in frames:
                frame = v
                if(plist_dict["metadata"]["format"] == 3):
                    frame['frame'] = frame['textureRect']
                    frame['rotated'] = frame['textureRotated']
                    frame['sourceSize'] = frame['spriteSourceSize']
                    frame['offset'] = frame['spriteOffset']

                rectlist = to_list(frame['frame'])
                width = int(float(rectlist[3] if frame['rotated'] else rectlist[2]))
                height = int(float(rectlist[2] if frame['rotated'] else rectlist[3]))
                frame['box'] = (
                    int(float(rectlist[0])),
                    int(float(rectlist[1])),
                    int(float(rectlist[0])) + width,
                    int(float(rectlist[1])) + height
                )
                real_rectlist = to_list(frame['sourceSize'])
                real_width = int(float(real_rectlist[1] if frame['rotated'] else real_rectlist[0]))
                real_height = int(float(real_rectlist[0] if frame['rotated'] else real_rectlist[1]))
                real_sizelist = [real_width, real_height]
                frame['real_sizelist'] = real_sizelist
                offsetlist = to_list(frame['offset'])
                offset_x = int(float(offsetlist[1] if frame['rotated'] else offsetlist[0]))
                offset_y = int(float(offsetlist[0] if frame['rotated'] else offsetlist[1]))

                if frame['rotated']:
                    frame['result_box'] = (
                        int(float((real_sizelist[0] - width) / 2 + offset_x)),
                        int(float((real_sizelist[1] - height) / 2 + offset_y)),
                        int(float((real_sizelist[0] + width) / 2 + offset_x)),
                        int(float((real_sizelist[1] + height) / 2 + offset_y))
                    )
                else:
                    frame['result_box'] = (
                        int(float((real_sizelist[0] - width) / 2 + offset_x)),
                        int(float((real_sizelist[1] - height) / 2 - offset_y)),
                        int(float((real_sizelist[0] + width) / 2 + offset_x)),
                        int(float((real_sizelist[1] + height) / 2 - offset_y))
                    )
            return frames

        else:
            print("Warning:Wrong data format on parsing: '" + ext + "'!")
            self.outputWritten.emit("Warning:Wrong data format on parsing: '" + ext + "'!\n")
            exit(1)


    def gen_png_from_data(self,dir_name, filename, ext):
        self.outputWritten.emit("unpack start!\n")
        openfile = dir_name +"/" + filename
        big_image = Image.open(openfile + ".png")
        frames = self.frames_from_data(openfile, ext)
        for k, v in frames:
            frame = v
            box = frame['box']
            rect_on_big = big_image.crop(box)
            real_sizelist = frame['real_sizelist']
            result_image = Image.new('RGBA', real_sizelist, (0, 0, 0, 0))
            result_box = frame['result_box']
            result_image.paste(rect_on_big, result_box, mask=0)
            if frame['rotated']:
                result_image = result_image.transpose(Image.ROTATE_90)
            if not os.path.isdir(openfile):
                os.mkdir(openfile)
            outfile = (openfile + '/' + k).replace('gift_', '')
            if not outfile.endswith('.png'):
                outfile += '.png'
            print(outfile, "generated")
            self.outputWritten.emit(outfile+" generated\n")
            result_image.save(outfile)
        self.outputWritten.emit("unpack end!\n")

    def endWith(self,s,*endstring):
        array = map(s.endswith,endstring)
        if True in array:
            return True
        else:
            return False


    def get_sources_file(self,filename,ext):
        data_filename = self.dir_name +"/" + filename + ext
        png_filename = self.dir_name +"/" + filename + '.png'
        print("get_sources_file",png_filename)
        if os.path.exists(data_filename) and os.path.exists(png_filename):
            self.gen_png_from_data(self.dir_name, filename, ext)
        else:
            print("Warning:Make sure you have both " + data_filename + " and " + png_filename + " files in the same directory")
            self.outputWritten.emit("Warning:Make sure you have both " + data_filename + " and " + png_filename + " files in the same directory\n")

    def run(self):
        if self.pathname == '':
            self.outputWritten.emit("Warning:请选择文件！\n")
            return
        # filename = sys.argv[1]
        print("filename1:",self.pathname)
        self.dir_name, self.file_name = os.path.split(self.pathname)
        path_or_name = os.path.splitext(self.file_name)[0]
        ext = '.plist'
        self.get_sources_file(path_or_name,ext)

# def start_run(filename):
#     start_run_thread.setPathName(filename)
#     start_run_thread.start()
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = mainui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.start_run_thread = StartRun()
        self.ui.btn_input.clicked.connect(self.ui.choose_png_file)
        self.ui.btn_output.clicked.connect(self.start_run)
        self.start_run_thread.finished.connect(self.handle_finished)

        self.start_run_thread.outputWritten.connect(self.handle_output_written)

    def start_run(self):
        filename = self.ui.lineEdit.text()
        self.start_run_thread.setPathName(filename)
        self.start_run_thread.start()

    def handle_finished(self):
        print("Thread finished")

    def handle_output_written(self, message):
        print(message)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     MainWindow = QMainWindow()

#     ui = mainui.Ui_MainWindow()
#     ui.setupUi(MainWindow)
#     ui.btn_input.clicked.connect(ui.choose_png_file)
#     ui.btn_output.clicked.connect(lambda:start_run(ui.lineEdit.text()))
#     start_run_thread = StartRun()
#     MainWindow.show()
#     sys.exit(app.exec_())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())