import numpy as np
import pandas as pd
import statsmodels.api as sm


# ---------- AI factor ----------

def remove_market(x, market):
    # regress x on the market and keep the residual
    # -> the part of x that the market can't explain
    df = pd.concat([x, market], axis=1, keys=["x", "m"]).dropna()
    X = sm.add_constant(df["m"])
    model = sm.OLS(df["x"], X).fit()
    return model.resid, model.params["m"]


def make_ai_factor(returns, market, ai_stocks, leave_out=None):
    # equal weighted basket of the AI stocks
    # leave_out: drop one stock, used when we estimate that stock's own beta
    members = [t for t in ai_stocks if t != leave_out]
    basket = returns[members].mean(axis=1)
    factor, b = remove_market(basket, market)
    return factor, b


# ---------- betas ----------

def regress(r, market, ai):
    # r = alpha + b_mkt*market + b_ai*ai + error
    df = pd.concat([r, market, ai], axis=1, keys=["r", "mkt", "ai"]).dropna()
    if len(df) < 78:   # need at least ~1.5 years
        return None
    X = sm.add_constant(df[["mkt", "ai"]])
    res = sm.OLS(df["r"], X).fit()
    return {
        "beta_mkt": res.params["mkt"],
        "beta_ai": res.params["ai"],
        "t_ai": res.tvalues["ai"],
        "ci_low": res.conf_int().loc["ai", 0],
        "ci_high": res.conf_int().loc["ai", 1],
        "r2": res.rsquared,
        "resid_var": res.resid.var(),
        "weeks": int(res.nobs),
    }


def all_betas(returns, market, ai_factor, stocks, ai_stocks):
    rows = {}
    for t in returns.columns:
        if t in ai_stocks:
            # don't measure an AI stock against a basket that includes itself
            f, _ = make_ai_factor(returns, market, ai_stocks, leave_out=t)
        else:
            f = ai_factor
        res = regress(returns[t], market, f)
        if res is None:
            print("skipping", t, "(too little data)")
            continue
        res["name"] = stocks[t][0]
        res["group"] = stocks[t][2]
        rows[t] = res
    df = pd.DataFrame(rows).T
    num = ["beta_mkt", "beta_ai", "t_ai", "ci_low", "ci_high", "r2", "resid_var", "weeks"]
    df[num] = df[num].astype(float)
    return df


# ---------- portfolio ----------

def make_weights(tickers, stocks, nordic_share, global_share):
    # equal weight inside each region
    nordic = [t for t in tickers if stocks[t][1] == "nordic"]
    glob = [t for t in tickers if stocks[t][1] == "global"]
    w = {}
    for t in nordic:
        w[t] = nordic_share / len(nordic)
    for t in glob:
        w[t] = global_share / len(glob)
    return pd.Series(w)


def portfolio_returns(returns, w):
    # if a stock has no data some week, spread its weight on the others
    w = w.reindex(returns.columns).fillna(0)
    has_data = returns.notna()
    weights = has_data * w
    weights = weights.div(weights.sum(axis=1), axis=0)
    return (returns.fillna(0) * weights).sum(axis=1)


def by_group(betas, w):
    df = betas[["group"]].copy()
    df["weight"] = w
    df["ai_contrib"] = w * betas["beta_ai"]
    g = df.groupby("group")[["weight", "ai_contrib"]].sum()
    g["share_of_ai"] = g["ai_contrib"] / g["ai_contrib"].sum()
    return g.sort_values("ai_contrib", ascending=False)


def risk_split(betas, w, market, ai_factor):
    # variance = market part + AI part + stock specific part
    # (market and ai factor are uncorrelated, so no cross term)
    b_mkt = (w * betas["beta_mkt"]).sum()
    b_ai = (w * betas["beta_ai"]).sum()
    market_part = b_mkt**2 * market.var()
    ai_part = b_ai**2 * ai_factor.var()
    stock_part = (w**2 * betas["resid_var"]).sum()
    total = market_part + ai_part + stock_part
    out = pd.Series({"market": market_part, "ai": ai_part, "stock_specific": stock_part}) / total
    vol = np.sqrt(total * 52)
    return out, vol


# ---------- stress ----------

def scenario(betas, w, b_basket, shock_ai, shock_market):
    # turn "AI basket -25%, market -10%" into an AI-specific shock first
    ai_shock = shock_ai - b_basket * shock_market
    est = betas["beta_mkt"] * shock_market + betas["beta_ai"] * ai_shock
    port = (w * est).sum()
    groups = (w * est).groupby(betas["group"]).sum() / w.groupby(betas["group"]).sum()
    return port, groups.sort_values(), ai_shock


def week_containing(date, index):
    return index[index >= pd.Timestamp(date)][0]


def calm_vs_stress(returns, market, w, ai_stocks):
    # stress = the 10% worst weeks for the market
    ai = [t for t in returns.columns if t in ai_stocks]
    rest = [t for t in returns.columns if t not in ai_stocks]
    ai_leg = portfolio_returns(returns[ai], w[ai])
    rest_leg = portfolio_returns(returns[rest], w[rest])
    stress = market <= market.quantile(0.10)
    table = pd.DataFrame({
        "weeks": [(~stress).sum(), stress.sum()],
        "corr_ai_vs_rest": [ai_leg[~stress].corr(rest_leg[~stress]),
                            ai_leg[stress].corr(rest_leg[stress])],
    }, index=["calm", "stress"])
    rolling = ai_leg.rolling(26).corr(rest_leg)
    return table, rolling, stress
