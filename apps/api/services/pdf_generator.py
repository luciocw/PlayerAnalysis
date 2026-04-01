from __future__ import annotations

import os
from datetime import date
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF

_PAGE_WIDTH, _PAGE_HEIGHT = A4
_MARGIN = 2.0 * cm

_COLOR_PRIMARY = colors.HexColor("#1a1a2e")
_COLOR_ACCENT = colors.HexColor("#e94560")
_COLOR_LIGHT = colors.HexColor("#f5f5f5")
_COLOR_DARK_TEXT = colors.HexColor("#333333")
_COLOR_CARD_BG = colors.HexColor("#eef2ff")


def _metric_card_table(
    label: str, value: str, unit: str
) -> Table:
    content = [
        [Paragraph(label, ParagraphStyle(
            "CardLabel",
            fontSize=8,
            textColor=_COLOR_PRIMARY,
            spaceAfter=2,
        ))],
        [Paragraph(f"{value}", ParagraphStyle(
            "CardValue",
            fontSize=18,
            textColor=_COLOR_ACCENT,
            fontName="Helvetica-Bold",
        ))],
        [Paragraph(unit, ParagraphStyle(
            "CardUnit",
            fontSize=8,
            textColor=_COLOR_DARK_TEXT,
        ))],
    ]
    card_w = (_PAGE_WIDTH - 2 * _MARGIN - 3 * 5 * mm) / 4
    t = Table(content, colWidths=[card_w])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _COLOR_CARD_BG),
        ("BOX", (0, 0), (-1, -1), 1, _COLOR_PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    return t


def _build_speed_chart(
    timestamps_s: List[float],
    speeds_kmh: List[float],
    sprint_speed_kmh: float,
    width: float,
    height: float,
) -> Drawing:
    d = Drawing(width, height)
    pad_left = 40
    pad_bottom = 30
    pad_right = 20
    pad_top = 20
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_bottom - pad_top

    d.add(Rect(0, 0, width, height, fillColor=_COLOR_LIGHT, strokeColor=None))

    if not timestamps_s or not speeds_kmh:
        d.add(String(width / 2, height / 2, "Sem dados", textAnchor="middle", fontSize=10))
        return d

    max_t = max(timestamps_s) or 1.0
    max_v = max(max(speeds_kmh), sprint_speed_kmh + 5) or 1.0

    def tx(t: float) -> float:
        return pad_left + (t / max_t) * plot_w

    def ty(v: float) -> float:
        return pad_bottom + (v / max_v) * plot_h

    sprint_y = ty(sprint_speed_kmh)
    d.add(Line(pad_left, sprint_y, pad_left + plot_w, sprint_y,
               strokeColor=colors.HexColor("#e94560"), strokeWidth=0.5,
               strokeDashArray=[4, 3]))

    n = len(timestamps_s)
    step = max(1, n // 300)
    pts = list(zip(timestamps_s[::step], speeds_kmh[::step]))

    for i in range(1, len(pts)):
        x0 = tx(pts[i - 1][0])
        y0 = ty(pts[i - 1][1])
        x1 = tx(pts[i][0])
        y1 = ty(pts[i][1])
        d.add(Line(x0, y0, x1, y1, strokeColor=_COLOR_PRIMARY, strokeWidth=1.2))

    d.add(Line(pad_left, pad_bottom, pad_left, pad_bottom + plot_h,
               strokeColor=_COLOR_DARK_TEXT, strokeWidth=1))
    d.add(Line(pad_left, pad_bottom, pad_left + plot_w, pad_bottom,
               strokeColor=_COLOR_DARK_TEXT, strokeWidth=1))

    for v_tick in range(0, int(max_v) + 1, 10):
        y = ty(v_tick)
        d.add(Line(pad_left - 3, y, pad_left, y, strokeColor=_COLOR_DARK_TEXT, strokeWidth=0.5))
        d.add(String(pad_left - 5, y - 3, str(v_tick), textAnchor="end", fontSize=6,
                     fillColor=_COLOR_DARK_TEXT))

    num_t_ticks = min(6, len(timestamps_s))
    for i in range(num_t_ticks):
        t_val = max_t * i / max(num_t_ticks - 1, 1)
        x = tx(t_val)
        minutes = int(t_val // 60)
        seconds = int(t_val % 60)
        label = f"{minutes}:{seconds:02d}"
        d.add(Line(x, pad_bottom, x, pad_bottom - 3, strokeColor=_COLOR_DARK_TEXT, strokeWidth=0.5))
        d.add(String(x, pad_bottom - 10, label, textAnchor="middle", fontSize=6,
                     fillColor=_COLOR_DARK_TEXT))

    d.add(String(pad_left + plot_w / 2, 4, "Tempo (mm:ss)", textAnchor="middle",
                 fontSize=7, fillColor=_COLOR_DARK_TEXT))
    d.add(String(8, pad_bottom + plot_h / 2, "km/h", textAnchor="middle",
                 fontSize=7, fillColor=_COLOR_DARK_TEXT))

    return d


def generate_pdf(
    session_id: str,
    metrics: dict,
    heatmap_path: str,
    output_path: str,
    sprint_speed_kmh: float = 18.0,
) -> str:
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=20,
        textColor=_COLOR_PRIMARY,
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=_COLOR_DARK_TEXT,
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontSize=13,
        textColor=_COLOR_PRIMARY,
        fontName="Helvetica-Bold",
        spaceBefore=16,
        spaceAfter=8,
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=_MARGIN,
        rightMargin=_MARGIN,
        topMargin=_MARGIN,
        bottomMargin=_MARGIN,
    )

    story = []

    today = date.today().strftime("%d/%m/%Y")
    story.append(Paragraph(f"Análise de Futsal — {today}", title_style))
    story.append(Paragraph("Relatório de desempenho individual", subtitle_style))
    story.append(Spacer(1, 0.3 * cm))

    players = metrics.get("players", [])
    player_data: Optional[dict] = players[0] if players else None

    total_distance = player_data["total_distance_m"] if player_data else 0.0
    max_speed = player_data["max_speed_kmh"] if player_data else 0.0
    avg_speed = player_data.get("avg_speed_kmh", 0.0) if player_data else 0.0
    sprint_count = player_data["sprint_count"] if player_data else 0
    player_label = player_data["label"] if player_data else "—"

    story.append(Paragraph(f"Jogador acompanhado: {player_label}", subtitle_style))

    cards = [
        _metric_card_table("Distância Total", f"{total_distance:.0f}", "metros"),
        _metric_card_table("Vel. Média", f"{avg_speed:.1f}", "km/h"),
        _metric_card_table("Vel. Máxima", f"{max_speed:.1f}", "km/h"),
        _metric_card_table("Arrancadas", str(sprint_count), "sprints"),
    ]

    card_table = Table(
        [cards],
        colWidths=[(_PAGE_WIDTH - 2 * _MARGIN) / 4] * 4,
    )
    card_table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(card_table)
    story.append(Spacer(1, 0.5 * cm))

    if heatmap_path and os.path.exists(heatmap_path):
        story.append(Paragraph("Mapa de Calor", section_style))
        heatmap_w = _PAGE_WIDTH - 2 * _MARGIN
        story.append(
            Image(heatmap_path, width=heatmap_w, height=heatmap_w * 0.5)
        )

    story.append(Paragraph("", styles["Normal"]))

    if player_data:
        timestamps_s = player_data.get("timestamps_s", [])
        speeds_kmh = player_data.get("speed_series", [])
        sprints = player_data.get("sprints", [])

        if timestamps_s and speeds_kmh:
            story.append(Paragraph("Velocidade ao Longo do Jogo", section_style))
            chart_w = float(_PAGE_WIDTH - 2 * _MARGIN)
            chart_h = 6.0 * cm
            chart = _build_speed_chart(
                timestamps_s, speeds_kmh, sprint_speed_kmh, chart_w, chart_h
            )
            story.append(chart)
            story.append(Spacer(1, 0.4 * cm))

        if sprints:
            story.append(Paragraph("Detalhes das Arrancadas", section_style))
            headers = ["Início (s)", "Fim (s)", "Distância (m)", "Vel. Máx (km/h)"]
            data = [headers] + [
                [
                    f"{s['start_s']:.1f}",
                    f"{s['end_s']:.1f}",
                    f"{s['distance_m']:.1f}",
                    f"{s['max_speed_kmh']:.1f}",
                ]
                for s in sprints
            ]
            sprint_table = Table(
                data,
                colWidths=[(_PAGE_WIDTH - 2 * _MARGIN) / 4] * 4,
            )
            sprint_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), _COLOR_PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _COLOR_LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(sprint_table)

    doc.build(story)
    return output_path
