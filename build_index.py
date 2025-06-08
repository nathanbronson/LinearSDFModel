import sys
from datetime import timedelta

import wrds
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

cmd = "select conm, mkvaltq, gvkey, rdq from comp.fundq"
cmd_shares = "select conm, cshoq, prccq, gvkey, rdq from comp.fundq"

if __name__ == "__main__":
    if sys.argv[1] == "get":
        with wrds.Connection() as db:
            gvkey_df = pd.read_excel("./dataset.xlsx", sheet_name="xoprq", index_col="gvkey")
            conm_df = pd.read_excel("./train_dataset.xlsx", sheet_name="xoprq", index_col="conm")
            val_df = pd.read_excel("./validation_dataset.xlsx", sheet_name="xoprq", index_col="conm")
            dates = pd.to_datetime(pd.concat((conm_df, val_df), axis=1).columns)
            max_date = dates.max()
            cmd += "\n where rdq <= '" + max_date.strftime("%Y-%m-%d") + "'"
            min_date = dates.min()
            cmd += "\n and rdq >= '" + (min_date - timedelta(days=365)).strftime("%Y-%m-%d") + "'"
            gvkeys = gvkey_df.index
            cmd += "\n and conm in ({})".format(", ".join(["'" + str(i).replace("'", "''") + "'" for i in conm_df.index]))
            df = db.raw_sql(cmd)
            df.to_excel("./mktval.xlsx")
    if sys.argv[1] == "get-shares":
        with wrds.Connection() as db:
            gvkey_df = pd.read_excel("./dataset.xlsx", sheet_name="xoprq", index_col="gvkey")
            conm_df = pd.read_excel("./train_dataset.xlsx", sheet_name="xoprq", index_col="conm")
            val_df = pd.read_excel("./validation_dataset.xlsx", sheet_name="xoprq", index_col="conm")
            dates = pd.to_datetime(pd.concat((conm_df, val_df), axis=1).columns)
            max_date = dates.max()
            cmd_shares += "\n where rdq <= '" + max_date.strftime("%Y-%m-%d") + "'"
            min_date = dates.min()
            cmd_shares += "\n and rdq >= '" + (min_date - timedelta(days=365)).strftime("%Y-%m-%d") + "'"
            gvkeys = gvkey_df.index
            cmd_shares += "\n and conm in ({})".format(", ".join(["'" + str(i).replace("'", "''") + "'" for i in conm_df.index]))
            df = db.raw_sql(cmd_shares)
            df["mkvaltq"] = df["cshoq"] * df["prccq"]
            df.drop(["cshoq", "prccq"], axis=1, inplace=True)
            df.to_excel("./mktval.xlsx")
    elif sys.argv[1] == "build":
        df = pd.read_excel("./mktval.xlsx", index_col="gvkey")
        df = df.rename({"mkvaltq": "mktval"}, axis=1).drop("Unnamed: 0", axis=1)
        with open("./company_gvkey_link.txt", "r") as doc:
            link = {v:k for k, v in eval(doc.read()).items()}
        df["conm"] = [link[i] for i in df.index]
        conm_df = pd.read_excel("./train_dataset.xlsx", sheet_name="excess_return", index_col="conm")
        val_df = pd.read_excel("./validation_dataset.xlsx", sheet_name="excess_return", index_col="conm")
        cdf = pd.concat((conm_df, val_df), axis=1)
        dates = pd.to_datetime(cdf.columns)
        for d in dates:
            df = pd.concat((df, pd.DataFrame([[0, 0, d.strftime("%Y-%m-%d"), ""]], columns=["mktval", "gvkey", "rdq", "conm"])))#df.append({"mktval": 0, "gvkey": 0, "rdq": d.strftime("%Y-%m-%d"), "conm": ""})
        df["rdq"] = pd.to_datetime(df["rdq"])
        df = df.pivot(index="conm", columns="rdq", values="mktval")
        df = df[df.columns.sort_values()]
        df = df.drop("", axis=0)
        df = df.ffill(axis=1)
        df = df[cdf.columns]
        sums = df.sum(axis=0)
        weights = df / sums
        if not np.all(np.abs(np.sum(weights.values, axis=0) - 1.) < .01):
            print("Warning: not all weight sums are one: got", np.sum(weights.values, axis=0)[np.abs(np.sum(weights.values, axis=0) - 1.) >= .01])
        if weights.shape[0] != cdf.shape[0]:
            print("Warning: different shapes for weights and original data: {} and {}".format(weights.shape[0], cdf.shape[0]))
        weighted_r_e = cdf.loc[weights.index].values * weights
        index_r_e = weighted_r_e.sum(axis=0)
        ew_r_e = np.mean(cdf.values, axis=0)
        pd.DataFrame.from_dict({"date": df.columns.values, "index_excess_return": index_r_e, "equal_weighted_excess_return": ew_r_e}, orient="columns").set_index("date").to_excel("./index.xlsx")
    elif sys.argv[1] == "inspect":
        df = pd.read_excel("./index.xlsx")
        df = df.rename({"index_excess_return": "index", "equal_weighted_excess_return": "equal_weighted"}, axis=1)
        conm_df = pd.read_excel("./train_dataset.xlsx", sheet_name="FEDFUNDS", index_col="conm")
        val_df = pd.read_excel("./validation_dataset.xlsx", sheet_name="FEDFUNDS", index_col="conm")
        cdf = pd.concat((conm_df, val_df), axis=1)
        (df["index"] + 1. + cdf.values[0, :]).cumprod().plot()
        (df["equal_weighted"] + 1. + cdf.values[0, :]).cumprod().plot()
        plt.legend()
        plt.ylabel("Cumulative Return")
        plt.xlabel("Month")
        plt.show()