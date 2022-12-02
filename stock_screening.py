import requests
import pandas as pd
import numpy as np


def get_data(source="fundamentus"):
    if source == "fundamentus":
        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"}
        html = requests.get("https://www.fundamentus.com.br/resultado.php", headers=header).text
        dataframe = pd.read_html(html, thousands=".", decimal=",")[0]
    else:
        dataframe = pd.read_csv("acoes.csv", sep=";")
    return dataframe


def coluna_to_float(x):
    if not pd.isnull(x):
        return float(x.replace(".", "").replace(",", "."))
    else:
        return None


source = "local"

df = get_data(source=source)

if source == "local":
    for col in ["P/L", "EV/EBIT", "ROE", "ROIC", " VPA", " LPA", "PRECO", ' VALOR DE MERCADO']:
        df[col] = df[col].apply(lambda x: coluna_to_float(x))

    df = df[df[' VALOR DE MERCADO'] > 500000000]

    for col in ["P/L", "EV/EBIT"]:
        df = df[df[col] > 0.5].reset_index(drop=True)
    for col in ["ROE", "ROIC"]:
        df = df[df[col] < 100].reset_index(drop=True)

    # Benjamin Graham intrinsic value
    df["intrinsic_value"] = np.sqrt(22.5 * df[" VPA"] * df[" LPA"])
    df["intrinsic_value_upside"] = (df["intrinsic_value"] / df["PRECO"]) - 1
    df = df[df["intrinsic_value_upside"] > 1]

    # Joel Greenblatt Magic Formula
    for col in ["P/L", "EV/EBIT"]:
        df[f"ranking_{col}"] = df[col].rank(axis=0, method="first").astype(int)

    for col in ["ROE", "ROIC", "intrinsic_value_upside"]:
        df[f"ranking_{col}"] = df[col].rank(axis=0, method="first", ascending=False).astype(int)

    df["ranking_greenblat"] = 0
    for col in ["P/L", "EV/EBIT", "ROE", "ROIC", "intrinsic_value_upside"]:
        df["ranking_greenblat"] = df["ranking_greenblat"] + df[f"ranking_{col}"]

    columns = ["TICKER", "P/L", "EV/EBIT", "ROE", "ROIC", "ranking_P/L", "ranking_EV/EBIT", "ranking_ROE",
               "ranking_ROIC", "ranking_intrinsic_value_upside",
               "ranking_greenblat", " VPA", " LPA", "intrinsic_value", "PRECO", "intrinsic_value_upside"]
    df = df[columns]
    print(df.sort_values(by="ranking_greenblat").head(20))
