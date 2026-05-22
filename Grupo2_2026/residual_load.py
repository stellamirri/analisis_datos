import pandas as pd


def calculate_residual_load(df):
    """
    Residual load calculation.

    residual load = demand - wind - solar
    """

    df = df.copy()

    df["residual_load"] = (
        df["demand"]
        - df["wind"]
        - df["solar"]
    )

    return df


def renewable_share(df):
    """
    Renewable share calculation.
    """

    df = df.copy()

    df["renewable_generation"] = (
        df["wind"]
        + df["solar"]
    )

    df["renewable_share"] = (
        df["renewable_generation"]
        / df["demand"]
    )

    return df