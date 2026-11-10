import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

COLORS = {
    "direct_ai": "#1d4e89", "power_grid": "#d1495b", "semi_supply": "#edae49",
    "other_tech": "#7b6d8d", "industrial": "#00798c", "financial": "#5c946e",
    "health": "#a3a3a3", "consumer": "#c4c4c4", "telecom": "#8d8d8d", "energy": "#6b4f3f",
}
NAMES = {
    "direct_ai": "Direct AI", "power_grid": "Power & grid", "semi_supply": "Chip suppliers",
    "other_tech": "Other tech", "industrial": "Industrials", "financial": "Financials",
    "health": "Health care", "consumer": "Consumer", "telecom": "Telecom", "energy": "Energy",
}
OUT = "output"


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_ai_betas(betas):
    # only the non-AI stocks, that's where the hidden exposure is
    b = betas[betas["group"] != "direct_ai"].sort_values("beta_ai")
    fig, ax = plt.subplots(figsize=(7, 0.22 * len(b) + 1))
    y = np.arange(len(b))
    ax.barh(y, b["beta_ai"], color=[COLORS[g] for g in b["group"]])
    err = [b["beta_ai"] - b["ci_low"], b["ci_high"] - b["beta_ai"]]
    ax.errorbar(b["beta_ai"], y, xerr=err, fmt="none", ecolor="black", lw=0.6, capsize=1.5)
    ax.set_yticks(y)
    ax.set_yticklabels(b["name"])
    ax.axvline(0, color="black", lw=0.6)
    ax.set_xlabel("AI beta (market removed), with 95% interval")
    ax.set_title("AI exposure in stocks outside the AI basket")
    groups = b["group"].unique()
    ax.legend([plt.Rectangle((0, 0), 1, 1, color=COLORS[g]) for g in groups],
              [NAMES[g] for g in groups], frameon=False, fontsize=7, loc="lower right")
    save(fig, "1_ai_betas.png")


def plot_weight_vs_ai(groups):
    g = groups.copy()
    g["weight_share"] = g["weight"] / g["weight"].sum()
    x = np.arange(len(g))
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.bar(x - 0.2, g["weight_share"] * 100, 0.4, color="#b0b7c3", label="% of portfolio weight")
    ax.bar(x + 0.2, g["share_of_ai"] * 100, 0.4, color=[COLORS[k] for k in g.index],
           label="% of portfolio AI beta")
    ax.set_xticks(x)
    ax.set_xticklabels([NAMES[k] for k in g.index], rotation=30, ha="right")
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel("%")
    ax.legend(frameon=False)
    ax.set_title("Weight vs share of AI exposure, by group")
    save(fig, "2_weight_vs_ai.png")


def plot_risk(split, vol):
    labels = ["Market", "AI-specific", "Stock-specific"]
    vals = split.values * 100
    fig, ax = plt.subplots(figsize=(4.5, 2.6))
    ax.bar(labels, vals, color=["#b0b7c3", "#1d4e89", "#d9d9d9"], width=0.6)
    for i, v in enumerate(vals):
        ax.text(i, v + 1.5, f"{v:.0f}%", ha="center", fontsize=8)
    ax.set_ylim(0, max(vals) * 1.15)
    ax.set_ylabel("% of portfolio variance")
    ax.set_title(f"Where the risk comes from (vol {vol*100:.1f}% per year)")
    save(fig, "3_risk_split.png")


def plot_rolling_corr(rolling, stress):
    fig, ax = plt.subplots(figsize=(7, 2.6))
    ax.plot(rolling.index, rolling, color="#1d4e89", lw=1.2)
    for d in stress[stress].index:
        ax.axvline(d, color="#d1495b", alpha=0.3, lw=2)
    ax.set_ylabel("correlation")
    ax.set_title("26-week correlation, AI stocks vs rest of portfolio (red = worst market weeks)")
    save(fig, "4_rolling_corr.png")


def plot_scenario(port, groups, title):
    s = groups * 100
    fig, ax = plt.subplots(figsize=(6, 2.8))
    ax.barh([NAMES[k] for k in s.index], s.values, color=[COLORS[k] for k in s.index])
    ax.axvline(port * 100, color="black", ls="--", lw=0.8)
    ax.text(port * 100, len(s) - 0.5, " portfolio", fontsize=7)
    ax.set_xlabel("estimated return, %")
    ax.set_title(title)
    save(fig, "5_scenario.png")
