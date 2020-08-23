# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from time import sleep
from requests import get
from urllib.request import urlretrieve, install_opener, build_opener, urlopen
import eyed3
from os import path, chdir, getcwd, listdir
from configparser import ConfigParser
from pathlib import Path
import pandas as pd


class mythread(QThread):
    val = pyqtSignal(int)
    msg = pyqtSignal(str)
    max = pyqtSignal(int)

    def __init__(self, parent=None):
        super(mythread, self).__init__(parent)
        self.pid = None

    def run(self):

        print(getcwd())
        # self.msg.emit(getcwd())
        try:
            pid = int(self.pid)  # 就算是数字，从textedit接收到的也是string
            r = get('http://music.163.com/api/playlist/detail?id=' + str(pid))
            if r.json()['code'] != 200:
                self.msg.emit("未找到歌单")
            else:
                meta = r.json()['result']
                print('更新来自【' + meta['creator']['nickname'] + '】的歌单--' + meta['name'])
                self.msg.emit('更新来自【' + meta['creator']['nickname'] + '】的歌单--' + meta['name'])
                # QtWidgets.QApplication.processEvents()
                ids = []
                titles = []
                artists = []
                albums = []
                album_pics = []

                for i in range(len(r.json()['result']['tracks'])):
                    ids.append(r.json()['result']['tracks'][i]['id'])
                    titles.append(r.json()['result']['tracks'][i]['name'])
                    artists.append(r.json()['result']['tracks'][i]['artists'][0]['name'])
                    albums.append(r.json()['result']['tracks'][i]['album']['name'])
                    album_pics.append(r.json()['result']['tracks'][i]['album']['blurPicUrl'])

                opener = build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                install_opener(opener)
                Path('./music').mkdir(parents=True, exist_ok=True)  # an robust way to add a new folder
                mp3_path = './music/'
                Path('./img').mkdir(parents=True, exist_ok=True)
                img_path = './img/'

                d = {'ids': ids, 'titles': titles, 'artists': artists, 'albums': albums, 'album_pics': album_pics}
                df = pd.DataFrame(data=d)

                old = [path.splitext(item)[0] for item in listdir(mp3_path)]
                new = list(set(titles) - set(old))
                print('本次更新曲目', *new, sep=',')
                self.msg.emit("本次更新曲目...")
                self.max.emit(len(new) - 1)
                for i in range(0, len(new)):
                    self.msg.emit(str(i + 1) + '. ' + new[i])
                    self.val.emit(i)
                    #     row=df.loc[df.titles == new[i]]
                    # reference cell value row.titles.values[0]
                    # better way
                    row = df.loc[df.titles == new[i]].to_dict(orient='records')[0]
                    song_url = 'http://music.163.com/song/media/outer/url?id=' + str(row['ids']) + '.mp3'
                    r = urlopen(song_url)
                    if r.geturl() == 'https://music.163.com/404':
                        print('歌曲【' + row['titles'] + "】无资源！")
                        self.msg.emit('歌曲【' + row['titles'] + "】无资源！")
                    else:
                        mp3_name = mp3_path + row['titles'].replace('/', '-') + '.mp3'
                        urlretrieve(song_url, mp3_name)

                        img_name = img_path + row['albums'].replace('/', '-') + '.jpg'
                        urlretrieve(row['album_pics'], img_name)

                        audiofile = eyed3.load(mp3_name)
                        audiofile.tag.artist = str(row['artists'])
                        audiofile.tag.album = str(row['albums'])
                        #         audiofile.tag.images.set(type_=3,img_data=None,mime_type='image/jpeg',img_url=album_pics[i])
                        # simple url reference won't work, you have to download it to your disk
                        # plus this method doesn't informed on the documentation, I found it on the stackoverflow
                        audiofile.tag.images.set(type_=3, img_data=None, mime_type='image/jpeg',
                                                 img_url=open(img_name, 'rb').read())
                        # id3 version is important, encoding is important
                        # the former granteened the id3 tag will be recognized by music players like Apple Music
                        # the latter made the saving process ending up no error like 'Latin1' error
                        audiofile.tag.save(version=eyed3.id3.ID3_V2_3, encoding='utf-8')
                        sleep(0.5)
                print("更新完成！")
                self.msg.emit("更新完成")
        except ValueError:
            # assert isinstance(pid, int), "id格式为纯数字"
            self.msg.emit('⚠️id格式应为纯数字')
            # print('aaaa')


class Ui_MainWindow(object):
    def __init__(self):
        self.folder = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(306, 298)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.pid = QtWidgets.QLineEdit(self.centralwidget)
        self.pid.setObjectName("pid")
        self.verticalLayout.addWidget(self.pid)
        self.pid.setText('5022293116')

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.submit = QtWidgets.QPushButton(self.centralwidget)
        self.submit.setObjectName("submit")
        self.horizontalLayout_2.addWidget(self.submit)
        self.folder_btn = QtWidgets.QToolButton(self.centralwidget)
        self.folder_btn.setObjectName("toolButton")
        self.horizontalLayout_2.addWidget(self.folder_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.info = QtWidgets.QTextBrowser(self.centralwidget)
        self.info.setObjectName("info")
        self.verticalLayout.addWidget(self.info)
        self.pbar = QtWidgets.QProgressBar(self.centralwidget)
        self.pbar.setProperty("value", 0)
        self.pbar.setObjectName("pbar")
        self.verticalLayout.addWidget(self.pbar)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "网易云歌单下载"))
        self.submit.setText(_translate("MainWindow", "submit"))
        self.folder_btn.setText(_translate("MainWindow", "..."))

        self.submit.clicked.connect(self.start_pbar)  #### no mycode()
        self.folder_btn.clicked.connect(self.select_folder)
        # for .app file
        # self.current_path=Path(QtCore.QCoreApplication.applicationDirPath()).parents[1]

        # for unix file
        self.current_path = path.expanduser("~")
        # print(self.current_path)
        self.cp = ConfigParser()

        self.config_dir = self.current_path + '/.batch'
        # print(self.config_dir)
        self.config_file = self.config_dir + '/settings.ini'
        # print(self.config_file)

        if not path.isfile(self.config_file):
            Path('./.batch').mkdir(parents=True, exist_ok=True)
            Path(self.config_file).touch(exist_ok=True)
            self.cp.add_section('Default')
            self.cp.add_section('User')
            self.cp['Default']['folder'] = self.current_path
            self.cp['User']['folder'] = ''
            with open(self.config_file, 'w') as f:
                self.cp.write(f)
        # load ini file
        self.cp.read(self.config_file)
        # if user had set cwd, use that cwd
        if self.cp['User']['folder'] != '':
            self.current_path = self.cp['User']['folder']
        input("Press enter to close program")
        # #####################
        # if getattr(sys,'frozen',False):
        #     # self.statusbar.showMessage(sys.executable)
        #     # chdir(path.dirname(sys.executable))
        #     # self.statusbar.showMessage(sys.argv[0])
        #     # self.current_path=sys.executable
        #     self.current_path=sys.argv[0]
        #     # chdir(path.dirname(sys.argv[0]))
        # else:
        #     self.current_path = path.abspath(path.dirname(__file__))
        #     #####################

        chdir(self.current_path)
        self.statusbar.showMessage('当前目录:' + getcwd())

        # self.statusbar.showMessage('当前目录:'+getcwd())
        # os getcwd未必一直正确
        # os path，你需要判断是script还是application bundle

    def start_pbar(self):
        self.thread = mythread()
        self.pbar.setValue(0)
        self.thread.pid = self.pid.text()
        # self.thread.folder = self.folder
        self.thread.val.connect(self.set_pbar)
        self.thread.msg.connect(self.set_msg)
        self.thread.max.connect(self.set_pbar_max)
        self.thread.start()
        # msg=QtWidgets.QMessageBox()
        # msg.setText("abc")

    def set_pbar(self, val):
        self.pbar.setValue(val)

    def set_pbar_max(self, max):
        self.pbar.setMaximum(max)

    def set_msg(self, msg):
        self.info.append(msg)

    def select_folder(self):
        self.folder = QFileDialog.getExistingDirectory()
        chdir(QFileDialog.getExistingDirectory())
        # ini file is load before, so you can just edit it
        self.cp['User']['folder'] = self.folder
        with open(self.config_file, 'w') as f:
            self.cp.write(f)
        self.statusbar.showMessage('当前目录:' + str(self.folder))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
