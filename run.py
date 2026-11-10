import os
import pandas as pd

import config as cfg
import data
import analysis as an
import plots

pd.set_option("display.width", 140)
pd.set_option("display.float_format", lambda x: f"{x:.3f}")

tickers = list(cfg.STOCKS)

# --- data ---
prices = data.get_prices_sek(tickers + [cfg.MARKET], cfg.START, cfg.END)
returns = data.weekly_returns(prices)
market = returns.pop(cfg.MARKET).dropna()
returns = returns.loc[market.index]
print(f"{len(returns)} weeks, {returns.index[0].date()} to {returns.index[-1].date()}")

# --- AI factor (AI basket with the market part removed) ---
ai_factor, b_basket = an.make_ai_factor(returns, market, cfg.AI_STOCKS)
print(f"AI basket beta vs market: {b_basket:.2f}")
print(f"check, corr(ai factor, market) = {ai_factor.corr(market):.3f}  (should be ~0)")

# --- betas ---
betas = an.all_betas(returns, market, ai_factor, cfg.STOCKS, cfg.AI_STOCKS)

# --- portfolio ---
w = an.make_weights(list(betas.index), cfg.STOCKS, cfg.NORDIC_SHARE, cfg.GLOBAL_SHARE)
betas["weight"] = w

b_mkt = (w * betas["beta_mkt"]).sum()
b_ai = (w * betas["beta_ai"]).sum()
groups = an.by_group(betas, w)
split, vol = an.risk_split(betas, w, market, ai_factor)

# sanity check: run the regression directly on the portfolio's returns
port = an.portfolio_returns(returns[betas.index], w)
check = an.regress(port, market, ai_factor)

print("\nBetas:")
print(betas[["name", "group", "weight", "beta_mkt", "beta_ai", "t_ai", "r2"]]
      .sort_values("beta_ai", ascending=False).to_string())
print(f"\nPortfolio beta_mkt = {b_mkt:.2f}, beta_ai = {b_ai:.2f}")
print(f"(regression on portfolio returns: {check['beta_mkt']:.2f}, {check['beta_ai']:.2f})")
print("\nBy group:")
print(groups.to_string())
print(f"\nRisk split (annual vol {vol:.1%}):")
print(split.to_string())

# --- stress tests ---
wk = an.week_containing(cfg.DEEPSEEK_DATE, returns.index)
pred = b_mkt * market[wk] + b_ai * ai_factor[wk]
print(f"\nDeepSeek week (ending {wk.date()}): market {market[wk]:.1%}, AI factor {ai_factor[wk]:.1%}")
print(f"portfolio actual {port[wk]:.1%}, model {pred:.1%}")
print((returns.loc[wk, betas.index] * w).groupby(betas["group"]).sum()
      / w.groupby(betas["group"]).sum())

scen_port, scen_groups, ai_shock = an.scenario(betas, w, b_basket, cfg.SCEN_AI, cfg.SCEN_MARKET)
print(f"\nScenario AI {cfg.SCEN_AI:.0%} / market {cfg.SCEN_MARKET:.0%} "
      f"(AI-specific shock {ai_shock:.1%}): portfolio {scen_port:.1%}")
print(scen_groups.to_string())

corr_table, rolling, stress = an.calm_vs_stress(returns[betas.index], market, w, cfg.AI_STOCKS)
print("\nCalm vs stress weeks:")
print(corr_table.to_string())

# --- save ---
os.makedirs("output", exist_ok=True)
betas.sort_values("beta_ai", ascending=False).to_csv("output/betas.csv")
groups.to_csv("output/groups.csv")

plots.plot_ai_betas(betas)
plots.plot_weight_vs_ai(groups)
plots.plot_risk(split, vol)
plots.plot_rolling_corr(rolling, stress)
plots.plot_scenario(scen_port, scen_groups, f"Scenario: AI basket {cfg.SCEN_AI:.0%}, market {cfg.SCEN_MARKET:.0%}")
print("\ncharts saved in output/")

# TODO: rolling betas over time (e.g. ABB) to see if AI exposure has grown since 2023
