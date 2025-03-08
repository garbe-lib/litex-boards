#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 D. Garbe <105213927+garbe-lib@users.noreply.github.com>
# SPDX-License-Identifier: BSD-2-Clause
from migen import Signal, ClockDomain, If
from migen.genlib.resetsync import AsyncResetSynchronizer


from platforms import trenz_cr00103_03_A

from litex.gen import LiteXModule

from litespi.modules import MT25QL128
from litespi.opcodes import SpiNorFlashOpCodes as Codes

from litex.soc.cores.clock import NXOSCA, NXPLL
from litex.soc.cores.hyperbus import HyperRAM
from litex.soc.cores.led import LedChaser
from litex.soc.cores.ram import NXLRAM
from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import Builder

from util.constants import KiB, MiB

import os

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):

        self.rst = Signal()

        self.cd_sys = ClockDomain()
        self.cd_osc = ClockDomain()
        self.cd_por = ClockDomain(reset_less=True)
        
        # Internal OSC
        self.osc = osc = NXOSCA(platform)
        osc.create_hf_clk(self.cd_osc, 50e6)
        self.specials += AsyncResetSynchronizer(self.cd_osc, self.rst)

        # POR
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(osc.hf_clk_out[0])
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = NXPLL(platform=platform)
        self.comb += pll.reset.eq(~por_done | self.rst)
        pll.register_clkin(osc.hf_clk_out[0], 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll.locked | self.rst)

class BaseSoC(SoCCore):
    def __init__(self, 
                 sys_clk_freq=50e6,
                 bios_flash_offset= 0x80_0000,
                 app_flash_offset= 0x84_0000,
                 toolchain="radiant",
                 with_led_chaser = True,
                 **kwargs):

        platform = trenz_cr00103_03_A.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        kwargs["integrated_rom_size"] = 0 
        kwargs["integrated_sram_size"] = 0

        SoCCore.__init__(self, platform, sys_clk_freq, 
                         ident="LiteX SoC on CR00103-03-A evaluation board", 
                         **kwargs)
        
        # Add ROM linker region --------------------------------------------------------------------
        #self.add_spi_flash(mode="4x", module=MT25QL128(Codes.READ_1_1_4), clk_freq=25e6, with_master=False)
        self.add_spi_flash(mode="1x", module=MT25QL128(Codes.READ_1_1_1), clk_freq=25e6, with_master=False)
        
        self.bus.add_region("rom", SoCRegion(
            origin = self.bus.regions["spiflash"].origin + bios_flash_offset,
            size   = 64 * KiB,
            linker = True)
        )
        self.cpu.set_reset_address(self.bus.regions["rom"].origin)

        # 128KiB LRAM (used as SRAM) ---------------------------------------------------------------
        size = 128*KiB
        self.submodules.spram = NXLRAM(32, size)
        self.bus.add_slave("sram", 
                           slave=self.spram.bus, 
                           region = SoCRegion(origin=self.mem_map["sram"], size=size))

        # 8MiB HyperRAM (used as Main-RAM) ---------------------------------------------------------
        size = 8*MiB
        hr_pads = platform.request("hyperram")
        self.hyperram = HyperRAM(hr_pads, sys_clk_freq=sys_clk_freq)
        self.bus.add_slave("main_ram", slave=self.hyperram.bus, region=SoCRegion(origin=self.mem_map["main_ram"], size=size, mode="rwx"))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("led"), # request_all("led")
                sys_clk_freq = sys_clk_freq)

        self.add_constant("FLASH_BOOT_ADDRESS", self.bus.regions["spiflash"].origin + app_flash_offset)

def get_application_file(builder: Builder):
    return os.path.join(builder.software_dir, "../firmware", "dpusc_fm3.fbi")

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=trenz_cr00103_03_A.Platform,
                                 description="LiteX SoC on CR00103-03-A bpard.")
    parser.add_target_argument("--sys-clk-freq", default=50e6, type=float,  help="System clock frequency.")
    parser.add_target_argument("--flash",        action="store_true",       help="Flash bitstream and BIOS to SPI Flash.")
    parser.add_target_argument("--upload",       action=None, type=str,     help="Flash application to SPI Flash.")
    parser.add_target_argument("--address",      default=0x0,               help="Flash address to program bitstream at.")
    parser.add_target_argument("--bios-flash-offset", default=0x80_0000,    help="Bios address offset in flash relative to --address.")
    parser.add_target_argument("--app-flash-offset",  default=0x84_0000,    help="Application address offset in flash relative to --address.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        import subprocess

        cmd = ["openFPGALoader",
               #"-b", "certusnx_versa_evn",
               "--cable", "ft2232",
               "--freq", "10000000",
               "-d", "/dev/ttyUSB0",
               "--bitstream", builder.get_bitstream_filename(mode="flash"),
               "--write-flash", 
               "--offset", str(args.address)
               ]
        subprocess.call(cmd)

        cmd = ["openFPGALoader",
               #"-b", "certusnx_versa_evn",
               "--cable", "ft2232",
               "--freq", "10000000",
               "-d", "/dev/ttyUSB0",
               "--bitstream", builder.get_bios_filename(),
               "--write-flash", 
               "--offset", str(args.address + args.bios_flash_offset),
               "--external-flash"
               ]
        subprocess.call(cmd)

    if args.upload:
        import subprocess

        cmd = ["openFPGALoader",
               #"-b", "certusnx_versa_evn",
               "--cable", "ft2232",
               "--freq", "10000000",
               "-d", "/dev/ttyUSB0",
               "--bitstream", args.upload,
               "--write-flash", 
               "--offset", str(args.address + args.app_flash_offset),
               "--external-flash"
               ]
        subprocess.call(cmd)


if __name__ == "__main__":
    main()

