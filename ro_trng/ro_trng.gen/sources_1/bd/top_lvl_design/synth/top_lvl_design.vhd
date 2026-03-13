--Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
--Copyright 2022-2025 Advanced Micro Devices, Inc. All Rights Reserved.
----------------------------------------------------------------------------------
--Tool Version: Vivado v.2025.2 (win64) Build 6299465 Fri Nov 14 19:35:11 GMT 2025
--Date        : Fri Mar 13 13:54:32 2026
--Host        : DESKTOP-L7RS5J6 running 64-bit major release  (build 9200)
--Command     : generate_target top_lvl_design.bd
--Design      : top_lvl_design
--Purpose     : IP block netlist
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity top_lvl_design is
  port (
    CLK100MHZ : in STD_LOGIC;
    uart_tx : out STD_LOGIC
  );
  attribute CORE_GENERATION_INFO : string;
  attribute CORE_GENERATION_INFO of top_lvl_design : entity is "top_lvl_design,IP_Integrator,{x_ipVendor=xilinx.com,x_ipLibrary=BlockDiagram,x_ipName=top_lvl_design,x_ipVersion=1.00.a,x_ipLanguage=VHDL,numBlks=6,numReposBlks=6,numNonXlnxBlks=0,numHierBlks=0,maxHierDepth=0,numSysgenBlks=0,numHlsBlks=0,numHdlrefBlks=4,numPkgbdBlks=0,bdsource=USER,synth_mode=Hierarchical}";
  attribute HW_HANDOFF : string;
  attribute HW_HANDOFF of top_lvl_design : entity is "top_lvl_design.hwdef";
end top_lvl_design;

architecture STRUCTURE of top_lvl_design is
  component top_lvl_design_raw_bits_0_0 is
  port (
    clk : in STD_LOGIC;
    rst_l : in STD_LOGIC;
    ro_sync : in STD_LOGIC_VECTOR ( 7 downto 0 );
    tx_ready : in STD_LOGIC;
    data_in : out STD_LOGIC_VECTOR ( 7 downto 0 );
    data_valid : out STD_LOGIC
  );
  end component top_lvl_design_raw_bits_0_0;
  component top_lvl_design_ro_bank_0_0 is
  port (
    enable : in STD_LOGIC;
    ro_vec : out STD_LOGIC_VECTOR ( 7 downto 0 )
  );
  end component top_lvl_design_ro_bank_0_0;
  component top_lvl_design_uart_tx_0_0 is
  port (
    clk : in STD_LOGIC;
    rst_l : in STD_LOGIC;
    data_in : in STD_LOGIC_VECTOR ( 7 downto 0 );
    data_valid : in STD_LOGIC;
    tx_ready : out STD_LOGIC;
    tx_out : out STD_LOGIC
  );
  end component top_lvl_design_uart_tx_0_0;
  component top_lvl_design_ro_sampler_0_0 is
  port (
    clk : in STD_LOGIC;
    rst_l : in STD_LOGIC;
    ro_vec : in STD_LOGIC_VECTOR ( 7 downto 0 );
    ro_sync : out STD_LOGIC_VECTOR ( 7 downto 0 )
  );
  end component top_lvl_design_ro_sampler_0_0;
  component top_lvl_design_xlconstant_0_0 is
  port (
    dout : out STD_LOGIC_VECTOR ( 0 to 0 )
  );
  end component top_lvl_design_xlconstant_0_0;
  component top_lvl_design_xlconstant_0_1 is
  port (
    dout : out STD_LOGIC_VECTOR ( 0 to 0 )
  );
  end component top_lvl_design_xlconstant_0_1;
  signal enable_dout : STD_LOGIC_VECTOR ( 0 to 0 );
  signal raw_bits_0_data_in : STD_LOGIC_VECTOR ( 7 downto 0 );
  signal raw_bits_0_data_valid : STD_LOGIC;
  signal ro_bank_0_ro_vec : STD_LOGIC_VECTOR ( 7 downto 0 );
  signal ro_sampler_0_ro_sync : STD_LOGIC_VECTOR ( 7 downto 0 );
  signal rst_l_dout : STD_LOGIC_VECTOR ( 0 to 0 );
  signal uart_tx_0_tx_ready : STD_LOGIC;
  attribute X_INTERFACE_INFO : string;
  attribute X_INTERFACE_INFO of CLK100MHZ : signal is "xilinx.com:signal:clock:1.0 CLK.CLK100MHZ CLK";
  attribute X_INTERFACE_PARAMETER : string;
  attribute X_INTERFACE_PARAMETER of CLK100MHZ : signal is "XIL_INTERFACENAME CLK.CLK100MHZ, CLK_DOMAIN top_lvl_design_CLK100MHZ, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, INSERT_VIP 0, PHASE 0.0";
begin
enable: component top_lvl_design_xlconstant_0_1
     port map (
      dout(0) => enable_dout(0)
    );
raw_bits_0: component top_lvl_design_raw_bits_0_0
     port map (
      clk => CLK100MHZ,
      data_in(7 downto 0) => raw_bits_0_data_in(7 downto 0),
      data_valid => raw_bits_0_data_valid,
      ro_sync(7 downto 0) => ro_sampler_0_ro_sync(7 downto 0),
      rst_l => rst_l_dout(0),
      tx_ready => uart_tx_0_tx_ready
    );
ro_bank_0: component top_lvl_design_ro_bank_0_0
     port map (
      enable => enable_dout(0),
      ro_vec(7 downto 0) => ro_bank_0_ro_vec(7 downto 0)
    );
ro_sampler_0: component top_lvl_design_ro_sampler_0_0
     port map (
      clk => CLK100MHZ,
      ro_sync(7 downto 0) => ro_sampler_0_ro_sync(7 downto 0),
      ro_vec(7 downto 0) => ro_bank_0_ro_vec(7 downto 0),
      rst_l => rst_l_dout(0)
    );
rst_l: component top_lvl_design_xlconstant_0_0
     port map (
      dout(0) => rst_l_dout(0)
    );
uart_tx_0: component top_lvl_design_uart_tx_0_0
     port map (
      clk => CLK100MHZ,
      data_in(7 downto 0) => raw_bits_0_data_in(7 downto 0),
      data_valid => raw_bits_0_data_valid,
      rst_l => rst_l_dout(0),
      tx_out => uart_tx,
      tx_ready => uart_tx_0_tx_ready
    );
end STRUCTURE;
