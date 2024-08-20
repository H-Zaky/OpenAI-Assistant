import os
import time
import logging
import azure.functions as func
from openai import AzureOpenAI
from dotenv import load_dotenv
import re
from datetime import datetime
import json

load_dotenv()
deployment = "ChatCompletionsDeploymentName"
api_key = "AzureOpenAIKey"
api_version = "2024-05-01-preview"
azure_endpoint = "AzureOpenAIEndpoint"
assistant_id = "AssistantID"

client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint
)

conversation_threads = {}

def reformat_filenames_in_response(response):
    response = re.sub(r"【\d+:\d+†(.+?)】", r" (\1) ", response)
    return response

def handle_vote_and_decision(prompt, conversation_id):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt_with_datetime = f"Current date and time: {current_datetime}\n\n{prompt}"

    try:
        if conversation_id in conversation_threads:
            thread_id = conversation_threads[conversation_id]
            logging.info("Using existing Thread ID: %s for Conversation ID: %s", thread_id, conversation_id)
        else:
            thread = client.beta.threads.create()
            thread_id = thread.id
            conversation_threads[conversation_id] = thread_id
            logging.info("New Thread Created: %s for Conversation ID: %s", thread_id, conversation_id)

        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt_with_datetime,
        )
        logging.info("User Message Added: %s", message)

        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )

        start_time = time.time()
        status = run.status

        while status not in ["completed", "cancelled", "expired", "failed"]:
            time.sleep(5)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            elapsed_time = time.time() - start_time
            logging.info("Elapsed time: %d minutes %d seconds", int(elapsed_time // 60), int(elapsed_time % 60))
            status = run.status
            logging.info('Run Status: %s', status)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        logging.info("Thread Messages after run completion: %s", messages.model_dump_json(indent=2))

        data = json.loads(messages.model_dump_json(indent=2))
        response = data['data'][0]['content'][0]['text']['value']

        # Reformat filenames within the response
        formatted_response = reformat_filenames_in_response(response)
        logging.info("Formatted Response: %s", formatted_response)

        return formatted_response, thread_id
    except Exception as e:
        logging.error(f"Error in handle_vote_and_decision: {e}")
        raise

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="test")
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    user_prompt = req.params.get('prompt')
    conversation_id = req.params.get('conversation_id')
    if not user_prompt:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = None

        if req_body:
            user_prompt = req_body.get('prompt')
            conversation_id = req_body.get('conversation_id')

    if user_prompt and conversation_id:
        try:
            decision_response, thread_id = handle_vote_and_decision(user_prompt, conversation_id)
            response_data = {
                "Assistant's Response": decision_response,
                "Thread ID": thread_id
            }
            return func.HttpResponse(json.dumps(response_data), status_code=200, mimetype="application/json")
        except Exception as e:
            logging.error(f"Error in main function: {e}")
            return func.HttpResponse("Internal Server Error", status_code=500)
    else:
        return func.HttpResponse(
            "Please pass a prompt and conversation_id on the query string or in the request body",
            status_code=400
        )
