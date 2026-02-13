from mesqual.typevars import DatasetType, FlagType, DatasetConfigType
from mesqual.databases import PickleDatabase
from mesqual_pypsa import PyPSADataset


class StudyDatabase(PickleDatabase):

    def _is_custom_flag(self, dataset: PyPSADataset, flag: str) -> bool:
        first_component = flag.split('.')[0]
        try:
            _ = getattr(dataset.n, first_component)
            return False
        except:
            return True

    def set(
            self,
            dataset: DatasetType,
            flag: FlagType,
            config: DatasetConfigType,
            value,
            **kwargs
    ):
        """Store data as pickle file.

        Args:
            dataset: Dataset type identifier
            flag: Processing flag or stage identifier
            config: Configuration object containing processing parameters
            value: Data to store (pandas Series or DataFrame)
            **kwargs: Additional keyword arguments for cache key generation
        """
        if not self._is_custom_flag(dataset, flag):
            return None
        return super().set(dataset, flag, config, value, **kwargs)

    def key_is_up_to_date(
            self,
            dataset: DatasetType,
            flag: FlagType,
            config: DatasetConfigType,
            **kwargs
    ):
        if not self._is_custom_flag(dataset, flag):
            return False
        return super().key_is_up_to_date(dataset, flag, config, **kwargs)
