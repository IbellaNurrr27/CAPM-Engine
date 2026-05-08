"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              CAPM YIELD ENGINE  //  Capital Asset Pricing Model             ║
║              E(Ri) = Rf + beta(E(Rm) - Rf)                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import pandas as pd
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.columns import Columns
from rich.rule import Rule
from rich.align import Align
from rich import box
import time

console = Console()

# ── Color Palette ──────────────────────────────────────────────────────────────
C_BLUE   = "bold #3D6EFF"
C_CYAN   = "bold #2EC4B6"
C_GOLD   = "bold #FF9F1C"
C_RED    = "bold #FF4D6D"
C_MUTED  = "#666688"
C_WHITE  = "bold white"
C_DIM    = "dim white"
C_GREEN  = "bold #2EC47A"
C_VIOLET = "#A78BFF"


def clear():
    """Clear terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    """Display the CAPM Engine banner."""
    clear()
    console.print()

    title_lines = [
        ("  ██████╗ █████╗ ██████╗ ███╗   ███╗", "#3D6EFF"),
        (" ██╔════╝██╔══██╗██╔══██╗████╗ ████║", "#5B7FFF"),
        (" ██║     ███████║██████╔╝██╔████╔██║", "#7B9FFF"),
        (" ██║     ██╔══██║██╔═══╝ ██║╚██╔╝██║", "#9BB8FF"),
        (" ╚██████╗██║  ██║██║     ██║ ╚═╝ ██║", "#AECBFF"),
        ("  ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚═╝", "dim #AECBFF"),
    ]

    title = Text()
    for line, color in title_lines:
        title.append(line + "\n", style=color)

    console.print(Align.center(title))

    subtitle = Text("  YIELD ENGINE  //  Capital Asset Pricing Model  //  v1.0", style=C_MUTED)
    console.print(Align.center(subtitle))
    console.print()

    formula_panel = Panel(
        Align.center(
            Text.from_markup(
                "[bold #FFD700]E(Ri)[/] [dim white]=[/] [bold #3D6EFF]Rf[/] [dim white]+[/] "
                "[bold #FF9F1C]beta[/] [dim white]x[/] [dim white]([/][bold #2EC4B6]E(Rm)[/] [dim white]-[/] [bold #3D6EFF]Rf[/][dim white])[/]\n\n"
                "[dim]Expected Return = Risk-Free Rate + Beta x Market Risk Premium[/]"
            )
        ),
        border_style="#3D6EFF",
        title="[bold #3D6EFF] CAPM FORMULA [/]",
        title_align="center",
        padding=(1, 4),
    )
    console.print(formula_panel)
    console.print()


def parse_rate(value_str: str, label: str) -> float:
    """
    Parse a rate input that can be decimal (0.05) or percentage (5 or 5%).
    Returns the value as a decimal (e.g., 0.05 for 5%).
    """
    value_str = value_str.strip().rstrip("%")
    try:
        value = float(value_str)
    except ValueError:
        raise ValueError(f"Invalid input for {label}: '{value_str}' — must be a number.")

    # Auto-detect: if abs(value) >= 1 treat as percentage
    if abs(value) >= 1:
        console.print(
            f"  [dim]  -> Interpreting {value}% as {value / 100:.4f} (decimal)[/dim]"
        )
        return value / 100.0
    return value


def get_market_params():
    """
    Prompt user for the global market parameters:
      - Risk-Free Rate (Rf)
      - Expected Market Return E(Rm)
    Returns both as decimals.
    """
    console.print(Panel(
        "[bold white]Step 1:[/] Enter the [bold #3D6EFF]global market parameters[/].\n"
        "[dim]These apply to ALL assets in this session.[/dim]",
        border_style="#333355",
        padding=(0, 2),
    ))
    console.print()

    # Risk-Free Rate
    console.print(f"  [bold #3D6EFF]Rf[/]  [dim]Risk-Free Rate[/dim]  [dim](e.g. 0.04 or 4%)[/dim]")
    rf_str = Prompt.ask("  [bold #3D6EFF]  ->[/]")
    rf = parse_rate(rf_str, "Risk-Free Rate (Rf)")

    console.print()

    # Expected Market Return
    console.print(f"  [bold #2EC4B6]E(Rm)[/]  [dim]Expected Market Return[/dim]  [dim](e.g. 0.10 or 10%)[/dim]")
    rm_str = Prompt.ask("  [bold #2EC4B6]  ->[/]")
    rm = parse_rate(rm_str, "Expected Market Return E(Rm)")

    # ── Market Risk Premium: calculated as a separate clarity step ──────────────
    mrp = rm - rf

    console.print()
    mrp_color = "#2EC47A" if mrp >= 0 else "#FF4D6D"
    mrp_panel = Panel(
        Text.from_markup(
            f"  [bold #3D6EFF]Rf[/]         = [bold white]{rf * 100:.4f}%[/]\n"
            f"  [bold #2EC4B6]E(Rm)[/]      = [bold white]{rm * 100:.4f}%[/]\n"
            f"  ─────────────────────────────\n"
            f"  [bold]MRP[/]        = [{mrp_color}]{mrp * 100:+.4f}%[/]  "
            f"[dim](Market Risk Premium = E(Rm) - Rf)[/dim]"
        ),
        title="[bold] Market Parameters Locked [/]",
        border_style="#2EC4B6",
        padding=(0, 2),
    )
    console.print(mrp_panel)
    console.print()

    return rf, rm


def classify_beta(beta: float) -> str:
    """Classify beta value into a human-readable risk profile."""
    if beta < 0:
        return "INVERSE"
    elif beta < 0.5:
        return "DEFENSIVE"
    elif beta < 1.0:
        return "LOW RISK"
    elif beta == 1.0:
        return "MARKET NEUTRAL"
    elif beta < 1.5:
        return "MODERATE"
    elif beta < 2.0:
        return "AGGRESSIVE"
    else:
        return "HIGH RISK"


def get_asset(index: int, rf: float, rm: float):
    """
    Prompt user for a single asset's data and compute its CAPM expected return.
    Returns a dict with all asset data, or None if user is done.
    """
    # Market Risk Premium (pre-calculated for display)
    mrp = rm - rf

    console.print(Rule(f"[bold #A78BFF] Asset #{index} [/]", style="#333355"))
    console.print()

    # Asset name
    name = Prompt.ask(
        f"  [bold #A78BFF]Asset name[/] [dim](e.g. 'AAPL', 'Stock A', or leave blank to finish)[/dim]"
    )
    if not name.strip():
        return None

    # Beta coefficient
    console.print(f"\n  [bold #FF9F1C]Beta[/]  [dim]Market sensitivity (e.g. 1.2 = 20% more volatile)[/dim]")
    beta_str = Prompt.ask("  [bold #FF9F1C]  ->[/]")
    beta = float(beta_str.strip())

    # ── CAPM CORE CALCULATION ──────────────────────────────────────────────────
    # E(Ri) = Rf + beta * (E(Rm) - Rf)
    expected_return = rf + beta * mrp
    premium_over_rf = expected_return - rf
    risk_profile = classify_beta(beta)

    console.print()
    with Progress(
        SpinnerColumn(style="#3D6EFF"),
        TextColumn("[bold #3D6EFF]Computing CAPM...[/]"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task("calc", total=None)
        time.sleep(0.45)

    result_panel = Panel(
        Text.from_markup(
            f"  [dim]E(Ri) = Rf + beta x MRP[/dim]\n"
            f"  [dim]E(Ri) = {rf*100:.3f}% + {beta} x {mrp*100:.3f}%[/dim]\n"
            f"  [dim]E(Ri) = {rf*100:.3f}% + {beta * mrp * 100:.3f}%[/dim]\n"
            f"  ─────────────────────────────────────────\n"
            f"  [bold #FFD700]E(Ri)[/] = [bold white]{expected_return * 100:.4f}%[/]  "
            f"  |  Risk Profile: [bold white]{risk_profile}[/bold white]\n"
            f"  [dim]Premium over Rf: +{premium_over_rf * 100:.4f}%[/dim]"
        ),
        title=f"[bold] {name} — CAPM Result [/]",
        border_style="#FFD700",
        padding=(0, 2),
    )
    console.print(result_panel)
    console.print()

    return {
        "Asset":            name,
        "Beta":             beta,
        "Risk Profile":     risk_profile,
        "Rf (%)":           round(rf * 100, 4),
        "E(Rm) (%)":        round(rm * 100, 4),
        "MRP (%)":          round(mrp * 100, 4),
        "Beta x MRP (%)":   round(beta * mrp * 100, 4),
        "E(Ri) (%)":        round(expected_return * 100, 4),
        "Premium > Rf (%)": round(premium_over_rf * 100, 4),
    }


def render_final_table(df: pd.DataFrame):
    """Render the full pandas DataFrame as a Rich table."""
    console.print()
    console.print(Rule("[bold #3D6EFF] FULL SESSION RESULTS [/]", style="#3D6EFF"))
    console.print()

    table = Table(
        box=box.SIMPLE_HEAVY,
        border_style="#333355",
        header_style="bold #3D6EFF",
        show_lines=True,
        padding=(0, 1),
        title="[bold white]CAPM Expected Returns — All Assets[/]",
        title_style="bold white",
        caption=(
            f"[dim]Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  "
            f"|  Formula: E(Ri) = Rf + beta x (E(Rm) - Rf)[/dim]"
        ),
    )

    table.add_column("Asset",        style="bold white",   justify="left",   min_width=12)
    table.add_column("Beta",         style="#FF9F1C",      justify="center", min_width=6)
    table.add_column("Risk Profile", style="white",        justify="center", min_width=14)
    table.add_column("Rf %",         style="#3D6EFF",      justify="right",  min_width=8)
    table.add_column("E(Rm) %",      style="#2EC4B6",      justify="right",  min_width=8)
    table.add_column("MRP %",        style="#A78BFF",      justify="right",  min_width=8)
    table.add_column("B x MRP %",    style="dim white",    justify="right",  min_width=9)
    table.add_column("E(Ri) %",      style="bold #FFD700", justify="right",  min_width=10)
    table.add_column("vs Rf",        justify="right",      min_width=9)

    for _, row in df.iterrows():
        er = row["E(Ri) (%)"]
        prem = row["Premium > Rf (%)"]
        beta = row["Beta"]

        # Color expected return by magnitude
        if er >= 15:
            er_str = f"[bold #FF4D6D]{er:.4f}%[/]"
        elif er >= 10:
            er_str = f"[bold #FF9F1C]{er:.4f}%[/]"
        elif er >= 5:
            er_str = f"[bold #FFD700]{er:.4f}%[/]"
        else:
            er_str = f"[bold white]{er:.4f}%[/]"

        prem_color = "#2EC47A" if prem >= 0 else "#FF4D6D"
        prem_str = f"[{prem_color}]{prem:+.4f}%[/]"

        if beta < 0:
            beta_str = f"[#FF4D6D]{beta}[/]"
        elif beta < 1:
            beta_str = f"[#2EC4B6]{beta}[/]"
        else:
            beta_str = f"[#FF9F1C]{beta}[/]"

        table.add_row(
            row["Asset"],
            beta_str,
            row["Risk Profile"],
            f"{row['Rf (%)']:.3f}%",
            f"{row['E(Rm) (%)']:.3f}%",
            f"{row['MRP (%)']:.3f}%",
            f"{row['Beta x MRP (%)']:.4f}%",
            er_str,
            prem_str,
        )

    console.print(table)
    console.print()


def render_summary(df: pd.DataFrame, rf: float, rm: float):
    """Show aggregate statistics cards."""
    mrp = rm - rf
    best  = df.loc[df["E(Ri) (%)"].idxmax()]
    worst = df.loc[df["E(Ri) (%)"].idxmin()]
    avg   = df["E(Ri) (%)"].mean()

    cards = [
        Panel(
            Text.from_markup(
                f"[bold #FFD700]{best['Asset']}[/]\n"
                f"[bold #2EC47A]{best['E(Ri) (%)']:.4f}%[/]"
            ),
            title="[dim] Highest Return [/]",
            border_style="#2EC47A",
            padding=(0, 2),
        ),
        Panel(
            Text.from_markup(
                f"[bold #FFD700]{worst['Asset']}[/]\n"
                f"[bold #FF4D6D]{worst['E(Ri) (%)']:.4f}%[/]"
            ),
            title="[dim] Lowest Return [/]",
            border_style="#FF4D6D",
            padding=(0, 2),
        ),
        Panel(
            Text.from_markup(
                f"[bold white]{len(df)} assets[/]\n"
                f"[bold #A78BFF]avg {avg:.4f}%[/]"
            ),
            title="[dim] Portfolio Avg [/]",
            border_style="#A78BFF",
            padding=(0, 2),
        ),
        Panel(
            Text.from_markup(
                f"[bold #3D6EFF]MRP[/]\n"
                f"[bold white]{mrp * 100:+.4f}%[/]"
            ),
            title="[dim] Market Premium [/]",
            border_style="#3D6EFF",
            padding=(0, 2),
        ),
    ]
    console.print(Columns(cards, equal=True))
    console.print()


def export_csv(df: pd.DataFrame):
    """Offer to export results to CSV."""
    if Confirm.ask("\n  [bold #3D6EFF]Export results to CSV?[/]", default=False):
        filename = f"capm_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        console.print(f"\n  [bold #2EC47A]checkmark[/] Saved to [bold white]{filename}[/]\n")


def main():
    """Main CAPM Engine entrypoint."""
    banner()

    try:
        # ── Step 1: Global market parameters ──────────────────────────────────
        rf, rm = get_market_params()

        # ── Step 2: Collect assets in a loop ──────────────────────────────────
        results = []
        console.print(Panel(
            "[bold white]Step 2:[/] Add assets to analyze.\n"
            "[dim]Enter an asset name to begin, or leave blank to finish and see results.[/dim]",
            border_style="#333355",
            padding=(0, 2),
        ))
        console.print()

        index = 1
        while True:
            asset_data = get_asset(index, rf, rm)
            if asset_data is None:
                if not results:
                    console.print("[bold #FF4D6D]  No assets entered. Exiting.[/]\n")
                    sys.exit(0)
                break
            results.append(asset_data)
            index += 1

            if not Confirm.ask("  [dim]Add another asset?[/]", default=True):
                break

        # ── Step 3: Build pandas DataFrame ────────────────────────────────────
        df = pd.DataFrame(results)

        # ── Step 4: Render final table and summary ─────────────────────────────
        render_final_table(df)
        render_summary(df, rf, rm)
        export_csv(df)

        console.print(Rule(style="#333355"))
        console.print(Align.center(
            Text.from_markup(
                "[dim #3D6EFF]CAPM Yield Engine // All calculations complete[/dim #3D6EFF]"
            )
        ))
        console.print()

    except KeyboardInterrupt:
        console.print("\n\n  [bold #FF4D6D]Session interrupted.[/]\n")
        sys.exit(0)
    except ValueError as e:
        console.print(f"\n  [bold #FF4D6D]Input error:[/] {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()