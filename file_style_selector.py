# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtWidgets import QComboBox, QMessageBox
from PySide6.QtCore import Signal, Slot
import sys
import traceback

class FileStyleSelector(QComboBox):

    file_style_changed = Signal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._text_idx = None
        self.currentTextChanged.connect(self.on_current_text_changed)
        self.currentIndexChanged.connect(self.file_style_changed)

    @Slot(list)
    def load_conf(self, text_list: list):
        try:
            self.clear()
            self._text_idx = text_list
            for text in self._text_idx:
                self.addItem(text)
        except:
            traceback.print_exc() 

    @Slot(int)
    def set_file_style(self, fileStyle):
        if fileStyle == -1:
            return
        self.setCurrentIndex(fileStyle)

    @Slot()
    def reset(self):
        self.setCurrentIndex(0)  # Default

    @Slot(str)
    def on_current_text_changed(self, text):
        if len(text) == 0:
            return
        
        index = 0
        for basic_text in self._text_idx:
            if text == basic_text:
                self.file_style_changed.emit(index)
                break
            index +=1
        else:
            message = f"{text}不是有效的文件格式"
            print(message, file=sys.stderr)
            QMessageBox.critical(self, "Invalid Value", message)

