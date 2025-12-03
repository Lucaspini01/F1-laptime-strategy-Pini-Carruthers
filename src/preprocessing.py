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
