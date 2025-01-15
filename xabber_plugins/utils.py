from django.contrib import messages

import tarfile
import os


def get_error_messages(request):
    error_messages = []

    # Get all messages for the current request
    message_list = messages.get_messages(request)

    # Filter messages with the 'error' tag
    for message in message_list:
        if message.tags == 'error':
            error_messages.append(message.message)

    return error_messages


def get_success_messages(request):
    success_messages = []

    # Get all messages for the current request
    message_list = messages.get_messages(request)

    # Filter messages with the 'error' tag
    for message in message_list:
        if message.tags == 'success':
            success_messages.append(message.message)

    return success_messages


def validate_module(file, plugin_name):
    try:
        # Check file extension
        if not file.name.endswith('.tar.gz'):
            raise ValueError("The file is not a .tar.gz archive.")

        # Open the tar.gz file
        file.seek(0)
        with tarfile.open(file.temporary_file_path(), 'r:gz') as archive:
            # Get the list of all files in the archive
            archive_members = archive.getnames()
            # Check for the required structure
            panel_path = f"panel/{plugin_name}/"
            spec_file = "module.spec"

            if not any(name.startswith(panel_path) for name in archive_members):
                raise ValueError(f"Expected directory structure 'panel/{plugin_name}/' not found.")

            if spec_file not in archive_members:
                raise ValueError(f"Expected file '{spec_file}' not found.")

            # Extract and read the module.spec file
            spec_file_content = archive.extractfile(spec_file).read().decode('utf-8')

            # Validate the content of the module.spec file
            if f"NAME = {plugin_name}" not in spec_file_content:
                raise ValueError(f"The module.spec file does not contain 'NAME = {plugin_name}'.")

        # If all checks pass
        return True

    except (tarfile.TarError, ValueError) as e:
        # Handle errors specific to tar files or validation
        print(f"Error: {e}")
        return False

    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error: {e}")
        return False