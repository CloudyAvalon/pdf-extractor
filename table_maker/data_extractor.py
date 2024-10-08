
import pymupdf
import traceback
import json
from .file_style import CNPC1, default, Sinopec1, base_matcher

class DataExtractor():
    def __init__(self) -> None:
        self._pattern_f = {
        }
        self._pump_setting = {}
        self._display_list = []

    @property
    def display_list(self):
        return self._display_list
    
    @property
    def pump_setting(self) -> tuple:
        return self._pump_setting

    def load_conf(self, file:str):
        #temp_list = [default.DefaultFileStyle(), CNPC1.CNPC1FileStyle(), Sinopec1.Sinopec1FileStyle()]
        conf = open(file, encoding="utf-8")
        try:
            self._display_list.clear()
            styles = json.load(conf)
            self._pump_setting["flow_gap"] = styles["pump"]["flow_gap"]
            self._pump_setting["lift_gap"] = styles["pump"]["lift_gap"]
            for i, style in enumerate(styles["styles"]):
                parser = base_matcher.BasicFileStyle()
                parser.setup(style["settings"])
                self._pattern_f[i] = parser
                self._display_list.append(style["name"])
            return None
        except:
            traceback.print_exc() 
            return "json格式错误"
        finally:
            conf.close()

    def writeback(self, src_file:str, filepath: str, pattern: int, data: list):
        try:
            matcher = self._pattern_f.get(pattern)
            if matcher is None:
                return None
            pdf_doc = pymupdf.open(src_file)
            data.reverse()
            temp_data = []
            temp_data.extend(data)
            for page in pdf_doc:
                matcher.writeback(page, temp_data)
            pdf_doc.save(filepath)
            pdf_doc.close()
            return None
        except Exception:
            traceback.print_exc() 
            return "写回失败"

    def extract(self, filepath: str, pattern: int):
        try:
            matcher = self._pattern_f.get(pattern)
            if matcher is None:
                return None
            result = []
            pdf_doc = pymupdf.open(filepath)
            for page in pdf_doc:
                matcher.parse(page, result)
            pdf_doc.close()
            return result
        except Exception:
            traceback.print_exc() 
            return None