import os
from pathlib import Path
import shutil


def create_folders_and_copy_files(base_dir, new_base_dir, paper_name):
    # List all the paper folders (depots, jobshop, etc.)
    folders = [
        f
        for f in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, f)) and f.startswith(paper_name)
    ]

    for folder in folders:
        # Get the category name (e.g., depots, jobshop, etc.)
        category_name = "-".join(folder.split("-")[1:])

        # Create a new category folder under the new base directory
        category_dir = os.path.join(new_base_dir, category_name)
        os.makedirs(category_dir, exist_ok=True)

        # Walk through the oneshot subfolders (1-oneshot, 2-oneshot, etc.)
        oneshot_folders = [
            f
            for f in os.listdir(os.path.join(base_dir, folder))
            if f.endswith("-oneshot")
        ]

        for i, oneshot_folder in enumerate(oneshot_folders, start=1):
            # Define the new instance folder (instance-1, instance-2, etc.)
            instance_folder = os.path.join(category_dir, f"instance-{i}")
            os.makedirs(instance_folder, exist_ok=True)

            # Define the source path for domain.pddl and problem.pddl
            oneshot_path = os.path.join(base_dir, folder, oneshot_folder)
            domain_file = os.path.join(oneshot_path, "domain.pddl")
            problem_file = os.path.join(oneshot_path, "problem.pddl")

            # Copy the files to the new instance folder
            if os.path.exists(domain_file):
                shutil.copy(domain_file, os.path.join(instance_folder, "domain.pddl"))
            if os.path.exists(problem_file):
                shutil.copy(problem_file, os.path.join(instance_folder, "problem.pddl"))

        print(f"Processed {category_name} with {len(oneshot_folders)} instances.")


# Specify the base directory containing your logs and the directory where the new structure should be created
base_dir = Path(__file__).parent.parent / "logs/aries-simple"
new_base_dir = Path(__file__).parent.parent / "logs/pddl"
paper_name = "ecai2025"

# Call the function to create the new structure and copy files
create_folders_and_copy_files(base_dir, new_base_dir, paper_name)
