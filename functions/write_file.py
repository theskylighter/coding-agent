import os
from google.genai import types

def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        working_directory = os.path.abspath(working_directory)
        converted_file_path = os.path.normpath(os.path.join(working_directory, file_path))

        valid_file_path = os.path.commonpath([working_directory, converted_file_path]) == working_directory

        if not valid_file_path:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        elif os.path.isdir(converted_file_path):
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        else:
            try: 
                os.makedirs(os.path.dirname(converted_file_path), exist_ok=True)
                with open(converted_file_path, "w") as f:
                    f.write(content)
                return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
            except Exception as e:
                return f'Error: "{e}" when trying to overwrite file content'
    except Exception as e:
        return f'Error: {e}'

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Overwrites the contents of a pointed file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties = {
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path that the function will overwrite the contents of.",
                ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content with which the file should be overwritten.",
                ),
        },
        required=["file_path", "content"],
    ),
)
