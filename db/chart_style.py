"""Estilo visual responsive para las gráficas de Sprint Monitor."""

import copy
import streamlit as st


_CTEIB_PURPLE = "#5B21B6"
_CTEIB_PINK = "#F50057"
_CTEIB_PALETTE = [
    _CTEIB_PURPLE,
    _CTEIB_PINK,
    "#7C3AED",
    "#DB2777",
    "#4F46E5",
    "#E11D48",
    "#9333EA",
    "#BE185D",
]


def _polish_spec(spec):
    if not isinstance(spec, dict):
        return spec

    polished = copy.deepcopy(spec)
    polished.setdefault("height", 300)
    polished["autosize"] = {"type": "fit", "contains": "padding", "resize": True}

    mark = polished.get("mark")
    if isinstance(mark, str):
        mark = {"type": mark}
        polished["mark"] = mark
    elif not isinstance(mark, dict):
        mark = {}
        polished["mark"] = mark

    mark_type = mark.get("type")
    if mark_type == "line":
        mark.setdefault("strokeWidth", 3)
        mark.setdefault("interpolate", "monotone")
        mark.setdefault("point", {"filled": True, "size": 70})
    elif mark_type == "bar":
        mark.setdefault("cornerRadiusTopLeft", 6)
        mark.setdefault("cornerRadiusTopRight", 6)
        mark.setdefault("opacity", 0.9)

    encoding = polished.get("encoding")
    if isinstance(encoding, dict):
        color = encoding.get("color")
        if isinstance(color, dict):
            scale = color.setdefault("scale", {})
            if isinstance(scale, dict):
                scale.setdefault("range", _CTEIB_PALETTE)
            legend = color.setdefault("legend", {})
            if isinstance(legend, dict):
                legend.setdefault("orient", "bottom")
                legend.setdefault("direction", "horizontal")
                legend.setdefault("columns", 2)
                legend.setdefault("labelLimit", 150)
                legend.setdefault("symbolSize", 100)
        elif color is None and mark_type in {"line", "bar"}:
            mark.setdefault("color", _CTEIB_PURPLE)

        for channel_name in ("x", "y"):
            channel = encoding.get(channel_name)
            if not isinstance(channel, dict):
                continue
            axis = channel.setdefault("axis", {})
            if isinstance(axis, dict):
                axis.setdefault("labelFontSize", 12)
                axis.setdefault("titleFontSize", 12)
                axis.setdefault("labelColor", "#475569")
                axis.setdefault("titleColor", "#334155")
                axis.setdefault("domainColor", "#CBD5E1")
                axis.setdefault("tickColor", "#CBD5E1")
                axis.setdefault("gridColor", "#E2E8F0")
                axis.setdefault("gridOpacity", 0.75)
                axis.setdefault("labelLimit", 90 if channel_name == "x" else 70)
                if channel_name == "x":
                    axis.setdefault("labelOverlap", "greedy")
                    axis.setdefault("labelAngle", 0)

    config = polished.setdefault("config", {})
    if isinstance(config, dict):
        view = config.setdefault("view", {})
        if isinstance(view, dict):
            view.setdefault("stroke", None)
        axis_cfg = config.setdefault("axis", {})
        if isinstance(axis_cfg, dict):
            axis_cfg.setdefault("labelFont", "sans-serif")
            axis_cfg.setdefault("titleFont", "sans-serif")
        legend_cfg = config.setdefault("legend", {})
        if isinstance(legend_cfg, dict):
            legend_cfg.setdefault("labelFontSize", 12)
            legend_cfg.setdefault("titleFontSize", 12)

    return polished


def install_chart_style():
    """Aplica el estilo solo a las gráficas Vega-Lite de la aplicación."""
    if getattr(st, "_sprint_monitor_chart_style_installed", False):
        return

    original = st.vega_lite_chart

    def styled_vega_lite_chart(data=None, spec=None, *args, **kwargs):
        # app.py pasa el spec como primer argumento posicional. También
        # mantenemos compatibilidad con la firma data=..., spec=....
        if spec is None and isinstance(data, dict) and ("mark" in data or "encoding" in data):
            data = _polish_spec(data)
        elif isinstance(spec, dict):
            spec = _polish_spec(spec)
        kwargs["use_container_width"] = True
        return original(data=data, spec=spec, *args, **kwargs)

    st.vega_lite_chart = styled_vega_lite_chart
    st._sprint_monitor_chart_style_installed = True
