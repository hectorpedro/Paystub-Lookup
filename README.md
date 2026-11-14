# Paystub Lookup

Pull one employee's pay stubs out of a stack of payroll PDFs and combine them into a single file.

Payroll exports (e.g. from Paylocity) usually come as one big PDF per check date, with every employee's stub inside. When an employee asks for their archived paystubs over a date range, you'd normally have to dig through each file by hand. This script does it for you: pick a folder, type an Employee ID, and it builds `<EMPLOYEE_ID>.pdf` with only that person's pages.

## How it works

For every file named `Check Stub - Check Date *.pdf` in the folder you choose, the script:

1. Finds each page that contains `Employee ID <your ID>` (exact match, so `22891` won't match `228910`).
2. Keeps that page.
3. If the **next** page has no "Employee ID" on it, treats it as that stub's check image and keeps it too. (Direct-deposit stubs have no check page, so nothing extra is added.)
4. Saves everything, in order, to `<EMPLOYEE_ID>.pdf` in the same folder and prints the employee's name and page count.

## Requirements

- Python 3.8+
- [PyMuPDF](https://pymupdf.readthedocs.io/)

```bash
pip3 install -r requirements.txt
```

## Usage

1. Put `paystub_lookup.py` in your **Downloads** folder.
2. Create a subfolder inside Downloads (e.g. `Downloads/Paystubs`).
3. Copy the payroll PDFs for the date range you need into that subfolder.
4. Open Terminal and run:

   ```bash
   python3 ~/Downloads/paystub_lookup.py
   ```

5. Pick the subfolder by number, then enter the Employee ID.

Example output:

```
Subfolders in /Users/you/Downloads:

  1. Paystubs

Select a folder by number: 1
Enter the Employee ID to look up: 22891
Scanning /Users/you/Downloads/Paystubs
Found 3 PDF(s)
  Check Stub - Check Date 2026-03-13.pdf: 2 page(s)
  Check Stub - Check Date 2026-03-27.pdf: 2 page(s)
  Check Stub - Check Date 2026-04-10.pdf: 2 page(s)

Total pages extracted: 6
Employee ID: 22891
Employee Name: Jordan Rivera

Done.
New compiled file created: 22891.pdf
```

## Try it with the sample data

`sample_data/SampleBatch/` has three **fake** payroll PDFs (made-up company, names and amounts) so you can test without real payroll files.

1. Copy the `SampleBatch` folder into your Downloads folder.
2. Run `python3 ~/Downloads/paystub_lookup.py` (or from wherever you cloned the repo), choose `SampleBatch`, and try these IDs:

| Employee ID | Name | What it tests | Expected pages |
|---|---|---|---|
| `22891` | Jordan Rivera | Paper check: stub + check image | 6 |
| `10450` | Casey Morgan | Direct deposit: stub only | 3 |
| `228910` | Taylor Brooks | Look-alike ID: must not mix with 22891 | 6 |
| `30117` | Avery Chen | Paper check, last employee in each file | 6 |
| `99999` | — | Not found | 0 |

To regenerate or customize the sample PDFs:

```bash
pip3 install reportlab
python3 tools/make_sample_pdfs.py
```

## Adapting to your payroll format

- **File names:** change `SOURCE_PATTERN` at the top of the script if your exports are named differently.
- **ID label:** the script searches for the text `Employee ID`. If your stubs say something else (e.g. `Emp #`), update the regex in `main()` and the `"Employee ID"` checks.
- **Folder location:** change `DOWNLOADS_DIR` to scan somewhere other than Downloads.

## ⚠️ Privacy

Real pay stubs contain personal and financial information. **Never commit real payroll PDFs to this repository.** The included `.gitignore` blocks all PDFs except the sample folder.

## Project layout

```
paystub-lookup/
├── paystub_lookup.py          # the tool
├── requirements.txt           # pymupdf
├── tools/
│   └── make_sample_pdfs.py    # builds the fake sample PDFs (needs reportlab)
└── sample_data/
    └── SampleBatch/           # 3 fake payroll PDFs for testing
```
