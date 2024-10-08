from enum import Enum, auto

SITE_CHAR={":", "："}

class ArgType(Enum):
    Common = 0
    Medium = 1
    Pump = 2
    Engine = 3
    Sales = 4

class CommonArgDef(Enum):
    DevTagNo = 0
    DevName = 1
    DevCount = 2
    ProjectName = 3
    UserName = 4
    DesignerName = 5
    FactoryName = 6
    Date = 7

class MediumArgDef(Enum):
    MediumName = 0
    MinTemperature = 1
    NormalTemperature = 2
    RatedTemperature = 3
    MaxTemperature = 4
    Density = 5
    Viscosity = 6
    MinInPressure = 7
    NormalInPressure = 8
    RatedInPressure = 9
    MaxInPressure = 10
    MinOutPressure = 11
    NormalOutPressure = 12
    RatedOutPressure = 13
    MaxOutPressure = 14
    MinFlow = 15
    NormalFlow = 16
    RatedFlow = 17
    MaxFlow = 18
    Lift = 19
    NPSHA = 20

class PumpArgDef(Enum):
    NPSHR = 0
    Prototype = 1
    PumpType = 2
    Material = 3
    Flow = 4
    Lift = 5
    Efficience = 6
    AxisPower = 7
    SealClassNo = 8
    SealFlushPlan = 9
    CoolingWaterPipe = 10

class EngineArgDef(Enum):
    Prototype = 0
    Power = 1
    ProtectClass = 2
    ElectricityUFP = 3

class SalesPumpInfo(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return start + count - 1
    
    Num = auto()
    PlanNum = auto()
    RawNum = auto()
    Prototype = auto()
    OriginPrototype = auto()
    Flow = auto()
    Lift = auto()
    Efficience = auto()
    Cavitation = auto()
    RSpeed = auto()
    #10
    PumpType = auto()
    PumpTag = auto()
    EngineFactory = auto()
    MatOfPump = auto()
    MatOfWheel = auto()
    MatOfAxis = auto()
    MatOfPumpRing = auto()
    MatOfWheelRing = auto()
    MatOfGuideVane = auto()
    MatOfSeries = auto()
    #20
    RPM = auto()
    RatedWheelSize = auto()
    MaxWheelSize = auto()
    MinWheelSize = auto()
    AxisEff = auto()
    ArgOfEfficience = auto()
    BestEffFlow = auto()
    BestWorkRange0 = auto()
    BestWorkRange1 = auto()
    AllowWorkRange0 = auto()
    #30
    AllowWorkRange1 = auto()
    MaxLift = auto()
    MaxPower = auto()
    NPSH3 = auto()
    RatioSpeed = auto()
    CavRSpeed = auto()
    Input = auto()
    Output = auto()
    LiquidExit = auto()
    ShellType = auto()
    #40
    ShellPressMAWP = auto()
    ShellPressMAWPT = auto()
    ShellPressTest = auto()
    ShellPressTestT = auto()
    ShellRotation = auto()
    AxisFac = auto()
    AxisLen = auto()
    RadialBearType = auto()
    RadialBearCnt = auto()
    RadialBear = auto()
    #50
    PushBearType = auto()
    PushBearCount = auto()
    PushBear = auto()
    LubOil = auto()
    CoolBear = auto()
    CoolChanger = auto()
    Cooler = auto()
    WeightPump = auto()
    WeightEngine = auto()
    WeightBottom = auto()
    #60
    Weight = auto()
    CurveTagNo = auto()
    InstallSizeTagNo = auto()