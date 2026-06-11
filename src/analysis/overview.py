import sqlite3
import pandas as pd

def get_population_frequency(db_path='cell-count.db') -> pd.DataFrame:
    query = """
    SELECT
        sample_id AS sample,
        SUM(count) OVER (PARTITION BY sample_id) AS total_count,
        population,
        count,
        ROUND(100.0 * count / SUM(count) OVER (PARTITION BY sample_id), 2) AS percentage
    FROM cell_counts
    ORDER BY sample_id, population
    """

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    df = df.rename(columns={'sample': 'sample_id'})
    conn.close()

    return df

if __name__ == '__main__':
    
    # path = '../../cell-count.db'
    df = get_population_frequency()
    print(df.head())