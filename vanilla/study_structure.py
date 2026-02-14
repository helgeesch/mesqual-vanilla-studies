from enum import Enum, auto


class StudyFolder(Enum):
    DATA = auto()
    TMP = auto()
    DOCS = auto()
    INPUT = auto()
    OUTPUT = auto()
    PRESENTATIONS = auto()
    RESOURCES = auto()
    SIM_RUNS = auto()
    NOTEBOOKS = auto()
    SCRIPTS = auto()
    SRC = auto()

    def __str__(self) -> str:
        return self.get_path()

    def get_path(self) -> str:
        paths = {
            StudyFolder.DATA: "data",
            StudyFolder.TMP: "dvc/_tmp",
            StudyFolder.DOCS: "dvc/docs",
            StudyFolder.INPUT: "dvc/input",
            StudyFolder.OUTPUT: "dvc/output",
            StudyFolder.PRESENTATIONS: "dvc/presentations",
            StudyFolder.RESOURCES: "dvc/resources",
            StudyFolder.SIM_RUNS: "dvc/sim_runs",
            StudyFolder.NOTEBOOKS: "notebooks",
            StudyFolder.SCRIPTS: "scripts",
            StudyFolder.SRC: "src"
        }
        return paths[self]
