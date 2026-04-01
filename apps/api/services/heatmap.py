from __future__ import annotations

from typing import List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scipy.stats import gaussian_kde


def _draw_futsal_court(
    ax: plt.Axes, field_width_m: float, field_height_m: float
) -> None:
    court_color = "#2d6a2d"
    line_color = "white"
    lw = 1.5

    ax.set_facecolor(court_color)

    border = patches.Rectangle(
        (0, 0),
        field_width_m,
        field_height_m,
        linewidth=lw,
        edgecolor=line_color,
        facecolor="none",
    )
    ax.add_patch(border)

    ax.axvline(x=field_width_m / 2, color=line_color, linewidth=lw)

    center_x = field_width_m / 2
    center_y = field_height_m / 2
    center_circle = plt.Circle(
        (center_x, center_y), 3.0, color=line_color, fill=False, linewidth=lw
    )
    ax.add_patch(center_circle)
    ax.plot(center_x, center_y, "o", color=line_color, markersize=3)

    penalty_area_w = 15.16
    penalty_area_h = 13.34
    penalty_y_offset = (field_height_m - penalty_area_h) / 2

    left_penalty = patches.Rectangle(
        (0, penalty_y_offset),
        penalty_area_w,
        penalty_area_h,
        linewidth=lw,
        edgecolor=line_color,
        facecolor="none",
    )
    ax.add_patch(left_penalty)

    right_penalty = patches.Rectangle(
        (field_width_m - penalty_area_w, penalty_y_offset),
        penalty_area_w,
        penalty_area_h,
        linewidth=lw,
        edgecolor=line_color,
        facecolor="none",
    )
    ax.add_patch(right_penalty)

    goal_h = 3.0
    goal_d = 1.0
    goal_y = (field_height_m - goal_h) / 2

    left_goal = patches.Rectangle(
        (-goal_d, goal_y),
        goal_d,
        goal_h,
        linewidth=lw,
        edgecolor=line_color,
        facecolor="none",
    )
    ax.add_patch(left_goal)

    right_goal = patches.Rectangle(
        (field_width_m, goal_y),
        goal_d,
        goal_h,
        linewidth=lw,
        edgecolor=line_color,
        facecolor="none",
    )
    ax.add_patch(right_goal)

    penalty_spot_x_left = 6.0
    penalty_spot_x_right = field_width_m - 6.0
    ax.plot(penalty_spot_x_left, center_y, "o", color=line_color, markersize=3)
    ax.plot(penalty_spot_x_right, center_y, "o", color=line_color, markersize=3)


def generate_heatmap(
    positions_m: List[Tuple[float, float]],
    output_path: str,
    field_width_m: float,
    field_height_m: float,
    player_label: str,
) -> str:
    scale = 60.0 / max(field_width_m, field_height_m)
    fig_w = field_width_m * scale / 10
    fig_h = field_height_m * scale / 10

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(-1.5, field_width_m + 1.5)
    ax.set_ylim(-1.5, field_height_m + 1.5)
    ax.set_aspect("equal")
    ax.axis("off")

    _draw_futsal_court(ax, field_width_m, field_height_m)

    fig.suptitle(
        f"Mapa de Calor — {player_label}",
        color="white",
        fontsize=10,
        y=0.98,
    )
    fig.patch.set_facecolor("#1a1a2e")

    if len(positions_m) < 10:
        ax.text(
            field_width_m / 2,
            field_height_m / 2,
            "Dados insuficientes",
            ha="center",
            va="center",
            color="white",
            fontsize=12,
        )
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        return output_path

    xs = np.array([p[0] for p in positions_m], dtype=float)
    ys = np.array([p[1] for p in positions_m], dtype=float)

    xs_clamped = np.clip(xs, 0.0, field_width_m)
    ys_clamped = np.clip(ys, 0.0, field_height_m)

    grid_res = 200
    xi = np.linspace(0, field_width_m, grid_res)
    yi = np.linspace(0, field_height_m, grid_res)
    xi_grid, yi_grid = np.meshgrid(xi, yi)

    kde_data = np.vstack([xs_clamped, ys_clamped])
    kde = gaussian_kde(kde_data, bw_method="scott")
    zi = kde(np.vstack([xi_grid.ravel(), yi_grid.ravel()])).reshape(grid_res, grid_res)

    ax.contourf(
        xi_grid,
        yi_grid,
        zi,
        levels=20,
        cmap="hot",
        alpha=0.65,
        zorder=1,
    )

    _draw_futsal_court(ax, field_width_m, field_height_m)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path
