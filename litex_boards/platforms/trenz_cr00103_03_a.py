#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 D. Garbe <105213927+garbe-lib@users.noreply.github.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import IOStandard, Misc, Pins, Subsignal
from litex.build.lattice import LatticeNexusPlatform
from litex.build.openfpgaloader import OpenFPGALoader
import re

_io = [
    ("clk12", 0, Pins("B1"), IOStandard("LVCMOS33")),
    
    ("programn", 0, Pins("A2"), IOStandard("LVCMOS33")),
    ("initn", 0, Pins("B2"), IOStandard("LVCMOS33")),
    ("done", 0, Pins("A3"), IOStandard("LVCMOS33")),
    ("user_btn", 0, Pins("A7"), IOStandard("LVCMOS33")),
    ("led", 0, Pins("A8"), IOStandard("LVCMOS33")),
    ("led", 1, Pins("B8"), IOStandard("LVCMOS33")),

    ("spiflash", 0,
        Subsignal("clk", Pins("B3")),
        Subsignal("cs_n", Pins("B4")),
        Subsignal("dq", Pins("A4 A5 A6 B7")),
        IOStandard("LVCMOS33")
    ),

    ("spiflash4x", 0,
        Subsignal("clk", Pins("B3")),
        Subsignal("cs_n", Pins("B4")),
        Subsignal("dq", Pins("A4 A5 A6 B7")),
        IOStandard("LVCMOS33")
    ), 

    ("hyperram", 0,
        Subsignal("dq", Pins("K4 N5 L6 M4 K5 L4 N4 P4"), IOStandard("LVCMOS18H")),
        Subsignal("rwds", Pins("P5"), IOStandard("LVCMOS18H")),
        Subsignal("flash_cs", Pins("N6"), IOStandard("LVCMOS18H")),
        Subsignal("rst_n", Pins("P6"), IOStandard("LVCMOS18H")),
        Subsignal("cs_n", Pins("M7"), IOStandard("LVCMOS18H")),
        Subsignal("clk", Pins("N7"), IOStandard("LVDS")),
        Misc("SLEWRATE=FAST")
    ),

    ("serial", 0,
        Subsignal("tx", Pins("F11")),
        Subsignal("rx", Pins("C11")),
        IOStandard("LVCMOS33")
    ),
        
    ("ftdi_b", 0,
        Subsignal("BDBUS", Pins("C11 F11 D12 F12 C14 D14 E13 E14")),
        Subsignal("BCBUS", Pins("G14 F10 G13 G10 G12")),
        IOStandard("LVCMOS33")
    )
    
]

_connectors = [
    ("LS_CRUVI", "B5 D1 C4 C1 D3 - C3 C2 D2 - - -"),
    ("HS_CRUVI", 
     #   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16    
        "-   L8  E10 -   D11 K10 E11 K9  -   M8  E9  -   -   K11 J14 K12 "
     #   17  18  19  20  21  22  23  24  25  26  27  28  29  30  31  32  
        "J13 -   -   K13 M14 K14 M13 -   -   L13 P11 L14 N11 -   -   M11 "
     #   33  34  35  36  37  38  39  40  41  42  43  44  45  46  47  48
        "P10 L12 XXX N10 -   N13 P9  N14 N9  -   -   P12 P8  P13 N8 -   " 
     #   49  50  51  52  53  54  55  56  57  58  59  60
        "-   -   E5  -   D5  -   F14 -   F13 -   E3  -"),
    ("J4", 
     #   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16
        "-   -   H5  H6  H3  H4  H1  H2  J1  J2  J3  J4  J5  J6  M9  L9 "
     #   17  18  19  20  21  22  23  24  25  26  27  28  29  30  31  32
        "-   -   D13 C10 C13 B10 B12 A10 B14 B9  A12 A9  H12 H13 H11 H14 "
     #   33  34
        "-   -"),
    ("J5", 
     #   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16
        "-   -   G5  G6  G3  G4  F5  F6  G1  G2  F2  F1  E2  E1  K7  K8 "
     #   17  18  19  20  21  22  23  24  25  26  27  28  29  30  31  32
        "-   -   C4  K2  D8  D6  D7  E6  D8  E7  B13 C9  K1  K3  L1  L3"
     #   33  34
        "-   -"),
]


'''
1	RFU1		    16	A0_N	LVDS	31	GND	    Ground	    46	A5_N	LVDS
2	HSIO		    17	B0_N	LVDS	32	A3_P	LVDS        47	B5_N	LVDS
3	ALERT/IRQ	    18	GND	    Ground	33	B3_P	LVDS	    48	GND	    Ground
4	VCC	3,3V	    19	GND	    Ground	34	A3_N	LVDS        49	GND	    Ground
5	SDA		        20	A1_P	LVDS	35	B3_N	LVDS	    50	RFU2_P	
6	HSO		        21	B1_P	LVDS	36	VADJ	1.2 to 3.3V	51	DI/TDI	JTAG, SPI(MISO)
7	SCL		        22	A1_N	LVDS	37	GND	    Ground	    52	RFU2_N	
8	HSRST		    23	B1_N	LVDS	38	A4_P	LVDS    	53	DO/TDO	JTAG, SPI(MOSI)
9	VCC	3.3V	    24	GND	    Ground	39	B4_P	LVDS	    54	GND	    Ground
10	HSI		        25	GND	    Ground	40	A4_N	LVDS	    55	SEL/TMS	JTAG, SPI(SEL)
11	REFCLK		    26	A2_P	LVDS    41	B4_N	LVDS	    56	RFU_P	
12	GND	Ground	    27	B2_P	LVDS	42	GND	    Ground	    57	MODE	JTAG EN
13	GND	Ground	    28	A2_N	LVDS    43	GND	    Ground	    58	RFU_N	
14	A0_P	LVDS	29	B2_N	LVDS	44	A5_P	LVDS	    59	SCK/TCK	JTAG, SPI(CLK)
15	B0_P	LVDS	30	GND	    Ground	45	B5_P	LVDS	    60	VBUS	5V
'''
# TODO VADJ 1.2V / 1.8V for hs_cruvi
_hs_cruvi_1V8 = [
    ("hs_cruvi", 0,
     Subsignal("hsmio",      Pins("HS_CRUVI:1"),  IOStandard("LVCMOS18H")),
     Subsignal("smb_alert",  Pins("HS_CRUVI:2"),  IOStandard("LVCMOS18H")),
     Subsignal("smb_sda",    Pins("HS_CRUVI:4"),  IOStandard("LVCMOS18H")),
     Subsignal("hso",        Pins("HS_CRUVI:5"),  IOStandard("LVCMOS18H")),
     Subsignal("smb_scl",    Pins("HS_CRUVI:6"),  IOStandard("LVCMOS18H")),
     Subsignal("hsrst",      Pins("HS_CRUVI:7"),  IOStandard("LVCMOS18H")),
     Subsignal("hsi",        Pins("HS_CRUVI:9"),  IOStandard("LVCMOS18H")),
     Subsignal("refclk",     Pins("HS_CRUVI:10"), IOStandard("LVCMOS18H")),
     Subsignal("a0_p",       Pins("HS_CRUVI:13"), IOStandard("LVDS")),
     Subsignal("b0_p",       Pins("HS_CRUVI:14"), IOStandard("LVDS")),
     Subsignal("a1_p",       Pins("HS_CRUVI:19"), IOStandard("LVDS")),
     Subsignal("b1_p",       Pins("HS_CRUVI:20"), IOStandard("LVDS")),  
     Subsignal("a2_p",       Pins("HS_CRUVI:25"), IOStandard("LVDS")),
     Subsignal("b2_p",       Pins("HS_CRUVI:26"), IOStandard("LVDS")),
     Subsignal("a3_p",       Pins("HS_CRUVI:31"), IOStandard("LVDS")),
     Subsignal("b3_p",       Pins("HS_CRUVI:32"), IOStandard("LVDS")),
     Subsignal("a4_p",       Pins("HS_CRUVI:37"), IOStandard("LVDS")),
     Subsignal("b4_p",       Pins("HS_CRUVI:38"), IOStandard("LVDS")), 
     Subsignal("a5_p",       Pins("HS_CRUVI:43"), IOStandard("LVDS")),
     Subsignal("b5_p",       Pins("HS_CRUVI:44"), IOStandard("LVDS")),
     Subsignal("jtdi",       Pins("HS_CRUVI:50"), IOStandard("LVCMOS33")),
     Subsignal("jtdo",       Pins("HS_CRUVI:52"), IOStandard("LVCMOS33")),
     Subsignal("jtms",       Pins("HS_CRUVI:54"), IOStandard("LVCMOS33")),
     Subsignal("jtagen",     Pins("HS_CRUVI:56"), IOStandard("LVCMOS33")),
     Subsignal("jtck",       Pins("HS_CRUVI:58"), IOStandard("LVCMOS33")),
    )
]

_hs_cruvi_1V2 = [
    ("hs_cruvi", 0,
     Subsignal("hsmio",      Pins("HS_CRUVI:1"),  IOStandard("LVCMOS12H")),
     Subsignal("smb_alert",  Pins("HS_CRUVI:2"),  IOStandard("LVCMOS12H")),
     Subsignal("smb_sda",    Pins("HS_CRUVI:4"),  IOStandard("LVCMOS12H")),
     Subsignal("hso",        Pins("HS_CRUVI:5"),  IOStandard("LVCMOS12H")),
     Subsignal("smb_scl",    Pins("HS_CRUVI:6"),  IOStandard("LVCMOS12H")),
     Subsignal("hsrst",      Pins("HS_CRUVI:7"),  IOStandard("LVCMOS12H")),
     Subsignal("hsi",        Pins("HS_CRUVI:9"),  IOStandard("LVCMOS12H")),
     Subsignal("refclk",     Pins("HS_CRUVI:10"), IOStandard("LVCMOS12H")),
     Subsignal("a0_p",       Pins("HS_CRUVI:13"), IOStandard("LVDS")),
     Subsignal("b0_p",       Pins("HS_CRUVI:14"), IOStandard("LVDS")),
     Subsignal("a1_p",       Pins("HS_CRUVI:19"), IOStandard("LVDS")),
     Subsignal("b1_p",       Pins("HS_CRUVI:20"), IOStandard("LVDS")),  
     Subsignal("a2_p",       Pins("HS_CRUVI:25"), IOStandard("LVDS")),
     Subsignal("b2_p",       Pins("HS_CRUVI:26"), IOStandard("LVDS")),
     Subsignal("a3_p",       Pins("HS_CRUVI:31"), IOStandard("LVDS")),
     Subsignal("b3_p",       Pins("HS_CRUVI:32"), IOStandard("LVDS")),
     Subsignal("a4_p",       Pins("HS_CRUVI:37"), IOStandard("LVDS")),
     Subsignal("b4_p",       Pins("HS_CRUVI:38"), IOStandard("LVDS")), 
     Subsignal("a5_p",       Pins("HS_CRUVI:43"), IOStandard("LVDS")),
     Subsignal("b5_p",       Pins("HS_CRUVI:44"), IOStandard("LVDS")),
     Subsignal("jtdi",       Pins("HS_CRUVI:50"), IOStandard("LVCMOS33")),
     Subsignal("jtdo",       Pins("HS_CRUVI:52"), IOStandard("LVCMOS33")),
     Subsignal("jtms",       Pins("HS_CRUVI:54"), IOStandard("LVCMOS33")),
     Subsignal("jtagen",     Pins("HS_CRUVI:56"), IOStandard("LVCMOS33")),
     Subsignal("jtck",       Pins("HS_CRUVI:58"), IOStandard("LVCMOS33")),
    )
]
'''
    1  SDA      2  SCL
    3  D3       4  SEL
    5  D2       6  GND
    7  D1       8  SCK
    9  D0       10 3V3
    11 RFU      12 5V
'''
_ls_cruvi = [
    ("ls_cruvi", 0,
     Subsignal("sda", Pins("LS_CRUVI:0"), IOStandard("LVCMOS33")),
     Subsignal("scl", Pins("LS_CRUVI:1"), IOStandard("LVCMOS33")),
     Subsignal("d3",  Pins("LS_CRUVI:2"), IOStandard("LVCMOS33")),
     Subsignal("sel", Pins("LS_CRUVI:3"), IOStandard("LVCMOS33")),
     Subsignal("d2",  Pins("LS_CRUVI:4"), IOStandard("LVCMOS33")),                             
     Subsignal("d1",  Pins("LS_CRUVI:6"), IOStandard("LVCMOS33")),
     Subsignal("sck", Pins("LS_CRUVI:7"), IOStandard("LVCMOS33")),
     Subsignal("d0",  Pins("LS_CRUVI:8"), IOStandard("LVCMOS33")),
    )
]

'''
    1  GND            2  5V
    3  XA0_P          4  XA0_N
    5  XA1_P          6  XA1_N
    7  XA2_P          8  XA2_N
    9  XA3_P          10 XA3_N
    11 XA4_P          12 XA4_N
    13 XA5_P          14 XA5_N
    15 HS2            16 HS3
    17 3V3            18 3V3
    19 LS18           20 LS19
    21 LS0            22 LS4
    23 LS1            24 LS5
    25 LS2            25 LS6
    27 LS3            28 LS7
    29 AN0            30 AN2
    31 AN1            32 AN3
    33 VIN            34 GND
'''
_j4 = (
    Subsignal("xa0_p", Pins("J4:2"),  IOStandard("LVCMOS33")),
    Subsignal("xa0_n", Pins("J4:3"),  IOStandard("LVCMOS33")),
    Subsignal("xa1_p", Pins("J4:4"),  IOStandard("LVCMOS33")),
    Subsignal("xa1_n", Pins("J4:5"),  IOStandard("LVCMOS33")),
    Subsignal("xa2_p", Pins("J4:6"),  IOStandard("LVCMOS33")),
    Subsignal("xa2_n", Pins("J4:7"),  IOStandard("LVCMOS33")),
    Subsignal("xa3_p", Pins("J4:8"),  IOStandard("LVCMOS33")),
    Subsignal("xa3_n", Pins("J4:9"),  IOStandard("LVCMOS33")),
    Subsignal("xa4_p", Pins("J4:10"), IOStandard("LVCMOS33")),
    Subsignal("xa4_n", Pins("J4:11"), IOStandard("LVCMOS33")),
    Subsignal("xa5_p", Pins("J4:12"), IOStandard("LVCMOS33")),
    Subsignal("xa5_n", Pins("J4:13"), IOStandard("LVCMOS33")),
    Subsignal("hs2",   Pins("J4:14"), IOStandard("LVCMOS18")),
    Subsignal("hs3",   Pins("J4:15"), IOStandard("LVCMOS18")),
    Subsignal("ls18",  Pins("J4:18"), IOStandard("LVCMOS33")),
    Subsignal("ls19",  Pins("J4:19"), IOStandard("LVCMOS33")),
    Subsignal("ls0",   Pins("J4:20"), IOStandard("LVCMOS33")),
    Subsignal("ls4",   Pins("J4:21"), IOStandard("LVCMOS33")),
    Subsignal("ls1",   Pins("J4:22"), IOStandard("LVCMOS33")),
    Subsignal("ls5",   Pins("J4:23"), IOStandard("LVCMOS33")),
    Subsignal("ls2",   Pins("J4:24"), IOStandard("LVCMOS33")),
    Subsignal("ls6",   Pins("J4:25"), IOStandard("LVCMOS33")),
    Subsignal("ls3",   Pins("J4:26"), IOStandard("LVCMOS33")),
    Subsignal("ls7",   Pins("J4:27"), IOStandard("LVCMOS33")),
    Subsignal("an0",   Pins("J4:28"), IOStandard("LVCMOS18H")),
    Subsignal("an2",   Pins("J4:29"), IOStandard("LVCMOS18H")),
    Subsignal("an1",   Pins("J4:30"), IOStandard("LVCMOS18H")),
    Subsignal("an3",   Pins("J4:31"), IOStandard("LVCMOS18H")),
)

_j5 = (
    Subsignal("xb0_p", Pins("J5:2"),  IOStandard("LVCMOS33")),
    Subsignal("xb0_n", Pins("J5:3"),  IOStandard("LVCMOS33")),
    Subsignal("xb1_p", Pins("J5:4"),  IOStandard("LVCMOS33")),
    Subsignal("xb1_n", Pins("J5:5"),  IOStandard("LVCMOS33")),
    Subsignal("xb2_p", Pins("J5:6"),  IOStandard("LVCMOS33")),
    Subsignal("xb2_n", Pins("J5:7"),  IOStandard("LVCMOS33")),
    Subsignal("xb3_p", Pins("J5:8"),  IOStandard("LVCMOS33")),
    Subsignal("xb3_n", Pins("J5:9"),  IOStandard("LVCMOS33")),
    Subsignal("xb4_p", Pins("J5:10"), IOStandard("LVCMOS33")),
    Subsignal("xb4_n", Pins("J5:11"), IOStandard("LVCMOS33")),
    Subsignal("xb5_p", Pins("J5:12"), IOStandard("LVCMOS33")),
    Subsignal("xb5_n", Pins("J5:13"), IOStandard("LVCMOS33")),
    Subsignal("hs0",   Pins("J5:14"), IOStandard("LVCMOS18")),
    Subsignal("hs1",   Pins("J5:15"), IOStandard("LVCMOS18")),
    Subsignal("ls16",  Pins("J5:18"), IOStandard("LVCMOS33")),
    Subsignal("ls17",  Pins("J5:19"), IOStandard("LVCMOS33")),
    Subsignal("ls8",   Pins("J5:20"), IOStandard("LVCMOS33")),
    Subsignal("ls12",  Pins("J5:21"), IOStandard("LVCMOS33")),
    Subsignal("ls9",   Pins("J5:22"), IOStandard("LVCMOS33")),
    Subsignal("ls13",  Pins("J5:23"), IOStandard("LVCMOS33")),
    Subsignal("ls10",  Pins("J5:24"), IOStandard("LVCMOS33")),
    Subsignal("ls14",  Pins("J5:25"), IOStandard("LVCMOS33")),
    Subsignal("ls11",  Pins("J5:26"), IOStandard("LVCMOS33")),
    Subsignal("ls15",  Pins("J5:27"), IOStandard("LVCMOS33")),
    Subsignal("an4",   Pins("J5:28"), IOStandard("LVCMOS18H")),
    Subsignal("an6",   Pins("J5:29"), IOStandard("LVCMOS18H")),
    Subsignal("an5",   Pins("J5:30"), IOStandard("LVCMOS18H")),
    Subsignal("an7",   Pins("J5:31"), IOStandard("LVCMOS18H")),
)

class Platform(LatticeNexusPlatform):
    default_clk_name = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, device="LFD2NX-40-7BG196I", toolchain="radiant", 
                 **kwargs):

        # Accept other LFD2NX-40-XBG196Y devices
        assert re.match("LFD2NX-40-[789]BG196[CIT]", device) is not None, """
        Expected device to be one of the following:
            LFD2NX-40-xBG196y, where
            x in {7,8,9} and y in {C,I,T}.
        """

        LatticeNexusPlatform.__init__(self, device, _io, _connectors, 
                                      toolchain=toolchain, **kwargs)
        
        # Release Master-SPI as general IO pins (see FPGA-AN-02048 4.1.7)
        self.add_platform_command("ldc_set_sysconfig {{MASTER_SPI_PORT=DISABLE}}")

    def create_programmer(self):
        return OpenFPGALoader(board="certusnx_versa_evn", freq=1000000)

    def do_finalize(self, fragment):
        LatticeNexusPlatform.do_finalize(self, fragment)


