#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# ./newae_cw305.py --csr-csr=csr.csv --build --load
# litex_server --jtag --jtag-config=openocd_xc7_ft232.cfg
# litex_term crossover

from migen import *

from litex.gen import LiteXModule

from litex_boards.platforms import newae_cw305

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex.soc.cores.clock import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        # CFGM Clk ~65MHz.
        cfgm_clk      = Signal()
        cfgm_clk_freq = int(65e6)
        self.specials += Instance("STARTUPE2",
            i_CLK       = 0,
            i_GSR       = 0,
            i_GTS       = 0,
            i_KEYCLEARB = 1,
            i_PACK      = 0,
            i_USRCCLKO  = cfgm_clk,
            i_USRCCLKTS = 0,
            i_USRDONEO  = 1,
            i_USRDONETS = 1,
            o_CFGMCLK   = cfgm_clk
        )

        # PLL
        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(cfgm_clk, cfgm_clk_freq)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), with_led_chaser=True, **kwargs):
        platform = newae_cw305.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["uart_name"] = "crossover"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on NewAE-CW305", **kwargs)

        # JTAGBone ---------------------------------------------------------------------------------
        self.add_jtagbone()

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq,
            )

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.argument_parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=newae_cw305.Platform, description="LiteX SoC on NewAE-CW305")
    parser.add_target_argument("--sys-clk-freq", default=100e6,       help="System clock frequency.")

    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = int(float(args.sys_clk_freq)),
        **parser.soc_core_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
