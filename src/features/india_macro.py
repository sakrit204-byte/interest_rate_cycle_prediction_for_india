"""Monthly India price and activity panel with the date each value became public.

Inputs: the MoSPI raw files saved by src.ingestion.mospi (latest per query).
Output: data/interim/india/india_macro_monthly.csv, one row per reference month.

Growth rates are computed within one index base (value against the same month a year
earlier on the same base), then spliced by taking the newest base that covers the month.
No linking factors are needed because rates, not levels, are spliced.

Publication dates are not in the API, so each series gets a conservative availability
rule (RELEASE_RULES). A value may only be used for a decision whose information cutoff is
on or after its available_from date. The rules are assumptions to verify against MoSPI and
Office of the Economic Adviser release calendars; see docs/data_access.md.

Usage: python -m src.features.india_macro
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "india" / "mospi"
OUT = ROOT / "data" / "interim" / "india" / "india_macro_monthly.csv"

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], start=1)}

CPI_SUBGROUPS = {
    "General-Overall": "cpi",
    "Consumer Food Price-Overall": "cpi_food",
    "Fuel and Light-Overall": "cpi_fuel",
}

# months after the reference month, and day of that month, from which a value is public
RELEASE_RULES = {
    "cpi": [("2014-01", 1, 15), (None, 1, "end")],   # about the 12th of t+1 from 2014
    "wpi": [(None, 1, 15)],                           # about the 14th of t+1
    "iip": [(None, 2, 15)],                           # about the 12th of t+2
}


def latest(prefix: str) -> Path:
    files = sorted(RAW.glob(f"{prefix}_*.csv"))
    if not files:
        raise FileNotFoundError(f"no raw file for {prefix}; run python -m src.ingestion.mospi")
    return files[-1]


def add_period(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["period"] = pd.PeriodIndex.from_fields(
        year=df["year"].astype(int), month=df["month"].map(MONTHS), freq="M")
    return df


def yoy(levels: pd.Series) -> pd.Series:
    """Percent change on the same month a year earlier; levels indexed by monthly period."""
    lag = levels.copy()
    lag.index = lag.index + 12
    return (levels / lag.reindex(levels.index) - 1) * 100


def cpi_series() -> tuple[pd.DataFrame, list[str]]:
    """CPI combined, All India, base 2012, with yoy recomputed and checked against MoSPI."""
    notes = []
    raw = add_period(pd.read_csv(latest("cpi_2012_all_india")))
    raw = raw[(raw["sector"] == "Combined") & raw["subgroup"].isin(CPI_SUBGROUPS)]
    raw = raw.dropna(subset=["index"])
    out = {}
    for subgroup, name in CPI_SUBGROUPS.items():
        s = raw[raw["subgroup"] == subgroup]
        dup = s["period"].duplicated(keep=False)
        if dup.any():
            # duplicate months (January to May 2013 on this API): keep the row that carries
            # the published inflation rate, which is the series MoSPI computes inflation on
            notes.append(f"{name}: {s.loc[dup, 'period'].nunique()} duplicated months resolved")
            s = s.sort_values("inflation", na_position="first").drop_duplicates("period", keep="last")
        s = s.set_index("period").sort_index()
        level = s["index"].astype(float)
        rate = yoy(level)
        published = pd.to_numeric(s["inflation"], errors="coerce")
        gap = (rate - published).abs().dropna()
        notes.append(f"{name}: yoy recomputed vs published, max abs gap {gap.max():.2f} pp over {len(gap)} months; "
                     f"months above 0.05 pp: {', '.join(str(p) for p in gap[gap > 0.05].index) or 'none'}")
        out[f"{name}_index"] = level
        # published rates are used where present: MoSPI computed January to May 2014 on revised
        # 2013 levels that differ from the 2013 levels kept on the API, so recomputing from
        # the stored levels would not reproduce the rates that were actually released
        out[f"{name}_yoy"] = published.combine_first(rate).round(4)
        if name == "cpi":
            out["cpi_imputed"] = s["status"].ne("F").astype(int)
    return pd.DataFrame(out), notes


def spliced_yoy(prefixes: list[str], value_col: str) -> tuple[pd.Series, pd.Series]:
    """yoy within each base, newest base first; returns the rate and the base used."""
    rate = pd.Series(dtype=float)
    base = pd.Series(dtype=object)
    for prefix in prefixes:  # newest first
        df = add_period(pd.read_csv(latest(prefix)))
        if "type" in df:
            df = df[df["category"] == "General"]
        level = df.set_index("period")[value_col].astype(float).sort_index()
        r = yoy(level).dropna()
        new = r.index.difference(rate.index)
        rate = pd.concat([rate, r.loc[new]])
        base = pd.concat([base, pd.Series(df["base_year"].iloc[0], index=new)])
    return rate.sort_index().round(4), base.sort_index()


def available_from(periods: pd.PeriodIndex, series: str) -> pd.Series:
    out = []
    for p in periods:
        for start, months_after, day in RELEASE_RULES[series]:
            if start is None or p >= pd.Period(start, "M"):
                release_month = p + months_after
                out.append(release_month.end_time.normalize() if day == "end"
                           else release_month.start_time + pd.Timedelta(days=day - 1))
                break
    return pd.Series(out, index=periods)


def imf_cpi_yoy() -> pd.Series:
    """IMF published yoy for India headline CPI, used only after the MoSPI 2012 base ends.

    The CPI 2024=100 series (from January 2026) is not on the MoSPI API; the IMF series
    continues it and matches MoSPI to a mean absolute 0.06 pp over 2012 to 2025.
    """
    files = sorted((ROOT / "data" / "raw" / "international" / "imf").glob("CPI_ind_cpi_*.csv"))
    if not files:
        return pd.Series(dtype=float)
    df = pd.read_csv(files[-1])
    df = df[(df["COICOP_1999"] == "_T") & (df["TYPE_OF_TRANSFORMATION"] == "YOY_PCH_PA_PT")]
    df = df.dropna(subset=["OBS_VALUE"])
    return pd.Series(df["OBS_VALUE"].astype(float).values,
                     index=pd.PeriodIndex(df["TIME_PERIOD"].str.replace("-M", "-"), freq="M"))


def build() -> tuple[pd.DataFrame, list[str]]:
    cpi, notes = cpi_series()
    imf = imf_cpi_yoy()
    overlap = (cpi["cpi_yoy"] - imf).abs().dropna()
    if len(overlap):
        notes.append(f"cpi vs IMF yoy: mean abs gap {overlap.mean():.3f} pp over {len(overlap)} months, "
                     f"{overlap.loc['2023-01':].mean():.3f} pp from 2023")
    fill = imf.loc[imf.index > cpi["cpi_yoy"].dropna().index.max()]
    cpi = cpi.reindex(cpi.index.union(fill.index))
    cpi["cpi_source"] = cpi["cpi_yoy"].notna().map({True: "mospi_2012", False: ""})
    cpi.loc[fill.index, "cpi_yoy"] = fill.round(4)
    cpi.loc[fill.index, "cpi_source"] = "imf"
    wpi, wpi_base = spliced_yoy(["wpi_2011_12_headline", "wpi_2004_05_headline", "wpi_1993_94_headline"], "index_value")
    iip, iip_base = spliced_yoy(["iip_2022_23_general", "iip_2011_12_general",
                                 "iip_2004_05_general", "iip_1993_94_general"], "index")
    panel = pd.DataFrame({"wpi_yoy": wpi, "wpi_base": wpi_base, "iip_yoy": iip, "iip_base": iip_base})
    panel = panel.join(cpi, how="outer").sort_index()
    for series in RELEASE_RULES:
        panel[f"{series}_available_from"] = available_from(panel.index, series).dt.date
    panel.index.name = "month"
    return panel, notes


def main() -> int:
    panel, notes = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT)
    for n in notes:
        print(n)
    for col in ["cpi_yoy", "wpi_yoy", "iip_yoy"]:
        s = panel[col].dropna()
        print(f"{col}: {s.index.min()} to {s.index.max()} ({len(s)} months)")
    print(f"written {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
