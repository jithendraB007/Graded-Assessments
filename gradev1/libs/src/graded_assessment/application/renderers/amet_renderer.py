from __future__ import annotations

from io import BytesIO

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

from graded_assessment.application.renderers._base import (
    insert_logo, open_template, set_col_widths, set_document_font, set_table_borders,
)
from graded_assessment.domain.amet_types import AmetAssessmentRequest


def _bold_center(doc: Document, text: str, size: int = 11) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(size)


def _cell_center(cell) -> None:
    """Center-align text horizontally in a cell."""
    for para in cell.paragraphs:
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER


def _cell_vcenter(cell) -> None:
    """Vertically center content in a table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    vAlign = OxmlElement("w:vAlign")
    vAlign.set(qn("w:val"), "center")
    tcPr.append(vAlign)


def _add_table_row(table, cells: list[str], bold: bool = False) -> None:
    row = table.add_row()
    for i, text in enumerate(cells):
        cell = row.cells[i]
        cell.text = text
        if bold:
            for para in cell.paragraphs:
                for run in para.runs:
                    run.bold = True
    # Center Q.No column (col 0) and Mark/BTL/CO (cols 2-4) horizontally and vertically
    for idx in (0, 2, 3, 4):
        _cell_center(row.cells[idx])
        _cell_vcenter(row.cells[idx])
    return row


def _add_part_header(table, label: str) -> None:
    """Add a full-width merged bold-centered part label row."""
    row = table.add_row()
    row.cells[0].merge(row.cells[4])
    row.cells[0].text = label
    for para in row.cells[0].paragraphs:
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in para.runs:
            run.bold = True


def _add_or_row(table) -> None:
    row = table.add_row()
    row.cells[0].merge(row.cells[4])
    row.cells[0].text = "(OR)"
    row.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER


def _invisible_table(doc: Document, rows: int, cols: int):
    """Add a table with no visible borders."""
    tbl = doc.add_table(rows=rows, cols=cols)
    tbl_elem = tbl._tbl
    tblPr = tbl_elem.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl_elem.insert(0, tblPr)
    tblBorders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        border = OxmlElement(f"w:{side}")
        border.set(qn("w:val"), "none")
        border.set(qn("w:sz"), "0")
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), "auto")
        tblBorders.append(border)
    tblPr.append(tblBorders)
    return tbl


def render(request: AmetAssessmentRequest) -> bytes:
    doc = open_template("AMET")
    set_document_font(doc)
    insert_logo(doc, "amet")

    # ── Exam type title ──────────────────────────────────────────
    _bold_center(doc, request.exam_type, size=13)

    # ── Header info: 2-column invisible table ────────────────────
    # col widths: left 3.7" | right 2.8" = 6.5"
    info = _invisible_table(doc, rows=3, cols=2)
    set_col_widths(info, [3.7, 2.8])
    header_rows = [
        (f"Programme & Batch: {request.programme}", f"Semester        : {request.semester}"),
        (f"Course Name       : {request.course_name}", f"Course Code     : {request.course_code}"),
        (f"Duration          : {request.duration}", f"Maximum Marks: {request.max_marks} marks"),
    ]
    for r_idx, (left, right) in enumerate(header_rows):
        info.rows[r_idx].cells[0].text = left
        info.rows[r_idx].cells[1].text = right

    doc.add_paragraph()

    # ── Instructions ────────────────────────────────────────────
    p = doc.add_paragraph()
    p.add_run("Instructions:").bold = True
    for i, instr in enumerate(request.instructions, start=1):
        doc.add_paragraph(f"{i}. {instr}")

    doc.add_paragraph()

    # ── Question table ──────────────────────────────────────────
    # col widths: Q.No (0.65") | Question (4.25") | Mark (0.6") | BTL (0.5") | CO (0.5") = 6.5"
    table = doc.add_table(rows=1, cols=5)
    set_table_borders(table)
    set_col_widths(table, [0.65, 4.25, 0.6, 0.5, 0.5])

    # Column header row — all centered and bold
    hdr = table.rows[0].cells
    for i, h in enumerate(["Question No", "Question", "Mark", "BTL", "CO"]):
        hdr[i].text = h
        hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        hdr[i].paragraphs[0].runs[0].bold = True

    # ── Part A ───────────────────────────────────────────────────
    _add_part_header(
        table,
        f"PART A ({request.part_a.total})  {request.part_a.instruction}",
    )
    for q in request.part_a.questions:
        _add_table_row(table, [q.number, q.text, str(q.mark), q.btl, q.co])

    # ── Part B ───────────────────────────────────────────────────
    _add_part_header(
        table,
        f"PART B ({request.part_b.total})  {request.part_b.instruction}",
    )
    for pair in request.part_b.question_pairs:
        _add_table_row(table, [pair.a.number, pair.a.text, str(pair.a.mark), pair.a.btl, pair.a.co])
        _add_or_row(table)
        _add_table_row(table, [pair.b.number, pair.b.text, str(pair.b.mark), pair.b.btl, pair.b.co])

    # ── Part C ───────────────────────────────────────────────────
    _add_part_header(
        table,
        f"PART C ({request.part_c.total})  {request.part_c.instruction}",
    )
    q = request.part_c.question
    _add_table_row(table, [q.number, q.text, str(q.mark), q.btl, q.co])

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()
