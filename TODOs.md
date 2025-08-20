
# TODOs

1. use the multi agent router in cli.
2. try to make system able to add multiple data sources. the data sources are added to the store.
3. the impl should be able to index and search the data sources / catalog in the store, so that the agent won't need to load all the datasources / catalog every time.
4. update and add relevant tests. reorganize the test structure if needed.
move root tests to each package tests folder.
5. Add exception and error raise specifically when issue happens. Don't do fallback silently.
6. update the documentation to reflect the changes made in the system.

### For any tasks, make sure:
1. no fallback silently. If any exception happens, raise it specifically.
2. try to implement in OOP way, so that future extension is easier.
3. try to model data and logic in classes. Try to avoid directly using dict or list to hold important data.
4. add type hints for functions and methods.
5. add docstrings for all classes, functions and methods.
6. add relevant tests for new features and logic.