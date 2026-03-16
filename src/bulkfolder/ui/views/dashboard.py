from __future__ import annotations

import customtkinter as ctk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ..theme import DR_BG, DR_SURFACE, DR_BORDER, DR_TEXT, DR_MUTED


class DashboardView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color=DR_BG)

        # Grid: 2 columns, 2 rows (bottom row spans both columns)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self.panel_left = self._panel("Files by category")
        self.panel_right = self._panel("Size by category")
        self.panel_bottom = self._panel("Top largest files")

        self.panel_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(10, 10))
        self.panel_right.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(10, 10))
        self.panel_bottom.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=0, pady=(0, 10))

        self._canvas_left = None
        self._canvas_right = None

        self.top_list = ctk.CTkTextbox(
            self.panel_bottom,
            fg_color=DR_SURFACE,
            border_color=DR_BORDER,
            text_color=DR_TEXT,
            corner_radius=10,
            height=140
        )
        self.top_list.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.panel_bottom.grid_rowconfigure(1, weight=1)

    def _panel(self, title: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=DR_SURFACE,
            border_color=DR_BORDER,
            border_width=1
        )
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(frame, corner_radius=0, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=DR_TEXT
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Live from scan",
            font=ctk.CTkFont(size=11),
            text_color=DR_MUTED
        ).grid(row=0, column=1, sticky="e")

        return frame

    def render(self, scanned, mapping: dict[str, str]) -> None:
        counts: dict[str, int] = {}
        sizes: dict[str, int] = {}

        files = []
        for item in scanned:
            if not item.is_file:
                continue
            ext = item.path.suffix.lower().lstrip(".")
            bucket = mapping.get(ext, "Other") if ext else "Other"

            counts[bucket] = counts.get(bucket, 0) + 1
            sizes[bucket] = sizes.get(bucket, 0) + item.size
            files.append(item)

        labels_count = sorted(counts.keys(), key=lambda k: counts[k], reverse=True)
        values_count = [counts[k] for k in labels_count]

        labels_size = sorted(sizes.keys(), key=lambda k: sizes[k], reverse=True)
        values_size_mb = [sizes[k] / (1024 * 1024) for k in labels_size]

        fig_left = self._donut_figure(
            title="Files",
            center_text=str(int(sum(values_count))),
            labels=labels_count,
            values=values_count
        )
        fig_right = self._donut_figure(
            title="Size (MB)",
            center_text=f"{sum(values_size_mb):.0f}MB",
            labels=labels_size,
            values=values_size_mb
        )

        # Replace old charts
        if self._canvas_left:
            self._canvas_left.get_tk_widget().destroy()
        if self._canvas_right:
            self._canvas_right.get_tk_widget().destroy()

        self._canvas_left = FigureCanvasTkAgg(fig_left, master=self.panel_left)
        self._canvas_left.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

        self._canvas_right = FigureCanvasTkAgg(fig_right, master=self.panel_right)
        self._canvas_right.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

        # Top 10 biggest files list
        files_sorted = sorted(files, key=lambda x: x.size, reverse=True)[:10]
        self.top_list.delete("1.0", "end")
        if not files_sorted:
            self.top_list.insert("end", "No files found.\n")
            return

        for i, f in enumerate(files_sorted, start=1):
            self.top_list.insert("end", f"{i:>2}. {f.path.name}   —   {self._human_bytes(f.size)}\n")

    def _donut_figure(self, title: str, center_text: str, labels: list[str], values: list[float]) -> Figure:
        # OPTIMISATION: DPI réduit à 75 pour un rendu plus fluide et rapide
        fig = Figure(figsize=(5, 3.2), dpi=75)
        ax = fig.add_subplot(111)

        if not values or sum(values) <= 0:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            ax.axis("off")
            return fig

        wedges, _ = ax.pie(
            values,
            startangle=90,
            wedgeprops=dict(width=0.42)
        )

        ax.text(0, 0, center_text, ha="center", va="center", fontsize=16, fontweight="bold")

        total = float(sum(values))
        legend_lines = []
        for label, v in zip(labels, values):
            pct = (v / total) * 100 if total else 0
            legend_lines.append(f"{label} — {v:.0f} ({pct:.1f}%)")

        ax.legend(
            wedges,
            legend_lines,
            title="Categories",
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            frameon=False
        )

        ax.set_title(title)
        ax.axis("equal")
        fig.tight_layout()
        return fig

    @staticmethod
    def _human_bytes(n: int) -> str:
        step = 1024.0
        units = ["B", "KB", "MB", "GB", "TB"]
        v = float(n)
        for u in units:
            if v < step:
                return f"{v:.1f} {u}"
            v /= step
        return f"{v:.1f} PB"