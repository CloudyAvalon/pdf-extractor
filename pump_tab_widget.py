from ui_pumpselectortab import Ui_pumpSelectTab

from PySide6.QtWidgets import (QWidget, QTableWidgetItem, QRadioButton, QButtonGroup)
from PySide6.QtCore import Slot

from table_maker.matched_arg import MatchedArg, PumpInfoGroup

class QPumpSelector(QWidget):
    def __init__(self, index, parent):
        super(QPumpSelector, self).__init__(parent)
        self.ui = Ui_pumpSelectTab()
        self.ui.setupUi(self, index)

        self._group = QButtonGroup(self.ui.selectPumpArea)

    def get_selected(self):
        return self._group.checkedId()

    @Slot()
    def prepare(self):
        self.ui.sourceInfoView.setColumnCount(3)
        self.ui.sourceInfoView.setHorizontalHeaderLabels(["参数", "值", "单位"])
        
    @Slot()
    def show_data(self, data: MatchedArg, pump_info: PumpInfoGroup):
        src_table = self.ui.sourceInfoView
        src_table.clearContents()

        src_args = []
        src_args.extend(data.id_info)
        src_args.extend(data.flow_and_lift)
        src_table.setRowCount(len(src_args))
        for i, entry in enumerate(src_args):
            item_name = QTableWidgetItem(entry.name)
            item_unit = QTableWidgetItem(entry.unit)
            item_value = None
            if entry.value is None:
                    item_value = QTableWidgetItem("")
            else:
                item_value = QTableWidgetItem(str(entry.value))
            src_table.setItem(i, 0, item_name)
            src_table.setItem(i, 1, item_value)
            src_table.setItem(i, 2, item_unit)

        pump_table = self.ui.pumpSelectWidget
        pump_table.clear()

        pumps = pump_info.pumps
        if len(pumps) == 0:
            return
        
        pump_table.setRowCount(len(pumps[0].args))
        header = [arg.get_title() for arg in pumps[0].args]
        pump_table.setVerticalHeaderLabels(header)
        pump_table.setColumnCount(len(pumps))

        selectArea = self.ui.selectPumpArea
        for button in self._group.buttons():
            selectArea.layout().removeWidget(button)
            self._group.removeButton(button)
            button.deleteLater()

        for i, pump in enumerate(pumps):
            id_text = i+1
            button = QRadioButton(str(id_text), selectArea)
            self._group.addButton(button, i)
            selectArea.layout().addWidget(button)

            for j, arg in enumerate(pump.args):
                item_value = None
                if arg.value is None:
                    item_value = QTableWidgetItem("")
                else:
                    item_value = QTableWidgetItem(str(arg.value))
                pump_table.setItem(j, i, item_value)

        src_table.show()
        self.ui.scrollArea.show()
        pump_table.show()