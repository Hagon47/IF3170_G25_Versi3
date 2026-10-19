import re
from pathlib import Path
from typing import Dict, List, Optional
import plotly.graph_objects as go

from .normalize import normalize_result
from .plots import plot_ga, plot_objective, plot_sa
from .truck_view import get_final_state, get_plot_state

def export_html(plots: List[go.Figure], path: Path, title: str, include_plotlyjs="cdn") -> Path:
    parts = [
        fig.to_html(full_html=False, include_plotlyjs=include_plotlyjs if i == 0 else False)
        for i, fig in enumerate(plots)
    ]
    
    html = (
        "<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{title}</title>\n</head>\n"
        "<body style=\"font-family: sans-serif; margin: 16px;\">\n"
        + "\n<hr>\n".join(parts)
        + "\n</body>\n</html>\n"
    )
    
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    
    return path

def _get_file_name(name: Optional[str], algorithm: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name or algorithm)

def get_plots(normalized: Dict) -> List[go.Figure]:
    if normalized["algorithm"] == "genetic_algorithm":
        return [plot_ga(normalized)]
    
    plots = [plot_objective(normalized)]
    
    if normalized["algorithm"] == "simulated_annealing":
        plots.append(plot_sa(normalized))
        
    return plots

def visualize(
    result: Dict,
    output_dir: str = "../output/visualization",
    name: Optional[str] = None,
    include_plotlyjs="cdn",
) -> Dict[str, Path]:
    normalized = normalize_result(result)
    file_name = _get_file_name(name, normalized["algorithm"])
    out = Path(output_dir)

    plots = [
        get_final_state(normalized),
        *get_plots(normalized),
        get_plot_state(normalized["final_state"], f"{normalized['label']}: state akhir"),
    ]
    
    html_path = export_html(
        plots, out / f"{file_name}.html", f"{file_name}: {normalized['label']}", include_plotlyjs,
    )

    return {"html": html_path, "normalized": normalized}
