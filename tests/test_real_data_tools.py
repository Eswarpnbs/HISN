import csv, importlib.util, subprocess, sys, zipfile, yaml

def test_official_retrieval_queries_are_sourced_from_the_government_portal():
    gold = yaml.safe_load(open("kb/retrieval_gold_official.yaml", encoding="utf-8"))
    assert len(gold) >= 12
    for g in gold:
        assert g["src"].startswith("https://u.ae/") and g["expected"] and g["q"].strip()

def test_smishing_tool_reads_the_dataset_layout(tmp_path):
    f = tmp_path / "d.csv"
    with open(f, "w", newline="") as h:
        w = csv.writer(h); w.writerow(["LABEL", "TEXT", "URL"])
        w.writerow(["Smishing", "Your account is blocked. Reply with your PIN now", "No"]); w.writerow(["ham", "see you at 5", "No"])
    spec = importlib.util.spec_from_file_location("rs", "tools/real_smishing_eval.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    rows, lab, txt = m.load(f.read_bytes())
    assert rows == [("smishing", "Your account is blocked. Reply with your PIN now"), ("ham", "see you at 5")] and (lab, txt) == ("LABEL", "TEXT")

def test_arabic_tool_reads_xlsx_without_extra_packages(tmp_path):
    ss = ('<?xml version="1.0"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>text</t></si>'
          '<si><t>label</t></si><si><t>ادفع الآن عبر الرابط</t></si><si><t>spam</t></si><si><t>صباح الخير</t></si><si><t>ham</t></si></sst>')
    sh = ('<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
          '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>'
          '<row r="2"><c r="A2" t="s"><v>2</v></c><c r="B2" t="s"><v>3</v></c></row>'
          '<row r="3"><c r="A3" t="s"><v>4</v></c><c r="B3" t="s"><v>5</v></c></row></sheetData></worksheet>')
    x = tmp_path / "a.xlsx"
    with zipfile.ZipFile(x, "w") as z: z.writestr("xl/sharedStrings.xml", ss); z.writestr("xl/worksheets/sheet1.xml", sh)
    spec = importlib.util.spec_from_file_location("ra", "tools/real_arabic_eval.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    header, body, lab, txt = m.pick_columns(m.read_xlsx(x))
    assert header[lab] == "label" and header[txt] == "text" and len(body) == 2
