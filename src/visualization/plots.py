from typing import Any, Dict, List

import plotly.graph_objects as go

from .normalize import format_duration


def _get_mode(values: List[float]) -> str:
    if len(values) <= 60:
        return "lines+markers"

    return "lines"

def _get_x(values: List[float], start: int = 0) -> List[int]:
    return list(range(start, start + len(values)))

def _set_integer_ticks(fig: go.Figure, length: int) -> None:
    if length <= 20:
        fig.update_xaxes(dtick=1)

def _set_layout(fig: go.Figure, title: str, subtitle: str, x_title: str, y_title: str, height: int = 480) -> None:
    fig.update_layout(
        title=dict(text=f"{title}<br><sup>{subtitle}</sup>"),
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_white",
        height=height,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

def detail_text(normalized: Dict[str, Any]) -> str:
    algorithm = normalized["algorithm"]
    info = normalized["info"]

    details = [
        f"Nilai awal {normalized['initial_value']} -> akhir {normalized['final_value']}",
        f"durasi {format_duration(normalized['duration'])}",
    ]

    if algorithm == "hc_steepest_accent":
        details.append(f"berhenti setelah {info.get('iterations')} iterasi (maks {info.get('max_iterations')})")

    elif algorithm == "hc_stochastic":
        details.append(f"berhenti setelah {info.get('iterations')} iterasi (maks {info.get('max_iterations')})")

    elif algorithm == "hc_sideways_move":
        details.append(f"berhenti setelah {info.get('iterations')} iterasi")
        details.append(f"sideways move {info.get('sideways_count')}/{info.get('max_sideways')}")

    elif algorithm == "hc_random_restart":
        details.append(f"{info.get('restart_count')} restart (maks {info.get('max_restarts')})")
        details.append(f"iterasi per restart {info.get('iterations_in_restarts')}")

    elif algorithm == "simulated_annealing":
        details.append(f"{info.get('iterations')} iterasi")
        details.append(f"frekuensi stuck {info.get('stuck_frequency')}")

    elif algorithm == "genetic_algorithm":
        details.append(f"populasi {info.get('population_size')}")
        details.append(f"{info.get('generations')} iterasi")

    return " · ".join(details)

def plot_objective(normalized: Dict[str, Any]) -> go.Figure:
    series = normalized["series"]
    fig = go.Figure()

    dashes = ["solid", "dash", "dot", "dashdot", "longdash", "longdashdot"]

    for index, (name, values) in enumerate(series):
        line = dict(color="#000000", width=2, dash=dashes[index % len(dashes)])

        fig.add_trace(go.Scatter(
            x=_get_x(values),
            y=values,
            mode=_get_mode(values),
            name=name,
            line=line,
        ))

    fig.add_hline(
        y=normalized["final_value"],
        line_dash="dot",
        line_color="#000000",
        annotation_text=f"nilai akhir {normalized['final_value']}",
        annotation_position="bottom right",
    )

    _set_layout(fig,
        title=f"{normalized['label']}: nilai objective per {normalized['x_label'].lower()}",
        subtitle=detail_text(normalized),
        x_title=normalized["x_label"],
        y_title="Nilai objective (total value)",
    )
    _set_integer_ticks(fig, max(len(values) for _, values in series))

    return fig

def plot_sa(normalized: Dict[str, Any], window: int = 50) -> go.Figure:
    acceptance = normalized["acceptance"] or []
    fig = go.Figure()

    if not acceptance:
        fig.add_annotation(text="Tidak ada data iterasi", showarrow=False, x=0.5, y=0.5, xref="paper", yref="paper")

    else:
        fig.add_trace(go.Scatter(
            x=_get_x(acceptance, start=1),
            y=acceptance,
            mode="markers",
            name="e^(ΔE/T)",
            marker=dict(size=4, color="#000000", opacity=0.3),
            hovertemplate="Iterasi %{x}<br>e^(ΔE/T) = %{y:.4f}<extra></extra>",
        ))

        moving_average = []
        for i in range(len(acceptance)):
            recent = acceptance[max(0, i - window + 1): i + 1]
            moving_average.append(sum(recent) / len(recent))

        fig.add_trace(go.Scatter(
            x=_get_x(moving_average, start=1),
            y=moving_average,
            mode="lines",
            name=f"Rata-rata {window} iterasi",
            line=dict(color="#000000", width=2.5),
        ))

    worse_count = sum(1 for value in acceptance if value < 1)

    _set_layout(
        fig,
        title="Simulated Annealing",
        subtitle=(
            f"frekuensi stuck {normalized['info'].get('stuck_frequency')} · "
            f"{worse_count} iterasi dengan nilai lebih buruk· "
            f"durasi {format_duration(normalized['duration'])}"
        ),
        x_title="Iterasi",
        y_title="e^(ΔE/T)",
        height=440,
    )
    fig.update_yaxes(range=[0, 1.05])

    return fig

def plot_ga(normalized: Dict[str, Any]) -> go.Figure:
    series = dict(normalized["series"])
    max_values = series["Maksimum"]
    mean_values = series["Rata-rata"]
    
    info = normalized["info"]
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=_get_x(max_values),
        y=max_values,
        mode=_get_mode(max_values),
        name="Maksimum populasi",
        line=dict(color="#000000", width=2.5),  
    ))

    fig.add_trace(go.Scatter(
        x=_get_x(mean_values),
        y=mean_values,
        mode=_get_mode(mean_values),
        name="Rata-rata populasi",
        line=dict(color="#000000", width=2, dash="dash"),
        opacity=0.55,
    ))

    _set_layout(
        fig,
        title="Genetic Algorithm",
        subtitle=(
            f"Populasi {info.get('population_size')} · {info.get('generations')} iterasi · "
            f"durasi {format_duration(normalized['duration'])} · nilai akhir {normalized['final_value']}"
        ),
        x_title="Iterasi",
        y_title="Nilai objective",
    )
    _set_integer_ticks(fig, len(max_values))

    return fig