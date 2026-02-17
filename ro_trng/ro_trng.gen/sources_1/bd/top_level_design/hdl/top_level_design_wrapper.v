//Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
//Copyright 2022-2025 Advanced Micro Devices, Inc. All Rights Reserved.
//--------------------------------------------------------------------------------
//Tool Version: Vivado v.2025.2 (win64) Build 6299465 Fri Nov 14 19:35:11 GMT 2025
//Date        : Tue Feb 17 14:33:35 2026
//Host        : DESKTOP-L7RS5J6 running 64-bit major release  (build 9200)
//Command     : generate_target top_level_design_wrapper.bd
//Design      : top_level_design_wrapper
//Purpose     : IP block netlist
//--------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

module top_level_design_wrapper
   (CLK100MHZ,
    uart_tx);
  input CLK100MHZ;
  output uart_tx;

  wire CLK100MHZ;
  wire uart_tx;

  top_level_design top_level_design_i
       (.CLK100MHZ(CLK100MHZ),
        .uart_tx(uart_tx));
endmodule
