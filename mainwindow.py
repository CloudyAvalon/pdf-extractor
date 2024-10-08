# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import math
import sys

from PySide6.QtPdf import QPdfBookmarkModel, QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import (QDialog, QFileDialog, QMainWindow, QMessageBox,
                               QSpinBox, QTableWidgetItem, QWidget)
from PySide6.QtCore import QModelIndex, QPoint, QStandardPaths, QUrl, Slot, Signal

from zoomselector import ZoomSelector
from file_style_selector import FileStyleSelector
from ui_mainwindow import Ui_MainWindow
from pump_tab_widget import QPumpSelector
from table_maker.data_extractor import DataExtractor
from table_maker.mstable_writer import MSTableWriter
from table_maker.pump_selector import PumpSelector
from table_maker.matched_arg import PumpInfoGroup

ZOOM_MULTIPLIER = math.sqrt(2.0)
MAX_PUMP_TABS = 8

class StandaloneSignals(QWidget):
    show_selected_pumps = Signal()
    reload_config = Signal(list)
    def __init__(self, parent) -> None:
        super(StandaloneSignals, self).__init__(parent)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._signals = StandaloneSignals(self)
        self.m_fileStyle = 0
        self.ui = Ui_MainWindow()
        self.m_zoomSelector = ZoomSelector(self)
        self.m_fileStyleSelector = FileStyleSelector(self)
        self.m_pageSelector = QSpinBox(self)
        self.m_document = QPdfDocument(self)
        self.m_filePath = None
        self.m_fileDialog = None
        self.m_tableDialog = None
        self.m_listTableDialog = None
        self.m_salesDialog = None
        self.m_loadDialog = None
        self.m_writePdfDialog = None
        self.m_readConfDialog = None
        self.m_confReady = False

        # 数据缓存对象
        self.m_extractedData = None
        self.m_dataExtractor = DataExtractor()
        self.m_tableWriter = MSTableWriter()
        self.m_pumpSelector = PumpSelector()
        self.m_pumpTabSource = []
        self.m_pumpTabs = []
        self.m_pumps = None

        #写回数据表的数据
        self.m_toWrite = None

        self.ui.setupUi(self)

        self.m_fileStyleSelector.setMaximumWidth(250)
        self.ui.mainToolBar.insertWidget(self.ui.actionOpen, self.m_fileStyleSelector)

        self.m_zoomSelector.setMaximumWidth(150)
        self.ui.mainToolBar.insertWidget(self.ui.actionZoom_In, self.m_zoomSelector)

        self.ui.mainToolBar.insertWidget(self.ui.actionForward, self.m_pageSelector)
        self.m_pageSelector.valueChanged.connect(self.page_selected)
        nav = self.ui.pdfView.pageNavigator()
        nav.currentPageChanged.connect(self.m_pageSelector.setValue)
        nav.backAvailableChanged.connect(self.ui.actionBack.setEnabled)
        nav.forwardAvailableChanged.connect(self.ui.actionForward.setEnabled)

        self.m_zoomSelector.zoom_mode_changed.connect(self.ui.pdfView.setZoomMode)
        self.m_zoomSelector.zoom_factor_changed.connect(self.ui.pdfView.setZoomFactor)
        self.m_zoomSelector.reset()

        self.m_fileStyleSelector.file_style_changed.connect(self.set_file_style)
        self.m_fileStyleSelector.reset()

        bookmark_model = QPdfBookmarkModel(self)
        bookmark_model.setDocument(self.m_document)

        self.ui.bookmarkView.setModel(bookmark_model)
        self.ui.bookmarkView.activated.connect(self.bookmark_selected)

        self.ui.dataExtractedWidget.setColumnCount(3)
        self.ui.dataExtractedWidget.setHorizontalHeaderLabels(["参数", "值", "单位"])

        self.ui.dataWritenWidget.setColumnCount(3)
        self.ui.dataWritenWidget.setHorizontalHeaderLabels(["参数", "值", "单位"])

        self.ui.pdfView.setDocument(self.m_document)

        self.setup_tabs()
        self._signals.show_selected_pumps.connect(self.show_selected_tabs)
        self._signals.reload_config.connect(self.m_fileStyleSelector.load_conf)

        self.ui.pdfView.zoomFactorChanged.connect(self.m_zoomSelector.set_zoom_factor)

        self.on_actionContinuous_triggered()

    def setup_tabs(self):
        tabWin = self.ui.sourceTabWidget
        for i in range(MAX_PUMP_TABS):
            tab = QPumpSelector(i, tabWin)
            self.m_pumpTabSource.append(tab)
            tabObj = self.m_pumpTabSource[i]
            tabWin.addTab(tabObj, str(i))
            tabWin.setTabVisible(i, False)

    @property
    def pump_tabs(self) -> list[QPumpSelector]:
        return self.m_pumpTabs

    def has_pump_info(self):
        if self.m_pumps is None:
            return False
        result = False
        for i, pump_tab in enumerate(self.pump_tabs):
            selected = pump_tab.get_selected()
            if selected != -1:
                self.m_pumps[i].selected = selected
                result = True
            
        return result

    @property
    def pdf_path(self):
        return self.m_filePath

    def log_error(self, title, message):
        print(message, file=sys.stderr)
        QMessageBox.critical(self, title, message)

    @Slot(int)
    def set_file_style(self, file_style):
        self.m_fileStyle = file_style

    @Slot(QUrl)
    def open(self, doc_location: QUrl):
        if doc_location.isLocalFile():
            self.m_document.load(doc_location.toLocalFile())
            self.m_filePath = doc_location.toLocalFile()
            document_title = doc_location.fileName()
            self.setWindowTitle(document_title if document_title else "数据表处理工具")
            self.page_selected(0)
            self.m_pageSelector.setMaximum(self.m_document.pageCount() - 1)
        else:
            self.log_error("Failed to open", f"{doc_location}不是有效的本地文件")

    @Slot(QUrl)
    def write_mstable(self, doc_location: QUrl):
        #写选型表
        err_msg = None
        if doc_location.isLocalFile():
            table_path = doc_location.toLocalFile()
            if self.has_pump_info():
                err_msg = self.m_tableWriter.write_table(table_path, self.m_extractedData, self.m_pumps)
            else:
                err_msg = self.m_tableWriter.write_table(table_path, self.m_extractedData)
            if err_msg is not None:
                self.log_error("Failed to write", err_msg)
        else:
            self.log_error("Failed to write", f"{doc_location}不是有效的选型表文件")
    
    @Slot(QUrl)
    def write_listTable(self, doc_location: QUrl):
        #写一览表
        err_msg = None
        if doc_location.isLocalFile():
            table_path = doc_location.toLocalFile()
            err_msg = self.m_tableWriter.write_list(table_path, self.m_extractedData, self.m_pumps)
            if err_msg is not None:
                self.log_error("Failed to write", err_msg)
        else:
            self.log_error("Failed to write", f"{doc_location}不是有效的一览表文件")

    @Slot(QUrl)
    def load_sales_table(self, doc_location: QUrl):
        if not self.m_pumpSelector.ready:
            self.log_error("Config not ready", err_msg)
            return

        #读销售表
        if doc_location.isLocalFile():
            table_path = doc_location.toLocalFile()
            self.m_pumps = [PumpInfoGroup(i) for i in range(len(self.m_extractedData))]
            err_msg = self.m_pumpSelector.load_table(table_path, None, self.m_extractedData, self.m_pumps)
            if err_msg is not None:
                self.log_error("Failed to load", err_msg)
                return

            cnt = len(self.m_extractedData)
            if cnt == 0:
                return
            if cnt > MAX_PUMP_TABS:
                self.log_error("Too many results", "提取到的项目太多")
                return

            tabWin = self.ui.sourceTabWidget
            self.m_pumpTabs = self.m_pumpTabSource[0:cnt]

            for i in range(MAX_PUMP_TABS):
                if i < cnt:
                    tabObj = self.pump_tabs[i]
                    tabObj.prepare()
                    tabWin.setTabVisible(i, True)
                else:
                    tabWin.setTabVisible(i, False)
                
            tabWin.setCurrentIndex(0)
            self._signals.show_selected_pumps.emit()
        else:
            self.log_error("Failed to load", f"{doc_location}不是有效的销售数据表文件")

    @Slot(QUrl)
    def load_ms_table(self, doc_location: QUrl):
        #读选型表
        err_msg = None
        if doc_location.isLocalFile():
            table_path = doc_location.toLocalFile()
            self.m_toWrite = []
            err_msg = self.m_tableWriter.read_table(table_path, len(self.m_extractedData), self.m_toWrite)
            if err_msg is not None:
                self.log_error("Failed to load", err_msg)
        else:
            self.log_error("Failed to load", f"{doc_location}不是有效的选型表文件")
    
    @Slot(QUrl)
    def load_style_config(self, doc_location: QUrl):
        if doc_location.isLocalFile():
            conf_path = doc_location.toLocalFile()
            self.m_confReady = False
            err = self.m_dataExtractor.load_conf(conf_path)
            if err is not None:
                self.log_error("Failed to load", err)
                return
            self.m_pumpSelector.setup(self.m_dataExtractor.pump_setting)
            self._signals.reload_config.emit(self.m_dataExtractor.display_list)
            self.m_confReady = True
        else:
            self.log_error("Failed to load", f"{doc_location}不是有效的配置文件")

    @Slot(QUrl)
    def write_data_pdf(self, doc_location: QUrl):
        #写一览表
        err_msg = None
        if doc_location.isLocalFile():
            self.ui.tabWidget.setCurrentIndex(2)
            table = self.ui.dataWritenWidget
            table.clearContents()

            pdf_path = doc_location.toLocalFile()
            err_msg = self.m_dataExtractor.writeback(self.m_filePath, pdf_path, self.m_fileStyle, self.m_toWrite)
            if err_msg is not None:
                self.log_error("Failed to write pdf", err_msg)
                return

            display_list = []
            for item in self.m_toWrite:
                to_add = item.display_list
                if len(to_add) != 0:
                    display_list.extend(to_add)
            table.setRowCount(len(display_list))
            for i, (name, unit, value) in enumerate(display_list):
                item_name = QTableWidgetItem(name)
                table.setItem(i, 0, item_name)
                if value is not None:
                    item_value = QTableWidgetItem(str(value))
                    table.setItem(i, 1, item_value)
                item_unit = QTableWidgetItem(unit)
                table.setItem(i, 2, item_unit)
            table.show()
        else:
            self.log_error("Failed to write pdf", f"{doc_location}不是有效的数据表文件")

    @Slot()
    def show_selected_tabs(self):
        cnt = len(self.m_extractedData)
        for i in range(cnt):
            tabObj = self.pump_tabs[i]
            tabObj.show_data(self.m_extractedData[i], self.m_pumps[i])

    @Slot(QModelIndex)
    def bookmark_selected(self, index):
        if not index.isValid():
            return
        page = index.data(int(QPdfBookmarkModel.Role.Page))
        zoom_level = index.data(int(QPdfBookmarkModel.Role.Level))
        self.ui.pdfView.pageNavigator().jump(page, QPoint(), zoom_level)

    @Slot(int)
    def page_selected(self, page):
        nav = self.ui.pdfView.pageNavigator()
        nav.jump(page, QPoint(), nav.currentZoom())

    @Slot()
    def on_actionOpen_triggered(self):
        if not self.m_fileDialog:
            directory = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            self.m_fileDialog = QFileDialog(self, "Choose a PDF", directory)
            self.m_fileDialog.setAcceptMode(QFileDialog.AcceptOpen)
            self.m_fileDialog.setMimeTypeFilters(["application/pdf"])
        if self.m_fileDialog.exec() == QDialog.Accepted:
            to_open = self.m_fileDialog.selectedUrls()[0]
            if to_open.isValid():
                self.open(to_open)
    
    @Slot()
    def on_actionExtract_Data_triggered(self):
        if not self.m_confReady:
            self.log_error("提取数据失败", f"未读取样式配置！")
            return
        
        if QPdfDocument.Status.Ready != self.m_document.status() or self.m_filePath is None:
            self.log_error("提取数据失败", f"未读取数据表文件！")
            return
        result = self.m_dataExtractor.extract(self.m_filePath, self.m_fileStyle)
        self.m_extractedData = result
        self.m_pumps = None
        self.m_toWrite = None

        if result is None:
            self.log_error("提取数据失败", f"无匹配数据！")
            return
        self.ui.tabWidget.setCurrentIndex(0)
        table = self.ui.dataExtractedWidget
        table.clearContents()
        display_list = []
        for item in result:
            to_add = item.display_list
            if len(to_add) != 0:
                display_list.extend(to_add)
        table.setRowCount(len(display_list))
        for i, (name, unit, value) in enumerate(display_list):
            item_name = QTableWidgetItem(name)
            table.setItem(i, 0, item_name)
            if value is not None:
                item_value = QTableWidgetItem(str(value))
                table.setItem(i, 1, item_value)
            item_unit = QTableWidgetItem(unit)
            table.setItem(i, 2, item_unit)
        table.show()

    @Slot()
    def on_actionWrite_MSTable_triggered(self):
        if self.m_extractedData is None:
            self.log_error("Failed to write", f"未提取到参数")
            return
        
        if not self.m_tableDialog:
            directory = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            self.m_tableDialog = QFileDialog(self, "选择写入表格", directory)
            self.m_tableDialog.setAcceptMode(QFileDialog.AcceptSave)
            self.m_tableDialog.setMimeTypeFilters(["application/xlsx"])
        if self.m_tableDialog.exec() == QDialog.Accepted:
            to_open = self.m_tableDialog.selectedUrls()[0]
            if to_open.isValid():
                self.write_mstable(to_open)

    @Slot()
    def on_actionWrite_ListTable_triggered(self):
        if self.m_extractedData is None:
            self.log_error("Failed to write", f"未提取到参数")
            return
        
        if not self.has_pump_info():
            self.log_error("Failed to write", f"缺少泵数据")
            return
        
        if not self.m_listTableDialog:
            directory = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            self.m_listTableDialog = QFileDialog(self, "选择写入一览表", directory)
            self.m_listTableDialog.setAcceptMode(QFileDialog.AcceptSave)
            self.m_listTableDialog.setMimeTypeFilters(["application/xlsx"])
        if self.m_listTableDialog.exec() == QDialog.Accepted:
            to_open = self.m_listTableDialog.selectedUrls()[0]
            if to_open.isValid():
                self.write_listTable(to_open)

    @Slot()
    def on_actionLoad_SalesTable_triggered(self):
        if self.m_extractedData is None:
            self.log_error("Failed to load", f"未提取到参数")
            return
        
        if not self.m_salesDialog:
            directory = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            self.m_salesDialog = QFileDialog(self, "选择销售数据", directory)
            self.m_salesDialog.setAcceptMode(QFileDialog.AcceptOpen)
            self.m_salesDialog.setMimeTypeFilters(["application/xlsx"])
        if self.m_salesDialog.exec() == QDialog.Accepted:
            to_open = self.m_salesDialog.selectedUrls()[0]
            self.ui.tabWidget.setCurrentIndex(1)
            if to_open.isValid():
                self.load_sales_table(to_open)

    @Slot()
    def on_actionLoad_MSTable_triggered(self):
        if self.m_extractedData is None:
            self.log_error("Failed to load", f"未提取到参数, 无法判断应读取行数")
            return

        if not self.m_loadDialog:
            directory = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            self.m_loadDialog = QFileDialog(self, "选择设备选型表", directory)
            self.m_loadDialog.setAcceptMode(QFileDialog.AcceptOpen)
            self.m_loadDialog.setMimeTypeFilters(["application/xlsx"])
        if self.m_loadDialog.exec() == QDialog.Accepted:
            to_open = self.m_loadDialog.selectedUrls()[0]
            if to_open.isValid():
                self.load_ms_table(to_open)
    
    @Slot()
    def on_actionWrite_DataPdf_triggered(self):
        if self.m_toWrite is None:
            self.log_error("Failed to write pdf", f"未读取泵数据")
            return

        if not self.m_writePdfDialog:
            directory = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            self.m_writePdfDialog = QFileDialog(self, "Choose PDF to write", directory)
            self.m_writePdfDialog.setAcceptMode(QFileDialog.AcceptSave)
            self.m_writePdfDialog.setMimeTypeFilters(["application/pdf"])
        if self.m_writePdfDialog.exec() == QDialog.Accepted:
            to_open = self.m_writePdfDialog.selectedUrls()[0]
            if to_open.isValid():
                self.write_data_pdf(to_open)
    
    @Slot()
    def on_actionReadStyleConfig_triggered(self):
        if not self.m_readConfDialog:
            directory = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            self.m_readConfDialog = QFileDialog(self, "Choose json config", directory)
            self.m_readConfDialog.setAcceptMode(QFileDialog.AcceptOpen)
            self.m_readConfDialog.setMimeTypeFilters(["application/json"])
        if self.m_readConfDialog.exec() == QDialog.Accepted:
            to_open = self.m_readConfDialog.selectedUrls()[0]
            if to_open.isValid():
                self.load_style_config(to_open)

    @Slot()
    def on_actionQuit_triggered(self):
        self.close()

    @Slot()
    def on_actionAbout_triggered(self):
        QMessageBox.about(self, "About PdfViewer",
                          "An example using QPdfDocument")

    @Slot()
    def on_actionAbout_Qt_triggered(self):
        QMessageBox.aboutQt(self)

    @Slot()
    def on_actionZoom_In_triggered(self):
        factor = self.ui.pdfView.zoomFactor() * ZOOM_MULTIPLIER
        self.ui.pdfView.setZoomFactor(factor)

    @Slot()
    def on_actionZoom_Out_triggered(self):
        factor = self.ui.pdfView.zoomFactor() / ZOOM_MULTIPLIER
        self.ui.pdfView.setZoomFactor(factor)

    @Slot()
    def on_actionPrevious_Page_triggered(self):
        nav = self.ui.pdfView.pageNavigator()
        nav.jump(nav.currentPage() - 1, QPoint(), nav.currentZoom())

    @Slot()
    def on_actionNext_Page_triggered(self):
        nav = self.ui.pdfView.pageNavigator()
        nav.jump(nav.currentPage() + 1, QPoint(), nav.currentZoom())

    @Slot()
    def on_actionContinuous_triggered(self):
        cont_checked = self.ui.actionContinuous.isChecked()
        mode = QPdfView.PageMode.MultiPage if cont_checked else QPdfView.PageMode.SinglePage
        self.ui.pdfView.setPageMode(mode)

    @Slot()
    def on_actionBack_triggered(self):
        self.ui.pdfView.pageNavigator().back()

    @Slot()
    def on_actionForward_triggered(self):
        self.ui.pdfView.pageNavigator().forward()
