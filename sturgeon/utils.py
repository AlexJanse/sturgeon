import zipfile
from warnings import warn 

import pandas as pd
import numpy as np

from sturgeon.constants import (
    UNMETHYL_VALUE,
    NOMEASURE_VALUE,
)

def validate_model_file(zip_file: str):
    """Validate the contents of a zip file

    Args:
        zip_file (str): path to the model zip file to be validated

    Raises an error if critical components are missing. Produces warnings if
    non-critical components are missing.
    """
    files_in_zip = zipfile.ZipFile(zip_file).namelist()

    mandatory_files = [
        'model.onnx',
        'decoding.json',
        'probes.csv'
    ]

    for mf in mandatory_files:
        if mf not in files_in_zip:
            err_msg = 'Mandatory file: {mf}, not found in {zf}'.format(
                mf = mf,
                zf = zip_file,
            )
            raise FileNotFoundError(err_msg)

    non_mandatory_files = {
        'calibration.npy': 'score calibration will not be possible',
        'colors.json': 'default colors will be used'
    }

    for nmf, err in non_mandatory_files.items():
        if nmf not in files_in_zip:
            wrn_msg = 'Mandatory file: {mf}, not found in {zf}: {err}'.format(
                mf = mf,
                zf = zip_file,
                err = err,
            )
            warn(wrn_msg)

    return True

def load_bed_file(bed_file: str):
    """Read the contents of a bed file

    Args:
        bed_file (str): path to methylation bed file to be read

    Returns a pandas.DataFrame with the contents of the bed file
    """

    bed_df =  pd.read_csv(
        bed_file, 
        header = 0, 
        index_col = None, 
        delim_whitespace=True
    )
    return bed_df

def validate_bed_file(bed_df: pd.DataFrame, probes_df: pd.DataFrame):
    """Validate the contents of a bed file

    Args:
        bed_file (pd.DataFrame): loaded dataframe with methylation status
        probes_df (pd.DataFrame): dataframe with the probes information

    Raises an error if critical components are missing. Produces warnings if
    non-critical components are missing.
    """

    mandatory_columns = ["methylation_call", "probe_id"]
    for mc in mandatory_columns:
        err_msg = "{} column missing in bed file".format(mc)
        assert mc in bed_df.columns, err_msg

    invalid_vals_idx = np.where(~bed_df['methylation_call'].isin([0, 1]))[0]
    if len(invalid_vals_idx) > 0:
        err_msg = """
        Valid methylation values in 'methylation_call' column are 0 or 1.
        Found the following invalid values:\n
        """
        for i in invalid_vals_idx:
            v = bed_df['methylation_call'].tolist()[i]
            err_msg += "Line {i}: {v}\n".format(i = i+1, v = v)
            raise ValueError(err_msg)

    

    return True





