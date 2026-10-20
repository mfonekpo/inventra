import pandas as pd
from data_profiling import ProfileReport
from pathlib import Path


profiles_dir = Path(__file__).parent.parent / "data_profiles"
profiles_dir.mkdir(exist_ok=True)
dataset_dir = Path("../dataset")
data_files = dataset_dir.glob("*.csv")


for files in data_files:
    try:
        if not dataset_dir.is_dir():
            print("Not a directory, skipping")
            continue
        if not files.is_file():
            print("Not a file, skipping")
            continue
        print(f"Profiling {files.name}...\n")
        df = pd.read_csv(files)
        profile = ProfileReport(df, title=f"Profile Report: {files.name}", explorative=True)
        profile.to_file(profiles_dir / f"{files.stem}.html")
        print(f"\n{files.stem} Report saved to {profiles_dir}")
    except FileNotFoundError:
        print("File not found, skipping")
    except NotADirectoryError:
        print("Not a directory, skipping")
