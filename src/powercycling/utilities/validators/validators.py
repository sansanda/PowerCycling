from tkinter import messagebox

def validate_time_parameters(time_parameters, valid_time_parameters):
    """
    Validate timing parameters used in the measurement sequence.

    This function checks that all timing values:
    - Respect their minimum allowed limits.
    - Are coherent with each other.
    - Are positive values.

    Parameters
    ----------
    time_parameters : dict
        Dictionary containing timing values:
        {
            "t_on": float,
            "t_off": float,
            "t_measure_high": float,
            "t_measure_low": float,
            "t_transfer_data": float
        }

    valid_time_parameters : dict
        Dictionary containing minimum allowed timing values:
        {
            "T_OFF_MIN": float,
            "T_MEASURE_LOW_MIN": float,
            "T_TRANSFER_DATA_MIN": float,
            "T_ON_MIN": float,
            "T_MEASURE_HIGH_MIN": float
        }

    Returns
    -------
    bool
        True if all parameters are valid.
        False if any validation fails.
    """

    # Extract timing values
    t_on = time_parameters["t_on"]
    t_off = time_parameters["t_off"]
    t_measure_high = time_parameters["t_measure_high"]
    t_measure_low = time_parameters["t_measure_low"]
    t_transfer_data = time_parameters["t_transfer_data"]

    # Extract limits
    t_on_min = valid_time_parameters["T_ON_MIN"]
    t_off_min = valid_time_parameters["T_OFF_MIN"]
    t_measure_high_min = valid_time_parameters["T_MEASURE_HIGH_MIN"]
    t_measure_low_min = valid_time_parameters["T_MEASURE_LOW_MIN"]
    t_transfer_data_min = valid_time_parameters["T_TRANSFER_DATA_MIN"]

    # Check negative values
    if any(t < 0 for t in [
        t_on,
        t_off,
        t_measure_high,
        t_measure_low,
        t_transfer_data
    ]):
        messagebox.showerror(
            message="Times must be positive",
            title="Time Definition Error"
        )
        return False

    # Minimum limits
    if t_on < t_on_min:
        messagebox.showerror(
            message=f"t_on must be greater than {t_on_min}",
            title="Time Definition Error"
        )
        return False

    if t_off < t_off_min:
        messagebox.showerror(
            message=f"t_off must be greater than {t_off_min}",
            title="Time Definition Error"
        )
        return False

    if t_measure_high < t_measure_high_min:
        messagebox.showerror(
            message=f"t_measure_high must be greater than {t_measure_high_min}",
            title="Time Definition Error"
        )
        return False

    if t_measure_low < t_measure_low_min:
        messagebox.showerror(
            message=f"t_measure_low must be greater than {t_measure_low_min}",
            title="Time Definition Error"
        )
        return False

    if t_transfer_data < t_transfer_data_min:
        messagebox.showerror(
            message=f"t_transfer_data must be greater than {t_transfer_data_min}",
            title="Time Definition Error"
        )
        return False

    # Coherency checks
    if t_on < t_measure_high:
        messagebox.showerror(
            message="t_on must be greater than t_measure_high",
            title="Time Definition Error"
        )
        return False

    if t_off < t_measure_low:
        messagebox.showerror(
            message="t_off must be greater than t_measure_low",
            title="Time Definition Error"
        )
        return False

    if t_off < t_transfer_data:
        messagebox.showerror(
            message="t_off must be greater than t_transfer_data",
            title="Time Definition Error"
        )
        return False

    if t_transfer_data < t_measure_low:
        messagebox.showerror(
            message="t_transfer_data must be greater than t_measure_low",
            title="Time Definition Error"
        )
        return False

    return True
