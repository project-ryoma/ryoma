import ast
import sys
import json
import os


def type_annotation_to_json_schema(annotation):
    # check if annotation.__class__ is str
    if annotation.__class__ == str:
        return "string" 
    elif annotation.__class__ == int:
        return "integer"
    elif annotation.__class__ == float:
        return "number"
    elif annotation.__class__ == bool:
        return "boolean"
    else:
        return "object"


def extract_function_metadata(function_node, module_name=None):
    function_metadata = {
        'name': function_node.name,
        'module': module_name,
        'description': ast.get_docstring(function_node),
        'parameters': {
            'type': 'object',
            'properties': {},
            'required': []
        }
    }

    for arg in function_node.args.args:
        param_info = {
            'type': type_annotation_to_json_schema(ast.dump(arg.annotation)) if arg.annotation else None
        }
        function_metadata['parameters']['properties'][arg.arg] = param_info
        function_metadata['parameters']['required'].append(arg.arg)

    return function_metadata


def extract_all_function_metadata(file_name):
    with open(file_name, 'r') as file:
        node = ast.parse(file.read())

    module_name = os.path.splitext(os.path.basename(file_name))[0]  # Extract module name from file name
    # Prepend "dataplatform." to the module name
    module_name = f"dataplatform.{module_name}"
    functions_metadata = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            function_metadata = extract_function_metadata(item, module_name)
            functions_metadata.append(function_metadata)

    return functions_metadata


def write_metadata_to_file(file_path, function_metadata):
    with open(file_path, 'w') as f:
        json.dump(function_metadata, f, indent=4)
  

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python function_extractor.py <file_name>")
        sys.exit(1)

    file_name = sys.argv[1]
    functions_metadata = extract_all_function_metadata(file_name)
    write_metadata_to_file('dataplatform/function_metadata.json', functions_metadata)
