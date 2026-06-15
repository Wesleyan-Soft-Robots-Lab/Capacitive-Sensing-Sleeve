import pandas as pd
import matplotlib.pyplot as plt
import math 

def normalizeData(csv_file):
    ds = pd.read_csv(csv_file)
    averages = {}
    max_vals = {} 
    min_vals = {}
    max_y = 0
    min_y = 0
    
    for col in ds.columns:
        if col != "Timestamp":
            if pd.api.types.is_numeric_dtype(ds[col]):
                averages[col] = ds[col].iloc[:1600].mean()
                ds[col] = ds[col] - averages[col]         
                max_vals[col] = ds[col].abs().max()
                min_vals[col] = ds[col].min()
                max_y = max(max_y, max_vals[col])
                min_y = min(min_y, min_vals[col])
    return ds, max_y, min_y

def plotGraphs(csv_file):
    normalized_ds, max_y, min_y = normalizeData(csv_file)
    
    cols_to_plot = [col for col in normalized_ds.columns if col != "Timestamp" and pd.api.types.is_numeric_dtype(normalized_ds[col])]
    num_plots = len(cols_to_plot)

    num_rows = math.ceil(num_plots / 2)
    
    fig, axes = plt.subplots(nrows=num_rows, ncols=2, figsize=(14, 3 * num_rows))
    
    if num_plots > 1:
        axes = axes.flatten()
    else:
        axes = [axes]
        
    for i, col in enumerate(cols_to_plot):
        normalized_ds.plot(x="Timestamp", y=col, ax=axes[i], title=col, ylim=(min_y*1.05, max_y*1.05))
        
    if num_plots > 1:
        for j in range(num_plots, len(axes)):
            axes[j].set_visible(False)
            
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    target_csv = "" 
    
    print(f"Loading and plotting data from {target_csv}...")
    try:
        plotGraphs(target_csv)
        print("Finished plotting all columns.")
    except FileNotFoundError:
        print(f"Error: Could not find the file '{target_csv}'")