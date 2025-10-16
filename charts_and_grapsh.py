# reads data csv file, outputs several graphics created with matplotlib

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def clean_and_convert_to_numeric(series):
    """
    Cleans a pandas Series by removing common non-numeric characters ($, %, ,)
    and converts it to a numeric type. Replaces common non-data entries
    with NaN and coerces conversion errors to NaN.
    """
    if pd.api.types.is_numeric_dtype(series):
        return series
        
    # Convert to string, remove symbols, and handle non-data entries
    cleaned = (
        series.astype(str)
        .str.replace(r'[$,%]', '', regex=True)
        .str.strip()
        .replace(['', 'N/A', 'nan'], np.nan)
    )
    # Convert to a numeric type, setting invalid parsing as NaN
    return pd.to_numeric(cleaned, errors='coerce')

def create_hybrid_plot(df, value_col, category_col, ax, title, ylabel):
    """
    Generates a hybrid violin/swarm plot with detailed annotations.
    - Violin plot for 'Independent' category.
    - Swarm plots for all categories, including 'Independent'.
    - Annotates min, median, and max values for every category.
    - Special handling for 'FPG Beers & Story' if it has a single price.
    """
    plot_df = df.dropna(subset=[value_col, category_col])
    if plot_df.empty or plot_df[category_col].nunique() == 0:
        ax.text(0.5, 0.5, f"No data available for {title}", ha='center', va='center')
        return

    category_order = sorted(plot_df[category_col].unique())
    
    # Separate data for different plot types
    independent_df = plot_df[plot_df[category_col] == 'Independent']
    corporate_df = plot_df[plot_df[category_col] != 'Independent']

    # 1. Plot violin for the large "Independent" category if it exists
    if not independent_df.empty:
        sns.violinplot(data=independent_df, x=category_col, y=value_col,
                       ax=ax, order=category_order, inner=None, color='#A9CDE1', linewidth=1.5)

    # 2. Plot swarm for all categories to show individual data points
    sns.swarmplot(data=plot_df, x=category_col, y=value_col,
                  ax=ax, order=category_order, color=".25", alpha=0.7, size=4.5)

    # 3. Add dynamic annotations for every category
    for i, cat in enumerate(category_order):
        cat_data = plot_df[plot_df[category_col] == cat][value_col]
        if cat_data.empty:
            continue

        # Special labeling for FPG if it has only one unique price point
        if cat == 'FPG Beers & Story' and cat_data.nunique() == 1:
            single_val = cat_data.iloc[0]
            ax.annotate(f'${single_val:,.0f}', xy=(i, single_val),
                        xytext=(0, 5), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold', color='black')
        else: # Default labeling for all other categories
            median_val = cat_data.median()
            min_val = cat_data.min()
            max_val = cat_data.max()

            # Annotate Median
            ax.plot([i - 0.2, i + 0.2], [median_val, median_val], color='black', lw=2)
            ax.annotate(f'Median: ${median_val:,.0f}', xy=(i, median_val),
                        xytext=(0, 5), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold', color='black')

            # Annotate Highest
            ax.annotate(f'${max_val:,.0f}', xy=(i, max_val),
                        xytext=(0, 5), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, color='firebrick')
            
            # Annotate Lowest
            ax.annotate(f'${min_val:,.0f}', xy=(i, min_val),
                        xytext=(0, -12), textcoords="offset points",
                        ha='center', va='top', fontsize=9, color='darkgreen')

    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel(category_col, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)

def main():
    """
    Main function to load, clean, and visualize funeral home data.
    """
    try:
        # --- Set a global theme for all plots for a modern look ---
        sns.set_theme(style="whitegrid", palette="muted")

        # --- 1. Load Data ---
        df = pd.read_csv('oct10-fh-data.csv')

        # --- Sanitize whitespace from all string columns ---
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()

        # --- 2. Data Cleaning ---
        cols_to_clean = [
            'Latitude', 'Longitude', 'BasicServicesFee', 
            'DirectCremationLowestPrice', 'DirectCremation_Pct_Change',
            'ImmediateBurialLowestPrice'
        ]
        for col in cols_to_clean:
            if col in df.columns:
                df[f'{col}_cleaned'] = clean_and_convert_to_numeric(df[col])
            else:
                print(f"Warning: Column '{col}' not found in the CSV file.")

        # --- 3. Create Visualizations ---

        # Visualization 1: Geographic Distribution
        fig1, ax1 = plt.subplots(figsize=(10, 8))
        plot_df1 = df.dropna(subset=['Latitude_cleaned', 'Longitude_cleaned', 'Ownership'])
        if not plot_df1.empty:
            sns.scatterplot(data=plot_df1, x='Longitude_cleaned', y='Latitude_cleaned', hue='Ownership', ax=ax1, alpha=0.7, s=50)
            ax1.set_title('Geographic Distribution of Funeral Homes by Ownership', fontsize=16, fontweight='bold')
            ax1.set_xlabel('Longitude', fontsize=12)
            ax1.set_ylabel('Latitude', fontsize=12)
            ax1.legend(title='Ownership')
        else:
            ax1.text(0.5, 0.5, "No data for Geographic Distribution plot.", ha='center', va='center')
        fig1.tight_layout()
        sns.despine(fig=fig1)
        fig1.savefig('geographic_distribution.png')

        # Visualization 2: Direct Cremation Price Distribution (Histogram)
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        plot_df2 = df.dropna(subset=['DirectCremationLowestPrice_cleaned'])
        if not plot_df2.empty:
            sns.histplot(data=plot_df2, x='DirectCremationLowestPrice_cleaned', bins=25, ax=ax2, kde=True)
            ax2.set_title('Distribution of Direct Cremation Lowest Price', fontsize=16, fontweight='bold')
            ax2.set_xlabel('Price ($)', fontsize=12)
            ax2.set_ylabel('Number of Funeral Homes', fontsize=12)
        else:
            ax2.text(0.5, 0.5, "No data for Direct Cremation Price plot.", ha='center', va='center')
        fig2.tight_layout()
        sns.despine(fig=fig2)
        fig2.savefig('cremation_price_distribution.png')

        # Visualization 3: Immediate Burial Price Distribution (Histogram)
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        plot_df3 = df.dropna(subset=['ImmediateBurialLowestPrice_cleaned'])
        if not plot_df3.empty:
            sns.histplot(data=plot_df3, x='ImmediateBurialLowestPrice_cleaned', bins=25, ax=ax3, kde=True, color='teal')
            ax3.set_title('Distribution of Immediate Burial Lowest Price', fontsize=16, fontweight='bold')
            ax3.set_xlabel('Price ($)', fontsize=12)
            ax3.set_ylabel('Number of Funeral Homes', fontsize=12)
        else:
            ax3.text(0.5, 0.5, "No data for Immediate Burial Price plot.", ha='center', va='center')
        fig3.tight_layout()
        sns.despine(fig=fig3)
        fig3.savefig('immediate_burial_price_distribution.png')
        
        # --- HYBRID CHARTS ---
        # Visualization 4: Hybrid Chart for Basic Services Fee
        fig4, ax4 = plt.subplots(figsize=(12, 8))
        create_hybrid_plot(df, 'BasicServicesFee_cleaned', 'Ownership', ax4,
                             'Distribution of Basic Services Fee by Ownership Type',
                             'Basic Services Fee ($)')
        fig4.tight_layout()
        sns.despine(fig=fig4)
        fig4.savefig('basic_services_fee_hybrid_plot.png')

        # Visualization 5: Hybrid Chart for Direct Cremation Lowest Price
        fig5, ax5 = plt.subplots(figsize=(12, 8))
        create_hybrid_plot(df, 'DirectCremationLowestPrice_cleaned', 'Ownership', ax5,
                             'Distribution of Direct Cremation Price by Ownership Type',
                             'Direct Cremation Lowest Price ($)')
        fig5.tight_layout()
        sns.despine(fig=fig5)
        fig5.savefig('direct_cremation_hybrid_plot.png')
        
        # Visualization 6: Hybrid Chart for Immediate Burial Lowest Price
        fig6, ax6 = plt.subplots(figsize=(12, 8))
        create_hybrid_plot(df, 'ImmediateBurialLowestPrice_cleaned', 'Ownership', ax6,
                             'Distribution of Immediate Burial Price by Ownership Type',
                             'Immediate Burial Lowest Price ($)')
        fig6.tight_layout()
        sns.despine(fig=fig6)
        fig6.savefig('immediate_burial_hybrid_plot.png')

        # Visualization 7: Distribution of Direct Cremation Percentage Change
        fig7, ax7 = plt.subplots(figsize=(10, 6))
        plot_df7 = df.dropna(subset=['DirectCremation_Pct_Change_cleaned'])
        if not plot_df7.empty:
            sns.histplot(data=plot_df7, x='DirectCremation_Pct_Change_cleaned', bins=25, ax=ax7, kde=True, color='skyblue')
            ax7.set_title('Distribution of Percentage Change in Direct Cremation Price', fontsize=16, fontweight='bold')
            ax7.set_xlabel('Percentage Change (%)', fontsize=12)
            ax7.set_ylabel('Number of Funeral Homes', fontsize=12)
        else:
            ax7.text(0.5, 0.5, "No data for Cremation Pct. Change plot.", ha='center', va='center')
        fig7.tight_layout()
        sns.despine(fig=fig7)
        fig7.savefig('cremation_percentage_change.png')

        # Visualization 8: Relationship between Basic Services Fee and Direct Cremation Price
        fig8, ax8 = plt.subplots(figsize=(11, 7))
        plot_df8 = df.dropna(subset=['BasicServicesFee_cleaned', 'DirectCremationLowestPrice_cleaned', 'Ownership'])
        if not plot_df8.empty:
            sns.scatterplot(data=plot_df8, x='DirectCremationLowestPrice_cleaned', y='BasicServicesFee_cleaned', 
                            hue='Ownership', ax=ax8, alpha=0.8, s=60, palette='viridis')
            sns.regplot(data=plot_df8, x='DirectCremationLowestPrice_cleaned', y='BasicServicesFee_cleaned', 
                        ax=ax8, scatter=False, color='black', line_kws={'linestyle':'--'})
            ax8.set_title('Basic Services Fee vs. Direct Cremation Price by Ownership', fontsize=16, fontweight='bold')
            ax8.set_xlabel('Direct Cremation Lowest Price ($)', fontsize=12)
            ax8.set_ylabel('Basic Services Fee ($)', fontsize=12)
        else:
            ax8.text(0.5, 0.5, "No data for Fee vs. Cremation Price plot.", ha='center', va='center')
        fig8.tight_layout()
        sns.despine(fig=fig8)
        fig8.savefig('fee_vs_cremation_price.png')

        print("Plots have been saved to the script's directory as PNG files.")

    except FileNotFoundError:
        print("Error: 'oct10-fh-data.csv' not found. Please ensure it's in the same directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

