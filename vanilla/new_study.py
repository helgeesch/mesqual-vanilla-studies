import pathlib
import sys

from vanilla.study_structure import StudyFolder


class StudyTemplateGenerator:
    """
    Creates a standardized folder structure for a new study project.

    The generator creates the following structure:
        study_name/
        ├── README.md
        ├── data/
        ├── dvc/
        │   ├── _tmp/
        │   ├── docs/
        │   ├── input/
        │   ├── output/
        │   ├── presentations/
        │   ├── resources/
        │   └── sim_runs/
        ├── notebooks/
        ├── scripts/
        └── src/

    The structure includes a README.md file explaining the purpose of each directory.

    Args:
        study_path: Path where the study should be created. Can be relative or absolute.

    Examples:
        >>> generator = StudyTemplateGenerator("./my_new_study")
        >>> generator.generate()
    """

    def __init__(self, study_path: str) -> None:
        self._study_path = pathlib.Path(study_path).resolve()

    def _create_directory(self, path: pathlib.Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def _create_readme(self) -> None:
        readme_content = f"# {self._study_path.name}"""
        readme_path = self._study_path / "README.md"
        with open(readme_path, "w") as f:
            f.write(readme_content)

    def generate(self) -> None:
        for folder in StudyFolder:
            self._create_directory(self._study_path / folder.get_path())
        self._create_readme()


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m vanilla.new_study studies/study_123_your_name")
        sys.exit(1)

    study_path = sys.argv[1]
    generator = StudyTemplateGenerator(study_path)
    generator.generate()


if __name__ == "__main__":
    main()
