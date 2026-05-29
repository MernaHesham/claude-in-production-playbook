import tempfile
import pathlib
from dotenv import load_dotenv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .base import BaseAgent, Artefact

load_dotenv()


class VizAgent(BaseAgent):
    system = """You receive tabular data as context. Call create_chart to visualise it.
Use bar chart for categorical comparisons, line chart for time series.
After the tool call, respond with ONLY the returned file path — no other text."""

    tools = [{
        "name": "create_chart",
        "description": "Create a chart from data and save it as a PNG file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chart_type": {"type": "string", "enum": ["bar", "line"]},
                "x_labels": {"type": "array", "items": {"type": "string"}},
                "y_values": {"type": "array", "items": {"type": "number"}},
                "title": {"type": "string"},
                "y_label": {"type": "string", "description": "Label for the Y axis, e.g. 'Revenue (EUR)'"}
            },
            "required": ["chart_type", "x_labels", "y_values", "title"]
        }
    }]

    def _dispatch_tool(self, name, inputs):
        fig, ax = plt.subplots(figsize=(10, 5))
        x, y = inputs["x_labels"], inputs["y_values"]
        if inputs["chart_type"] == "bar":
            ax.bar(x, y, color="#5B4FD4")
        else:
            ax.plot(x, y, marker="o", color="#5B4FD4", linewidth=2)
        ax.set_title(inputs["title"], fontsize=14)
        if inputs.get("y_label"):
            ax.set_ylabel(inputs["y_label"])
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        path = pathlib.Path(tempfile.mktemp(suffix=".png"))
        fig.savefig(path, dpi=150)
        plt.close(fig)
        return str(path)

    def _parse(self, text) -> Artefact:
        return Artefact(kind="chart", content=text.strip())
