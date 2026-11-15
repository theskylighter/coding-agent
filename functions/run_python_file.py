import os
import subprocess
from google.genai import types

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        working_directory = os.path.abspath(working_directory)
        converted_file_path = os.path.normpath(os.path.join(working_directory, file_path))

        valid_file_path = os.path.commonpath([working_directory, converted_file_path]) == working_directory

        if not valid_file_path:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        elif not os.path.isfile(converted_file_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        elif not converted_file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'
        else:
            command = ["python", converted_file_path]
            if args != None and len(args) > 0:
                command.extend(args)
            process = subprocess.run(
                    command,
                    cwd = working_directory,
                    capture_output = True,
                    text = True,
                    timeout = 30
                    )
            output = []
            if process.returncode != 0:
                output.append(f"Process exited with code {process.returncode}") 
            if not process.stdout and not process.stderr:
                output.append("No output produced")
            else:
                if process.stdout:
                    output.append(f'STDOUT:\n{process.stdout}')
                if process.stderr:
                    output.append(f'STDERR:\n{process.stderr}')
            return '\n'.join(output)
            
    except Exception as e:
        return f'Error: executing Python file: {e}'

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a specified Python file and returns its stdout and stderr outputs.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties = {
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path that the function will execute and return the ouput of.",
                ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                    ),
                description="The list of commands the function will take on and execute.",
                ),
        },
        required=["file_path"]
    ),
)
