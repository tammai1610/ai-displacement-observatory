"""Build census_occ2010 -> O*NET-SOC 2019 crosswalk.

Sources:
  occ2010.xls          Census 2010 Occupation Code List w/ 2010 SOC codes
  walk2010_2019.csv    O*NET-SOC 2010 -> O*NET-SOC 2019 crosswalk (onetcenter.org)
"""

import re
import pandas as pd

census = pd.read_excel("occ2010.xls", header=None).rename(
    columns={1: "desc", 2: "occ", 3: "soc"}
)
census = census[census["occ"].astype(str).str.strip().str.match(r"^\d{4}$")]
census = census[["desc", "occ", "soc"]].copy()
census["occ"] = census["occ"].astype(str).str.strip().astype(int)
census["soc"] = census["soc"].astype(str).str.strip().str.upper()
census["desc"] = census["desc"].astype(str).str.strip()
census = census[census["soc"].str.match(r"^\d{2}-[\dX]{4}$")]

walk = pd.read_csv("walk2010_2019.csv")
walk.columns = ["onet2010", "title2010", "onet2019", "title2019"]
walk["soc2010"] = walk["onet2010"].str.slice(0, 7)

# prefix of a census SOC pattern: drop trailing wildcard X and trailing zeros
def prefix(soc: str) -> str:
    p = soc.rstrip("X")
    while p.endswith("0") and not p.endswith("-"):
        p = p[:-1]
    return p


census["prefix"] = census["soc"].map(prefix)
census["is_residual"] = census["soc"].str.contains("X")

soc_codes = sorted(walk["soc2010"].unique())

# pass 1: specific patterns claim SOC codes
claimed = {}
for _, r in census[~census["is_residual"]].iterrows():
    for s in soc_codes:
        if s.startswith(r["prefix"]):
            claimed.setdefault(s, []).append(r["occ"])

pairs = [(occ, s) for s, occs in claimed.items() for occ in occs]

# pass 2: residual (XX) patterns take only unclaimed SOC codes under their prefix
for _, r in census[census["is_residual"]].iterrows():
    for s in soc_codes:
        if s.startswith(r["prefix"]) and s not in claimed:
            pairs.append((r["occ"], s))

link = pd.DataFrame(pairs, columns=["census_occ2010", "soc2010"]).drop_duplicates()
out = (
    link.merge(walk[["soc2010", "onet2019"]], on="soc2010", how="inner")
    .rename(columns={"onet2019": "onet_code"})[["census_occ2010", "onet_code"]]
    .drop_duplicates()
    .sort_values(["census_occ2010", "onet_code"])
)

out.to_csv("census_occ_to_onet_crosswalk.csv", index=False)
print("rows", len(out), "census codes", out["census_occ2010"].nunique(),
      "onet codes", out["onet_code"].nunique())

unmapped = sorted(set(census["occ"]) - set(out["census_occ2010"]))
print("census occ with no onet match:", unmapped)
