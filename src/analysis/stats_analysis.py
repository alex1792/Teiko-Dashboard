import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

from src.analysis.overview import get_population_frequency
# from overview import get_population_frequency

POPULATIONS = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']

def get_miraclib_melanoma_pbmc(path: str='cell-count.db') -> pd.DataFrame:
    '''
    find subjects with:
    1. subject.condition == 'melanoma' and subject.project == 'miraclib'
    2. subject.treatment == 'miraclib'
    3. join sample on  sample.subject_id == subject.subject_id
    4. sample.sample_type == 'PBMC
    
    '''

    # get population frequency dataframe from part2 using function in overview.py
    freq_df = get_population_frequency(path)

    # find subjects with conditions above
    query = """
    SELECT
        s.sample_id,
        sub.subject_id,
        sub.response,
        sub.condition,
        sub.treatment,
        s.sample_type,
        s.time_from_treatment_start
    FROM subjects sub
    JOIN samples s ON sub.subject_id = s.subject_id
    WHERE sub.condition = 'melanoma' 
        AND sub.treatment = 'miraclib'
        AND s.sample_type = 'PBMC'
        AND sub.response IN ('yes', 'no')
    """
    conn = sqlite3.connect(path)
    df = pd.read_sql_query(query, conn)
    conn.close()

    # merge the frequency and the subjects dataframe
    df = freq_df.merge(df, left_on='sample_id', right_on='sample_id', how='inner')

    # filter out, only keep sample_id, population, percentage, response
    analysis_df = df[['sample_id', 'population', 'percentage', 'response']]
    return analysis_df

def plot_response_boxplots(df: pd.DataFrame) -> plt.Figure:
    """Return a faceted boxplot comparing responders vs non-responders."""
    g = sns.catplot(
        data=df,
        x="response",
        y="percentage",
        col="population",
        col_order=POPULATIONS,
        order=["no", "yes"],
        kind="box",
        col_wrap=3,
        sharey=False,
        height=4,
    )
    g.set_axis_labels("Response", "Relative Frequency (%)")
    g.set_titles("{col_name}")
    g.fig.suptitle(
        "Miraclib Melanoma PBMC: Responders vs Non-responders",
        y=1.02,
    )
    return g.fig

def compare_response_groups(df: pd.DataFrame) -> None:
    '''
    compare the response of the subjects in different groups
    '''

    results = []

    for population in POPULATIONS:
        yes_vals = df[(df['population'] == population) & (df['response'] == 'yes')]['percentage']
        no_vals = df[(df['population'] == population) & (df['response'] == 'no')]['percentage']

        stat, p = mannwhitneyu(yes_vals, no_vals, alternative='two-sided')

        results.append({
            'population': population,
            'responder_median': yes_vals.median(),
            'non_responder_median': no_vals.median(),
            'p_value': p,
            'significance': p < 0.05
        })
    
    return pd.DataFrame(results)

# PART 4
def data_subset_analysis(path: str='cell-count.db'):
    query_1 = """
    SELECT sub.project, COUNT(*) AS sample_count
    FROM subjects sub
    JOIN samples s ON sub.subject_id = s.subject_id
    WHERE sub.condition = 'melanoma'
        AND s.sample_type = 'PBMC'
        AND s.time_from_treatment_start = 0
        AND sub.treatment = 'miraclib'
    GROUP BY sub.project
    """

    query_2 = """
    SELECT sub.response, COUNT(DISTINCT sub.subject_id) AS response_count
    FROM subjects sub
    JOIN samples s ON sub.subject_id = s.subject_id
    WHERE sub.condition = 'melanoma'
        AND s.sample_type = 'PBMC'
        AND s.time_from_treatment_start = 0
        AND sub.treatment = 'miraclib'
        AND sub.response IN ('yes', 'no')
    GROUP BY sub.response
    """

    query_3 = """
    SELECT sub.sex, COUNT(DISTINCT sub.subject_id) AS sex_count
    FROM subjects sub
    JOIN samples s ON sub.subject_id = s.subject_id
    WHERE sub.condition = 'melanoma'
        AND s.sample_type = 'PBMC'
        AND s.time_from_treatment_start = 0
        AND sub.treatment = 'miraclib'
    GROUP BY sub.sex
    """

    conn = sqlite3.connect(path)
    df_1 = pd.read_sql_query(query_1, conn)
    df_2 = pd.read_sql_query(query_2, conn)
    df_3 = pd.read_sql_query(query_3, conn)

    conn.close()

    return df_1, df_2, df_3

# PART 5 in GOOGLE FORM
def male_melanoma_responder_average_b_cell_count_at_time_0(path: str='cell-count.db'):
    query = """
    SELECT ROUND(AVG(cc.count), 2) AS average_B_cell_count
    FROM cell_counts cc
    JOIN samples s ON s.sample_id = cc.sample_id
    JOIN subjects sub ON sub.subject_id = s.subject_id
    WHERE sub.condition = 'melanoma'
        AND sub.sex = 'M'
        AND cc.population = 'b_cell'
        AND sub.response = 'yes'
        AND s.time_from_treatment_start = 0
    """

    conn = sqlite3.connect(path)
    df = pd.read_sql_query(query, conn)
    conn.close()

    return df

if __name__ == '__main__':
    # df = get_miraclib_melanoma_pbmc()
    # print(df.head())

    # plot_response_boxplots(df)
    # response_comparison_df = compare_response_groups(df)

    # part4
    # df_1, df_2, df_3 = data_subset_analysis()
    df = male_melanoma_responder_average_b_cell_count_at_time_0()
    print(df.head())