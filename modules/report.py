# modules/report.py
"""Report Module for VigiLo.

Gathers system metadata, security logs, and photo evidence, compiling them
into a professional, insurance/police-ready PDF report using ReportLab.
"""

from __future__ import annotations

import os
import socket
import platform
import getpass
import uuid
import datetime
import psutil
import json

from modules.base import BaseModule
from utils.system import get_captures_dir
from logs.logger import logger


def get_local_ip() -> str:
    """Returns the primary local IP address of the target workstation."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_mac_address() -> str:
    """Returns the hardware MAC address of the active network interface."""
    try:
        mac = uuid.getnode()
        return ":".join(("%012X" % mac)[i : i + 2] for i in range(0, 12, 2))
    except Exception:
        return "Unknown"


def get_boot_time() -> str:
    """Returns the system boot timestamp formatted as YYYY-MM-DD HH:MM:SS."""
    try:
        bt = psutil.boot_time()
        return datetime.datetime.fromtimestamp(bt).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Unknown"


def get_logged_in_user() -> str:
    """Bulletproof username resolution supporting SYSTEM service context fallbacks."""
    for func in [os.getlogin, getpass.getuser]:
        try:
            val = func()
            if val:
                return val
        except Exception:
            pass
    for env in ["USERNAME", "USER", "LOGNAME"]:
        val = os.environ.get(env)
        if val:
            return val
    return "SYSTEM / Background Logon"


class ReportModule(BaseModule):
    """Compiles recovery evidence and generates a professional security PDF report."""

    def __init__(self) -> None:
        pass

    def execute(self, save_dir: str | None = None) -> str | None:
        """Compiles device info, stats, and timeline to write and return a PDF path."""
        if not save_dir:
            save_dir = get_captures_dir()

        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_name = f"VigiLo_Incident_Report_{timestamp_str}.pdf"
        pdf_path = os.path.join(save_dir, pdf_name)

        try:
            # 1. Compile System Metadata
            sys_info = {
                "Workstation Hostname": socket.gethostname(),
                "Operating System": f"{platform.system()} {platform.release()} ({platform.version()})",
                "Active User Account": get_logged_in_user(),
                "Local IP Address": get_local_ip(),
                "MAC Address": get_mac_address(),
                "System Boot Time": get_boot_time(),
            }

            # 2. Load Face Verification Statistics
            stats_path = os.path.join(get_captures_dir(), "face_stats.json")
            stats = {"suppressed_owner_matches": 0, "escalated_intrusions": 0}
            if os.path.exists(stats_path):
                try:
                    with open(stats_path, "r", encoding="utf-8") as f:
                        stats = json.load(f)
                except Exception:
                    pass

            stats_info = {
                "Total Suppressed Owner False Alarms": str(
                    stats.get("suppressed_owner_matches", 0)
                ),
                "Total Escalated Intruder Alarms": str(
                    stats.get("escalated_intrusions", 0)
                ),
                "Face Verification State": "ACTIVE (ONNX Face Recognition)",
            }

            # 3. Build Timeline from captured intruder photos
            timeline_events = []
            image_evidence_path = None
            latest_time = 0

            # Scan captures directory for alert_*.jpg files
            if os.path.exists(save_dir):
                for filename in os.listdir(save_dir):
                    if filename.startswith("alert_") and (
                        filename.endswith(".jpg") or filename.endswith(".png")
                    ):
                        filepath = os.path.join(save_dir, filename)
                        file_mtime = os.path.getmtime(filepath)

                        # Try extracting timestamp from alert_<timestamp>.jpg filename
                        try:
                            parts = filename.split("_")
                            if len(parts) > 1:
                                ts = int(parts[1].split(".")[0])
                            else:
                                ts = int(file_mtime)
                        except Exception:
                            ts = int(file_mtime)

                        dt_str = datetime.datetime.fromtimestamp(ts).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        timeline_events.append(
                            (dt_str, "WORKSTATION INTRUSION ESCALATED")
                        )

                        if ts > latest_time:
                            latest_time = ts
                            image_evidence_path = filepath

            # Sort timeline by time (earliest first)
            timeline_events.sort(key=lambda x: x[0])

            # Keep only the last 10 timeline entries for report brevity
            timeline_events = timeline_events[-10:]

            # 4. Generate the PDF
            self._compile_pdf(
                pdf_path=pdf_path,
                sys_info=sys_info,
                stats_info=stats_info,
                timeline_events=timeline_events,
                image_path=image_evidence_path,
            )

            logger.info(f"ReportModule: PDF Report generated successfully: {pdf_path}")
            return pdf_path

        except Exception as exc:
            logger.error(f"ReportModule: Failed to compile security PDF report: {exc}")
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except Exception:
                    pass
            return None

    def _compile_pdf(
        self,
        pdf_path: str,
        sys_info: dict,
        stats_info: dict,
        timeline_events: list,
        image_path: str | None,
    ) -> None:
        """ReportLab helper to build and format the PDF flowables document."""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            Image,
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#4A90D9"),
            spaceAfter=12,
        )

        h2_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1e1e1e"),
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True,
        )

        body_style = ParagraphStyle(
            "BodyTextCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#333333"),
        )

        bold_style = ParagraphStyle(
            "BodyBoldCustom", parent=body_style, fontName="Helvetica-Bold"
        )

        story = []

        # Header Title
        story.append(Paragraph("VigiLo Security Incident Report", title_style))

        # Metadata subtitle
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(
            Paragraph(
                f"<b>Report Generated:</b> {now_str} (Local Workstation Time)",
                body_style,
            )
        )
        story.append(Spacer(1, 15))

        # Section 1: Device Info
        story.append(Paragraph("1. Target Device Information", h2_style))
        sys_data = [
            [
                Paragraph("<b>Property</b>", bold_style),
                Paragraph("<b>Value</b>", bold_style),
            ]
        ]
        for k, v in sys_info.items():
            sys_data.append(
                [Paragraph(str(k), body_style), Paragraph(str(v), body_style)]
            )

        t_sys = Table(sys_data, colWidths=[150, 390])
        t_sys.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#eff4f9")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdcdc")),
                    ("PADDING", (0, 0), (-1, -1), 5),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(t_sys)
        story.append(Spacer(1, 15))

        # Section 2: Security Stats
        story.append(Paragraph("2. Intrusion & Verification Statistics", h2_style))
        stats_data = [
            [
                Paragraph("<b>Metric</b>", bold_style),
                Paragraph("<b>Count / Status</b>", bold_style),
            ]
        ]
        for k, v in stats_info.items():
            stats_data.append(
                [Paragraph(str(k), body_style), Paragraph(str(v), body_style)]
            )

        t_stats = Table(stats_data, colWidths=[250, 290])
        t_stats.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#eff4f9")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdcdc")),
                    ("PADDING", (0, 0), (-1, -1), 5),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(t_stats)
        story.append(Spacer(1, 15))

        # Section 3: Timeline
        story.append(Paragraph("3. Recent Intrusion Timeline", h2_style))
        if timeline_events:
            time_data = [
                [
                    Paragraph("<b>Time of Attempt</b>", bold_style),
                    Paragraph("<b>Verification Result</b>", bold_style),
                ]
            ]
            for t, res in timeline_events:
                time_data.append(
                    [Paragraph(str(t), body_style), Paragraph(str(res), body_style)]
                )

            t_time = Table(time_data, colWidths=[200, 340])
            t_time.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#eff4f9")),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdcdc")),
                        ("PADDING", (0, 0), (-1, -1), 5),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                )
            )
            story.append(t_time)
        else:
            story.append(
                Paragraph(
                    "No failed login attempts recorded in the offline queue.",
                    body_style,
                )
            )
        story.append(Spacer(1, 15))

        # Section 4: Image Evidence
        if image_path and os.path.exists(image_path):
            story.append(
                Paragraph(
                    "4. Captured Photo Evidence (Last Escalated Attempt)", h2_style
                )
            )
            try:
                img_flowable = Image(image_path, width=240, height=180)
                story.append(img_flowable)
            except Exception as e:
                story.append(
                    Paragraph(
                        f"<i>Could not render evidence image: {e}</i>",
                        body_style,
                    )
                )

        doc.build(story)
