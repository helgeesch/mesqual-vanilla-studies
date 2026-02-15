# study_database.py

[:octicons-mark-github-16: View on GitHub](https://github.com/helgeesch/mesqual-vanilla-studies/blob/main/studies/study_02_pypsa_eur_example/src/study_database.py){ .md-button }

Study-specific caching strategy built on `PickleDatabase`. Only caches custom (computed) flags — raw PyPSA data is read directly from the network files each time, avoiding stale cache issues when networks are updated.

```python
--8<-- "studies/study_02_pypsa_eur_example/src/study_database.py"
```
