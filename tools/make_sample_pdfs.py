#!/usr/bin/env python3
"""
make_sample_pdfs.py — Generate FAKE payroll PDFs for testing paystub_lookup.py.

All names, IDs, companies and amounts are invented. Each PDF mimics the layout
the lookup script relies on:

  * A stub page that contains the text "Employee ID <id>" with the employee's
    name on the line just above it.
  * For paper checks, a following "check image" page that does NOT contain the
    words "Employee ID".
  * For direct deposit, no check image page (the next page is another stub).

Usage:
    pip install reportlab
    python3 tools/make_sample_pdfs.py            # writes to sample_data/SampleBatch
    python3 tools/make_sample_pdfs.py OUT_DIR    # writes somewhere else
"""

import os
import sys

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

COMPANY = "Acme Sample Co. (FICTIONAL)"

# (employee_id, name, hourly_rate, hours, paid_by_check)
EMPLOYEES = [
    ("22891", "Jordan Rivera", 24.50, 80, True),
    ("10450", "Casey Morgan", 31.00, 80, False),   # direct deposit -> no check page
    ("228910", "Taylor Brooks", 19.75, 72, True),  # look-alike ID to test exact matching
    ("30117", "Avery Chen", 27.25, 80, True),
]

CHECK_DATES = [
    ("2026-03-13", "02/28/2026 - 03/13/2026"),
    ("2026-03-27", "03/14/2026 - 03/27/2026"),
    ("2026-04-10", "03/28/2026 - 04/10/2026"),
]


def money(x):
    return f"${x:,.2f}"


def draw_watermark(c):
    c.saveState()
    c.setFont("Helvetica-Bold", 60)
    c.setFillGray(0.9)
    c.translate(306, 396)
    c.rotate(35)
    c.drawCentredString(0, 0, "SAMPLE")
    c.restoreState()


def draw_stub(c, emp, check_date, period, check_no):
    emp_id, name, rate, hours, by_check = emp
    gross = rate * hours
    fed = round(gross * 0.10, 2)
    ss = round(gross * 0.062, 2)
    med = round(gross * 0.0145, 2)
    state = round(gross * 0.04, 2)
    net = gross - fed - ss - med - state

    draw_watermark(c)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 740, COMPANY)
    c.setFont("Helvetica", 9)
    c.drawString(50, 726, "100 Example Street, Sample City, CA 90000")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 690, "EARNINGS STATEMENT")
    c.setFont("Helvetica", 10)
    # Order matters: lines just above "Employee ID" contain digits, so the
    # script's name-detection picks the name line, not these.
    c.drawString(50, 670, f"Check Date {check_date}")
    c.drawString(50, 656, f"Pay Period {period}")
    c.drawString(50, 642, f"Check No {check_no}" if by_check else "Direct Deposit 0001")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 622, name)
    c.setFont("Helvetica", 10)
    c.drawString(50, 608, f"Employee ID {emp_id}")

    y = 570
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Earnings")
    c.drawString(250, y, "Hours")
    c.drawString(330, y, "Rate")
    c.drawString(430, y, "Current")
    c.setFont("Helvetica", 10)
    y -= 16
    c.drawString(50, y, "Regular")
    c.drawString(250, y, f"{hours:.2f}")
    c.drawString(330, y, money(rate))
    c.drawString(430, y, money(gross))

    y -= 36
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Taxes / Deductions")
    c.drawString(430, y, "Current")
    c.setFont("Helvetica", 10)
    for label, amt in [
        ("Federal Income Tax", fed),
        ("Social Security", ss),
        ("Medicare", med),
        ("State Income Tax", state),
    ]:
        y -= 16
        c.drawString(50, y, label)
        c.drawString(430, y, money(amt))

    y -= 36
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Gross Pay")
    c.drawString(430, y, money(gross))
    y -= 18
    c.drawString(50, y, "Net Pay")
    c.drawString(430, y, money(net))

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 40, "Sample document generated for testing. Not a real pay statement.")
    c.showPage()
    return net


def draw_check_image(c, name, check_date, check_no, net):
    """A fake check image page. Must NOT contain the words 'Employee ID'."""
    draw_watermark(c)
    c.rect(50, 480, 512, 220)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(65, 680, COMPANY)
    c.setFont("Helvetica", 10)
    c.drawRightString(545, 680, f"No. {check_no}")
    c.drawRightString(545, 664, f"Date {check_date}")
    c.drawString(65, 620, "PAY TO THE ORDER OF")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(200, 620, name)
    c.rect(440, 610, 105, 22)
    c.drawString(448, 617, money(net))
    c.setFont("Helvetica", 10)
    c.drawString(65, 590, "VOID - SAMPLE CHECK - NON NEGOTIABLE")
    c.line(360, 520, 545, 520)
    c.setFont("Helvetica", 8)
    c.drawString(360, 508, "Authorized Signature")
    c.setFont("Courier", 11)
    c.drawString(65, 492, "C000000C A000000000A 0000000000C")
    c.showPage()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "sample_data", "SampleBatch")
    os.makedirs(out_dir, exist_ok=True)

    check_no = 5001
    for check_date, period in CHECK_DATES:
        path = os.path.join(out_dir, f"Check Stub - Check Date {check_date}.pdf")
        c = canvas.Canvas(path, pagesize=letter)
        c.setTitle(f"SAMPLE Check Stubs {check_date}")
        for emp in EMPLOYEES:
            net = draw_stub(c, emp, check_date, period, check_no)
            if emp[4]:
                draw_check_image(c, emp[1], check_date, check_no, net)
                check_no += 1
        c.save()
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
