import os
from google.genai import types

def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        working_directory = os.path.abspath(working_directory) 
        target_directory = os.path.normpath(os.path.join(working_directory, directory))

        valid_target_dir = os.path.commonpath([working_directory, target_directory]) == working_directory
        
        if not valid_target_dir: 
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        elif not os.path.isdir(target_directory):
            return f'Error: "{directory}" is not a directory'
        else:
            try:
                contents = os.listdir(target_directory)
                lines = []
                for i in contents:
                    path = os.path.normpath(os.path.join(target_directory, i))
                    name = i
                    file_size = os.path.getsize(path)
                    is_dir = os.path.isdir(path)
                    lines.append(f'- {name}: file_size={file_size} bytes, is_dir={is_dir}')
                return "\n".join(lines)
            except Exception as e:
                return f'Error: "{e}" raised when trying to parse through the contents of the folder'

    except Exception as e:
        return f'Error: "{e}"'

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)
