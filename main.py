import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.call_function import available_functions, call_function
from prompts import system_prompt

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if api_key == None:
    raise RuntimeError("api key was not found")

client = genai.Client(api_key=api_key)

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

messages: list[types.Content] = [
    types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
]

conversation_history = []

for _ in range(20):
    result = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )

    results_list = []

    if result.function_calls != None:
        for i in result.function_calls:
            function_call_result = call_function(i, args.verbose)
            if not function_call_result.parts:
                raise Exception
            if function_call_result.parts[0].function_response == None:
                raise Exception
            if function_call_result.parts[0].function_response.response == None:
                raise Exception
            if args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")
            results_list.append(function_call_result.parts[0])

    for candidate in result.candidates:
        conversation_history.append(candidate)
        messages.append(candidate.content)

    messages.append(
        types.Content(role="user", parts=results_list)
    ) if results_list else None

    # Get usage metadata
    if args.verbose == True:
        if result.usage_metadata != None:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {result.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {result.usage_metadata.candidates_token_count}")
            print(result.text)
        else:
            raise RuntimeError("no usage metadata returned")

    if result.function_calls == None:
        print("Final response:")
        print(result.text)
        break
else:
    print("The agent exhausted its limit")
    exit(1)
