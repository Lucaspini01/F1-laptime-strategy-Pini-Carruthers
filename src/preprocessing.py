import numpy as np
import pandas as pd

def clean_session(col_laps, laptime_max_s=None, delta_from_best=None, verbose=True):
    """
    Limpia una sesión de prácticas filtrando vueltas demasiado lentas.
    
    Parámetros
    ----------
    col_laps : DataFrame de una práctica (solo Colapinto)
    laptime_max_s : float o None
        Umbral absoluto en segundos. Se mantienen solo vueltas con LapTime_s <= laptime_max_s.
    delta_from_best : float o None
        Si se pasa, se ignora laptime_max_s y se define:
        cut = best_lap + delta_from_best
    """
    df = col_laps.copy()
    
    if "LapTime_s" not in df.columns:
        df["LapTime_s"] = df["LapTime"].dt.total_seconds()
    
    best = df["LapTime_s"].min()
    
    if delta_from_best is not None:
        cut = best + delta_from_best
    elif laptime_max_s is not None:
        cut = laptime_max_s
    else:
        raise ValueError("Tenés que pasar laptime_max_s o delta_from_best")
    
    before = len(df)
    df = df[df["LapTime_s"] <= cut].copy()
    after = len(df)
    
    if verbose:
        print(f"Best lap: {best:.3f} s, corte: {cut:.3f} s")
        print(f"Vueltas antes: {before}, después del filtrado: {after} (se eliminaron {before - after})")
    
    return df, cut


# FEATURE ENGINEERING

# src/preprocessing.py

import pandas as pd
import numpy as np

def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering v1 para el problema de LapTime.
    No usa LapTime ni info futura. Devuelve un nuevo DataFrame.
    """
    df = df.copy()

    # 1) LapNumber normalizado por sesión (fase de la sesión)
    if {"Session", "LapNumber"}.issubset(df.columns):
        max_laps_session = df.groupby("Session")["LapNumber"].transform("max")
        df["lap_norm_session"] = df["LapNumber"] / max_laps_session

    # 2) Progresión dentro del stint
    if {"Session", "Stint", "LapNumber"}.issubset(df.columns):
        # largo del stint
        stint_sizes = df.groupby(["Session", "Stint"])["LapNumber"].transform("count")
        df["stint_len"] = stint_sizes

        # índice de vuelta dentro del stint (1..stint_len)
        df["stint_lap_index"] = (
            df.groupby(["Session", "Stint"]).cumcount() + 1
        )

        # normalizado 0..1
        df["stint_lap_norm"] = df["stint_lap_index"] / df["stint_len"]

    # 3) TyreLife normalizado dentro del stint
    if {"Session", "Stint", "TyreLife"}.issubset(df.columns):
        max_tyre_stint = df.groupby(["Session", "Stint"])["TyreLife"].transform("max")
        # evitar división por cero o NaN
        df["tyrelife_norm_stint"] = df["TyreLife"] / max_tyre_stint.replace(0, np.nan)

    # 4) Indicador de carrera vs práctica
    if "Session" in df.columns:
        df["is_race"] = (df["Session"] == "RACE").astype(int)

    # 5) Orden de compuestos (más blando -> más duro)
    if "Compound" in df.columns:
        compound_map = {
            "SOFT": 0,
            "MEDIUM": 1,
            "HARD": 2,
            "INTERMEDIATE": 3,
            "WET": 4,
        }
        df["compound_order"] = df["Compound"].map(compound_map).astype("float")

    return df
