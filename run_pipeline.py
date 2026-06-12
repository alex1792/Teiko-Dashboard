"""Run the full analysis pipeline (Parts 1-4) and write outputs to output/."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from load_data import build_database
from src.analysis.overview import get_population_frequency
from src.analysis.stats_analysis import (
    compare_response_groups,
    data_subset_analysis,
    get_miraclib_melanoma_pbmc,
    plot_response_boxplots,
)

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "cell-count.db"
OUTPUT_DIR = ROOT / "output"


def run_pipeline(
    db_path: Path = DB_PATH,
    output_dir: Path = OUTPUT_DIR,
    csv_path: Path = ROOT / "cell-count.csv",
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Part 1: Loading data into SQLite...")
    build_database(str(db_path), str(csv_path))

    print("Part 2: Computing population frequencies...")
    overview_df = get_population_frequency(str(db_path))
    part2_df = overview_df.rename(columns={"sample_id": "sample"})
    part2_df.to_csv(output_dir / "population_frequencies.csv", index=False)

    print("Part 3: Response analysis...")
    analysis_df = get_miraclib_melanoma_pbmc(str(db_path))
    analysis_df.to_csv(output_dir / "response_analysis_data.csv", index=False)

    results_df = compare_response_groups(analysis_df)
    results_df.to_csv(output_dir / "response_comparison.csv", index=False)

    fig = plot_response_boxplots(analysis_df)
    fig.savefig(output_dir / "response_boxplots.png", bbox_inches="tight", dpi=150)
    plt.close(fig)

    print("Part 4: Baseline subset analysis...")
    samples_by_project, subjects_by_response, subjects_by_sex = data_subset_analysis(
        str(db_path)
    )
    samples_by_project.to_csv(output_dir / "subset_samples_by_project.csv", index=False)
    subjects_by_response.to_csv(
        output_dir / "subset_subjects_by_response.csv", index=False
    )
    subjects_by_sex.to_csv(output_dir / "subset_subjects_by_sex.csv", index=False)

    print(f"Pipeline complete. Outputs written to {output_dir}/")


if __name__ == "__main__":
    run_pipeline()
