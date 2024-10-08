from .const_def import ArgType, CommonArgDef, MediumArgDef, SalesPumpInfo

_COMMON_NAME_UNITS = [("设备位号", None), ("设备名称", None), ("设备数量", None), ("工程/项目/装置", None),
               ("用户",None), ("设计方", None), ("制造厂", None), ("日期", None)]
_MEDIUM_NAME_UNITS = [("名称",None),("最小温度","℃"),("正常温度","℃"),("额定温度","℃"),("最大温度","℃"),("密度","kg/m³"),("粘度", "mPa.s"),
                      ("最小入口压力", "MPaG"),("正常入口压力", "MPaG"), ("额定入口压力", "MPaG"),("最大入口压力", "MPaG"),
                      ("最小出口压力", "MPaG"),("正常出口压力", "MPaG"),("额定出口压力", "MPaG"),("最大出口压力", "MPaG"),
                      ("最小流量","m³/h"), ("正常流量","m³/h"), ("额定流量","m³/h"), ("最大流量","m³/h"), ("扬程","m"), ("NPSHA", "m")]
_PUMP_NAME_UNITS = [("NPSHR", "m"), ("型号", None), ("型式", None), ("材质", None), ("流量","m³/h"),
                    ("扬程","m"), ("效率","%"), ("轴功率", "kW"), ("密封分类编码", None), ("密封冲洗方案", None), ("冷却水管路", None)]
_ENGINE_NAME_UNITS = [("型号", None), ("功率","kW"), ("防爆/防护等级",None), ("电压/频率/相",None)]

_SALES_NAME_UNITS = [
    ("序号", None), ("计划号", None), ("序号2", None), ("型号", None), ("原型号", None), 
    ("流量","m³/h"), ("扬程","m"), ("效率","%"), ("汽蚀", "m"), ("转速", None), ("泵型式", None), ("泵标牌", None), ("电机制造厂", None),
    ("泵体材料", None), ("叶轮材料", None), ("轴材料", None), ("泵体口环材料", None), ("叶轮口环材料", None), ("导叶材料", None), ("材料级数", None), 
    ("RPM(转速)", None), ("额定叶轮直径", None), ("最大叶轮直径", None), ("最小叶轮直径", None), ("轴功率","kW"), ("泵效率","%"),
    ("最佳效率点流量","m³/h"), ("优先工作区起值","m³/h"), ("优先工作区止值","m³/h"), ("允许工作区起值","m³/h"), ("允许工作区止值","m³/h"), 
    ("额定叶轮的最大扬程", "m"), ("额定叶轮的最大功率", "kW"), ("额定流量下的NPSH3", "m"), ("比转速", "ns(美制)"), ("气蚀比转速", "加仑/分钟(美制)"),
    ("吸入口", None), ("排出口", None), ("排液口", None), ("壳体型式", None), 
    ("壳体承压等级MAWP压力", "MPaG"), ("壳体承压等级MAWP温度", "℃"), ("壳体承压等级水压试验压力", "MPaG"), ("壳体承压等级水压试验温度", "℃"),
    ("转向:(从联轴器端看)", None), ("制造厂", None), ("中节长", None), ("径向轴承型式", None), ("径向轴承数量", None), ("径向轴承型号", None),
    ("推力轴承型式", None), ("推力轴承数量", None), ("推力轴承型号", None), ("润滑油粘度的ISO等级号", None), ("轴承箱冷却水","m³/h"), ("换热器冷却水","m³/h"), ("总冷却水","m³/h"),
    ("泵重量","kg"), ("驱动机重量","kg"), ("底座重量","kg"), ("总重","kg"), ("曲线号", None), ("安装尺寸图号", None)
]

class ArgEntry():
    def __init__(self, index:tuple, name:str, unit:str) -> None:
        self._index = index
        self._name = name
        self._unit = unit
        self._value = None
        self._location = None

    @property
    def index(self):
        return self._index
    
    @property
    def name(self):
        return self._name

    @property
    def unit(self):
        return self._unit

    @property
    def value(self):
        return self._value
    
    @property
    def location(self):
        return self._location
    @location.setter
    def location(self, value):
        self.location = value

    def set_value(self, value):
        self._value = value

    def to_tuple(self):
        return (self._name, self._unit, self._value)
    
    def get_title(self):
        if self._unit is None:
            return self.name
        else:
            return f"{self.name}({self._unit})"

class MatchedArg():
    def __init__(self) -> None:
        self._all_args = [
            [ArgEntry((ArgType.Common.value,i), item[0], item[1]) for i, item in enumerate(_COMMON_NAME_UNITS)], 
            [ArgEntry((ArgType.Medium.value,i), "介质" + item[0], item[1]) for i, item in enumerate(_MEDIUM_NAME_UNITS)], 
            [ArgEntry((ArgType.Pump.value,i), "泵" + item[0], item[1]) for i, item in enumerate(_PUMP_NAME_UNITS)], 
            [ArgEntry((ArgType.Engine.value,i), "引擎" + item[0], item[1]) for i, item in enumerate(_ENGINE_NAME_UNITS)]
        ]
        self._found_args = []

    @property
    def found_args(self):
        return self._found_args

    def get_arg(self, argtype, index) -> ArgEntry:
        return self._all_args[argtype][index]

    def add_found(self, index: tuple):
        self._found_args.append(index)

    @property
    def id_info(self):
        return (self._all_args[ArgType.Common.value][CommonArgDef.DevTagNo.value],
                self._all_args[ArgType.Common.value][CommonArgDef.DevName.value],
                self._all_args[ArgType.Common.value][CommonArgDef.DevCount.value],
                self._all_args[ArgType.Common.value][CommonArgDef.ProjectName.value],
                self._all_args[ArgType.Common.value][CommonArgDef.UserName.value],
                self._all_args[ArgType.Medium.value][MediumArgDef.MediumName.value])

    @property
    def flow_and_lift(self):
        return (self._all_args[ArgType.Medium.value][MediumArgDef.MinFlow.value],
                self._all_args[ArgType.Medium.value][MediumArgDef.NormalFlow.value],
                self._all_args[ArgType.Medium.value][MediumArgDef.RatedFlow.value],
                self._all_args[ArgType.Medium.value][MediumArgDef.MaxFlow.value],
                self._all_args[ArgType.Medium.value][MediumArgDef.Lift.value])

    def get_flow_and_lift_val(self) -> tuple:
        flow_val = None
        rated_src = self._all_args[ArgType.Medium.value][MediumArgDef.RatedFlow.value]
        normal_src = self._all_args[ArgType.Medium.value][MediumArgDef.NormalFlow.value]
        
        rated_val = None
        normal_val = None
        if rated_src is not None and rated_src.value is not None:
            rated_val = float(rated_src.value)
        if normal_src is not None and normal_src.value is not None:
            normal_val = float(normal_src.value)
        
        if rated_val is not None or normal_val is not None:
            flow_val = max(rated_val if rated_val is not None else 0, normal_val if normal_val is not None else 0)

        lift_val = None
        lift = self._all_args[ArgType.Medium.value][MediumArgDef.Lift.value]
        if lift is not None and lift.value is not None:
            lift_val = float(lift.value)
        return (flow_val, lift_val)

    @property
    def display_list(self) -> list:
        #[(name1, unit1, value1), (name2, unit2, value2)]
        return [self.get_arg(arg[0], arg[1]).to_tuple() for arg in self._found_args]

class PumpInfoArg():
    def __init__(self) -> None:
        self._pumps = [ArgEntry((ArgType.Sales.value,i), item[0], item[1]) for i, item in enumerate(_SALES_NAME_UNITS)]
        self._writen_args = []
    
    @property
    def writen_args(self):
        return self._writen_args
    
    @property
    def args(self):
        return self._pumps

    @property
    def flow_and_lift(self):
        return (self._pumps[SalesPumpInfo.Flow.value],
                self._pumps[SalesPumpInfo.Lift.value])
    
    def get_arg(self, index) -> ArgEntry:
        return self._pumps[index]
    
    @property
    def display_list(self) -> list:
        #[(name1, unit1, value1), (name2, unit2, value2)]
        return [self.get_arg(i).to_tuple() for i in self._writen_args]

class PumpInfoGroup():
    def __init__(self, src_id: int) -> None:
        self._src_id = src_id
        self._pumps = []
        self._selected = -1

    @property
    def selected(self):
        return self._selected
    @selected.setter
    def selected(self, value):
        self._selected = value
        
    @property
    def pumps(self) -> list[PumpInfoArg]:
        return self._pumps

    def add_pump(self) -> PumpInfoArg:
        new_pump = PumpInfoArg()
        self._pumps.append(new_pump)
        return new_pump
    
    def reset(self):
        self._pumps.clear()

    @property
    def src_id(self):
        return self._src_id