import pymupdf
from pymupdf.utils import getColor
import traceback

from ..matched_arg import ArgEntry, MatchedArg, PumpInfoArg
from ..const_def import SITE_CHAR
from .basic import get_real_page_num_default, get_real_page_num_by_header, text_to_num, text_to_num_by_fac

class BasicFileStyle:
    def __init__(self) -> None:
        self._matchers = [[],[],[],[]]
        self._locators = []

        # 由于一个文件中会有多个泵，该表需要支持重置
        self._matcher_q = []
        # 用于定位写回数据的队列
        self._loc_q = []
        self._section = None
        self._skip_step = 0

        self._font_size = None
        self._h_pos = None
        self._v_pos = None
        self._color = None

        self._page_num = None

    def parse_arg(self, args: list):
        result = []
        for arg in args:
            if isinstance(arg, list):
                arg_set = set(arg)
                result.append(arg_set)
            else:
                result.append(arg)
        return result

    def set_matcher(self, index: tuple, conf:dict|None):
        if conf is None:
            self._matchers[index[0]].append(None)
            return
        
        if conf["type"] == "list":
            post_arg = conf.get("post")
            post_ls = []
            if post_arg is not None:
                post_ls = self.parse_arg(post_arg)
            self._matchers[index[0]].append(
                lambda row, args: self.match_list(self.parse_arg(conf["pre"]), post_ls, row, args, conf.get("to_join", 0), conf.get("skip", True))
            )
        elif conf["type"] == "change":
            hd_c = conf["handler"]
            hd = None
            if hd_c["type"] == "factor":
                hd = lambda x: text_to_num_by_fac(x, hd_c["arg"])
            else:
                raise NotImplementedError
            self._matchers[index[0]].append(
                lambda row, args: self.match_and_change(self.parse_arg(conf["pre"]), hd, row, args)
            )
        elif conf["type"] == "header":
            self._matchers[index[0]].append(
                lambda row, args: self.match_header_and_join(self.parse_arg(conf["pre"]), row, args, conf.get("to_join", 0), conf.get("skip", True))
            )
        else:
            raise NotImplementedError

    def set_locator(self, index:int, conf:dict|None):
        if conf is None:
            self._locators.append(None)
            return

        self._locators.append(
            lambda page, row, args: self.write_pos(self.parse_arg(conf["pre"]), conf["offset"], page, row, args, conf.get("skip", True), conf.get("is_cn", False), conf.get("dir", 0))
        )

    def setup(self, conf: dict):
        self._page_num = conf["page_num"]
        ex_conf = conf["extract"]
        for i, group in enumerate(ex_conf["matchers"]):
            for j, matcher in enumerate(group):
                self.set_matcher((i,j), matcher)
        wb_conf = conf["writeback"]
        for i, locator in enumerate(wb_conf["matchers"]):
            self.set_locator(i, locator)
        self._font_size = wb_conf["font_size"]
        self._h_pos = wb_conf["h_pos"]
        self._v_pos = wb_conf["v_pos"]
        self._font_color = getColor(wb_conf["font_color"])

    def _skip_cite(self, next_pos:int, words: list):
        if words[next_pos][4] in SITE_CHAR:
            self._skip_step += 1
            return next_pos + 1
        return next_pos
    
    def write_pos(self, prefix: list, offset: int, page: pymupdf.Page, words: list, arg: ArgEntry, skip = True, china=False, dir=0):
        #dir为方向，0为平行，1为垂直
        p_len = len(prefix)
        w_len = len(words)
        if p_len > w_len:
            return None
        
        word = None
        for i, to_check in enumerate(prefix):
            if to_check is None:
                continue
            word = words[i]
            text = word[4]

            if text[-1] in SITE_CHAR:
                text = text[0:-1]

            if text != to_check:
                return None
            
            if text == "吸入口":
                pass
        
        if word is None:
            return None
        ### pymupdf以topleft为起始点，word返回矩形的对角两点坐标，即依次为左，上，右，下
        if dir == 0:
            loc = (word[2]+offset, (word[1] + word[3]) / 2 + self._v_pos)
        else:
            loc = ((word[0] + word[2]) / 2 - self._h_pos, word[3] + offset)

        p = pymupdf.Point(loc[0], loc[1])
        if china:
            page.insert_text(p, str(arg.value), fontname="china-s", fontsize=self._font_size, color=self._font_color)
        else:
            to_write = arg.value
            if arg.unit is not None:
                to_write = round(to_write, 3)
            page.insert_text(p, str(to_write), fontsize=self._font_size, color=self._font_color)

        if skip:
            self._skip_step += p_len - 1
            return 1

        return 0
    
    def match_header_and_join(self, prefix: list, words: list, arg: ArgEntry, to_join = 0, skip=True):
        p_len = len(prefix)
        w_len = len(words)
        if p_len > w_len:
            return None
        
        text_len = 0
        for i, to_check in enumerate(prefix):
            if to_check is None:
                continue
            # information items will be found prefixed with their "key"
            word = words[i]
            text = word[4]

            text_len = len(to_check)
            if len(text) < text_len:
                return None
            
            if text[0:text_len] != to_check:
                return None

        val_t = words[p_len-1][4][text_len:]
        total = to_join
        while to_join > 0:
            val_t += words[p_len + total - to_join][4]
            to_join -= 1

        if arg.unit is not None:
            value = text_to_num(val_t)
            if value is None:
                return None
            arg.set_value(value)
        else:
            arg.set_value(val_t)

        if skip:
            self._skip_step += p_len - 1
            return 1
        
        return 0

    def match_list(self, prefix: list, postfix: list, words: list, arg: ArgEntry, to_join = 0, skip=True):
        p_len = len(prefix)
        post_len = len(postfix)
        w_len = len(words)
        if p_len + post_len > w_len:
            return None
        
        for i, to_check in enumerate(prefix):
            if to_check is None:
                continue
            # information items will be found prefixed with their "key"
            word = words[i]
            text = word[4]
            if text[-1] in SITE_CHAR:
                text = text[0:-1]

            if isinstance(to_check, set):
                if text not in to_check:
                    return None
            else:
                if text != to_check:
                    return None
        
        for j, to_check_j in enumerate(postfix):
            if to_check_j is None:
                continue

            word = words[p_len + 1 + j]
            text = word[4]
            if text[-1] in SITE_CHAR:
                text = text[0:-1]

            if len(text) == 0:
                continue

            if isinstance(to_check_j, set):
                if text not in to_check_j:
                    return None
            else:
                if text != to_check_j:
                    return None

        val_t = words[p_len][4]
        total = to_join
        while to_join > 0:
            val_t += words[p_len + 1 + total - to_join][4]
            to_join -= 1

        if arg.unit is not None:
            value = text_to_num(val_t)
            if value is None:
                return None
            arg.set_value(value)
        else:
            arg.set_value(val_t)

        if skip:
            self._skip_step += p_len - 1
            return 1
        return 0

    def match_and_change(self, prefix: list, handler, words: list, arg: ArgEntry):
        p_len = len(prefix)
        w_len = len(words)

        if p_len > w_len:
            return None

        for i, to_check in enumerate(prefix):
            if to_check is None:
                continue
            # information items will be found prefixed with their "key"
            word = words[i]
            text = word[4]
            if text[-1] in SITE_CHAR:
                text = text[0:-1]

            if isinstance(to_check, set):
                if text not in to_check:
                    return None
            else:
                if text != to_check:
                    return None
        
        value = handler(words[p_len][4])
        if value is None:
            return None
        arg.set_value(value)
        return 1

    def reset_queue(self):
        self._section = None
        self._matcher_q.clear()
        self._loc_q.clear()
        for i, group in enumerate(self._matchers):
            for j, matcher in enumerate(group):
                if matcher is not None:
                    self._matcher_q.append(((i, j), matcher))

        for m, locator in enumerate(self._locators):
            if locator is not None:
                self._loc_q.append((m, locator))

    def search(self, words: list, args: MatchedArg):
        to_pop = []
        self._skip_step = 0
        max_len = len(words)
        for i, _ in enumerate(words):
            if self._skip_step > 0:
                self._skip_step -= 1
                continue
            if i > max_len - 1:
                continue
            for j, matcher in enumerate(self._matcher_q):
                arg = args.get_arg(matcher[0][0], matcher[0][1])
                result = matcher[1](words[i:], arg)
                if result is not None:
                    to_pop.append(j)
                    args.add_found((matcher[0][0], matcher[0][1]))
                    if result > 0:
                        # 当前位置只有一个匹配
                        break

        to_pop.sort(reverse=True)
        for m in to_pop:
            self._matcher_q.pop(m)

    def parse_page(self, page: pymupdf.Page):
        if self._page_num == "default":
            return get_real_page_num_default(page)
        elif self._page_num == "header":
            return get_real_page_num_by_header(page)
        else:
            raise NotImplementedError

    def parse(self, page: pymupdf.Page, result: list):
        try:
            args = None
            if len(result) > 0:
                args = result[-1]
            page_no = self.parse_page(page)
            if page_no == 1:
                args = MatchedArg()
                result.append(args)
                self.reset_queue()
                if self._page_num == "default":
                    #该格式跳过第一页
                    return None
                
            if len(self._matcher_q) == 0:
                return None
            words = page.get_text("words", sort=False)
            self.search(words, args)
            return result
        except Exception:
            traceback.print_exc() 
            return None
    
    def locate(self, page: pymupdf.Page, words: list, args: PumpInfoArg):
        found = []
        self._skip_step = 0
        for i, _ in enumerate(words):
            if self._skip_step > 0:
                self._skip_step -= 1
                continue
            for j, locator in enumerate(self._loc_q):
                arg = args.get_arg(locator[0])
                if arg.value is None:
                    continue
                result = locator[1](page, words[i:], arg)
                if result is not None:
                    found.append(j)
                    args.writen_args.append(locator[0])
                    if result > 0:
                        break

        found.sort(reverse=True)
        for j in found:
            self._loc_q.pop(j)
        
    def writeback(self, page: pymupdf.Page, result: list[PumpInfoArg]):
        try:
            args = None
            if len(result) == 0:
                return "无可写回数据"
            page_no = self.parse_page(page)
            if page_no == 1:
                args = result.pop()
                result.insert(0, args)
                self.reset_queue()
                if self._page_num == "default":
                    #该格式跳过第一页
                    return None
            else:
                args = result[0]
            if len(self._loc_q) == 0:
                return None
            words = page.get_text("words", sort=False)
            self.locate(page, words, args)
            return result
        except Exception:
            traceback.print_exc() 
            return None