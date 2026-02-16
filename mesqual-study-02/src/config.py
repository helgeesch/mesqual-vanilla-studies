from pathlib import Path
from studies.study_02_pypsa_eur_example.src.study_dataset import *
from studies.study_02_pypsa_eur_example.src.study_database import StudyDatabase
from mesqual.utils import theme

STUDY_FOLDER = Path('studies/study_02_pypsa_eur_example')
theme.plotly_theme_light.apply()
