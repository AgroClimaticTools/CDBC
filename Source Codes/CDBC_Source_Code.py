from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys,os,time
from scipy.stats import gamma, norm, beta
import matplotlib.pyplot as plt
from datetime import date, timedelta
import numpy as np
import tkinter
from os import listdir
from os.path import isfile, join

def sorted_values(Obs,Sim):
    count = 0
    for i in range(len(Obs)):
        if Obs[i] == 0:
            count += 1
    Rank = [i+1 for i in range(len(Obs))]
    Dict = dict(zip(Rank,Sim))
    SortedSim = sorted(Dict.values())
    SortedRank = sorted(Dict, key=Dict.get)
    for i in range(count):
        SortedSim[i] = 0
    ArrangedDict = dict(zip(SortedRank,SortedSim))
    SortedDict_by_Rank = sorted(ArrangedDict.items())
    ArrangedSim = [v for k,v in SortedDict_by_Rank]
    return ArrangedSim

def sorted_values_thresh(Sim, Fut):
    try:
        Min_Positive_Value_Sim = min(i for i in sim if i > 0)
    except:
        Min_Positive_Value_Sim = 0
    for i in range(len(Fut)):
        if Fut[i] < Min_Positive_Value_Sim:
            Fut[i] = 0
    return Fut

class TitleBar(QDialog):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        StyleTitleBar='''QDialog{
background-color: rgb(2,36,88);
}
QLabel{
color: rgb(0, 255, 255);
font: 11pt "MS Shell Dlg 2";
}'''
        self.setStyleSheet(StyleTitleBar)
        self.setAutoFillBackground(True)
        self.setFixedSize(750,30)
        Style_minimize='''QToolButton{
background-color: transparent;
color: rgb(255, 255, 255);
border: none;
}
QToolButton:hover{
background-color: rgb(66, 131, 221,230);
border: none;
}'''
        Style_close='''QToolButton{
background-color: rgb(217, 0, 0);
color: rgb(255, 255, 255);
border: none;
}
QToolButton:hover{
background-color: rgb(255, 0, 0);
border: none;
}'''
        Font=QFont('MS Shell Dlg 2',11)
        Font.setBold(True)
        
        self.minimize = QToolButton(self)
        self.minimize.setText('–')
        self.minimize.setFixedHeight(20)
        self.minimize.setFixedWidth(25)
        self.minimize.setStyleSheet(Style_minimize)
        self.minimize.setFont(Font)
        
        self.close = QToolButton(self)
        self.close.setText(u"\u00D7")
        self.close.setFixedHeight(20)
        self.close.setFixedWidth(45)
        self.close.setStyleSheet(Style_close)
        self.close.setFont(Font)

        image = QPixmap(r"Interpolation-2.png")
        labelImg =QLabel(self)
        labelImg.setFixedSize(QSize(20,20))
        labelImg.setScaledContents(True)
        labelImg.setPixmap(image)
        labelImg.setStyleSheet('border: none;')
        label = QLabel(self)
        label.setText("  Climate Data Bias Corrector (RAIN, TEMP, SRAD)")
        label.setFont(Font)
        label.setStyleSheet('border: none;')
        hbox=QHBoxLayout(self)
        hbox.addWidget(labelImg)
        hbox.addWidget(label)
        hbox.addWidget(self.minimize)
        hbox.addWidget(self.close)
        hbox.insertStretch(2,600)
        hbox.setSpacing(1)
        hbox.setContentsMargins(5,0,5,0)
        
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.maxNormal=False
        self.close.clicked.connect(self.closeApp)
        self.minimize.clicked.connect(self.showSmall)

    def showSmall(self):
        widget.showMinimized();

    def closeApp(self):
        widget.close()

    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton:
            widget.moving = True
            widget.offset = event.pos()

    def mouseMoveEvent(self,event):
        if widget.moving:
            widget.move(event.globalPos()-widget.offset)

class HFTab(QTabWidget):
    def __init__(self, parent = None):
        super(HFTab, self).__init__(parent)
        self.HTab = QWidget()
        self.FTab = QWidget()
		
        self.setStyleSheet('QTabBar { font: bold }')
        self.addTab(self.HTab,"For Historical Data")
        self.addTab(self.FTab,"For Future Data")
        self.HTabUI()
        self.FTabUI()
        self.started = False

    def HTabUI(self):
        grid = QGridLayout()
        grid.addWidget(self.input(), 0, 0)
        grid.addWidget(self.output(), 1, 0)
        grid.addWidget(self.method(), 2, 0)
        grid.addWidget(self.progress(), 3, 0)
        grid.setContentsMargins(0,0,0,0)
        
##        self.setTabText(0,"Historical")
        self.HTab.setLayout(grid)

    def input(self):

        ##########Layout for taking input climate data to be bias corrected ##########

        gBox = QGroupBox("Inputs:")
        layout1 = QGridLayout()
        
        self.Obsfile = QLineEdit()
        self.browse2 = QPushButton("...")
        self.browse2.setMaximumWidth(25)
        self.browse2.clicked.connect(self.browse2_file)
        self.q1 = QPushButton("?")
        self.q1.setMaximumWidth(15)
        self.q1.clicked.connect(self.Info1)
        self.Obsfile.setPlaceholderText("File with observed climate data (*.csv or *.txt)")

        layout1.addWidget(self.Obsfile,1,0,1,3)
        layout1.addWidget(self.q1,1,3,1,1)
        layout1.addWidget(self.browse2,1,4,1,1)


        self.ModHfile = QLineEdit()
        self.ModHfile.setPlaceholderText("File with GCM outputs (*.csv or *.txt)")
        self.q2 = QPushButton("?")
        self.q2.setMaximumWidth(15)
        self.q2.clicked.connect(self.Info2)
        self.browse3 = QPushButton("...")
        self.browse3.setMaximumWidth(25)
        self.browse3.clicked.connect(self.browse3_file)
        layout1.addWidget(self.ModHfile,2,0,1,3)
        layout1.addWidget(self.q2,2,3,1,1)
        layout1.addWidget(self.browse3,2,4,1,1)

##        ##########Layout for taking comma delimited vs tab delimited################################

##        sublayout1 = QGridLayout()
##
##        self.label1 = QLabel("Input Format:\t")
##        self.b1 = QRadioButton("Comma Delimated (*.csv)")
##        #self.b1.setChecked(True)
##        self.b2 = QRadioButton("Tab Delimited (*.txt)")
##
##        self.b1.toggled.connect(lambda:self.btnstate(self.b1))
##        self.b2.toggled.connect(lambda:self.btnstate(self.b2))
##
##        sublayout1.addWidget(self.label1,1,0)
##        sublayout1.addWidget(self.b1,1,1)
##        sublayout1.addWidget(self.b2,1,2)
##        layout1.addLayout(sublayout1,3,0)
        
        gBox.setLayout(layout1)
        return gBox

    def output(self):

        ##########Layout for output file location and interpolation##########

        gBox = QGroupBox("Outputs:")
        layout4 = QGridLayout()
        
        self.outputfile_location = QLineEdit()
        self.outputfile_location.setPlaceholderText("Folder to save bias corrected GCM outputs")
        self.browse4 = QPushButton("...")
        self.browse4.setMaximumWidth(25)
        self.browse4.clicked.connect(self.browse4_file)
        layout4.addWidget(self.outputfile_location,1,0,1,3)
        layout4.addWidget(self.browse4,1,3,1,1)

        ########################Layout for taking comma delimited vs tab delimited################################

        sublayout2 = QGridLayout()
        output_label = QLabel("Output Format:\t")
        self.b3 = QRadioButton("Comma Delimated (*.csv)")
        #self.b3.setChecked(True)
        self.b4 = QRadioButton("Tab Delimited (*.txt)")

        self.b3.toggled.connect(lambda:self.btn2state(self.b3))
        self.b4.toggled.connect(lambda:self.btn2state(self.b4))
        
        sublayout2.addWidget(output_label,1,0)
        sublayout2.addWidget(self.b3,1,1)
        sublayout2.addWidget(self.b4,1,2)
        layout4.addLayout(sublayout2,2,0)
        gBox.setLayout(layout4)
        return gBox

    def method(self):

        ########################Layout for taking methods of Bias Correction ################################
        gBox = QGroupBox("Variable/Distribution")
        layout5 = QGridLayout()
        self.b5 = QRadioButton("Rainfall/Gamma")
        #self.b3.setChecked(True)
        self.b6 = QRadioButton("Temperature/Normal")
        self.b7 = QRadioButton("Solar Radiation/Beta")

        self.b5.toggled.connect(lambda:self.btn3state(self.b5))
        self.b6.toggled.connect(lambda:self.btn3state(self.b6))
        self.b7.toggled.connect(lambda:self.btn3state(self.b7))
        
        self.show_hide = QPushButton("Show Details")
        Font=QFont()
        Font.setBold(True)
        #self.show_hide.setFont(Font)
        self.show_hide.setCheckable(True)
        #self.show_hide.toggle()
        self.show_hide.clicked.connect(self.ShowHide)
        self.show_hide.setFixedWidth(90)
        self.show_hide.setFixedHeight(25)
        Style_show_hide_Button = """
QPushButton{
color: rgb(255, 255, 255);
background-color: rgb(66, 131, 221);
border: none;
}
QPushButton:Checked{
background-color: rgb(66, 131, 221);
border: none;
}
QPushButton:hover{
background-color: rgb(66, 131, 221,230);
border: none;
}
"""
        self.show_hide.setStyleSheet(Style_show_hide_Button)

        self.show_plots = QPushButton("Show Plots")
        self.show_plots.clicked.connect(self.ShowPlots)
        self.show_plots.setFixedWidth(75)
        self.show_plots.setFixedHeight(25)
        self.show_plots.setStyleSheet(Style_show_hide_Button)
        
        self.start = QPushButton("Run")
        self.start.setFixedWidth(50)
        self.start.setFixedHeight(25)
        Style_Run_Button = """
QPushButton{
color: rgb(255, 255, 255);
background-color: rgb(0,121,0);
border-color: none;
border: none;
}
QPushButton:hover{
background-color: rgb(0,121,0,230);
}
"""
        self.start.clicked.connect(self.start_correctionH)
        #self.start.setFont(Font)
        self.start.setStyleSheet(Style_Run_Button)
        
        self.stop = QPushButton("Cancel")
        self.stop.setMaximumWidth(60)
        self.stop.setFixedHeight(25)
        Style_Cancel_Button = """
QPushButton{
color: rgb(255, 255, 255);
background-color: rgb(180,0,0,240);
border-color: none;
border: none;
}
QPushButton:hover{
background-color: rgb(180,0,0,220);
}
"""
        self.stop.clicked.connect(self.stop_correctionH)
        #self.stop.setFont(Font)
        self.stop.setStyleSheet(Style_Cancel_Button)
        
        layout5.addWidget(self.b5,1,1)
        layout5.addWidget(self.b6,1,2)
        layout5.addWidget(self.b7,1,3)
        layout5.addWidget(self.show_hide,1,7)
        layout5.addWidget(self.start,1,4)
        layout5.addWidget(self.stop,1,6)
        layout5.addWidget(self.show_plots,1,5)
##        layout5.addWidget(self.b5,1,1)
##        layout5.addWidget(self.b6,1,2)
##        layout5.addWidget(self.b7,1,3)
##        layout5.addWidget(self.show_hide,2,5)
##        layout5.addWidget(self.start,1,4)
##        layout5.addWidget(self.stop,2,4)
##        layout5.addWidget(self.show_plots,1,5)
        
        gBox.setLayout(layout5)
        return gBox

        ########## Layout for progress of Bias Correction ##########
    def progress(self):
        gBox = QGroupBox()
        layout6 = QVBoxLayout() 
        
        STYLE2 = """
QProgressBar{
text-align: center;
}
QProgressBar::chunk {
background-color: rgb(0,121,0);
}
"""
        self.status = QLabel('')
        self.progressbar = QProgressBar()
##        self.progressbarfinal = QProgressBar()
##        self.progressbar.setMinimum(1)
        self.progressbar.setFixedHeight(13)
##        self.progressbarfinal.setFixedHeight(13)
        self.progressbar.setStyleSheet(STYLE2)
##        self.progressbarfinal.setStyleSheet(STYLE2)
        self.textbox = QTextEdit()
        self.textbox.setReadOnly(True)
        self.textbox.moveCursor(QTextCursor.End)
        self.textbox.hide()
        self.scrollbar = self.textbox.verticalScrollBar()

        layout6.addWidget(self.status)
        layout6.addWidget(self.progressbar)
##        layout6.addWidget(self.progressbarfinal)
        layout6.addWidget(self.textbox)
        gBox.setLayout(layout6)
        return gBox 


      
    ########################### Control Buttons ####################################################
    def browse2_file(self):
        Obs_file = QFileDialog.getOpenFileName(self,caption = "Open File",directory=r"C:\Users\gupta\OneDrive\0. M.Tech. Research Work\Codes\GUIs\Bias Correction\\",
                                                   filter="Comma Delimated (*.csv);;Tab Delimated (*.txt)")
        self.Obsfile.setText(QDir.toNativeSeparators(Obs_file))
        
    def browse3_file(self):
        ModH_file = QFileDialog.getOpenFileName(self,caption = "Open File", directory=r"C:\Users\gupta\OneDrive\0. M.Tech. Research Work\Codes\GUIs\Bias Correction\\",
                                                filter="Comma Delimated (*.csv);;Tab Delimated (*.txt)")
        self.ModHfile.setText(QDir.toNativeSeparators(ModH_file))
        
    def browse4_file(self):
        output_file = QFileDialog.getExistingDirectory(self, "Save File in Folder", r"C:\Users\gupta\OneDrive\0. M.Tech. Research Work\Codes\GUIs\Bias Correction\\",
                                                       QFileDialog.ShowDirsOnly)
        self.outputfile_location.setText(QDir.toNativeSeparators(output_file))  

    def Info1(self):
        QMessageBox.information(self, "Information About Input Files (Observed)",
                                '''Sample input (.csv or .txt) should be same as it is shown in Sample Example:\nC:\Program Files (x86)\Climate Data Bias Corrector\Sample Input (Obs).csv
                                ''')
    def Info2(self):
        QMessageBox.information(self, "Information About Input File (Model)",
                                '''Sample input (.csv or .txt) should be same as it is shown in Sample Example:\nC:\Program Files (x86)\Climate Data Bias Corrector\Sample Input (Mod).csv
                                ''')

##    def btnstate(self,b):
##        if b.text() == "Comma Delimated (*.csv)" and b.isChecked() == True:
##            self.seperator = ','
##            self.seperatorname = '.csv'
##        if b.text() == "Tab Delimited (*.txt)" and b.isChecked() == True:
##            self.seperator = '\t'
##            self.seperatorname = '.txt'

    def btn2state(self,b):
        if b.text() == "Comma Delimated (*.csv)" and b.isChecked() == True:
            self.seperator2 = ','
            self.seperatorname2 = '.csv'
        if b.text() == "Tab Delimited (*.txt)" and b.isChecked() == True:
            self.seperator2 = '\t'
            self.seperatorname2 = '.txt'

    def btn3state(self,b):
        if b.text() == "Rainfall/Gamma" and b.isChecked() == True:
            self.methodname = b.text()
        if b.text() == "Temperature/Normal" and b.isChecked() == True:
            self.methodname = b.text()
        if b.text() == "Solar Radiation/Beta" and b.isChecked() == True:
            self.methodname = b.text()
            
    def start_correctionH(self):
        self.started = True
        self.BiasCorrectH()

    def stop_correctionH(self):
        if self.started:
            self.started = False
            QMessageBox.information(self, "Information", "Bias correction is aborted.")

    def ShowHide(self):
        if self.show_hide.text() == "Hide Details" and self.show_hide.isChecked() == False:
            self.textboxF.hide()
            self.textbox.hide()
##            self.setFixedSize(700,372)
            ShowHide(self.show_hideF.text())
            ShowHide(self.show_hide.text())
            self.show_hideF.setText('Show Details')
            self.show_hide.setText('Show Details')
        if self.show_hide.text() == "Show Details" and self.show_hide.isChecked() == True:
            self.textboxF.show()
            self.textbox.show()
##            self.setFixedSize(700,620)
            ShowHide(self.show_hideF.text())
            ShowHide(self.show_hide.text())
            self.show_hideF.setText('Hide Details')
            self.show_hide.setText('Hide Details')
        
    def BiasCorrectH(self):
        if self.Obsfile.text() == "":
            QMessageBox.critical(self, "Message", "File containing observed climate data (*.csv or *.txt) is not given.")
            self.started = False
        if self.ModHfile.text() == "":
            QMessageBox.critical(self, "Message", "File containing GCM outputs (*.csv or *.txt) is not given.")
            self.started = False
        if self.outputfile_location.text() == "":
            QMessageBox.critical(self, "Message", "Folder to save bias corrected GCM outputs is not given")
            self.started = False

        try:
##            sep = self.seperator
##            sepname = self.seperatorname

            sep2 = self.seperator2
            sepname2 = self.seperatorname2
        except:
            QMessageBox.critical(self, "Message", "Format is not defined.")
            self.started = False
        try:
            method = self.methodname
        except:
            QMessageBox.critical(self, "Message", "Variable/Distribution is not defined.")
            self.started = False
        
        self.textbox.setText("")
        
        start = time.time()
        self.status.setText('Status: Correcting')
##        self.progressbarfinal.setMinimum(0)
##        self.progressbarfinal.setValue(0)
        self.progressbar.setMinimum(0)
        self.progressbar.setValue(0)

        Fobs = self.Obsfile.text()
        Fmod = self.ModHfile.text()

        ObsData, ModData, CorrectedData = [], [], []
        
        with open(Fobs) as f:
            line = [line for line in f]
            for i in range(len(line)):
                if Fobs.endswith('.csv'):
                    ObsData.append([word for word in line[i].split(",") if word])
                if Fobs.endswith('.txt'):
                    ObsData.append([word for word in line[i].split("\t") if word])
        lat = [float(ObsData[0][c]) for c in range(1,len(ObsData[0]))]
        lon = [float(ObsData[1][c]) for c in range(1,len(ObsData[0]))]
        Latitude = []
        Longitude = []
        
        with open(Fmod) as f:
            line = [line for line in f]
            for i in range(len(line)):
                if Fmod.endswith('.csv'):
                    ModData.append([word for word in line[i].split(",") if word])
                if Fmod.endswith('.txt'):
                    ModData.append([word for word in line[i].split("\t") if word])

        DateObs = [ObsData[r][0] for r in range(len(ObsData))]
        DateMod = [ModData[r][0] for r in range(len(ModData))]

        OutPath = self.outputfile_location.text()
        CorrectedData.append(DateMod)
        YMod = int(DateMod[2][-4:])
        YObs = int(DateObs[2][-4:])
        app.processEvents()
        if len(lat)>1:
            random_count = np.random.randint(len(lat),size=(1))
        else:
            random_count = 0
        fig = plt.figure(figsize=(15,7))
        plt.style.use('ggplot')
##        plt.style.use('fivethirtyeight')
        for j in range(len(lat)):
            obs = [float(ObsData[r][j+1]) for r in range(2,len(ObsData))]
            MOD = [float(ModData[r][j+1]) for r in range(2,len(ModData))]

            Date = [date(YMod,1,1)+timedelta(i) for i in range(len(MOD))]
            DateObs = [date(YObs,1,1)+timedelta(i) for i in range(len(obs))]

            if method == 'Rainfall/Gamma' and self.started == True:
                MOD_Month=[]
                Obs_Monthwise = [[] for m in range(12)]
                Obs_MonthFreq = [[] for m in range(12)]
                MOD_Monthwise = [[] for m in range(12)]
                MOD_MonthFreq = [[] for m in range(12)]
                Cor_Monthwise = []
                Date_Monthwise= [[] for m in range(12)]
                for m in range(12):
                    for i in range(len(obs)):
                        if Date[i].month == m+1:
                            Date_Monthwise[m].append(Date[i])
                            Obs_Monthwise[m].append(obs[i])
                            MOD_Monthwise[m].append(MOD[i])
                for m in range(12):
                    MOD_Month.append(sorted_values(Obs_Monthwise[m],MOD_Monthwise[m]))

                MOD_Monthwise = MOD_Month
                for m in range(12):
                    for i in range(len(MOD_Monthwise[m])):
                        if MOD_Monthwise[m][i]>0:
                            MOD_MonthFreq[m].append(MOD_Monthwise[m][i])
                        if Obs_Monthwise[m][i]>0:
                            Obs_MonthFreq[m].append(Obs_Monthwise[m][i])

                nplot=1
                for m in range(12):
                    Cor = []
                    if len(MOD_MonthFreq[m])>0 and len(Obs_MonthFreq[m])>0:
                        Mo, Mg, Vo, Vg = np.mean(Obs_MonthFreq[m]), np.mean(MOD_MonthFreq[m]), np.std(Obs_MonthFreq[m])**2, np.std(MOD_MonthFreq[m])**2
                        if not any(param<0.000001 for param in [Mo, Mg, Vo, Vg]):
                            O_alpha, O_beta, G_alpha, G_beta = Mo**2/Vo, Vo/Mo, Mg**2/Vg, Vg/Mg
                            O_loc, G_loc = 0, 0
    ##                        print('G',O_alpha, O_beta, G_alpha, G_beta)
                        else:
                            O_alpha, O_loc, O_beta = gamma.fit(Obs_MonthFreq[m], loc=0)
                            G_alpha, G_loc, G_beta = gamma.fit(MOD_MonthFreq[m], loc=0)
    ##                        print('fit',O_alpha, O_beta, G_alpha, G_beta)
    ##                    print(O_alpha, O_beta, G_alpha, G_beta)
                        prob = gamma.cdf(MOD_Monthwise[m],G_alpha, scale=G_beta)
                        Corr = gamma.ppf(prob, O_alpha, scale=O_beta)
                    for i in range(len(Obs_Monthwise[m])):
                        if len(MOD_MonthFreq[m])>0:
                            if MOD_Monthwise[m][i] >= min(MOD_MonthFreq[m]):
                                Cor.append(Corr[i])
                            else:
                                Cor.append(0)
                        else:
                            
                            Cor.append(0)
                    for c in Cor:
                        Cor_Monthwise.append('%.1f'%c)
                    
                    if j == random_count:
                        ax = fig.add_subplot(3,4,nplot)
                        obs_cdf = gamma.cdf(Obs_Monthwise[m], O_alpha, O_loc, O_beta)
                        mod_cdf = gamma.cdf(MOD_Monthwise[m], G_alpha, G_loc, G_beta)
                        Mc, Vc = np.mean(Cor), np.std(Cor)**2
                        if not any(param<0.000001 for param in [Mc, Vc]):
                            CF_alpha, CF_beta = Mc**2/Vc, Vc/Mc
                            CF_loc, G_loc = 0, 0
                        else:
                            CF_alpha, CF_loc, CF_beta=gamma.fit(Cor)
                        cor_cdf = gamma.cdf(Cor, CF_alpha, CF_loc, CF_beta)
                        ax.set_title('Month: '+str(m+1), fontsize=12)
                        o, = ax.plot(Obs_Monthwise[m], obs_cdf, '.b')
                        m, = ax.plot(MOD_Monthwise[m], mod_cdf, '.r')
                        c, = ax.plot(Cor, cor_cdf, '.g')
                        nplot=nplot+1
                        fig.legend([o,m,c,(o,m,c,)],['Observed','Before Correction','After Correction'],ncol=3,loc=8,frameon=False, fontsize=14)
                        plt.subplots_adjust(hspace=0.3, wspace=0.3)
                        plt.suptitle('CDF Plots of ' + method.split('/')[0] + ' for Randomly Selected Lat: '+str(lat[j])+' Lon: '+str(lon[j]),fontsize=16)
                        
                
            if method =='Temperature/Normal' and self.started == True:
                MOD_Month=[]
                Obs_Monthwise = [[] for m in range(12)]
                MOD_Monthwise = [[] for m in range(12)]
                Cor_Monthwise = []
                Date_Monthwise= [[] for m in range(12)]
                for m in range(12):
                    for i in range(len(MOD)):
                        if Date[i].month == m+1:
                            Date_Monthwise[m].append(Date[i])
                            MOD_Monthwise[m].append(MOD[i])
                
                for m in range(12):
                    for i in range(len(obs)):
                        if DateObs[i].month == m+1:
                            Obs_Monthwise[m].append(obs[i])
                nplot=1
                for m in range(12):
                    Cor = []
                    Mo, So = norm.fit(Obs_Monthwise[m])
                    Mg, Sg = norm.fit(MOD_Monthwise[m])
                    prob = norm.cdf(MOD_Monthwise[m],Mg, Sg)
                    Cor = norm.ppf(prob, Mo, So)
                    for c in Cor:
                        Cor_Monthwise.append('%.1f'%c)

                    if j == random_count:
                        ax = fig.add_subplot(3,4,nplot)
                        obs_cdf = norm.cdf(Obs_Monthwise[m], Mo, So)
                        mod_cdf = norm.cdf(MOD_Monthwise[m], Mg, Sg)
                        Mc, Sc = norm.fit(Cor)
                        cor_cdf = norm.cdf(Cor, Mc, Sc)
                        ax.set_title('Month: '+str(m+1), fontsize=12)
                        o, = ax.plot(Obs_Monthwise[m], obs_cdf, '.b')
                        m, = ax.plot(MOD_Monthwise[m], mod_cdf, '.r')
                        c, = ax.plot(Cor, cor_cdf, '.g')
                        nplot=nplot+1
                        fig.legend([o,m,c,(o,m,c,)],['Observed','Before Correction','After Correction'],ncol=3,loc=8,frameon=False, fontsize=14)
                        plt.subplots_adjust(hspace=0.3, wspace=0.3)
                        plt.suptitle('CDF Plots of ' + method.split('/')[0] + ' for Randomly Selected Lat: '+str(lat[j])+' Lon: '+str(lon[j]),fontsize=16)
                        
            if method =='Solar Radiation/Beta' and self.started == True:
                MOD_Month=[]
                Obs_Monthwise = [[] for m in range(12)]
                MOD_Monthwise = [[] for m in range(12)]
                Cor_Monthwise = []
                Date_Monthwise= [[] for m in range(12)]
                for m in range(12):
                    for i in range(len(MOD)):
                        if Date[i].month == m+1:
                            Date_Monthwise[m].append(Date[i])
                            MOD_Monthwise[m].append(MOD[i])
                
                for m in range(12):
                    for i in range(len(obs)):
                        if DateObs[i].month == m+1:
                            Obs_Monthwise[m].append(obs[i])
                nplot=1
                for m in range(12):
                    Cor = []
                    oMin, oMax = min(Obs_Monthwise[m]), max(Obs_Monthwise[m])
                    gMin, gMax = min(MOD_Monthwise[m]), max(MOD_Monthwise[m])
                    Mo = (np.mean(Obs_Monthwise[m])-oMin)/(oMax - oMin)
                    Mg = (np.mean(MOD_Monthwise[m])-gMin)/(gMax - gMin)
                    Vo = np.std(Obs_Monthwise[m])**2/(oMax - oMin)**2
                    Vg = np.std(MOD_Monthwise[m])**2/(gMax - gMin)**2
                    ao, ag = -Mo*(Vo + Mo**2 - Mo)/Vo, -Mg*(Vg + Mg**2 - Mg)/Vg
                    bo, bg = ao*(1 - Mo)/Mo, ag*(1 - Mg)/Mg
                    TransO = [(Obs_Monthwise[m][i]-oMin)/(oMax-oMin) for i in range(len(Obs_Monthwise[m]))]
                    TransG = [(MOD_Monthwise[m][i]-gMin)/(gMax-gMin) for i in range(len(MOD_Monthwise[m]))]
                    prob = beta.cdf(TransG, ag, bg)
                    TransC = beta.ppf(prob, ao, bo)
                    Cor = [TransC[i]*(oMax-oMin)+oMin for i in range(len(TransC))]
                    for c in Cor:
                        Cor_Monthwise.append('%.1f'%c)
                    if j == random_count:
                        ax = fig.add_subplot(3,4,nplot)
                        obs_cdf = beta.cdf(TransO, ao, bo)
                        mod_cdf = beta.cdf(TransG, ag, bg)
                        Mc = (np.mean(Cor)-min(Cor))/(max(Cor)-min(Cor))
                        Vc = np.std(Cor)**2/(max(Cor)-min(Cor))**2
                        ac = -Mc*(Vc + Mc**2 - Mc)/Vc
                        bc = ac*(1 - Mc)/Mc
                        cor_cdf = beta.cdf(TransC, ac, bc)
                        ax.set_title('Month: '+str(m+1), fontsize=12)
                        o, = ax.plot(Obs_Monthwise[m], obs_cdf, '.b')
                        m, = ax.plot(MOD_Monthwise[m], mod_cdf, '.r')
                        c, = ax.plot(Cor, cor_cdf, '.g')
                        nplot=nplot+1
                        fig.legend([o,m,c,(o,m,c,)],['Observed','Before Correction','After Correction'],ncol=3,loc=8,frameon=False, fontsize=14)
                        plt.subplots_adjust(hspace=0.3, wspace=0.3)
                        plt.suptitle('CDF Plots of ' + method.split('/')[0] + ' for Randomly Selected Lat: '+str(lat[j])+' Lon: '+str(lon[j]),fontsize=16)

            Date_Month=[]
            for m in range(12):
                for i in range(len(Date_Monthwise[m])):
                    Date_Month.append(Date_Monthwise[m][i])
            DateCorr_Dict = dict(zip(Date_Month,Cor_Monthwise))

            SortedCorr = sorted(DateCorr_Dict.items())
            CorrectedData.append([lat[j],lon[j]]+[v for k,v in SortedCorr])
            app.processEvents()
            self.scrollbar.setValue(self.scrollbar.maximum())
            self.progressbar.setValue(j)
##            self.progressbarfinal.setValue(j)
            self.progressbar.setMaximum(len(lat)+len(CorrectedData[0])-2)
##            self.progressbarfinal.setMaximum(len(lat)+len(CorrectedData[0])-2)
            self.textbox.append('Corrected '+ str(j+1)+' out of '+str(len(lat))+':\tLat: %.1f'%lat[j]+'\tLon: %.1f'%lon[j])
            
        self.status.setText('Status: Writing Bias Corrected Data to File.')
        self.textbox.append('\nWriting Bias Corrected Data to File.')
        app.processEvents()
        if sep2 == ',':
            f = open(OutPath+'\Bias Corrected '+method.split('/')[0]+' '+str(YMod)+'.csv','w')
            for c in range(len(CorrectedData[0])):
                app.processEvents()
                if self.started==True:
                    f.write(','.join(str(CorrectedData[r][c]) for r in range(len(CorrectedData))))
                    f.write('\n')
                    if (c+1)%10 == 1 and (c+1) != 11:
                        self.textbox.append("Writing %dst day data" % (c+1))
                    elif (c+1)%10 == 2:
                        self.textbox.append("Writing %dnd day data" % (c+1))
                    elif (c+1)%10 == 3:
                        self.textbox.append("Writing %drd day data" % (c+1))
                    else:
                        self.textbox.append("Writing %dth day data" % (c+1))
                    app.processEvents()
                    self.scrollbar.setValue(self.scrollbar.maximum())
                    self.progressbar.setValue(len(lat)+c+1)
    ##                self.progressbarfinal.setValue(len(lat)+c+1)
                    self.progressbar.setMaximum(len(lat)+len(CorrectedData[0])-2)
    ##                self.progressbarfinal.setMaximum(len(lat)+len(CorrectedData[0])-2)

                    if c == len(CorrectedData[0])-1:
                        end = time.time()
                        t = end-start
                        self.status.setText('Status: Completed.')
                        self.textbox.append("\nTotal Time Taken: %.2d:%.2d:%.2d" % (t/3600,(t%3600)/60,t%60))
                        QMessageBox.information(self, "Information", "Bias Correction is completed.")
            f.close()
        if sep2 == '\t':
            f = open(OutPath+'\Bias Corrected '+method.split('/')[0]+' '+str(YMod)+'.txt','w')
            for c in range(len(CorrectedData[0])):
                app.processEvents()
                if self.started==True:
                    f.write('\t'.join(str(CorrectedData[r][c]) for r in range(len(CorrectedData))))
                    f.write('\n')
                    if (c+1)%10 == 1 and (c+1) != 11:
                        self.textbox.append("Writing %dst day data" % (c+1))
                    elif (c+1)%10 == 2:
                        self.textbox.append("Writing %dnd day data" % (c+1))
                    elif (c+1)%10 == 3:
                        self.textbox.append("Writing %drd day data" % (c+1))
                    else:
                        self.textbox.append("Writing %dth day data" % (c+1))
                    app.processEvents()
                    self.scrollbar.setValue(self.scrollbar.maximum())
                    self.progressbar.setValue(len(lat)+c+1)
                    self.progressbar.setMaximum(len(lat)+len(CorrectedData[0])-2)
    ##                self.progressbarfinal.setValue(len(lat)+c+1)
    ##                self.progressbarfinal.setMaximum(len(lat)+len(CorrectedData[0])-2)

                    if c == len(CorrectedData[0])-1:
                        end = time.time()
                        t = end-start
                        self.status.setText('Status: Completed.')
                        self.textbox.append("\nTotal Time Taken: %.2d:%.2d:%.2d" % (t/3600,(t%3600)/60,t%60))
                        QMessageBox.information(self, "Information", "Bias Correction is completed.")
            f.close()

    def ShowPlots(self):
        plt.show()

		
    def FTabUI(self):
        gridF = QGridLayout()
        gridF.addWidget(self.inputF(), 0, 0)
        gridF.addWidget(self.outputF(), 1, 0)
        gridF.addWidget(self.methodF(), 2, 0)
        gridF.addWidget(self.progressF(), 3, 0)
        gridF.setContentsMargins(0,0,0,0)
        
##        self.setTabText(0,"Historical")
        self.FTab.setLayout(gridF)

    def inputF(self):

        ##########Layout for taking input climate data to be bias corrected ##########

        gBoxF = QGroupBox("Inputs:")
        layout1F = QGridLayout()
        
        self.ObsfileF = QLineEdit()
        self.browse2F = QPushButton("...")
        self.browse2F.setMaximumWidth(25)
        self.browse2F.clicked.connect(self.browse2_fileF)
        self.q1F = QPushButton("?")
        self.q1F.setMaximumWidth(15)
        self.q1F.clicked.connect(self.Info1F)
        self.ObsfileF.setPlaceholderText("File with observed historical climate data (*.csv or *.txt)")

        self.ModHfileF = QLineEdit()
        self.browse1F = QPushButton("...")
        self.browse1F.setMaximumWidth(25)
        self.browse1F.clicked.connect(self.browse1_fileF)
        self.q0F = QPushButton("?")
        self.q0F.setMaximumWidth(15)
        self.q0F.clicked.connect(self.Info0F)
        self.ModHfileF.setPlaceholderText("File with GCM historical climate projections (*.csv or *.txt)")

        layout1F.addWidget(self.ObsfileF,1,0,1,3)
        layout1F.addWidget(self.q1F,1,3,1,1)
        layout1F.addWidget(self.browse2F,1,4,1,1)
        layout1F.addWidget(self.ModHfileF,1,5,1,3)
        layout1F.addWidget(self.q0F,1,8,1,1)
        layout1F.addWidget(self.browse1F,1,9,1,1)


        self.ModFfileF = QLineEdit()
        self.ModFfileF.setPlaceholderText("File with GCM future climate projections (*.csv or *.txt)")
        self.q2F = QPushButton("?")
        self.q2F.setMaximumWidth(15)
        self.q2F.clicked.connect(self.Info2F)
        self.browse3F = QPushButton("...")
        self.browse3F.setMaximumWidth(25)
        self.browse3F.clicked.connect(self.browse3_fileF)
        layout1F.addWidget(self.ModFfileF,3,0,1,8)
        layout1F.addWidget(self.q2F,3,8,1,1)
        layout1F.addWidget(self.browse3F,3,9,1,1)

##        ##########Layout for taking comma delimited vs tab delimited################################

##        sublayout1 = QGridLayout()
##
##        self.label1 = QLabel("Input Format:\t")
##        self.b1 = QRadioButton("Comma Delimated (*.csv)")
##        #self.b1.setChecked(True)
##        self.b2 = QRadioButton("Tab Delimited (*.txt)")
##
##        self.b1.toggled.connect(lambda:self.btnstate(self.b1))
##        self.b2.toggled.connect(lambda:self.btnstate(self.b2))
##
##        sublayout1.addWidget(self.label1,1,0)
##        sublayout1.addWidget(self.b1,1,1)
##        sublayout1.addWidget(self.b2,1,2)
##        layout1.addLayout(sublayout1,3,0)
        
        gBoxF.setLayout(layout1F)
        return gBoxF

    def outputF(self):

        ##########Layout for output file location and interpolation##########

        gBoxF = QGroupBox("Outputs:")
        layout4F = QGridLayout()
        
        self.outputfile_locationF = QLineEdit()
        self.outputfile_locationF.setPlaceholderText("Folder to save bias corrected GCM outputs")
        self.browse4F = QPushButton("...")
        self.browse4F.setMaximumWidth(25)
        self.browse4F.clicked.connect(self.browse4_fileF)
        layout4F.addWidget(self.outputfile_locationF,1,0,1,3)
        layout4F.addWidget(self.browse4F,1,3,1,1)

        ########################Layout for taking comma delimited vs tab delimited################################

        sublayout2F = QGridLayout()
        output_labelF = QLabel("Output Format:\t")
        self.b3F = QRadioButton("Comma Delimated (*.csv)")
        #self.b3.setChecked(True)
        self.b4F = QRadioButton("Tab Delimited (*.txt)")

        self.b3F.toggled.connect(lambda:self.btn2stateF(self.b3F))
        self.b4F.toggled.connect(lambda:self.btn2stateF(self.b4F))
        
        sublayout2F.addWidget(output_labelF,1,0)
        sublayout2F.addWidget(self.b3F,1,1)
        sublayout2F.addWidget(self.b4F,1,2)
        layout4F.addLayout(sublayout2F,2,0)
        gBoxF.setLayout(layout4F)
        return gBoxF

    def methodF(self):

        ########################Layout for taking methods of Bias Correction ################################
        gBoxF = QGroupBox("Variable/Distribution")
        layout5F = QGridLayout()
        self.b5F = QRadioButton("Rainfall/Gamma")
        #self.b3F.setChecked(True)
        self.b6F = QRadioButton("Temperature/Normal")
        self.b7F = QRadioButton("Solar Radiation/Beta")

        self.b5F.toggled.connect(lambda:self.btn3stateF(self.b5F))
        self.b6F.toggled.connect(lambda:self.btn3stateF(self.b6F))
        self.b7F.toggled.connect(lambda:self.btn3stateF(self.b7F))
        
        self.show_hideF = QPushButton("Show Details")
        Font=QFont()
        Font.setBold(True)
        #self.show_hideF.setFont(Font)
        self.show_hideF.setCheckable(True)
        #self.show_hideF.toggle()
        self.show_hideF.clicked.connect(self.ShowHideF)
        self.show_hideF.setFixedWidth(90)
        self.show_hideF.setFixedHeight(25)
        Style_show_hideF_Button = """
QPushButton{
color: rgb(255, 255, 255);
background-color: rgb(66, 131, 221);
border: none;
}
QPushButton:Checked{
background-color: rgb(66, 131, 221);
border: none;
}
QPushButton:hover{
background-color: rgb(66, 131, 221,230);
border: none;
}
"""
        self.show_hideF.setStyleSheet(Style_show_hideF_Button)

        self.show_plotsF = QPushButton("Show Plots")
        self.show_plotsF.clicked.connect(self.ShowPlotsF)
        self.show_plotsF.setFixedWidth(75)
        self.show_plotsF.setFixedHeight(25)
        self.show_plotsF.setStyleSheet(Style_show_hideF_Button)
        
        self.startF = QPushButton("Run")
        self.startF.setFixedWidth(50)
        self.startF.setFixedHeight(25)
        Style_RunF_Button = """
QPushButton{
color: rgb(255, 255, 255);
background-color: rgb(0,121,0);
border-color: none;
border: none;
}
QPushButton:hover{
background-color: rgb(0,121,0,230);
}
"""
        self.startF.clicked.connect(self.start_correctionF)
        #self.startF.setFont(Font)
        self.startF.setStyleSheet(Style_RunF_Button)
        
        self.stopF = QPushButton("Cancel")
        self.stopF.setMaximumWidth(60)
        self.stopF.setFixedHeight(25)
        Style_CancelF_Button = """
QPushButton{
color: rgb(255, 255, 255);
background-color: rgb(180,0,0,240);
border-color: none;
border: none;
}
QPushButton:hover{
background-color: rgb(180,0,0,220);
}
"""
        self.stopF.clicked.connect(self.stop_correctionF)
        #self.stopF.setFont(Font)
        self.stopF.setStyleSheet(Style_CancelF_Button)
        
        layout5F.addWidget(self.b5F,1,1)
        layout5F.addWidget(self.b6F,1,2)
        layout5F.addWidget(self.b7F,1,3)
        layout5F.addWidget(self.show_hideF,1,7)
        layout5F.addWidget(self.startF,1,4)
        layout5F.addWidget(self.stopF,1,6)
        layout5F.addWidget(self.show_plotsF,1,5)
##        layout5F.addWidget(self.b5F,1,1)
##        layout5F.addWidget(self.b6F,1,2)
##        layout5F.addWidget(self.b7F,1,3)
##        layout5F.addWidget(self.show_hideF,2,5)
##        layout5F.addWidget(self.startF,1,4)
##        layout5F.addWidget(self.stopF,2,4)
##        layout5F.addWidget(self.show_plotsF,1,5)
        
        gBoxF.setLayout(layout5F)
        return gBoxF

        ########## Layout for progress of Bias Correction ##########
    def progressF(self):
        gBoxF = QGroupBox()
        layout6F = QVBoxLayout() 
        
        STYLE2 = """
QProgressBar{
text-align: center;
}
QProgressBar::chunk {
background-color: rgb(0,121,0);
}
"""
        self.statusF = QLabel('')
        self.progressbarF = QProgressBar()
##        self.progressbarfinalF = QProgressBar()
        #self.progressbarF.setMinimum(1)
        self.progressbarF.setFixedHeight(13)
##        self.progressbarfinalF.setFixedHeight(13)
        self.progressbarF.setStyleSheet(STYLE2)
##        self.progressbarfinalF.setStyleSheet(STYLE2)
        self.textboxF = QTextEdit()
        self.textboxF.setReadOnly(True)
        self.textboxF.moveCursor(QTextCursor.End)
        self.textboxF.hide()
        self.scrollbarF = self.textboxF.verticalScrollBar()

        layout6F.addWidget(self.statusF)
        layout6F.addWidget(self.progressbarF)
##        layout6F.addWidget(self.progressbarfinalF)
        layout6F.addWidget(self.textboxF)
        gBoxF.setLayout(layout6F)
        return gBoxF 


      
    ########################### Control Buttons ####################################################
    def browse1_fileF(self):
        ModH_fileF = QFileDialog.getOpenFileName(self,caption = "Open File",directory=r"C:\Users\gupta\OneDrive\0. M.Tech. Research Work\Codes\GUIs\Bias Correction\\",
                                                   filter="Comma Delimated (*.csv);;Tab Delimated (*.txt)")
        self.ModHfileF.setText(QDir.toNativeSeparators(ModH_fileF))
    
    def browse2_fileF(self):
        Obs_fileF = QFileDialog.getOpenFileName(self,caption = "Open File",directory=r"C:\Users\gupta\OneDrive\0. M.Tech. Research Work\Codes\GUIs\Bias Correction\\",
                                                   filter="Comma Delimated (*.csv);;Tab Delimated (*.txt)")
        self.ObsfileF.setText(QDir.toNativeSeparators(Obs_fileF))
        
    def browse3_fileF(self):
        ModF_fileF = QFileDialog.getOpenFileName(self,caption = "Open File", directory=r"C:\Users\gupta\OneDrive\0. M.Tech. Research Work\Codes\GUIs\Bias Correction\\",
                                                filter="Comma Delimated (*.csv);;Tab Delimated (*.txt)")
        self.ModFfileF.setText(QDir.toNativeSeparators(ModF_fileF))
        
    def browse4_fileF(self):
        output_fileF = QFileDialog.getExistingDirectory(self, "Save File in Folder", r"C:\Users\gupta\OneDrive\0. M.Tech. Research Work\Codes\GUIs\Bias Correction\\",
                                                       QFileDialog.ShowDirsOnly)
        self.outputfile_locationF.setText(QDir.toNativeSeparators(output_fileF))  

    def Info0F(self):
        QMessageBox.information(self, "Information About Input Files (Model Historical)",
                                '''Sample input (.csv or .txt) should be same as it is shown in Sample Example:\nC:\Program Files (x86)\Climate Data Bias Corrector\Sample Input (ModH).csv
                                ''')
    def Info1F(self):
        QMessageBox.information(self, "Information About Input Files (Observed Historical)",
                                '''Sample input (.csv or .txt) should be same as it is shown in Sample Example:\nC:\Program Files (x86)\Climate Data Bias Corrector\Sample Input (ObsH).csv
                                ''')
    def Info2F(self):
        QMessageBox.information(self, "Information About Input File (Model Future)",
                                '''Sample input (.csv or .txt) should be same as it is shown in Sample Example:\nC:\Program Files (x86)\Climate Data Bias Corrector\Sample Input (ModF).csv
                                ''')

##    def btnstateF(self,b):
##        if b.text() == "Comma Delimated (*.csv)" and b.isChecked() == True:
##            self.seperatorF = ','
##            self.seperatornameF = '.csv'
##        if b.text() == "Tab Delimited (*.txt)" and b.isChecked() == True:
##            self.seperatorF = '\t'
##            self.seperatornameF = '.txt'

    def btn2stateF(self,b):
        if b.text() == "Comma Delimated (*.csv)" and b.isChecked() == True:
            self.seperator2F = ','
            self.seperatorname2F = '.csv'
        if b.text() == "Tab Delimited (*.txt)" and b.isChecked() == True:
            self.seperator2F = '\t'
            self.seperatorname2F = '.txt'

    def btn3stateF(self,b):
        if b.text() == "Rainfall/Gamma" and b.isChecked() == True:
            self.methodnameF = b.text()
        if b.text() == "Temperature/Normal" and b.isChecked() == True:
            self.methodnameF = b.text()
        if b.text() == "Solar Radiation/Beta" and b.isChecked() == True:
            self.methodnameF = b.text()
            
    def start_correctionF(self):
        self.started = True
        self.BiasCorrectF()

    def stop_correctionF(self):
        if self.started:
            self.started = False
            QMessageBox.information(self, "Information", "Bias correction is aborted.")

    def ShowHideF(self):
        if self.show_hideF.text() == "Hide Details" and self.show_hideF.isChecked() == False:
            self.textboxF.hide()
            self.textbox.hide()
##            self.setFixedSize(700,372)
            ShowHide(self.show_hideF.text())
            ShowHide(self.show_hide.text())
            self.show_hideF.setText('Show Details')
            self.show_hide.setText('Show Details')
        if self.show_hideF.text() == "Show Details" and self.show_hideF.isChecked() == True:
            self.textboxF.show()
            self.textbox.show()
##            self.setFixedSize(700,620)
            ShowHide(self.show_hideF.text())
            ShowHide(self.show_hide.text())
            self.show_hideF.setText('Hide Details')
            self.show_hide.setText('Hide Details')
        
    def BiasCorrectF(self):
        if self.ObsfileF.text() == "":
            QMessageBox.critical(self, "Message", "File with observed historical climate data (*.csv or *.txt) is not given.")
            self.started = False
        if self.ModHfileF.text() == "":
            QMessageBox.critical(self, "Message", "File with GCM historical climate projections (*.csv or *.txt) is not given.")
            self.started = False
        if self.ModFfileF.text() == "":
            QMessageBox.critical(self, "Message", "File with GCM future climate projections (*.csv or *.txt) is not given.")
            self.started = False
        if self.outputfile_locationF.text() == "":
            QMessageBox.critical(self, "Message", "Folder to save bias corrected GCM outputs is not given")
            self.started = False

        try:
##            sepF = self.seperator
##            sepnameF = self.seperatorname

            sep2F = self.seperator2F
            sepname2F = self.seperatorname2F
        except:
            QMessageBox.critical(self, "Message", "Format is not defined.")
            self.started = False
        try:
            method = self.methodnameF
        except:
            QMessageBox.critical(self, "Message", "Variable/Distribution is not defined.")
            self.started = False
        
        self.textboxF.setText("")
        
        start = time.time()
        self.statusF.setText('Status: Correcting.')
##        self.progressbarfinalF.setMinimum(0)
##        self.progressbarfinalF.setValue(0)
        self.progressbarF.setMinimum(0)
        self.progressbarF.setValue(0)

        FobsH = self.ObsfileF.text()
        FmodH = self.ModHfileF.text()
        FmodF = self.ModFfileF.text()

        ObsHData, ModHData, ModFData, CorrectedData = [], [], [], []
        
        with open(FobsH) as f:
            line = [line for line in f]
            for i in range(len(line)):
                if FobsH.endswith('.csv'):
                    ObsHData.append([word for word in line[i].split(",") if word])
                if FobsH.endswith('.txt'):
                    ObsHData.append([word for word in line[i].split("\t") if word])
        lat = [float(ObsHData[0][c]) for c in range(1,len(ObsHData[0]))]
        lon = [float(ObsHData[1][c]) for c in range(1,len(ObsHData[0]))]
        Latitude = []
        Longitude = []
        
        with open(FmodH) as f:
            line = [line for line in f]
            for i in range(len(line)):
                if FmodH.endswith('.csv'):
                    ModHData.append([word for word in line[i].split(",") if word])
                if FmodH.endswith('.txt'):
                    ModData.append([word for word in line[i].split("\t") if word])

        with open(FmodF) as f:
            line = [line for line in f]
            for i in range(len(line)):
                if FmodF.endswith('.csv'):
                    ModFData.append([word for word in line[i].split(",") if word])
                if FmodF.endswith('.txt'):
                    ModFData.append([word for word in line[i].split("\t") if word])

        DateObsH = [ObsHData[r][0] for r in range(len(ObsHData))]
        DateModH = [ModHData[r][0] for r in range(len(ModHData))]
        DateModF = [ModFData[r][0] for r in range(len(ModFData))]
        
        OutPath = self.outputfile_locationF.text()
        CorrectedData.append(DateModF)
        
        YObsH = int(DateObsH[2][-4:])
        YModH = int(DateModH[2][-4:])
        YModF = int(DateModF[2][-4:])
        
        app.processEvents()
        if len(lat)>1:
            random_count = np.random.randint(len(lat),size=(1))
        else:
            random_count = 0
        fig = plt.figure(figsize=(15,7))
        plt.style.use('ggplot')
##        plt.style.use('fivethirtyeight')
        for j in range(len(lat)):
            ObsH = [float(ObsHData[r][j+1]) for r in range(2,len(ObsHData))]
            ModH = [float(ModHData[r][j+1]) for r in range(2,len(ModHData))]
            ModF = [float(ModFData[r][j+1]) for r in range(2,len(ModFData))]

            DateObsH = [date(YObsH,1,1)+timedelta(i) for i in range(len(ObsH))]
            DateModH = [date(YModH,1,1)+timedelta(i) for i in range(len(ModH))]
            DateModF = [date(YModF,1,1)+timedelta(i) for i in range(len(ModF))]

            if method == 'Rainfall/Gamma' and self.started == True:
                DateH=DateModH
                DateF=DateModF
                ModH_Month=[]
                ModF_Month=[]
                Cor_Monthwise = []
                ObsH_Monthwise = [[] for m in range(12)]
                ObsH_MonthFreq = [[] for m in range(12)]
                ModH_Monthwise = [[] for m in range(12)]
                ModH_MonthFreq = [[] for m in range(12)]
                ModF_Monthwise = [[] for m in range(12)]
                ModF_MonthFreq = [[] for m in range(12)]
                DateH_Monthwise= [[] for m in range(12)]
                DateF_Monthwise= [[] for m in range(12)]
                for m in range(12):
                    for i in range(len(ObsH)):
                        if DateH[i].month == m+1:
                            DateH_Monthwise[m].append(DateH[i])
                            ObsH_Monthwise[m].append(ObsH[i])
                            ModH_Monthwise[m].append(ModH[i])
                for m in range(12):
                    for i in range(len(ModF)):
                        if DateF[i].month == m+1:
                            DateF_Monthwise[m].append(DateF[i])
                            ModF_Monthwise[m].append(ModF[i])

                for m in range(12):
                    ModH_Month.append(sorted_values(ObsH_Monthwise[m],ModH_Monthwise[m]))
                    ModF_Month.append(sorted_values_thresh(ModH_Month[m], ModF_Monthwise[m]))

                ModH_Monthwise = ModH_Month
                ModF_Monthwise = ModF_Month
                
                for m in range(12):
                    for i in range(len(ModH_Monthwise[m])):
                        if ModH_Monthwise[m][i]>0:
                            ModH_MonthFreq[m].append(ModH_Monthwise[m][i])
                        if ObsH_Monthwise[m][i]>0:
                            ObsH_MonthFreq[m].append(ObsH_Monthwise[m][i])
                    for i in range(len(ModF_Monthwise[m])):
                        if ModF_Monthwise[m][i]>0:
                            ModF_MonthFreq[m].append(ModF_Monthwise[m][i])

                nplot=1
                for m in range(12):
                    Cor = []
                    if len(ModH_MonthFreq[m])>0 and len(ObsH_MonthFreq[m])>0 and len(ModF_MonthFreq[m])>0:
                        Moh, Mgh, Mgf, Voh, Vgh, Vgf = np.mean(ObsH_MonthFreq[m]), np.mean(ModH_MonthFreq[m]), np.mean(ModF_MonthFreq[m]), np.std(ObsH_MonthFreq[m])**2, np.std(ModH_MonthFreq[m])**2, np.std(ModF_MonthFreq[m])**2
                        if not any(param<0.000001 for param in [Moh, Mgh, Mgf, Voh, Vgh, Vgf]):
                            aoh, boh, agh, bgh, agf, bgf = Moh**2/Voh, Voh/Moh, Mgh**2/Vgh, Vgh/Mgh, Mgf**2/Vgf, Vgf/Mgf
                            loh, lgh, lgf = 0, 0, 0
                        else:
                            aoh, loh, boh = gamma.fit(ObsH_MonthFreq[m], loc=0)
                            agh, lgh, bgh = gamma.fit(ModH_MonthFreq[m], loc=0)
                            agf, lgf, bgf = gamma.fit(ModF_MonthFreq[m], loc=0)
                        'CDF of ModF with ModH Parameters'
                        Prob_ModF_ParaModH = gamma.cdf(ModF_Monthwise[m],agh, scale=bgh)

                        'Inverse of Prob_ModF_ParaModH with ParaObsH to get corrected transformed values of Future Model Time Series'
                        Cor = gamma.ppf(Prob_ModF_ParaModH, aoh, scale=boh)
                    else:
                        for i in range(len(ModF_Monthwise[m])):
                            Cor.append(0)

                    for c in Cor:
                        Cor_Monthwise.append('%.1f'%c)
                    
                    if j == random_count:
                        ax = fig.add_subplot(3,4,nplot)
                        obsH_cdf = gamma.cdf(ObsH_Monthwise[m], aoh, loh, boh)
                        modF_cdf = gamma.cdf(ModF_Monthwise[m], agf, lgf, bgf)
                        Mc, Vc = np.mean(Cor), np.std(Cor)**2
                        if not any(param<0.000001 for param in [Mc, Vc]):
                            acf, bcf = Mc**2/Vc, Vc/Mc
                            lcf = 0
                        else:
                            acf, lcf, bcf = gamma.fit(Cor)
                        cor_cdf = gamma.cdf(Cor, acf, lcf, bcf)
                        ax.set_title('Month: '+str(m+1), fontsize=12)
                        o, = ax.plot(ObsH_Monthwise[m], obsH_cdf, '.b')
                        m, = ax.plot(ModF_Monthwise[m], modF_cdf, '.r')
                        c, = ax.plot(Cor, cor_cdf, '.g')
                        nplot=nplot+1
                        fig.legend([o,m,c,(o,m,c,)],['Observed','Before Correction','After Correction'],ncol=3,loc=8,frameon=False, fontsize=14)
                        plt.subplots_adjust(hspace=0.3, wspace=0.3)
                        plt.suptitle('CDF Plots of ' + method.split('/')[0] + ' for Randomly Selected Lat: '+str(lat[j])+' Lon: '+str(lon[j]),fontsize=16)
                        
                
            if method =='Temperature/Normal' and self.started == True:
                DateH=DateModH
                DateF=DateModF
                Cor_Monthwise = []
                ObsH_Monthwise = [[] for m in range(12)]
                ModH_Monthwise = [[] for m in range(12)]
                ModF_Monthwise = [[] for m in range(12)]
                DateH_Monthwise= [[] for m in range(12)]
                DateF_Monthwise= [[] for m in range(12)]
                
                for m in range(12):
                    for i in range(len(ObsH)):
                        if DateH[i].month == m+1:
                            DateH_Monthwise[m].append(DateH[i])
                            ObsH_Monthwise[m].append(ObsH[i])
                            ModH_Monthwise[m].append(ModH[i])

                for m in range(12):
                    for i in range(len(ModF)):
                        if DateF[i].month == m+1:
                            DateF_Monthwise[m].append(DateF[i])
                            ModF_Monthwise[m].append(ModF[i])

                nplot=1
                for m in range(12):
                    Cor = []
                    Moh, Mgh, Mgf, Soh, Sgh, Sgf = np.mean(ObsH_Monthwise[m]), np.mean(ModH_Monthwise[m]), np.mean(ModF_Monthwise[m]), np.std(ObsH_Monthwise[m]), np.std(ModH_Monthwise[m]), np.std(ModF_Monthwise[m])

                    Prob_ModF = norm.cdf(ModF_Monthwise[m], Mgf, Sgf)

                    Inv_of_Prob_ModF_ParaObsH = norm.ppf(Prob_ModF, Moh, Soh)
                    Inv_of_Prob_ModF_ParaModH = norm.ppf(Prob_ModF, Mgh, Sgh)
                    
                    for i in range(len(ModF_Monthwise[m])):
                        Cor.append(ModF_Monthwise[m][i]+Inv_of_Prob_ModF_ParaObsH[i]-Inv_of_Prob_ModF_ParaModH[i])

                    for c in Cor:
                        Cor_Monthwise.append('%.1f'%c)

                    if j == random_count:
                        ax = fig.add_subplot(3,4,nplot)
                        obsH_cdf = norm.cdf(ObsH_Monthwise[m], Moh, Soh)
                        modF_cdf = norm.cdf(ModF_Monthwise[m], Mgf, Sgf)
                        Mcf, Scf = norm.fit(Cor)
                        cor_cdf = norm.cdf(Cor, Mcf, Scf)
                        ax.set_title('Month: '+str(m+1), fontsize=12)
                        o, = ax.plot(ObsH_Monthwise[m], obsH_cdf, '.b')
                        m, = ax.plot(ModF_Monthwise[m], modF_cdf, '.r')
                        c, = ax.plot(Cor, cor_cdf, '.g')
                        nplot=nplot+1
                        fig.legend([o,m,c,(o,m,c,)],['Observed','Before Correction','After Correction'],ncol=3,loc=8,frameon=False, fontsize=14)
                        plt.subplots_adjust(hspace=0.3, wspace=0.3)
                        plt.suptitle('CDF Plots of ' + method.split('/')[0] + ' for Randomly Selected Lat: '+str(lat[j])+' Lon: '+str(lon[j]),fontsize=16)
                        
            if method =='Solar Radiation/Beta' and self.started == True:
                ModH_Month=[]
                Cor_Monthwise = []
                ObsH_Monthwise = [[] for m in range(12)]
                ModH_Monthwise = [[] for m in range(12)]
                ModF_Monthwise = [[] for m in range(12)]
                DateObsH_Monthwise= [[] for m in range(12)]
                DateModH_Monthwise= [[] for m in range(12)]
                DateModF_Monthwise= [[] for m in range(12)]
                
                for m in range(12):
                    for i in range(len(ObsH)):
                        if DateObsH[i].month == m+1:
                            DateObsH_Monthwise[m].append(DateObsH[i])
                            ObsH_Monthwise[m].append(ObsH[i])

                for m in range(12):
                    for i in range(len(ModH)):
                        if DateModH[i].month == m+1:
                            DateModH_Monthwise[m].append(DateModH[i])
                            ModH_Monthwise[m].append(ModH[i])

                for m in range(12):
                    for i in range(len(ModF)):
                        if DateModF[i].month == m+1:
                            DateModF_Monthwise[m].append(DateModF[i])
                            ModF_Monthwise[m].append(ModF[i])
                
                nplot=1
                for m in range(12):
                    Cor = []
                    'Maximum and minimum value monthwise of whole time series are calculated below for ObsH, ModH and ModF'
                    ohMin, ohMax = min(ObsH_Monthwise[m]), max(ObsH_Monthwise[m])
                    ghMin, ghMax = min(ModH_Monthwise[m]), max(ModH_Monthwise[m])
                    gfMin, gfMax = min(ModF_Monthwise[m]), max(ModF_Monthwise[m])

                    'Mean and variance value monthwise of whole time series are calculated below for ObsH, ModH and ModF'
                    Moh = (np.mean(ObsH_Monthwise[m])-ohMin)/(ohMax - ohMin)
                    Mgh = (np.mean(ModH_Monthwise[m])-ghMin)/(ghMax - ghMin)
                    Mgf = (np.mean(ModF_Monthwise[m])-gfMin)/(gfMax - gfMin)
                    Voh = np.std(ObsH_Monthwise[m])**2/(ohMax - ohMin)**2
                    Vgh = np.std(ModH_Monthwise[m])**2/(ghMax - ghMin)**2
                    Vgf = np.std(ModF_Monthwise[m])**2/(gfMax - gfMin)**2

                    'a,b parameters in beta distribution, monthwise of whole time series, are calculated below for ObsH, ModH and ModF'
                    aoh, agh, agf = -Moh*(Voh + Moh**2 - Moh)/Voh, -Mgh*(Vgh + Mgh**2 - Mgh)/Vgh, -Mgf*(Vgf + Mgf**2 - Mgf)/Vgf
                    boh, bgh, bgf = aoh*(1 - Moh)/Moh, agh*(1 - Mgh)/Mgh, agf*(1 - Mgf)/Mgf

                    'All the time series are transformed to range (0,1)'
                    TransOH = [(ObsH_Monthwise[m][i]-ohMin)/(ohMax-ohMin) for i in range(len(ObsH_Monthwise[m]))]
                    TransGH = [(ModH_Monthwise[m][i]-ghMin)/(ghMax-ghMin) for i in range(len(ModH_Monthwise[m]))]
                    TransGF = [(ModF_Monthwise[m][i]-gfMin)/(gfMax-gfMin) for i in range(len(ModF_Monthwise[m]))]

                    'CDF of ModF with ModH Parameters'
                    Prob_ModF_ParaModH = beta.cdf(TransGF, agh, bgh)
                    
                    'Inverse of Prob_ModF_ParaModH with ParaObsH to get corrected transformed values of Future Model Time Series'
                    TransC = beta.ppf(Prob_ModF_ParaModH, aoh, boh)

                    Cor = [TransC[i]*(ohMax-ohMin)+ohMin for i in range(len(TransC))]

                    for c in Cor:
                        Cor_Monthwise.append('%.1f'%c)

                    DateF_Monthwise = DateModF_Monthwise
                    
                    if j == random_count:
                        ax = fig.add_subplot(3,4,nplot)
                        obsH_cdf = beta.cdf(TransOH, aoh, boh)
                        modF_cdf = beta.cdf(TransGF, agf, bgf)
                        Mcf = (np.mean(Cor)-min(Cor))/(max(Cor)-min(Cor))
                        Vcf = np.std(Cor)**2/(max(Cor)-min(Cor))**2
                        acf = -Mcf*(Vcf + Mcf**2 - Mcf)/Vcf
                        bcf = acf*(1 - Mcf)/Mcf
                        cor_cdf = beta.cdf(TransC, acf, bcf)
                        ax.set_title('Month: '+str(m+1), fontsize=12)
                        o, = ax.plot(ObsH_Monthwise[m], obsH_cdf, '.b')
                        m, = ax.plot(ModF_Monthwise[m], modF_cdf, '.r')
                        c, = ax.plot(Cor, cor_cdf, '.g')
                        nplot=nplot+1
                        fig.legend([o,m,c,(o,m,c,)],['Observed','Before Correction','After Correction'],ncol=3,loc=8,frameon=False, fontsize=14)
                        plt.subplots_adjust(hspace=0.3, wspace=0.3)
                        plt.suptitle('CDF Plots of ' + method.split('/')[0] + ' for Randomly Selected Lat: '+str(lat[j])+' Lon: '+str(lon[j]),fontsize=16)

            Date_Month=[]
            for m in range(12):
                for i in range(len(DateF_Monthwise[m])):
                    Date_Month.append(DateF_Monthwise[m][i])
            DateCorr_Dict = dict(zip(Date_Month,Cor_Monthwise))

            SortedCorr = sorted(DateCorr_Dict.items())
            CorrectedData.append([lat[j],lon[j]]+[v for k,v in SortedCorr])
            app.processEvents()
            self.scrollbarF.setValue(self.scrollbarF.maximum())
            self.progressbarF.setValue(j)
##            self.progressbarfinalF.setValue(j)
            self.progressbarF.setMaximum(len(lat)+len(CorrectedData[0])-2)
##            self.progressbarfinalF.setMaximum(len(lat)+len(CorrectedData[0])-2)
            self.textboxF.append('Corrected '+ str(j+1)+' out of '+str(len(lat))+':\tLat: %.1f'%lat[j]+'\tLon: %.1f'%lon[j])

        self.statusF.setText('Status: Writing Bias Corrected Data to File.')
        self.textboxF.append('\nWriting Bias Corrected Data to File.')
        app.processEvents()
        if sep2F == ',':
            f = open(OutPath+'\Bias Corrected '+method.split('/')[0]+' '+str(YModF)+'.csv','w')
            for c in range(len(CorrectedData[0])):
                app.processEvents()
                if self.started==True:
                    f.write(','.join(str(CorrectedData[r][c]) for r in range(len(CorrectedData))))
                    f.write('\n')
                    if (c+1)%10 == 1 and (c+1) != 11:
                        self.textboxF.append("Writing %dst day data" % (c+1))
                    elif (c+1)%10 == 2:
                        self.textboxF.append("Writing %dnd day data" % (c+1))
                    elif (c+1)%10 == 3:
                        self.textboxF.append("Writing %drd day data" % (c+1))
                    else:
                        self.textboxF.append("Writing %dth day data" % (c+1))
                    app.processEvents()
                    self.scrollbarF.setValue(self.scrollbarF.maximum())
                    self.progressbarF.setValue(len(lat)+c+1)
    ##                self.progressbarfinalF.setValue(len(lat)+c+1)
                    self.progressbarF.setMaximum(len(lat)+len(CorrectedData[0])-2)
    ##                self.progressbarfinalF.setMaximum(len(lat)+len(CorrectedData[0])-2)

                    if c == len(CorrectedData[0])-1:
                        end = time.time()
                        t = end-start
                        self.statusF.setText('Status: Completed.')
                        self.textboxF.append("\nTotal Time Taken: %.2d:%.2d:%.2d" % (t/3600,(t%3600)/60,t%60))
                        QMessageBox.information(self, "Information", "Bias Correction is completed.")
            f.close()
        if sep2F == '\t':
            f = open(OutPath+'\Bias Corrected '+method.split('/')[0]+' '+str(YModF)+'.txt','w')
            for c in range(len(CorrectedData[0])):
                app.processEvents()
                if self.started==True:
                    f.write('\t'.join(str(CorrectedData[r][c]) for r in range(len(CorrectedData))))
                    f.write('\n')
                    if (c+1)%10 == 1 and (c+1) != 11:
                        self.textboxF.append("Writing %dst day data" % (c+1))
                    elif (c+1)%10 == 2:
                        self.textboxF.append("Writing %dnd day data" % (c+1))
                    elif (c+1)%10 == 3:
                        self.textboxF.append("Writing %drd day data" % (c+1))
                    else:
                        self.textboxF.append("Writing %dth day data" % (c+1))
                    app.processEvents()
                    self.scrollbarF.setValue(self.scrollbarF.maximum())
                    self.progressbarF.setValue(len(lat)+c+1)
                    self.progressbarF.setMaximum(len(lat)+len(CorrectedData[0])-2)
    ##                self.progressbarfinalF.setValue(len(lat)+c+1)
    ##                self.progressbarfinalF.setMaximum(len(lat)+len(CorrectedData[0])-2)

                    if c == len(CorrectedData[0])-1:
                        end = time.time()
                        t = end-start
                        self.statusF.setText('Status: Completed.')
                        self.textboxF.append("\nTotal Time Taken: %.2d:%.2d:%.2d" % (t/3600,(t%3600)/60,t%60))
                        QMessageBox.information(self, "Information", "Bias Correction is completed.")
            f.close()
    def ShowPlotsF(self):
        plt.show()



class BiasCorrection(QWidget):
    def __init__(self, parent=None):
        super(BiasCorrection,self).__init__(parent)
        grid = QGridLayout()
        self.m_titlebar=TitleBar(self)
        grid.addWidget(self.m_titlebar, 0, 0)
        self.tabs = HFTab(self)
        grid.addWidget(self.tabs, 1, 0)
        self.setLayout(grid)
        grid.setContentsMargins(0,0,0,0)
##        self.setWindowTitle("Weather Data Interpolator")
        self.setFocus()
        self.adjustSize()
        self.Widget_Width  = self.frameGeometry().width()
        self.Widget_Height = self.frameGeometry().height()
        
##        self.setFixedSize(750,354)
        self.setFixedSize(750,self.Widget_Height)
##        self.move(350,100)
        self.setWindowFlags(Qt.FramelessWindowHint)
##        self.setWindowFlags(Qt.WindowMaximizeButtonHint)
        started = False

       
app = QApplication(sys.argv)
widget = BiasCorrection()
app_icon = QIcon()
app_icon.addFile('Interpolation-2.ico', QSize(40,40))
app.setWindowIcon(app_icon)
pixmap = QPixmap("Splash_CDBC.png")
splash = QSplashScreen(pixmap)
splash.show()
screen_resolution = app.desktop().screenGeometry()
width, height = screen_resolution.width(), screen_resolution.height()
widget.move(width/2-widget.width()/2,height/2-widget.height()/2)
time.sleep(2)
def ShowHide(text):
    if text == 'Show Details':
        widget.setFixedSize(750,BiasCorrection().Widget_Height+BiasCorrection().Widget_Height*2/3)
        print(widget.height())
##        widget.setFixedSize(750,620)
    if text == 'Hide Details':
        widget.setFixedSize(750,BiasCorrection().Widget_Height+1)
        print(widget.height())
##        widget.setFixedSize(750,354)
##widget.setFixedWidth(500)
##widget.setFixedHeight(400)
widget.show()
splash.finish(widget)
app.exec_()
