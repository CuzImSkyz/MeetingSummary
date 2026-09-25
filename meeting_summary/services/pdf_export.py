"""PDF-Ausgabe mit ReportLab."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
)

from ..exceptions import PdfExportError
from ..models import MeetingProtocol


class _Checkbox(Flowable):
    """Zeichnet eine leere Checkbox als Vektorgrafik."""

    def __init__(self, size: float = 3.5 * mm) -> None:
        super().__init__()
        self.width = size
        self.height = size

    def draw(self) -> None:
        self.canv.rect(
            0,
            0,
            self.width,
            self.height,
            stroke=1,
            fill=0,
        )


class ReportLabExporter:
    def export(self, protocol: MeetingProtocol, target_path: Path) -> Path:
        """Erzeugt ein formatiertes PDF aus einem Meeting-Protokoll."""

        output_path = target_path.with_suffix(".pdf")

        try:
            styles = getSampleStyleSheet()
            document = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                title="Meeting-Protokoll",
            )
            story = [
                Paragraph("Meeting-Protokoll", styles["Title"]),
                Spacer(1, 6 * mm),
                Paragraph("Kurzfassung", styles["Heading2"]),
                Paragraph(
                    escape(protocol.short_summary),
                    styles["BodyText"],
                ),
            ]

            if protocol.topics:
                story.extend(
                    [
                        Spacer(1, 6 * mm),
                        Paragraph("Themen", styles["Heading2"]),
                    ]
                )
                for topic in protocol.topics:
                    story.append(
                        Paragraph(
                            escape(topic.title),
                            styles["Heading3"],
                        )
                    )
                    story.append(
                        ListFlowable(
                            [
                                ListItem(
                                    Paragraph(
                                        escape(bullet_point),
                                        styles["BodyText"],
                                    )
                                )
                                for bullet_point in topic.bullet_points
                            ],
                            bulletType="bullet",
                            leftIndent=6 * mm,
                        )
                    )
            if protocol.todos:
                story.extend(
                    [
                        Spacer(1, 6 * mm),
                        Paragraph("To-dos", styles["Heading2"]),
                    ]
                )
                todo_rows = []
                for todo in protocol.todos:
                    todo_text = escape(todo.task)

                    if todo.assignee:
                        todo_text += (
                            f" - <b>Zuständig:</b> {escape(todo.assignee)}"
                        )

                    todo_rows.append(
                        [
                            _Checkbox(),
                            Paragraph(todo_text, styles["BodyText"]),
                        ]
                    )
                story.append(
                    Table(
                        todo_rows,
                        colWidths=(6 * mm, None),
                        style=[
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (0, -1), 2 * mm),
                            ("TOPPADDING", (0, 0), (-1, -1), 1 * mm),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 1 * mm),
                        ],
                    )
                )

            document.build(story)
        except Exception as exc:
            raise PdfExportError(
                f"PDF konnte nicht erstellt werden: {output_path}"
            ) from exc

        return output_path
