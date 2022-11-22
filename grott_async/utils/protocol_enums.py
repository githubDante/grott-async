import enum


class Fault1(int, enum.Enum):

    Error_100 = 1
    Error_101 = 2
    Error_102 = 3
    Error_103 = 4
    Error_104 = 5
    Error_105 = 6
    Error_106 = 7
    Error_107 = 8
    Error_108 = 9
    Error_109 = 10
    Error_110 = 11
    Error_111 = 12
    Error_112 = 13
    Error_113 = 14
    Error_114 = 15
    Error_115 = 16
    Error_116 = 17
    Error_117 = 18
    Error_118 = 19
    Error_119 = 20
    Error_120 = 21
    Error_121 = 22
    Error_123 = 23
    Auto_Test_Failed = 24
    No_AC_Connection = 25
    PV_Isolation_Low = 26
    Residual_I_High  = 27
    Output_High_DCI  = 28
    PV_Voltage_High  = 29
    AC_Voltage_Out_of_Range = 30
    AC_Frequency_Out_of_Range = 31
    Module_Too_Hot = 32
    # Custom error
    Error_Undocummented = 0

    @classmethod
    def _missing_(cls, value: object):
        return Fault1.Error_Undocummented


class Fault8(int, enum.Enum):

    Communication_Error         = 0x00000002  # 2
    StrReverse_or_StrShortage   = 0x00000008  # 8
    Model_Init_Fault            = 0x00000010  # 16
    Grid_Voltage_Sample_Diff    = 0x00000020  # 32
    ISO_Sample_Diff             = 0x00000040  # 64
    GFCI_Sample_Diff            = 0x00000080  # 128
    AFCI_Fault                  = 0x00001000  # 4096
    AFCI_Module_Fault           = 0x00004000  # etc ...
    RelayCheck_Fault            = 0x00020000
    Communication_Error2        = 0x00200000
    BusVoltage_Error            = 0x00400000
    AutoTest_Failure            = 0x00800000
    No_Utility                  = 0x01000000
    PV_Isolation_low            = 0x02000000
    Residual_I_High             = 0x04000000
    Output_DCI_High             = 0x08000000
    PV_Voltage_High             = 0x10000000
    AC_Voltage_OutRange         = 0x20000000
    AC_Frequency_OutRange       = 0x40000000
    High_Temperature            = 0x80000000

    # Custom
    Undocumented                = 0xdeadbeaf

    @classmethod
    def _missing_(cls, value: object):
        return Fault8.Undocumented
