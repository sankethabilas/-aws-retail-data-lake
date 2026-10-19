# data/

Local raw and processed data files. Everything in this folder except this README is git-ignored.

## Getting the data

From the repo root, with the virtual environment active:

```powershell
python -m src.download_data
```

The script:

1. Downloads `online_retail.zip` from the UCI Machine Learning Repository into `data/raw/`. If the zip is already there, it skips the download.
2. Extracts `Online Retail.xlsx`.
3. Converts the workbook once to `data/raw/online_retail.csv`, about 48 MB and 541,909 rows.
   - This CSV is the pipeline's source file. Nothing reads the `.xlsx` again.
   - All columns are written as text, so IDs like `85123A` keep their exact form.

Reading the workbook takes a minute or two. To use a different folder, pass `--raw-dir <path>`.

## Dataset credit

Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository.
<https://doi.org/10.24432/C5BW33>. Licensed under CC BY 4.0.
