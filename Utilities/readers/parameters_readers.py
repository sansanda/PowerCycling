
def read_time_parameters(config):
    """
    Extract timing parameters from configuration dictionary.
    """

    return {
        "t_on": float(config["Time on"]),
        "t_off": float(config["Time off"]),
        "initial_delay": float(config["Initial delay"]),
        "t_measure_high": float(config["Time measure high"]),
        "t_measure_low": float(config["Time measure low"]),
        "t_transfer_data": float(config["Time transfer data"])
    }


def read_current_parameters(config):
    """
    Extract current-related parameters.
    """

    return {
        "curr_low": float(config["Current low"]),
        "curr_high": float(config["Current high"]),
        "slew_rate": float(config["Slew Rate"]),
        "current_range": float(config["Current Range"])
    }


def read_gpib_addrs(config):
    """
    Extract GPIB addresses.
    """

    return {
        "electronic_load": int(config["Electronic Load GPIBAddr"]),
        "multimeter": int(config["Keithley 3706 GPIBAddr"])
    }


def read_file_parameters(config):
    """
    Extract file-related parameters.
    """

    return {
        "csv_file_path": config["Csv file path"]
    }


def read_channel_parameters(config):
    """
    Extract channel configuration parameters.
    """

    voltage_channels = config["Voltage channels"]
    temperature_channels = config["Temperature channels"]
    current_channels = config["Current channel"]

    v_start, v_end = map(int, voltage_channels.split(":"))
    t_start, t_end = map(int, temperature_channels.split(":"))
    c_start, c_end = map(int, current_channels.split(":"))

    return {

        "voltage_channels_string": voltage_channels,
        "temperature_channels_string": temperature_channels,
        "current_channels_string": current_channels,

        "n_voltage_channels": v_end - v_start + 1,
        "n_temperature_channels": t_end - t_start + 1,
        "n_current_channels": c_end - c_start + 1,

        "number_total_channels":
            (v_end - v_start + 1) + (t_end - t_start + 1) + (c_end - c_start + 1)
    }