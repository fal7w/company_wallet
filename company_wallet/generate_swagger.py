import json
import os
import ast
import frappe
import docstring_parser


def get_docstring_and_args(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        docstring_and_args = {}
        for function in functions:
            docstring = ast.get_docstring(function)
            parsed_docstring = docstring_parser.parse(docstring) if docstring else None
            args = [
                {
                    "name": param.arg,
                    "type": param.annotation.id if param.annotation else "string",
                    "optional": any(p.arg_name == param.arg and p.is_optional for p in parsed_docstring.params) if parsed_docstring else True
                }
                for param in function.args.args
            ]
            return_type = parsed_docstring.returns.type_name if parsed_docstring and parsed_docstring.returns else "object"
            return_description = parsed_docstring.returns.description if parsed_docstring and parsed_docstring.returns else "No return description available"
            raises = [
                {"exception": exc.type_name, "description": exc.description}
                for exc in parsed_docstring.raises
            ] if parsed_docstring and parsed_docstring.raises else []

            docstring_and_args[function.name] = {
                "docstring": parsed_docstring,
                "args": args,
                "return_type": return_type,
                "return_description": return_description,
                "raises": raises,
            }

        return docstring_and_args


def map_type_to_openapi(type_name):
    # this is to meet openapi spec
    type_mapping = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "list": "array",
        "Optional[str]": "string",
        "Optional[int]": "integer",
        "Optional[float]": "number",
        "Optional[bool]": "boolean",
        "List[str]": "array",
        "List[int]": "array",
        "List[float]": "array",
        "List[dict]": "array",
        "List[Dict[str, Any]]": "array",
        "dict": "object"
    }
    return type_mapping.get(type_name, "string")


def generate_openapi_spec(api_dir):
    openapi_spec = {
        "openapi": "3.0.1",
        "info": {
            "title": "Frappe API Documentation",
            "description": "Documentation for Frappe APIs",
            "version": "1.0.0"
        },
        "paths": {}
    }
    app_path = frappe.get_app_path("company_wallet")

    for root, _, files in os.walk(api_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                docstring_and_args = get_docstring_and_args(file_path)
                method_path = file_path.replace(app_path, "").replace("/", ".")
                method_path = method_path[0:-3]  # remove ".py"
                for func_name, details in docstring_and_args.items():
                    if details["docstring"]:
                        openapi_spec["paths"][f"/api/method/company_wallet{method_path}.{func_name}"] = {
                            "post": {
                                "summary": details["docstring"].short_description if details["docstring"] else "",
                                "description": details["docstring"].long_description if details["docstring"] else "",
                                "tags": [file[0:-3]],
                                "parameters": [
                                    {
                                        "name": "X-Frappe-CSRF-Token",
                                        "in": "header",
                                        "required": True,
                                        "schema": {
                                            "type": "string",
                                            "default": "{{ csrf_token }}",
                                        },
                                        "description": "CSRF Token"
                                    },
                                    *[
                                        {
                                            "name": arg['name'],
                                            "in": "query",
                                            "required": not arg['optional'],
                                            "schema": {"type": map_type_to_openapi(arg['type'])},
                                            "description": arg['name']
                                        } for arg in details["args"]
                                    ]
                                ],
                                "requestBody": {
                                    "required": any(not arg['optional'] for arg in details["args"]),
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "object",
                                                "properties": {arg['name']: {"type": map_type_to_openapi(arg['type'])} for arg in details["args"]}
                                            }
                                        }
                                    }
                                },
                                "responses": {
                                    "200": {
                                        "description": details["return_description"],
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                    "type": details["return_type"],
                                                    "properties": {
                                                        "result":
                                                        {
                                                            "type": details["return_type"],
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    **{
                                        exc['exception']: {
                                            "description": exc['description'],
                                            "content": {
                                                "application/json": {
                                                    "schema": {
                                                        "type": "object",
                                                        "properties": {
                                                            "error": {"type": "string", "example": exc['exception']}
                                                        }
                                                    }
                                                }
                                            }
                                        } for exc in details["raises"]
                                    }
                                }
                            }
                        }

    return openapi_spec


def write_openapi_spec(api_dir, output_file_path):
    openapi_spec = generate_openapi_spec(api_dir)
    with open(output_file_path, "w") as output_file:
        json.dump(openapi_spec, output_file)


# Example usage:
# write_openapi_spec("path/to/api_dir", "output/file/path.json")
