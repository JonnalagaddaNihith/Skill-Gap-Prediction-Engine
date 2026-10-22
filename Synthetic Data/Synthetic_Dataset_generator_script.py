import pandas as pd #type: ignore
from sdv.metadata import Metadata #type: ignore
from sdv.single_table import GaussianCopulaSynthesizer #type: ignore
from openpyxl import load_workbook #type: ignore
from openpyxl.worksheet.table import Table, TableStyleInfo #type: ignore

INPUT_FILE  = "learner_assessments.xlsx"
SHEET_NAME  = "Learner_Assessment"
TABLE_NAME  = "Learner_Assessment"
OUTPUT_FILE = "Generated_Learner_Assessment.xlsx"
METADATA_FILE = "Generated_metadata.json"
NUM_ROWS    = 100000

df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)
print(f"Loaded {len(df)} rows and {len(df.columns)} columns.")

metadata = Metadata._detect_from_dataframe(
    data=df,
    table_name=TABLE_NAME,
)

metadata.remove_primary_key(table_name=TABLE_NAME)

categorical_cols = [
    "student_id","question_id","skill_id","correct","attempt_number","response_time","hint_used","difficulty","course_id","answer_attempt","problem_type"
]
for col in categorical_cols:
    metadata.update_column(column_name=col, sdtype="categorical")

metadata.save_to_json(METADATA_FILE)

synthesizer = GaussianCopulaSynthesizer(metadata)
synthesizer.fit({TABLE_NAME: df})

result = synthesizer.sample(num_rows=NUM_ROWS)
synthetic_data = result[TABLE_NAME] if isinstance(result, dict) else result
print(f"Generated {len(synthetic_data)} synthetic rows.")

with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    synthetic_data.to_excel(writer, sheet_name="Synthetic", index=False)

wb = load_workbook(OUTPUT_FILE)

def add_excel_table(ws, display_name, style="TableStyleMedium9"):
    """Register the used range of a worksheet as an Excel Table."""
    ref = f"A1:{ws.cell(row=ws.max_row, column=ws.max_column).coordinate}"
    table = Table(displayName=display_name, ref=ref)
    table.tableStyleInfo = TableStyleInfo(
        name=style,
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    ws.add_table(table)

add_excel_table(wb["Synthetic"], "SyntheticStudentPerformance", style="TableStyleMedium9")

wb.save(OUTPUT_FILE)

print(f"Saved workbook with Excel Tables -> {OUTPUT_FILE}")