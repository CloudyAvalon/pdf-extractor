from openpyxl import load_workbook
import traceback

from .matched_arg import MatchedArg, PumpInfoGroup

_START_ROW = 8
_FLOW_COL_ID = 5
_LIFT_COL_ID = 6

class PumpSelector():
    def __init__(self) -> None:
        self._pos = []
        self._ready = False

    @property
    def ready(self):
        return self._ready

    def setup(self, setting: dict):
        self._ready = True
        self._flow_gap = setting.get("flow_gap", None)
        self._lift_gap = setting.get("lift_gap", None)

    def check_row_to_pump(self, row: tuple, to_check: list[tuple], output: list[PumpInfoGroup]):
        flow = 0
        lift = 0
        try:
            flow = float(row[_FLOW_COL_ID])
            lift = float(row[_LIFT_COL_ID])
        except:
            return

        flow_gap = self._flow_gap
        lift_gap = self._lift_gap

        for i, src in enumerate(to_check):
            flow_src, lift_src = src
            matched = True
            if flow_src is not None:
                matched = flow < flow_src + flow_gap and flow > flow_src - flow_gap
            
            if not matched:
                continue

            if lift_src is not None:
                matched = matched and lift < lift_src + lift_gap and lift > lift_src - lift_gap
            
            if not matched:
                continue

            group = output[i]
            pump_info = group.add_pump()

            for j, cell in enumerate(row):
                if cell is None:
                    continue
                arg = pump_info.get_arg(j)
                if arg is None:
                    continue
                arg.set_value(cell)

    def load_table(self, table_name: str, start_row: int, result: list[MatchedArg], output: list[PumpInfoGroup]):
        err_msg = None
        if start_row is None:
            start_row = _START_ROW
        try:
            wb = load_workbook(table_name, read_only=True, data_only=True)
            ws = wb["总单"]

            to_check = [arg.get_flow_and_lift_val() for arg in result]
            for group in output:
                group.reset()
            for i, row in enumerate(ws.values):
                if i < start_row:
                    continue
                self.check_row_to_pump(row, to_check, output)
                if row[0] is None:
                    break
            
            return err_msg
        except Exception:
            traceback.print_exc() 
            if err_msg is None:
                err_msg = "写入错误，详见堆栈信息"
            return err_msg