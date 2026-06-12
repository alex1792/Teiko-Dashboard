import sys
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.overview import get_population_frequency
from src.analysis.stats_analysis import (
    compare_response_groups,
    get_miraclib_melanoma_pbmc,
    plot_response_boxplots,
    data_subset_analysis,
)

DB_PATH = ROOT / "cell-count.db"

st.set_page_config(
    page_title="Teiko Immune Cell Analysis",
    page_icon="🧬",
    layout="wide",
)

st.title("Immune Cell Population Analysis")
st.caption("Clinical trial dashboard for Bob Loblaw — Loblaw Bio")

if not DB_PATH.exists():
    st.error("Database not found. Run `make pipeline` first.")
    st.stop()


@st.cache_data
def load_overview(db_path: str):
    return get_population_frequency(db_path)


@st.cache_data
def load_response_analysis(db_path: str):
    return get_miraclib_melanoma_pbmc(db_path)


@st.cache_data
def load_subset_analysis(db_path: str):
    return data_subset_analysis(db_path)

# @st.cache_data
# def load_male_melanoma_responder_average_b_cell_count_at_time_0(db_path: str):
#     return male_melanoma_responder_average_b_cell_count_at_time_0(db_path)


tab_overview, tab_response, tab_subset = st.tabs(
    ["Part 2: Population Frequencies", "Part 3: Response Analysis", "Part 4: Data Subset Analysis"]
)

with tab_overview:
    st.header("Population Relative Frequencies")
    st.write(
        "Relative frequency of each immune cell population per sample, "
        "expressed as a percentage of total cell count."
    )

    overview_df = load_overview(str(DB_PATH))

    col1, col2, col3 = st.columns(3)
    col1.metric("Samples", overview_df["sample_id"].nunique())
    col2.metric("Populations", overview_df["population"].nunique())
    col3.metric("Rows", len(overview_df))

    populations = sorted(overview_df["population"].unique())
    selected_populations = st.multiselect(
        "Filter by population",
        populations,
        default=populations,
    )
    sample_search = st.text_input("Search by sample ID", placeholder="e.g. sample00000")

    filtered = overview_df[overview_df["population"].isin(selected_populations)]
    if sample_search:
        filtered = filtered[filtered["sample_id"].str.contains(sample_search, case=False)]

    st.dataframe(filtered, width='stretch', hide_index=True)

with tab_response:
    st.header("Miraclib Melanoma PBMC — Response Comparison")
    st.write(
        "Compare relative frequencies between responders (`yes`) and non-responders (`no`) "
        "for melanoma patients treated with miraclib (PBMC samples only)."
    )

    analysis_df = load_response_analysis(str(DB_PATH))
    results_df = compare_response_groups(analysis_df)

    responders = analysis_df[analysis_df["response"] == "yes"]["sample_id"].nunique()
    non_responders = analysis_df[analysis_df["response"] == "no"]["sample_id"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Responder Samples", responders)
    col2.metric("Non-responder Samples", non_responders)
    col3.metric(
        "Significant Populations",
        results_df["significance"].sum(),
    )

    fig = plot_response_boxplots(analysis_df)
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Statistical Results")
    st.write(
        "Mann-Whitney U test comparing relative frequencies between responders and "
        "non-responders. Significance threshold: p < 0.05."
    )

    display_results = results_df.copy()
    display_results["p_value"] = display_results["p_value"].map(lambda p: f"{p:.4f}")
    display_results["responder_median"] = display_results["responder_median"].map(
        lambda v: f"{v:.2f}%"
    )
    display_results["non_responder_median"] = display_results["non_responder_median"].map(
        lambda v: f"{v:.2f}%"
    )
    display_results = display_results.rename(
        columns={
            "population": "Population",
            "responder_median": "Responder Median",
            "non_responder_median": "Non-responder Median",
            "p_value": "p-value",
            "significance": "Significant",
        }
    )
    st.dataframe(display_results, width='stretch', hide_index=True)

    significant = results_df[results_df["significance"]]["population"].tolist()
    if significant:
        st.success(
            "Populations with significant differences in relative frequency: "
            + ", ".join(f"**{pop}**" for pop in significant)
        )
    else:
        st.info("No populations showed a significant difference at p < 0.05.")

    with st.expander("View filtered analysis data"):
        st.dataframe(analysis_df, width='stretch', hide_index=True)

with tab_subset:
    st.header("Baseline Miraclib Melanoma PBMC Subset")
    st.write(
        "Melanoma patients treated with miraclib, PBMC samples only, "
        "at baseline (`time_from_treatment_start = 0`)."
    )

    samples_by_project, subjects_by_response, subjects_by_sex = load_subset_analysis(
        str(DB_PATH)
    )

    total_samples = samples_by_project["sample_count"].sum()
    total_subjects = subjects_by_response["response_count"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Samples", int(total_samples))
    col2.metric("Total Subjects", int(total_subjects))
    col3.metric("Projects", len(samples_by_project))

    col_left, col_mid, col_right = st.columns(3)

    with col_left:
        st.subheader("Samples by Project")
        st.write(
            "Total number of samples from each project"
        )
        st.dataframe(
            samples_by_project.rename(
                columns={"project": "Project", "sample_count": "Sample Count"}
            ),
            width='stretch',
            hide_index=True,
        )

    with col_mid:
        st.subheader("Subjects by Response")
        st.write(
            "Total number of subjects were responders/non-responders"
        )
        st.dataframe(
            subjects_by_response.rename(
                columns={"response": "Response", "response_count": "Subject Count"}
            ),
            width='stretch',
            hide_index=True,
        )

    with col_right:
        st.subheader("Subjects by Sex")
        st.write(
            "Total number of subjects were males/females"
        )
        st.dataframe(
            subjects_by_sex.rename(
                columns={"sex": "Sex", "sex_count": "Subject Count"}
            ),
            width='stretch',
            hide_index=True,
        )
