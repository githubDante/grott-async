from .packet import GrottRegister, RegType

""" Mapping for registers used by inverters with 125 words per section
    See below for shorter maps 
"""
"""
  _    _    _     _    _    _    _    _    _    _    _    _  
 / \  / \  / \   / \  / \  / \  / \  / \  / \  / \  / \  / \ 
( 1 )( 2 )( 5 ) ( r )( e )( g )( i )( s )( t )( e )( r )( s )
 \_/  \_/  \_/   \_/  \_/  \_/  \_/  \_/  \_/  \_/  \_/  \_/ 

"""
"""
    This one is used for report packets
    Holding Register in the documentation
"""
map_03_125 = {

        34: GrottRegister(34, RegType.TEXT, 'm_info', length=7),
        43: GrottRegister(43, RegType.INT, 'DTC', length=1),
        125: GrottRegister(125, RegType.TEXT, 'device_type', length=7)
}

"""
    Mapping for data packets
    Input Reg in the documentation
"""
map_04_125 = {
        0:  GrottRegister(0, RegType.INT, 'pvstatus', length=1, divide=1),
        1:  GrottRegister(1, RegType.FLOAT, 'in_power', length=2, divide=10),

        3:  GrottRegister(3, RegType.FLOAT, 'pv1_voltage', length=1, divide=10),
        4:  GrottRegister(4, RegType.FLOAT, 'pv1_current', length=1, divide=10),
        5:  GrottRegister(5, RegType.FLOAT, 'pv1_power', length=2, divide=10),
        7:  GrottRegister(7, RegType.FLOAT, 'pv2_voltage', length=1, divide=10),
        8:  GrottRegister(8, RegType.FLOAT, 'pv2_current', length=1, divide=10),
        9:  GrottRegister(9, RegType.FLOAT, 'pv2_power', length=2, divide=10),
        11: GrottRegister(11, RegType.FLOAT, 'pv3_voltage', length=1, divide=10),
        12: GrottRegister(12, RegType.FLOAT, 'pv3_current', length=1, divide=10),
        13: GrottRegister(13, RegType.FLOAT, 'pv3_power', length=2, divide=10),
        15: GrottRegister(15, RegType.FLOAT, 'pv4_voltage', length=1, divide=10),
        16: GrottRegister(16, RegType.FLOAT, 'pv4_current', length=1, divide=10),
        17: GrottRegister(17, RegType.FLOAT, 'pv4_power', length=2, divide=10),
        19: GrottRegister(19, RegType.FLOAT, 'pv5_voltage', length=1, divide=10),
        20: GrottRegister(20, RegType.FLOAT, 'pv5_current', length=1, divide=10),
        21: GrottRegister(21, RegType.FLOAT, 'pv5_power', length=2, divide=10),
        23: GrottRegister(23, RegType.FLOAT, 'pv6_voltage', length=1, divide=10),
        24: GrottRegister(24, RegType.FLOAT, 'pv6_current', length=1, divide=10),
        25: GrottRegister(25, RegType.FLOAT, 'pv6_power', length=2, divide=10),
        27: GrottRegister(27, RegType.FLOAT, 'pv7_voltage', length=1, divide=10),
        28: GrottRegister(28, RegType.FLOAT, 'pv7_current', length=1, divide=10),
        29: GrottRegister(29, RegType.FLOAT, 'pv7_power', length=2, divide=10),
        31: GrottRegister(31, RegType.FLOAT, 'pv8_voltage', length=1, divide=10),
        32: GrottRegister(32, RegType.FLOAT, 'pv8_current', length=1, divide=10),
        33: GrottRegister(33, RegType.FLOAT, 'pv8_power', length=2, divide=10),

        35: GrottRegister(35, RegType.FLOAT, 'out_power', length=2, divide=10),
        37: GrottRegister(37, RegType.FLOAT, 'grid_freq', length=1, divide=100),
        38: GrottRegister(38, RegType.FLOAT, 'grid_voltage_phase_1', length=1, divide=10),

        39: GrottRegister(39, RegType.FLOAT, 'grid_out_current_phase_1', length=1, divide=10),
        40: GrottRegister(40, RegType.FLOAT, 'grid_out_watt_VA_pahse_1', length=2, divide=10),
        42: GrottRegister(42, RegType.FLOAT, 'grid_voltage_phase_2', length=1, divide=10),
        43: GrottRegister(43, RegType.FLOAT, 'grid_out_current_phase_2', length=1, divide=10),
        44: GrottRegister(44, RegType.FLOAT, 'grid_out_watt_VA_pahse_2', length=2, divide=10),
        46: GrottRegister(46, RegType.FLOAT, 'grid_voltage_phase_3', length=1, divide=10),
        47: GrottRegister(47, RegType.FLOAT, 'grid_out_current_phase_3', length=1, divide=10),
        48: GrottRegister(48, RegType.FLOAT, 'grid_out_watt_VA_pahse_3', length=2, divide=10),

        50: GrottRegister(50, RegType.FLOAT, 'VAC_RS', length=1, divide=10),
        51: GrottRegister(51, RegType.FLOAT, 'VAC_ST', length=1, divide=10),
        52: GrottRegister(52, RegType.FLOAT, 'VAC_TR', length=1, divide=10),
        53: GrottRegister(53, RegType.FLOAT, 'energy_today', length=2, divide=10),
        55: GrottRegister(55, RegType.FLOAT, 'energy_total', length=2, divide=10),
        57: GrottRegister(57, RegType.FLOAT, 'working_time', length=2, divide=7200),

        59: GrottRegister(59, RegType.FLOAT, 'pv1_energy_today', length=2, divide=10),
        61: GrottRegister(61, RegType.FLOAT, 'pv1_energy_total', length=2, divide=10),
        63: GrottRegister(63, RegType.FLOAT, 'pv2_energy_today', length=2, divide=10),
        65: GrottRegister(65, RegType.FLOAT, 'pv2_energy_total', length=2, divide=10),
        67: GrottRegister(67, RegType.FLOAT, 'pv3_energy_today', length=2, divide=10),
        69: GrottRegister(69, RegType.FLOAT, 'pv3_energy_total', length=2, divide=10),
        71: GrottRegister(71, RegType.FLOAT, 'pv4_energy_today', length=2, divide=10),
        73: GrottRegister(73, RegType.FLOAT, 'pv4_energy_total', length=2, divide=10),
        75: GrottRegister(75, RegType.FLOAT, 'pv5_energy_total', length=2, divide=10),
        77: GrottRegister(77, RegType.FLOAT, 'pv5_energy_total', length=2, divide=10),
        79: GrottRegister(79, RegType.FLOAT, 'pv6_energy_total', length=2, divide=10),
        81: GrottRegister(81, RegType.FLOAT, 'pv6_energy_total', length=2, divide=10),
        83: GrottRegister(83, RegType.FLOAT, 'pv7_energy_total', length=2, divide=10),
        85: GrottRegister(85, RegType.FLOAT, 'pv7_energy_total', length=2, divide=10),
        87: GrottRegister(87, RegType.FLOAT, 'pv8_energy_total', length=2, divide=10),
        89: GrottRegister(89, RegType.FLOAT, 'pv8_energy_total', length=2, divide=10),
        91: GrottRegister(91, RegType.FLOAT, 'pv_energy_total', length=2, divide=10),

        93: GrottRegister(93, RegType.FLOAT, 'inverter_temp', length=1, divide=10),
        94: GrottRegister(94, RegType.FLOAT, 'inverter_inside_temp', length=1, divide=10),
        95: GrottRegister(95, RegType.FLOAT, 'boost_temp', length=1, divide=10),
        97: GrottRegister(97, RegType.FLOAT, 'batt_v', length=1, divide=10),
        98: GrottRegister(98, RegType.FLOAT, 'Pbus_volt', length=1, divide=10),
        99: GrottRegister(99, RegType.FLOAT, 'Nbus_volt', length=1, divide=10),
        100: GrottRegister(100, RegType.FLOAT, 'power_factor_now', length=1, divide=20000),
        101: GrottRegister(101, RegType.FLOAT, 'real_out_power_pct', length=1, divide=100),
        102: GrottRegister(102, RegType.FLOAT, 'out_max_power', length=2, divide=10),
        104: GrottRegister(104, RegType.FLOAT, 'derating_mode', length=1, divide=1),
        105: GrottRegister(105, RegType.FAULT_1, 'inverter_fault_code', length=1, divide=1),
        106: GrottRegister(106, RegType.FAULT_8, 'inverter_fault_bit', length=2, divide=1),
        110: GrottRegister(110, RegType.INT, 'inverter_warning_bit', length=2, divide=1),

        125: GrottRegister(125, RegType.FLOAT, 'pv1_pid_voltage', length=1, divide=10),
        126: GrottRegister(126, RegType.FLOAT, 'pv1_pid_current', length=1, divide=10),
        127: GrottRegister(127, RegType.FLOAT, 'pv2_pid_voltage', length=1, divide=10),
        128: GrottRegister(128, RegType.FLOAT, 'pv2_pid_current', length=1, divide=10),
        129: GrottRegister(129, RegType.FLOAT, 'pv3_pid_voltage', length=1, divide=10),
        130: GrottRegister(130, RegType.FLOAT, 'pv3_pid_current', length=1, divide=10),
        131: GrottRegister(131, RegType.FLOAT, 'pv4_pid_voltage', length=1, divide=10),
        132: GrottRegister(132, RegType.FLOAT, 'pv4_pid_current', length=1, divide=10),
        133: GrottRegister(133, RegType.FLOAT, 'pv5_pid_voltage', length=1, divide=10),
        134: GrottRegister(134, RegType.FLOAT, 'pv5_pid_current', length=1, divide=10),
        135: GrottRegister(135, RegType.FLOAT, 'pv6_pid_voltage', length=1, divide=10),
        136: GrottRegister(136, RegType.FLOAT, 'pv6_pid_current', length=1, divide=10),
        137: GrottRegister(137, RegType.FLOAT, 'pv7_pid_voltage', length=1, divide=10),
        138: GrottRegister(138, RegType.FLOAT, 'pv7_pid_current', length=1, divide=10),
        139: GrottRegister(139, RegType.FLOAT, 'pv8_pid_voltage', length=1, divide=10),
        140: GrottRegister(140, RegType.FLOAT, 'pv8_pid_current', length=1, divide=10),
        141: GrottRegister(140, RegType.BIT, 'pv_pid_status', length=1, divide=1),

        142: GrottRegister(142, RegType.FLOAT, 'string1_voltage', length=1, divide=10),
        143: GrottRegister(143, RegType.FLOAT, 'string1_current', length=1, divide=10),
        144: GrottRegister(144, RegType.FLOAT, 'string2_voltage', length=1, divide=10),
        145: GrottRegister(145, RegType.FLOAT, 'string2_current', length=1, divide=10),
        146: GrottRegister(146, RegType.FLOAT, 'string3_voltage', length=1, divide=10),
        147: GrottRegister(147, RegType.FLOAT, 'string3_current', length=1, divide=10),
        148: GrottRegister(148, RegType.FLOAT, 'string4_voltage', length=1, divide=10),
        149: GrottRegister(149, RegType.FLOAT, 'string4_current', length=1, divide=10),
        150: GrottRegister(150, RegType.FLOAT, 'string5_voltage', length=1, divide=10),
        151: GrottRegister(151, RegType.FLOAT, 'string5_current', length=1, divide=10),
        152: GrottRegister(152, RegType.FLOAT, 'string6_voltage', length=1, divide=10),
        153: GrottRegister(153, RegType.FLOAT, 'string6_current', length=1, divide=10),
        154: GrottRegister(154, RegType.FLOAT, 'string7_voltage', length=1, divide=10),
        155: GrottRegister(155, RegType.FLOAT, 'string7_current', length=1, divide=10),
        156: GrottRegister(156, RegType.FLOAT, 'string8_voltage', length=1, divide=10),
        157: GrottRegister(157, RegType.FLOAT, 'string8_current', length=1, divide=10),

        158: GrottRegister(158, RegType.FLOAT, 'string9_voltage', length=1, divide=10),
        159: GrottRegister(159, RegType.FLOAT, 'string9_current', length=1, divide=10),
        160: GrottRegister(160, RegType.FLOAT, 'string10_voltage', length=1, divide=10),
        161: GrottRegister(161, RegType.FLOAT, 'string10_current', length=1, divide=10),
        162: GrottRegister(162, RegType.FLOAT, 'string11_voltage', length=1, divide=10),
        163: GrottRegister(163, RegType.FLOAT, 'string11_current', length=1, divide=10),
        164: GrottRegister(164, RegType.FLOAT, 'string12_voltage', length=1, divide=10),
        165: GrottRegister(165, RegType.FLOAT, 'string12_current', length=1, divide=10),
        166: GrottRegister(166, RegType.FLOAT, 'string13_voltage', length=1, divide=10),
        167: GrottRegister(167, RegType.FLOAT, 'string13_current', length=1, divide=10),
        168: GrottRegister(168, RegType.FLOAT, 'string14_voltage', length=1, divide=10),
        169: GrottRegister(169, RegType.FLOAT, 'string14_current', length=1, divide=10),
        170: GrottRegister(170, RegType.FLOAT, 'string15_voltage', length=1, divide=10),
        171: GrottRegister(171, RegType.FLOAT, 'string15_current', length=1, divide=10),
        172: GrottRegister(172, RegType.FLOAT, 'string16_voltage', length=1, divide=10),
        173: GrottRegister(173, RegType.FLOAT, 'string16_current', length=1, divide=10),

        174: GrottRegister(174, RegType.BIT, 'string_unmatch', length=1, divide=1),
        175: GrottRegister(175, RegType.BIT, 'string_cur_unbalance', length=1, divide=1),
        176: GrottRegister(176, RegType.BIT, 'string_disconnect', length=1, divide=1),
        177: GrottRegister(177, RegType.BIT, 'pid_fault_code', length=1, divide=1),
        178: GrottRegister(178, RegType.BIT, 'string_prompt', length=1, divide=1),
        179: GrottRegister(179, RegType.INT, 'pv_warn_val', length=1, divide=1),

        180: GrottRegister(180, RegType.INT, 'DSP_075_warning', length=1, divide=1),
        181: GrottRegister(181, RegType.INT, 'DSP_075_fault', length=1, divide=1),

        200: GrottRegister(200, RegType.INT, 'pv_iso_kOhm', length=1, divide=1),
        201: GrottRegister(201, RegType.FLOAT, 'R_DCI_current', length=1, divide=10),
        202: GrottRegister(202, RegType.FLOAT, 'S_DCI_current', length=1, divide=10),
        203: GrottRegister(203, RegType.FLOAT, 'T_DCI_current', length=1, divide=10),
        204: GrottRegister(204, RegType.FLOAT, 'pid_bus_voltage', length=1, divide=10),

        206: GrottRegister(206, RegType.BIT, 'svg_apf_status_ratio', length=1, divide=1),

        229: GrottRegister(229, RegType.BIT, 'fan_fault', length=1, divide=11),

        230: GrottRegister(230, RegType.FLOAT, 'out_apparent_power', length=2, divide=10),
        232: GrottRegister(232, RegType.FLOAT, 'out_reactive_power', length=2, divide=10),
        234: GrottRegister(234, RegType.FLOAT, 'max_reactive_power', length=2, divide=10),
        236: GrottRegister(236, RegType.FLOAT, 'tot_reactive_power', length=2, divide=10),

}


"""
  _    _     _    _    _    _    _    _    _    _    _  
 / \  / \   / \  / \  / \  / \  / \  / \  / \  / \  / \ 
( 4 )( 5 ) ( r )( e )( g )( i )( s )( t )( e )( r )( s )
 \_/  \_/   \_/  \_/  \_/  \_/  \_/  \_/  \_/  \_/  \_/ 

"""
"""
To be added later
"""
map_03_45 = {

}

map_04_45 = {

}
