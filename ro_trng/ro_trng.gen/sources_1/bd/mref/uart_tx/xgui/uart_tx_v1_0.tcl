# Definitional proc to organize widgets for parameters.
proc init_gui { IPINST } {
  ipgui::add_param $IPINST -name "Component_Name"
  #Adding Page
  set Page_0 [ipgui::add_page $IPINST -name "Page 0"]
  ipgui::add_param $IPINST -name "clks_per_bit" -parent ${Page_0}


}

proc update_PARAM_VALUE.clks_per_bit { PARAM_VALUE.clks_per_bit } {
	# Procedure called to update clks_per_bit when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.clks_per_bit { PARAM_VALUE.clks_per_bit } {
	# Procedure called to validate clks_per_bit
	return true
}


proc update_MODELPARAM_VALUE.clks_per_bit { MODELPARAM_VALUE.clks_per_bit PARAM_VALUE.clks_per_bit } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.clks_per_bit}] ${MODELPARAM_VALUE.clks_per_bit}
}

