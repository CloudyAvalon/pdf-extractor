# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pumpselectortab.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QScrollArea, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_pumpSelectTab(object):
    def setupUi(self, pumpSelectTab, index):
        if not pumpSelectTab.objectName():
            pumpSelectTab.setObjectName(u"pumpSelectTab" + str(index))
        pumpSelectTab.resize(276, 608)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(pumpSelectTab.sizePolicy().hasHeightForWidth())
        pumpSelectTab.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(pumpSelectTab)
        self.verticalLayout.setObjectName(u"verticalLayout" + str(index))
        self.sourceInfoView = QTableWidget(pumpSelectTab)
        self.sourceInfoView.setObjectName(u"sourceInfoView" + str(index))
        self.sourceInfoView.setMaximumSize(QSize(16777215, 255))

        self.verticalLayout.addWidget(self.sourceInfoView)

        self.tabSplitLine = QFrame(pumpSelectTab)
        self.tabSplitLine.setObjectName(u"tabSplitLine" + str(index))
        self.tabSplitLine.setLineWidth(1)
        self.tabSplitLine.setMidLineWidth(1)
        self.tabSplitLine.setFrameShape(QFrame.Shape.HLine)
        self.tabSplitLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.tabSplitLine)

        self.salesLabel = QLabel(pumpSelectTab)
        self.salesLabel.setObjectName(u"salesLabel" + str(index))

        self.verticalLayout.addWidget(self.salesLabel)

        self.scrollArea = QScrollArea(pumpSelectTab)
        self.scrollArea.setObjectName(u"scrollArea" + str(index))
        self.scrollArea.setMaximumSize(QSize(16777215, 35))
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.selectPumpArea = QWidget()
        self.selectPumpArea.setObjectName(u"selectPumpArea" + str(index))
        self.selectPumpArea.setGeometry(QRect(0, 0, 256, 34))
        self.horizontalLayout = QHBoxLayout(self.selectPumpArea)
        self.horizontalLayout.setObjectName(u"horizontalLayout" + str(index))
        self.selectLabel = QLabel(self.selectPumpArea)
        self.selectLabel.setObjectName(u"selectLabel" + str(index))
        self.selectLabel.setFrameShape(QFrame.Shape.NoFrame)

        self.horizontalLayout.addWidget(self.selectLabel)

        self.scrollArea.setWidget(self.selectPumpArea)

        self.verticalLayout.addWidget(self.scrollArea)

        self.pumpSelectWidget = QTableWidget(pumpSelectTab)
        self.pumpSelectWidget.setObjectName(u"pumpSelectWidget" + str(index))
        self.pumpSelectWidget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)

        self.verticalLayout.addWidget(self.pumpSelectWidget)


        self.retranslateUi(pumpSelectTab)

        QMetaObject.connectSlotsByName(pumpSelectTab)
    # setupUi

    def retranslateUi(self, pumpSelectTab):
        pumpSelectTab.setWindowTitle(QCoreApplication.translate("pumpSelectTab", u"Form", None))
        self.salesLabel.setText(QCoreApplication.translate("pumpSelectTab", u"\u5339\u914d\u7684\u6cf5\u6570\u636e", None))
        self.selectLabel.setText(QCoreApplication.translate("pumpSelectTab", u"\u8bf7\u9009\u62e9", None))
    # retranslateUi

