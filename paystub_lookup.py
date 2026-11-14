#!/usr/bin/env python3
"""
paystub_lookup.py — Extract one employee's pay stubs from a folder of payroll PDFs.

Keep this script in your Downloads folder and drop each batch of payroll PDFs into
its own subfolder inside Downloads (e.g. Downloads/March2026).

Then just run it with no arguments:

    python3 paystub_lookup.py

It will:
  1. List the subfolders in Downloads so you can pick one by number.
  2. Ask for the Employee ID to look for.

It then scans every "Check Stub - Check Date *.pdf" in the chosen subfolder, pulls
out the pages belonging to that employee (plus the following check-image page), and
saves them to <EMPLOYEE_ID>.pdf in that same subfolder.
"""

import glob
import os
import re
import sys

import fitz  # pymupdf

SOURCE_PATTERN = "Check Stub - Check Date *.pdf"

# Always look in the user's Downloads folder, wherever the script is run from.
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")


def choose_subfolder():
    """List the subfolders in Downloads and let the user pick one by number."""
    subfolders = sorted(
        name
        for name in os.listdir(DOWNLOADS_DIR)
        if os.path.isdir(os.path.join(DOWNLOADS_DIR, name)) and not name.startswith(".")
    )

    if not subfolders:
        print(f"No subfolders found in {DOWNLOADS_DIR}")
        print("Create a subfolder there, drop your payroll PDFs in it, and run again.")
        sys.exit(1)

    print(f"Subfolders in {DOWNLOADS_DIR}:\n")
    for num, name in enumerate(subfolders, start=1):
        print(f"  {num}. {name}")

    while True:
        choice = input("\nSelect a folder by number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(subfolders):
            return os.path.join(DOWNLOADS_DIR, subfolders[int(choice) - 1])
        print(f"Please enter a number between 1 and {len(subfolders)}.")


def main():
    # 1. Let the user pick which subfolder of Downloads to scan.
    source_dir = choose_subfolder()

    # 2. Ask the user which Employee ID to look for.
    employee_id = input("Enter the Employee ID to look up: ").strip()
    if not employee_id:
        print("No Employee ID entered.")
        sys.exit(1)

    pdf_pattern = os.path.join(source_dir, SOURCE_PATTERN)
    pdf_files = sorted(glob.glob(pdf_pattern))

    if not pdf_files:
        print(f"No payroll PDFs found in {source_dir}")
        print(f"  (looking for files matching: {SOURCE_PATTERN})")
        sys.exit(1)

    print(f"Scanning {source_dir}")
    print(f"Found {len(pdf_files)} PDF(s)")

    output_pdf = fitz.open()
    total_pages = 0
    employee_name = None

    # Regex: "Employee ID" followed by whitespace then the exact ID (word-bounded).
    pattern = re.compile(r"Employee\s+ID\s+" + re.escape(employee_id) + r"\b")

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        doc = fitz.open(pdf_path)
        pages_found = 0

        i = 0
        while i < len(doc):
            page_text = doc[i].get_text()

            if pattern.search(page_text):
                # Rule 1: this is a paystub page for our employee — include it.
                output_pdf.insert_pdf(doc, from_page=i, to_page=i)
                pages_found += 1

                # Try to extract the employee name from this page (first match only).
                if not employee_name:
                    lines = page_text.split("\n")
                    for idx, line in enumerate(lines):
                        if "Employee ID" in line and employee_id in line:
                            for nearby in range(max(0, idx - 3), min(len(lines), idx + 3)):
                                candidate = lines[nearby].strip()
                                if (
                                    candidate
                                    and candidate != employee_id
                                    and "Employee ID" not in candidate
                                ):
                                    if re.match(r"^[A-Za-z\s,.'-]+$", candidate) and len(candidate) > 3:
                                        employee_name = candidate
                                        break
                            break

                # Rule 2: if the next page has no "Employee ID", treat it as this
                # stub's check image and include it too.
                if i + 1 < len(doc):
                    next_text = doc[i + 1].get_text()
                    if "Employee ID" not in next_text:
                        output_pdf.insert_pdf(doc, from_page=i + 1, to_page=i + 1)
                        pages_found += 1
                        i += 2
                        continue
            i += 1

        print(f"  {filename}: {pages_found} page(s)")
        total_pages += pages_found
        doc.close()

    if total_pages == 0:
        print(f"\nNo pages found for Employee ID {employee_id}")
        sys.exit(1)

    output_path = os.path.join(source_dir, f"{employee_id}.pdf")
    output_pdf.save(output_path)
    output_pdf.close()

    print(f"\nTotal pages extracted: {total_pages}")
    print(f"Employee ID: {employee_id}")
    if employee_name:
        print(f"Employee Name: {employee_name}")
    print("\nDone.")
    print(f"New compiled file created: {os.path.basename(output_path)}")


if __name__ == "__main__":
    main()
