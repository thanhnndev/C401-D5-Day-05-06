"""Chart spec extraction and rendering from LLM response."""

import json
import os
import re

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

CHART_TYPES = {'bar', 'line', 'scatter', 'pie'}
REQUIRED_KEYS = {'type', 'title', 'x_col', 'y_col'}
OUTPUT_DIR = 'output'


def extract_viz_spec(raw: str) -> list[dict]:
    """Parse LLM response to extract viz block specifications."""
    specs = []
    blocks = re.findall(r'```viz\s*(.*?)\s*```', raw, re.DOTALL)
    for block in blocks:
        try:
            obj = json.loads(block)
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(obj, dict):
            continue
        if not REQUIRED_KEYS.issubset(obj.keys()):
            continue
        if obj['type'] not in CHART_TYPES:
            continue
        specs.append(obj)
    return specs


def render_chart(cols: list[str], rows: list[tuple], spec: dict) -> str | None:
    """Render a chart from SQL result data. Returns file path or None."""
    x_col = spec['x_col']
    y_col = spec['y_col']
    chart_type = spec['type']

    if x_col not in cols or y_col not in cols:
        print(f'Warning: columns not found for chart "{spec["title"]}"')
        return None

    x_idx = cols.index(x_col)
    y_idx = cols.index(y_col)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    idx_count = len(os.listdir(OUTPUT_DIR))
    output_path = os.path.join(OUTPUT_DIR, f'viz_{idx_count}.png')

    x_data = [row[x_idx] for row in rows]
    y_data = [_safe_float(row[y_idx]) for row in rows]

    if not x_data or not rows:
        print(f'Warning: no data for chart "{spec["title"]}"')
        return None

    fig, ax = plt.subplots()

    if chart_type == 'bar':
        ax.bar(x_data, y_data)
    elif chart_type == 'line':
        ax.plot(x_data, y_data)
    elif chart_type == 'scatter':
        ax.scatter(x_data, y_data)
    elif chart_type == 'pie':
        ax.pie(y_data, labels=x_data, autopct='%1.1f%%')

    if chart_type != 'pie':
        ax.set_title(spec['title'])
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.tick_params(axis='x', rotation=45)

    fig.savefig(output_path, bbox_inches='tight')
    plt.close(fig)
    return output_path


def _safe_float(value: object) -> float:
    """Convert value to float, return 0.0 on failure."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
