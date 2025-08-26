
# TODOs

## Tasks
1. There are two places doing the indexing for datasource catalog and metadata. one is in catalog_manager that use catalog_store, and the other is in vector_store/base that has index_datasource. they do similar functionalities, how this should be refactored and optimized?
2. for the internal agent implementation, there are multiple llm calls, which use the prompt in the module, I think it would be better to move to the prompt/ folder, and make it more modular, so that we can easily add more prompts in the future.
3. 
4. Update and Optimize the docs, there are a lot of missing docs since last code change and version. we need to update the docs in details now. please check all pages, think about what are missing, especially on tutorial, how to use the agent, how to use the cli, how to set the configs etc.


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