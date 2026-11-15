import os
from config import MAX_CHARS
from google.genai import types

def get_file_content(working_directory: str, file_path: str) -> str:
     try:
        working_directory = os.path.abspath(working_directory)
        converted_file_path = os.path.normpath(os.path.join(working_directory, file_path))

        valid_file_path = os.path.commonpath([working_directory, converted_file_path]) == working_directory

        if not valid_file_path:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        elif not os.path.isfile(converted_file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        else:
            with open(converted_file_path, "r") as f:
                content = f.read(MAX_CHARS)
                if f.read(1):
                    content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            return content
     except Exception as e:
        return f'Error: "{e}" when trying to get file content'

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Returns the first 1000 characters of the contents of a file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties = {
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path that the function will read the contents of.",
            ),
        },
        required=["file_path"],
    ),
)

