# Crop disease medicine datasets

Place these two CSV files in this folder so the app can suggest **medicine** and **fertilizer** and show **disease analysis** (pathogen, symptoms) after prediction:

1. **final_merged_crop_disease_medicine_dataset.csv**  
   Columns: `Crop`, `Disease`, `Pathogen`, `Symptoms`, `Recommended_Medicine`, `Application_Notes`, `Severity`

2. **huge_crop_dataset_tomato_potato_corn_sugarcane.csv**  
   Columns: `Crop`, `Disease`, `Pathogen`, `Symptoms`, `Severity`, `Recommended_Medicine`, `Application_Notes`

The app looks for the CSVs in this order:

1. **This folder** – `backend\data\` (same filenames as below)
2. **Your Downloads folder** – `final_merged_crop_disease_medicine_dataset.csv` and `huge_crop_dataset_tomato_potato_corn_sugarcane.csv`
3. **Paths set by env** – see below

Copy from your Desktop or Downloads to:

- `backend\data\final_merged_crop_disease_medicine_dataset.csv`
- `backend\data\huge_crop_dataset_tomato_potato_corn_sugarcane.csv`

Alternatively, set environment variables to use files elsewhere:

- `MEDICINE_CSV_PATH` – path to the merged medicine CSV
- `CROP_DATASET_CSV_PATH` – path to the tomato/potato/corn/sugarcane CSV
