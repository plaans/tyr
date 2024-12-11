from pathlib import Path


def filter_bins(in_folder: Path, out_folder: Path):
    """
    Filter the contents of a log folder to keep only the binary
    files (problem.binpb) and the PDDL files (domain.pddl, problem.pddl).

    Args:
        in_folder (Path): The folder containing the logs to filter.
        out_folder (Path): The folder to save the filtered logs.
    """

    for folder in in_folder.iterdir():
        if not folder.is_dir():
            continue
        for subfolder in folder.iterdir():
            if not subfolder.is_dir():
                continue
            if "oneshot" not in subfolder.stem:
                continue
            out = (
                out_folder
                / folder.stem
                / ("instance-" + subfolder.stem.replace("-oneshot", ""))
            )
            out.mkdir(parents=True, exist_ok=True)
            for file in subfolder.iterdir():
                if not file.is_file():
                    continue
                if file.name not in ["domain.pddl", "problem.pddl", "problem.binpb"]:
                    continue
                (out / file.name).write_bytes(file.read_bytes())


if __name__ == "__main__":
    import sys

    BASE = Path(__file__).parent
    in_folder = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "logs/aries"
    out_folder = Path(sys.argv[2]) if len(sys.argv) > 2 else BASE / "filtered_bins"
    filter_bins(in_folder, out_folder)
