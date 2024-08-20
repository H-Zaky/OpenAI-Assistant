# Azure Function for Conversational AI with Azure OpenAI

## This ReadMe File is for Documentation Purposes only, using the exact code will not work as you need to identify some variables from your end

This repository contains an Azure Function designed to interact with Azure OpenAI's beta features for managing conversation threads, handling user prompts, and making decisions based on those prompts. The function processes HTTP requests, leverages the Azure OpenAI API to handle conversations, and formats responses for client consumption.

## Features

- **Conversation Thread Management**: Automatically handles creation and continuation of conversation threads using Azure OpenAI's beta API.
- **Prompt Handling**: Processes user prompts, adding contextual information like the current date and time.
- **Real-time Status Monitoring**: Monitors the status of the AI's decision-making process and provides logs of elapsed time.
- **Response Formatting**: Replaces placeholder text in filenames within the AI response with the actual names.

## Prerequisites

Before running this function, ensure you have the following set up:

1. **Azure Account**: You must have an active Azure account with access to Azure OpenAI.
2. **Azure OpenAI Service**: An OpenAI resource with beta API access.
3. **Python 3.9+**: The function is developed using Python 3.9. Ensure you have the correct version installed.

## Environment Variables

The following environment variables need to be set in the `.env` file for the function to work correctly:

- `AzureOpenAIEndpoint`: The endpoint for your Azure OpenAI service.
- `AzureOpenAIKey`: The API key for your Azure OpenAI service.
- `ChatCompletionsDeploymentName`: The name of the deployment for chat completions.
- `AssistantID`: The ID of the assistant used for generating responses.

## Installation

1. Clone this repository to your local machine.

2. Install the required Python packages.

    ```sh
    pip install -r requirements.txt
    ```

3. Set up your environment variables by creating a `.env` file in the root directory of the project:

    ```plaintext
    AzureOpenAIEndpoint=<Your Azure OpenAI Endpoint>
    AzureOpenAIKey=<Your Azure OpenAI API Key>
    ChatCompletionsDeploymentName=<Your Deployment Name>
    AssistantID=<Your Assistant ID>
    ```

4. Deploy the function to Azure using the Azure Functions Core Tools or via the Azure portal.

## Usage

- **Endpoint**: The function is exposed via an HTTP trigger at the route `/test`.
- **Request**: Send a GET or POST request with `prompt` and `conversation_id` parameters.
  
    Example GET Request:

    ```sh
    curl "https://your-function-app.azurewebsites.net/api/test?prompt=Your+Question&conversation_id=12345"
    ```

    Example POST Request:

    ```sh
    curl -X POST "https://your-function-app.azurewebsites.net/api/test" \
        -H "Content-Type: application/json" \
        -d '{"prompt": "Your Question", "conversation_id": "12345"}'
    ```

- **Response**: The function returns a JSON object containing the assistant's formatted response and the conversation's thread ID.

    Example Response:

    ```json
    {
        "Assistant's Response": "This is the formatted response from the AI.",
        "Thread ID": "your-thread-id"
    }
    ```

## Logging

The function logs important steps and errors, which can be viewed in the Azure portal or locally via the terminal when running the function.
