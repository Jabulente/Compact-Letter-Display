from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.formula.api import ols as smf_ols 
from statsmodels.stats.anova import anova_lm 
import pandas as pd
import numpy as np

def compute_compact_letter_table(df, group_column, numeric_cols=None):
    if numeric_cols is None:  numeric_cols = df.select_dtypes(include=[np.number]).columns
        
    def calculate_stats_for_column(col_name):
        model = smf_ols(f'{col_name}~C({group_column})', data=df).fit()
        anova_results = anova_lm(model)
        p_value = anova_results.loc[f'C({group_column})', 'PR(>F)']
        tukey = pairwise_tukeyhsd(df[col_name], df[group_column])
        Turkey_results = pd.DataFrame(data=tukey._results_table.data[1:], columns=tukey._results_table.data[0])
        group_labels = letters(Turkey_results)
        stats = df.groupby(group_column)[col_name].agg(['mean', 'sem']).round(2)
        stats['letter'] = stats.index.map(group_labels)
        stats['formatted'] = stats.apply(
            lambda x: f"{x['mean']:.2f} ± {x['sem']:.2f} {x['letter']}", axis=1)
        
        return stats['formatted'], p_value
    results = {}
    p_values = {}
    
    for col in numeric_cols: results[col], p_values[col] = calculate_stats_for_column(col)
    
    results_df = pd.DataFrame(results)
    results_df.index.name = group_column
    p_values_formatted = {col: f"{p:.4f}" + ('***' if p <= 0.001 else '**' if p <= 0.01 else '*' if p <= 0.05 else 'ns') 
                         for col, p in p_values.items()}
    p_value_df = pd.DataFrame([p_values_formatted], index=['p-value'])
    final_results = pd.concat([results_df, p_value_df])
    return final_results

def compact_letter_table(df: pd.DataFrame, group_col: str, exclude: list = None) -> pd.DataFrame:
    def standardize_name(name: str) -> str:
        return re.sub(r'[^a-zA-Z]', '', name)

    if exclude: df = df.drop(columns=exclude)
    cleaned_group = standardize_name(group_col)
    df = df.rename(columns={col: standardize_name(col) for col in df.columns})
    results = compute_compact_letter_table(df, cleaned_group, numeric_cols=None)
    results.columns = df.select_dtypes(include=[np.number]).columns
    
    return results