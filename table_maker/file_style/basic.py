import pymupdf

def text_to_num(src: str):
    if not src.replace(".", "1").isdigit():
        return None
    return float(src)

def text_to_num_by_fac(src: str,  fac: float):
    if not src.replace(".", "1").isdigit():
        return None
    return float(src) * fac

def get_real_page_num_default(page: pymupdf.Page):
    words = page.get_text("words", sort=False)
    for i, word in enumerate(words):
        text = word[4]
        if text == "第":
            checkpoint = words[i+2][4]
            if checkpoint[0] in {"张", "页"}:
                return int(words[i+1][4])
    return None

def get_real_page_num_by_header(page: pymupdf.Page):
    words = page.get_text("words", sort=False)
    for i, word in enumerate(words):
        text = word[4]
        if text[0:2] == "页码":
            if text[2] in {"：", ":"}:
                if len(text) > 3:
                    return int(text[3])
                else:
                    return int(words[i+1][4][0])
    return None

class TableContext():
    def __init__(self) -> None:
        self._section = None
        self._name_id = None
        self._unit_id = None
        # 最大，额定，正常，最小
        self._minmax_id = None

    @property
    def section(self):
        return self._section
    @section.setter
    def section(self, section: str):
        self._section = section
        self._name_id = None
        self._unit_id = None
        self._minmax_id = None
    
    @property
    def name(self):
        return self._name_id
    @name.setter
    def name(self, name: int):
        self._name_id = name

    @property
    def unit(self):
        return self._unit_id
    @unit.setter
    def unit(self, unit: int):
        self._unit_id = unit

    @property
    def index(self):
        return self._minmax_id
    @index.setter
    def index(self, index: tuple):
        self._minmax_id = index
