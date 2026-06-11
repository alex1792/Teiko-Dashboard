import pandas as pd
from src.db.schema import POPULATIONS
import sqlite3
from src.db.schema import init_schema
import os

'''
project,subject,condition,age,sex,treatment,response,sample,sample_type,time_from_treatment_start,b_cell,cd8_t_cell,cd4_t_cell,nk_cell,monocyte

for each subject:
    subject_id,
    project,
    condition,
    age,
    sex,
    treatment,
    response

for each sample:
    sample_id,
    subject_id,
    sample_type,
    time_from_treatment_start

for each cell_count:
    id,
    sample_id,
    population,
    count
'''


def load_data(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)

def load_subjects(data: pd.DataFrame) -> pd.DataFrame:
    subjects = data[['subject','project', 'condition', 'age', 'sex', 'treatment', 'response']].drop_duplicates()
    return subjects

def load_samples(data: pd.DataFrame) -> pd.DataFrame:
    samples = data[['sample', 'subject', 'sample_type', 'time_from_treatment_start']]
    return samples

def load_cell_counts(data: pd.DataFrame) -> pd.DataFrame:
    cell_counts = data.melt(
        id_vars = ['sample'],
        value_vars = list(POPULATIONS),
        var_name = 'population',
        value_name = 'count',
    )

    cell_counts = cell_counts.rename(columns={'sample': 'sample_id'})
    return cell_counts



if __name__ == '__main__':
    # check if .db file exists
    if os.path.exists('cell-count.db'):
        os.remove('cell-count.db')
    
    # get data from csv file
    path = 'cell-count.csv'
    data = load_data(path)
    # print(data.head())

    # load data from csv file, table by table
    subjects = load_subjects(data)
    subjects = subjects.rename(columns={'subject': 'subject_id'})
    # print(subjects.head())

    samples = load_samples(data)
    samples = samples.rename(columns={'sample': 'sample_id', 'subject': 'subject_id'})
    # print(samples.head())

    cell_counts = load_cell_counts(data)
    # print(cell_counts['population'].unique())
    # print(cell_counts[cell_counts['population'] == 'cd8_t_cell'].head())

    # write data into database
    conn = sqlite3.connect('cell-count.db')
    init_schema(conn)

    # write subjects, samples into database
    subjects.to_sql('subjects', conn, if_exists='append', index=False, 
        dtype={'subject_id': 'TEXT', 'project': 'TEXT', 'condition': 'TEXT', 'age': 'INTEGER', 'sex': 'TEXT', 'treatment': 'TEXT', 'response': 'TEXT'}
    )

    samples.to_sql('samples', conn, if_exists='append', index=False,
        dtype={'sample_id': 'TEXT', 'subject_id': 'TEXT', 'sample_type': 'TEXT', 'time_from_treatment_start': 'INTEGER'}
    )

    # then write cell_counts into database
    cell_counts.to_sql('cell_counts', conn, if_exists='append', index=False,
        dtype={'sample_id': 'TEXT', 'population': 'TEXT', 'count': 'INTEGER'}
    )

    conn.commit()
    conn.close()

    
