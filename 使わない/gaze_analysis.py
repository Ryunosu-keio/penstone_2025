import pandas as pd
import os

directory = "C:\Users\ryuno\Box\中西研究室2023\ペンストン\実験データ\0816\視線データログ"  # Change this to the path of your directory containing the CSV files

excel_filepath = directory + "gaze_data_cleaned.xlsx" # Change this to the path of your output Excel file
# Create an Excel writer object
with pd.ExcelWriter(excel_filepath) as writer:
    sheet_num = 1
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            data_csv = pd.read_csv(filepath)
            
            # Remove rows from the beginning to the last row where CUE is 1
            last_cue_index = data_csv[data_csv['CUE'] == 1].index[-1]
            data_csv = data_csv.iloc[last_cue_index+1:]
            
            # Convert the 'FMR' column to time (FMR's difference from the first value divided by 60)
            initial_FMR = data_csv['FMR'].iloc[0]
            data_csv['FMR'] = (data_csv['FMR'] - initial_FMR) / 60.0
            
            # Rename the 'FMR' column to 'sec'
            data_csv.rename(columns={'FMR': 'sec'}, inplace=True)
            
            # Drop the specified columns
            data_csv = data_csv.drop(columns=['CUE', 'LP', 'RP', 'CX', 'CY'])
            
            # Write the modified data to a new sheet in the Excel file
            data_csv.to_excel(writer, sheet_name=f'Sheet{sheet_num}', index=False)
            sheet_num += 1
