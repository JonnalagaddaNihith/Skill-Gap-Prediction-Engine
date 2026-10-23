import pandas as pd  # type: ignore
import os  # type: ignore
from sdv.metadata import Metadata  # type: ignore
from sdv.single_table import GaussianCopulaSynthesizer  # type: ignore

INPUT_FILE  = "DataSet_Output/synthetic_learner_assessments.xlsx"
SHEET_NAME  = "Learner_Assessment"
TABLE_NAME  = "Learner_Assessment"
OUTPUT_FILE = "DataSet_Output/Generated_Learner_Assessment.csv"
METADATA_FILE = "DataSet_Output/Generated_metadata.json"
NUM_ROWS    = 500000

# Remove existing files if they exist
if os.path.exists(METADATA_FILE):
    os.remove(METADATA_FILE)
    print(f"Removed existing {METADATA_FILE}")

if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)
    print(f"Removed existing {OUTPUT_FILE}")

df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)
print(f"Loaded {len(df)} rows and {len(df.columns)} columns.")

metadata = Metadata._detect_from_dataframe(
    data=df,
    table_name=TABLE_NAME,
)

metadata.remove_primary_key(table_name=TABLE_NAME)

categorical_cols = [
    "student_id","question_id","skill_id","correct","attempt_number","response_time",
    "hint_used","difficulty","course_id","problem_type"
]
for col in categorical_cols:
    metadata.update_column(column_name=col, sdtype="categorical")

metadata.save_to_json(METADATA_FILE)

synthesizer = GaussianCopulaSynthesizer(metadata)
synthesizer.fit({TABLE_NAME: df})

result = synthesizer.sample(num_rows=NUM_ROWS)
synthetic_data = result[TABLE_NAME] if isinstance(result, dict) else result
print(f"Generated {len(synthetic_data)} synthetic rows.")

synthetic_data.to_csv(OUTPUT_FILE, index=False)
print(f"Saved CSV -> {OUTPUT_FILE}")