"""Chart spec extraction and rendering from LLM response."""

import json
import os
import re

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

CHART_TYPES = {'bar', 'line', 'scatter', 'pie', 'area'}
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
        # Support both old format (x_col, y_col) and new format (encoding)
        has_old = 'x_col' in obj and 'y_col' in obj
        has_new = 'encoding' in obj
        if not (has_old or has_new):
            continue
        if obj.get('type') not in CHART_TYPES:
            continue
        specs.append(obj)
    return specs


def render_chart(cols: list[str], rows: list[tuple], spec: dict) -> str | None:
    """Render a chart from SQL result data. Returns file path or None."""
    # Support both old format (x_col, y_col, title) and new format (type, encoding)
    if 'x_col' in spec and 'y_col' in spec:
        x_col = spec['x_col']
        y_col = spec['y_col']
    elif 'encoding' in spec:
        # Extract from Vega-Lite style encoding
        encoding = spec['encoding']
        x_col = encoding.get('x', {}).get('field', '')
        y_col = encoding.get('y', {}).get('field', '')
    else:
        print(f'Warning: spec missing required columns: {spec}')
        return None

    chart_type = spec['type']
    title = spec.get('title', f'{x_col} vs {y_col}')

    if x_col not in cols:
        print(f'Warning: x_col "{x_col}" not found in {cols}')
        return None
    if y_col not in cols:
        print(f'Warning: y_col "{y_col}" not found in {cols}')
        return None

    x_idx = cols.index(x_col)
    y_idx = cols.index(y_col)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    idx_count = len(os.listdir(OUTPUT_DIR))
    output_path = os.path.join(OUTPUT_DIR, f'viz_{idx_count}.png')

    x_data = [row[x_idx] for row in rows]
    y_data = [_safe_float(row[y_idx]) for row in rows]

    if not x_data or not rows:
        print(f'Warning: no data for chart "{title}"')
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
    elif chart_type == 'area':
        ax.fill_between(x_data, y_data, alpha=0.5)

    if chart_type != 'pie':
        ax.set_title(title)
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
