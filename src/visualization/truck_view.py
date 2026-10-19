from typing import Dict, List, Optional, Set
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from problem import Package, State, get_constraints, is_valid
from .normalize import format_duration

PACKAGE_COLORS = [
    "#4C78A8", "#54A24B", "#EECA3B", "#B279A2", "#72B7B2", "#9D755D", "#F58518",
    "#8CD17D", "#A0CBE8", "#B6992D", "#79706E", "#FFBE7D", "#499894", "#D4A6C8",
]

FRAGILE_COLOR = "#D62728"
TRUCK_COLOR = "#333333"
BOX_OPACITY = 0.55

_BOX_I = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
_BOX_J = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
_BOX_K = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

def _get_corners(bounds):
    x0, y0, z0, x1, y1, z1 = bounds
    
    xs = [x0, x0, x1, x1, x0, x0, x1, x1]
    ys = [y0, y1, y1, y0, y0, y1, y1, y0]
    zs = [z0, z0, z0, z0, z1, z1, z1, z1]
    return xs, ys, zs

def _get_edges(bounds):
    x0, y0, z0, x1, y1, z1 = bounds
    edges = []
    
    for y in (y0, y1):
        for z in (z0, z1):
            edges.append(((x0, y, z), (x1, y, z)))
    for x in (x0, x1):
        for z in (z0, z1):
            edges.append(((x, y0, z), (x, y1, z)))
    for x in (x0, x1):
        for y in (y0, y1):
            edges.append(((x, y, z0), (x, y, z1)))

    xs, ys, zs = [], [], []
    for start, end in edges:
        xs += [start[0], end[0], None]
        ys += [start[1], end[1], None]
        zs += [start[2], end[2], None]

    return xs, ys, zs

def get_package_color(state: State, index: int) -> str:
    if state.packages[index].is_fragile:
        return FRAGILE_COLOR
    
    return PACKAGE_COLORS[index % len(PACKAGE_COLORS)]

def _package_hover(p: Package) -> str:
    dx, dy, dz = p.get_dimensions
    w, l, h = p.dimensions
    orientation = ", ".join(f"{k}→{v}" for k, v in p.get_orientation().items())
    fragile = "Ya" if p.is_fragile else "Tidak"
    
    return (
        f"<b>{p.id}</b>{' (fragile)' if p.is_fragile else ''}<br>"
        f"Posisi (x, y, z): {tuple(p.position)}<br>"
        f"Ukuran setelah rotasi: {dx} * {dy} * {dz}<br>"
        f"Ukuran asli: {w} * {l} * {h}<br>"
        f"Orientasi: {orientation}<br>"
        f"Value: {p.value}<br>Weight: {p.weight}<br>Fragile: {fragile}"
        "<extra></extra>"
    )

def draw_state(fig: go.Figure, state: State, row: int, col: int, shown_legend: Optional[Set[str]] = None) -> None:
    if shown_legend is None:
        shown_legend = set()

    w, l, h = state.truck.dimensions
    xs, ys, zs = _get_edges((0, 0, 0, w, l, h))
    
    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs, mode="lines",
        line=dict(color=TRUCK_COLOR, width=4),
        name=f"Truk {w}*{l}*{h}", legendgroup="truck",
        showlegend="truck" not in shown_legend, hoverinfo="skip",
    ), row=row, col=col)
    
    shown_legend.add("truck")

    for index, p in enumerate(state.packages):
        if not p.is_placed:
            continue

        bounds = p.get_bounds()
        color = get_package_color(state, index)
        
        name = f"{p.id} (fragile)" if p.is_fragile else p.id
        vx, vy, vz = _get_corners(bounds)

        fig.add_trace(go.Mesh3d(
            x=vx, y=vy, z=vz, i=_BOX_I, j=_BOX_J, k=_BOX_K,
            color=color, opacity=BOX_OPACITY, flatshading=True,
            name=name, legendgroup=p.id, showlegend=p.id not in shown_legend,
            hovertemplate=_package_hover(p),
        ), row=row, col=col)

        ex, ey, ez = _get_edges(bounds)
        fig.add_trace(go.Scatter3d(
            x=ex, y=ey, z=ez, mode="lines",
            line=dict(color=FRAGILE_COLOR if p.is_fragile else "#222222", width=6 if p.is_fragile else 2),
            legendgroup=p.id, showlegend=False, hoverinfo="skip",
        ), row=row, col=col)
        
        shown_legend.add(p.id)

def get_info(state: State) -> List[List[str]]:
    total = len(state.packages)
    inside = len(state.inside())
    
    rows = [
        ["Total value", str(state.total_value())],
        ["Berat / kapasitas", f"{state.total_weight()} / {state.truck.max_capacity}"],
        ["Paket di dalam / total", f"{inside} / {total}"],
        ["Paket di luar", str(total - inside)],
    ]

    if is_valid(state):
        rows.append(["Status", "VALID"])
        
    else:
        rows.append(["Status", "TIDAK VALID"])
        for key, count in get_constraints(state).items():
            if count:
                rows.append([f"Pelanggaran {key}", str(count)])
                
    return rows

def get_state_info(state: State) -> go.Table:
    rows = get_info(state)
    valid = is_valid(state)
    
    status_color = "#E3F1E5" if valid else "#FBE3E3"
    fill = [["white"] * len(rows), ["white"] * 4 + [status_color] * (len(rows) - 4)]
    
    return go.Table(
        columnwidth=[1.2, 1],
        header=dict(values=["<b>Keterangan</b>", "<b>Nilai</b>"], fill_color="#E8E8E8", align="left"),
        cells=dict(values=[[r[0] for r in rows], [r[1] for r in rows]], fill_color=fill, align="left", height=24),
    )

def get_outside_info(state: State) -> go.Table:
    outside = state.outside()
    header = ["<b>ID</b>", "<b>Ukuran asli (w×l×h)</b>", "<b>Value</b>", "<b>Weight</b>", "<b>Fragile</b>"]

    if not outside:
        columns = [["Tidak ada"], [""], [""], [""], [""]]
    else:
        columns = [
            [p.id for p in outside],
            ["{} × {} × {}".format(*p.dimensions) for p in outside],
            [p.value for p in outside],
            [p.weight for p in outside],
            ["Ya" if p.is_fragile else "Tidak" for p in outside],
        ]

    return go.Table(
        columnwidth=[0.7, 1.4, 0.7, 0.7, 0.7],
        header=dict(values=header, fill_color="#E8E8E8", align="left"),
        cells=dict(values=columns, align="left", height=22),
    )

def _get_scene() -> Dict:
    return dict(
        aspectmode="data",
        xaxis=dict(title="x (width)"),
        yaxis=dict(title="y (length)"),
        zaxis=dict(title="z (height)"),
        camera=dict(eye=dict(x=1.6, y=-1.4, z=1.0)),
    )

def get_plot_state(state: State, title: str = "State") -> go.Figure:
    fig = make_subplots(
        rows=2, cols=2,
        column_widths=[0.62, 0.38], row_heights=[0.4, 0.6],
        specs=[[{"type": "scene", "rowspan": 2}, {"type": "table"}], [None, {"type": "table"}]],
        subplot_titles=("Peti kemas truk", "Ringkasan state", "Paket di luar truk"),
        horizontal_spacing=0.03, vertical_spacing=0.08,
    )

    draw_state(fig, state, row=1, col=1)
    fig.add_trace(get_state_info(state), row=1, col=2)
    fig.add_trace(get_outside_info(state), row=2, col=2)

    fig.update_scenes(**_get_scene())
    
    fig.update_layout(
        title=dict(text=f"{title}<br><sup>Total value {state.total_value()} · merah = paket fragile</sup>"),
        height=760, margin=dict(l=10, r=10, t=90, b=10),
        legend=dict(title="Paket (klik untuk sembunyikan)", orientation="h", yanchor="top", y=-0.02),
    )
    return fig

def get_final_state(normalized: Dict) -> go.Figure:
    initial_state: State = normalized["initial_state"]
    final_state: State = normalized["final_state"]

    fig = make_subplots(
        rows=3, cols=2,
        row_heights=[0.58, 0.17, 0.25],
        specs=[
            [{"type": "scene"}, {"type": "scene"}],
            [{"type": "table"}, {"type": "table"}],
            [{"type": "table"}, {"type": "table"}],
        ],
        
        subplot_titles=(
            f"State awal (value {normalized['initial_value']})",
            f"State akhir (value {normalized['final_value']})",
            "Ringkasan state awal", "Ringkasan state akhir",
            "Paket di luar truk (awal)", "Paket di luar truk (akhir)",
        ),
        horizontal_spacing=0.03, vertical_spacing=0.05,
    )

    shown_legend: Set[str] = set()
    for col, state in ((1, initial_state), (2, final_state)):
        draw_state(fig, state, row=1, col=col, shown_legend=shown_legend)
        fig.add_trace(get_state_info(state), row=2, col=col)
        fig.add_trace(get_outside_info(state), row=3, col=col)

    subtitle = f"Durasi {format_duration(normalized['duration'])} · merah = paket fragile"
    
    if normalized["algorithm"] == "genetic_algorithm":
        subtitle += " · Catatan: state awal GA = individu terbaik populasi awal"

    fig.update_scenes(**_get_scene())
    fig.update_layout(
        title=dict(text=(
            f"{normalized['label']}: value {normalized['initial_value']} → {normalized['final_value']}"
            f"<br><sup>{subtitle}</sup>"
        )),
        height=1150, margin=dict(l=10, r=10, t=90, b=10),
        legend=dict(title="Paket (klik untuk sembunyikan)", orientation="h", yanchor="top", y=-0.01),
    )
    
    return fig
