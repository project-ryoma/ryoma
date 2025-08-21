
# TODOs

## Tasks



## backlogs
1. the impl should be able to index and search the data sources / catalog in the store, so that the agent won't need to load all the datasources / catalog every time.
2. update the documentation to reflect the changes made in the system.
3. optimize and add more tests.
4. fix the mypy for the entire project ryoma_ai
5. fix the mypy for the entire project ryoma_lab

## Important
1. For any code, no fallback silently.
2. If any exception happens, raise it specific Exception. if Exception doesn't exsits, create one.
2. Always try to implement in OOP way, which means more module, and more class so that future extension is easier.
3. try to model data and logic separately. Try to avoid directly using dict or list to hold data.
4. Always add type hints for functions and methods.
5. Always add docstrings for all classes, functions and methods.
6. Always add relevant tests for new features and logic.