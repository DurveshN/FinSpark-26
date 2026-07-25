"""Minimal styled-PDF builder on fpdf2 — headings, paragraphs, bullets, tables,
callouts, code, title/section pages. Used by the notes + business-case generators.
"""
from __future__ import annotations
from fpdf import FPDF

# palette (dark-accent on white for print legibility)
INK = (17, 24, 39)
MUTED = (100, 116, 139)
PRIMARY = (79, 70, 229)
ACCENT = (124, 58, 237)
LINE = (226, 232, 240)
CHIP_BG = (238, 242, 255)
CALLOUT_BG = (245, 243, 255)
OK = (16, 122, 87)
WARN = (180, 83, 9)


def _clean(s: str) -> str:
    """Map non-latin-1 glyphs to ASCII so the core fonts render everywhere."""
    repl = {
        "—": "-", "–": "-", "‘": "'", "’": "'",
        "“": '"', "”": '"', "…": "...", "•": "-",
        "→": "->", "≥": ">=", "≤": "<=", "×": "x",
        "₹": "Rs ", "β": "B", "₀": "0", "₁": "1", "₂": "2",
        "‑": "-", " ": " ", "≈": "~", "²": "2",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "replace").decode("latin-1")


class Doc(FPDF):
    def __init__(self, title: str, subtitle: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.doc_title = title
        self.doc_sub = subtitle
        self.set_auto_page_break(True, margin=18)
        self.set_margins(18, 18, 18)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8, _clean(f"{self.doc_title}  -  FinSpark'26 - Team Hexacon"), 0, 0, "L")
        self.cell(0, 8, f"{self.page_no()}", 0, 0, "R")

    # --- building blocks ---
    def cover(self):
        self.add_page()
        self.ln(40)
        self.set_fill_color(*PRIMARY)
        self.rect(18, self.get_y(), 40, 2, "F")
        self.ln(10)
        self.set_font("Helvetica", "B", 30)
        self.set_text_color(*INK)
        self.multi_cell(0, 12, _clean(self.doc_title))
        self.ln(2)
        self.set_font("Helvetica", "", 14)
        self.set_text_color(*MUTED)
        self.multi_cell(0, 8, _clean(self.doc_sub))
        self.ln(16)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*ACCENT)
        self.cell(0, 7, "QTD-HGNN  -  Quantum-Topological Threat Correlation", 0, 1)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*MUTED)
        self.cell(0, 6, "Problem Statement 2: AI-Driven Correlation of Cybersecurity", 0, 1)
        self.cell(0, 6, "Telemetry & Transactional Behaviour", 0, 1)
        self.ln(8)
        self.set_draw_color(*LINE)
        self.line(18, self.get_y(), 192, self.get_y())

    def h1(self, text: str):
        if self.get_y() > 240:
            self.add_page()
        self.ln(4)
        self.set_font("Helvetica", "B", 17)
        self.set_text_color(*PRIMARY)
        self.multi_cell(0, 9, _clean(text))
        self.set_draw_color(*LINE)
        self.line(18, self.get_y() + 1, 192, self.get_y() + 1)
        self.ln(4)

    def h2(self, text: str):
        if self.get_y() > 250:
            self.add_page()
        self.ln(2)
        self.set_font("Helvetica", "B", 12.5)
        self.set_text_color(*INK)
        self.multi_cell(0, 7, _clean(text))
        self.ln(1)

    def para(self, text: str):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.6, _clean(text))
        self.ln(1.5)

    def bullet(self, text: str, label: str | None = None):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(*PRIMARY)
        x = self.get_x()
        self.cell(6, 5.6, "-", 0, 0)
        self.set_text_color(*INK)
        if label:
            self.set_font("Helvetica", "B", 10.5)
            lbl = _clean(label + ": ")
            self.cell(self.get_string_width(lbl), 5.6, lbl, 0, 0)
            self.set_font("Helvetica", "", 10.5)
        self.multi_cell(0, 5.6, _clean(text))
        self.set_x(x)

    def code(self, text: str):
        self.set_font("Courier", "", 8.2)
        self.set_fill_color(245, 246, 250)
        self.set_text_color(*INK)
        avail = 210 - self.l_margin - self.r_margin
        for line in text.split("\n"):
            self.set_x(self.l_margin)
            self.multi_cell(avail, 4.6, _clean(line), 0, "L", fill=True)
        self.ln(2)

    def callout(self, title: str, text: str, tone=ACCENT):
        if self.get_y() > 245:
            self.add_page()
        y0 = self.get_y()
        self.set_fill_color(*CALLOUT_BG)
        self.set_draw_color(*tone)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*tone)
        pad = 3
        self.set_xy(18, y0 + pad)
        self.set_x(22)
        self.multi_cell(170, 5.4, _clean(title))
        self.set_x(22)
        self.set_font("Helvetica", "", 9.8)
        self.set_text_color(*INK)
        self.multi_cell(170, 5.0, _clean(text))
        y1 = self.get_y() + pad
        self.set_fill_color(*tone)
        self.rect(18, y0, 1.6, y1 - y0, "F")
        self.ln(4)

    def table(self, headers: list[str], rows: list[list[str]], widths: list[float]):
        if self.get_y() > 235:
            self.add_page()
        self.set_font("Helvetica", "B", 8.8)
        self.set_fill_color(*PRIMARY)
        self.set_text_color(255, 255, 255)
        for h, w in zip(headers, widths):
            self.cell(w, 7, _clean(h), 0, 0, "L", fill=True)
        self.ln(7)
        self.set_font("Helvetica", "", 8.6)
        self.set_text_color(*INK)
        fill = False
        for row in rows:
            # compute row height from wrapped lines
            line_h = 4.6
            row = [self._fit(_clean(str(c)), w) for c, w in zip(row, widths)]
            heights = []
            for c, w in zip(row, widths):
                n = max(1, self._nlines(c, w - 2))
                heights.append(n * line_h)
            rh = max(heights)
            if self.get_y() + rh > 275:
                self.add_page()
                self.set_font("Helvetica", "B", 8.8)
                self.set_fill_color(*PRIMARY); self.set_text_color(255, 255, 255)
                for h, w in zip(headers, widths):
                    self.cell(w, 7, _clean(h), 0, 0, "L", fill=True)
                self.ln(7)
                self.set_font("Helvetica", "", 8.6); self.set_text_color(*INK)
            self.set_fill_color(248, 249, 252) if fill else self.set_fill_color(255, 255, 255)
            x0, y0 = self.get_x(), self.get_y()
            for c, w in zip(row, widths):
                x = self.get_x(); y = self.get_y()
                self.multi_cell(w, line_h, _clean(str(c)), 0, "L", fill=True)
                self.set_xy(x + w, y)
            self.set_xy(x0, y0 + rh)
            self.set_draw_color(*LINE)
            self.line(18, self.get_y(), 192, self.get_y())
            fill = not fill
        self.ln(3)

    def _fit(self, text: str, w: float) -> str:
        """Break any single token wider than column width w (mm) so multi_cell won't fail."""
        self.set_font("Helvetica", "", 8.6)
        out = []
        for word in text.split(" "):
            if self.get_string_width(word) <= w - 2:
                out.append(word); continue
            cur = ""
            for ch in word:
                if self.get_string_width(cur + ch) > w - 2 and cur:
                    out.append(cur); cur = ch
                else:
                    cur += ch
            if cur:
                out.append(cur)
        return " ".join(out)

    def _nlines(self, text: str, w: float) -> int:
        self.set_font("Helvetica", "", 8.6)
        words = text.split(" ")
        lines, cur = 1, ""
        for word in words:
            trial = (cur + " " + word).strip()
            if self.get_string_width(trial) > w and cur:
                lines += 1; cur = word
            else:
                cur = trial
        return lines
