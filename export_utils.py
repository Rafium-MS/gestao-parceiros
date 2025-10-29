"""Utilities to generate report exports in different formats."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Iterable, List, Mapping, MutableMapping, Optional

from config.settings import EXPORT_DIR


@dataclass
class ExportResult:
    """Container for a generated export file."""

    buffer: BytesIO
    filename: str
    mimetype: str
    path: Path


class ExportManager:
    """Create binary exports for report data.

    The manager centralises the creation of Excel and PDF files and stores a
    copy of the generated file under ``config.settings.EXPORT_DIR`` so that the
    backend keeps an audit trail of exported documents.
    """

    DEFAULT_BASENAME = "relatorio"
    EXCEL_MIMETYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    PDF_MIMETYPE = "application/pdf"

    def __init__(self, export_dir: Path | str = EXPORT_DIR) -> None:
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export(self, data: Iterable[Mapping[str, object]], fmt: str, *, filename: Optional[str] = None) -> ExportResult:
        """Export ``data`` to ``fmt`` and return a :class:`ExportResult`.

        Parameters
        ----------
        data:
            Iterable of dictionaries containing the rows that should be exported.
        fmt:
            Either ``"excel"`` or ``"pdf"`` (case-insensitive).
        filename:
            Optional filename (with or without extension). When omitted a
            timestamped name is generated automatically.
        """

        normalized = [dict(row) for row in data]
        fmt = (fmt or "").strip().lower()
        if fmt not in {"excel", "pdf"}:
            raise ValueError("Formato de exportação inválido. Use 'excel' ou 'pdf'.")

        if filename:
            filename = self._ensure_extension(filename, fmt)
        else:
            filename = self._default_filename(fmt)

        if fmt == "excel":
            buffer = self._export_excel(normalized)
            mimetype = self.EXCEL_MIMETYPE
        else:
            buffer = self._export_pdf(normalized)
            mimetype = self.PDF_MIMETYPE

        path = self._persist_copy(buffer, filename)
        buffer.seek(0)
        return ExportResult(buffer=buffer, filename=filename, mimetype=mimetype, path=path)

    # ------------------------------------------------------------------
    # Helpers
    def _default_filename(self, fmt: str) -> str:
        extension = "xlsx" if fmt == "excel" else "pdf"
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{self.DEFAULT_BASENAME}_{timestamp}.{extension}"

    def _ensure_extension(self, filename: str, fmt: str) -> str:
        filename = filename.strip()
        expected_ext = ".xlsx" if fmt == "excel" else ".pdf"
        if not filename.lower().endswith(expected_ext):
            filename = f"{filename}{expected_ext}"
        return filename

    def _export_excel(self, data: List[MutableMapping[str, object]]) -> BytesIO:
        from pandas import DataFrame, ExcelWriter

        buffer = BytesIO()
        columns = list(data[0].keys()) if data else []
        df = DataFrame(data if data else [], columns=columns)
        with ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Relatório")
        buffer.seek(0)
        return buffer

    def _export_pdf(self, data: List[MutableMapping[str, object]]) -> BytesIO:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [Paragraph("Relatório de Marcas e Lojas", styles["Title"]), Spacer(1, 12)]

        if data:
            headers = list(data[0].keys())
            rows = [[str(row.get(col, "")) for col in headers] for row in data]
            table_data = [headers] + rows
        else:
            table_data = [["Sem dados disponíveis"]]

        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ]
            )
        )
        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def _persist_copy(self, buffer: BytesIO, filename: str) -> Path:
        path = self.export_dir / filename
        buffer.seek(0)
        path.write_bytes(buffer.getvalue())
        return path


__all__ = ["ExportManager", "ExportResult"]
