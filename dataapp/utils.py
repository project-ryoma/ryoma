# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
from termcolor import colored
import json

class Utils:

    def check_config(app):
        '''Returns a message to user for missing configuration

        Args:
            app (Flask): Flask app object

        Returns:
            string: Error info
        '''

        if app.config['AUTHENTICATION_MODE'] == '':
            return 'Please specify one of the two authentication modes'
        if app.config['AUTHENTICATION_MODE'].lower() == 'serviceprincipal' and app.config['TENANT_ID'] == '':
            return 'Tenant ID is not provided in the config.py file'
        elif app.config['REPORT_ID'] == '':
            return 'Report ID is not provided in config.py file'
        elif app.config['WORKSPACE_ID'] == '':
            return 'Workspace ID is not provided in config.py file'
        elif app.config['CLIENT_ID'] == '':
            return 'Client ID is not provided in config.py file'
        elif app.config['AUTHENTICATION_MODE'].lower() == 'masteruser':
            if app.config['POWER_BI_USER'] == '':
                return 'Master account username is not provided in config.py file'
            elif app.config['POWER_BI_PASS'] == '':
                return 'Master account password is not provided in config.py file'
        elif app.config['AUTHENTICATION_MODE'].lower() == 'serviceprincipal':
            if app.config['CLIENT_SECRET'] == '':
                return 'Client secret is not provided in config.py file'
        elif app.config['SCOPE_BASE'] == '':
            return 'Scope base is not provided in the config.py file'
        elif app.config['AUTHORITY_URL'] == '':
            return 'Authority URL is not provided in the config.py file'
        
        return None


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "grey",
    }
    formatted_messages = []
    for message in messages:
        if message["role"] == "system":
            formatted_messages.append(f"system: {message['content']}\n")
        elif message["role"] == "user":
            formatted_messages.append(f"user: {message['content']}\n")
        elif message["role"] == "assistant" and message.get("function_call"):
            formatted_messages.append(f"\n   >>> function call ({message['function_call']['name']}): {json.dumps(message['function_call']['arguments'])}")
        elif message["role"] == "assistant" and not message.get("function_call"):
            formatted_messages.append(f"assistant: {message['content']}\n")
        elif message["role"] == "function":
            formatted_messages.append(f"   <<< function result ({message['name']}): {message['content']}\n")
    for formatted_message in formatted_messages:
        
        if (formatted_message.startswith("\n") or formatted_message.startswith(" ")):
            print(
                colored(
                    formatted_message,
                    role_to_color[messages[formatted_messages.index(formatted_message)]["role"]],
                )
            )
        else:
            print(
                colored(
                    formatted_message,
                    role_to_color[messages[formatted_messages.index(formatted_message)]["role"]],
                    attrs=["bold"],
                )
            )