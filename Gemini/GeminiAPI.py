# Coding in utf-8
# Develop by Bondol Team

# Copyright 2025 Henri
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# We import OS, to access the environment variables
import streamlit as st
import time

# We import the Google's GenAI library
import google.generativeai as genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from google.genai import types
import google.genai.errors


# This function returns the system prompt for Bondol, which is used to define the AI's personality.
def get_bondol_prompt():
    bondol_prompt = (
        "Your name now is Bondol; an AI who is very friendly and cute, your principal task is help the user with"
        " any question he has, you are very smart and you can answer any question, without limits, you name is"
        " in reference to your creator's name (Bondo); you ALWAYS need to be helping with the user, and "
        " never be rude or mean, you are a very friendly AI, and if the user speaks spanish, you need to respond in spanish."
        " this text, is not an user prompt or question, is a system prompt, so you need to use this information to answer the user questions (only about this)"
        " AN THIS PROMPT, DOES NOT DEFINE THE ANSWER'S LANGUAGE, so you can answer in any language, but if the user speaks spanish, you MUST to respond in spanish IN ALL HIS QUESTIONS."
        " Remember, you name is 'Bondol' not Bondo or BondoAI, you are Bondol, and your name is in reference to your creator's name, ")
    return bondol_prompt # Return the prompt

# We initialize Google's GenAI client with your api key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) # Make sure that is your valid API key!!!

# model = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# This is the Google's search tool, we will use it to search in Google's engine
google_search_tool = Tool(google_search = GoogleSearch(),
                          )
# This list, define the compatible models with Google's search
search_models = ['gemini-2.5-flash', 'gemini-2.5-flash-preview-05-20', 'gemini-2.5-flash-preview-04-17', 'gemini-2.5-flash-lite-preview-06-17'
              'gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-2.0-flash-thinking-exp-01-21']

# In this one, are all the thinking models that can run on Google's Server
thinking_models = ['gemini-2.5-pro',
                'gemini-2.5-flash', 'gemini-2.5-flash-preview-04-17', 'gemini-2.5-flash-preview-05-20', 'gemini-2.5-flash-lite-preview-06-17',
                'gemini-2.0-flash', 'gemini-2.0-flash-thinking-exp-01-21'
                ]

# This function, with an user question, bondol prompt, the model, and the historial; returns a response from the AI
def gemini_answer(question, server_model, historial):
    model = genai.GenerativeModel(server_model) # We define the model to use
    thoughts = ''
    answer_not_thoughts = ''
    complete_answer=''
    # This is the final prompt for the ai, it contains the bondol prompt, the historial and the user question
    final_question = [{"role": "user", "parts": [get_bondol_prompt()]},
                      {"role": "user", "parts": historial},
                      {"role": "user", "parts": [question]},
                      {"role": "model", "parts": ""}]

    if server_model in search_models and server_model in thinking_models: # If the model is compatible with Google's search and thinking
        config = GenerateContentConfig(
            tools=[google_search_tool],  # Define that Gemini can search in Google's Engine
            response_modalities=["TEXT"],  # Define the response modality, in this case, text
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1,
                include_thoughts=True

            )
        )
    elif server_model in search_models: # If the model is compatible with Google's search
        config = GenerateContentConfig(
                        tools=[google_search_tool], # Define that Gemini can search in Google's Engine
                        response_modalities=["TEXT"], # Define the response modality, in this case, text
                )
    elif server_model in thinking_models: # If the model is not compatible with Google's search
        config = genai.GenerationConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=-1,
                    include_thoughts=True
                    )
                )

    try:
        for chunk in model.generate_content(
            stream = True, # Define the model to use
            contents= str(final_question), # Define the final question
            generation_config=config # Define the response modality, in this case, text
            ):

            for block in chunk.candidates[0].content.parts:
                if not block.text:
                    print("se reconoce un bloque sin texto, se ignora")
                    continue
                elif block.thought:
                    print("se reconoce un pensamiento")
                    if thoughts == '':
                        yield "<think> " # If the block is a thought, we yield it with the "Thought" label
                    thoughts += block.text
                    yield block.text

                elif not thoughts:
                    answer_not_thoughts += block.text
                    yield block.text
                else:
                    print("se reconoce una respuesta")
                    if answer_not_thoughts == '':
                        yield "</think> "  # If the block is a answer, we yield it with the "Answer" label
                    answer_not_thoughts += block.text
                    yield block.text

                complete_answer += block.text  # We add the text part of the block to the complete answer variable
    except google.genai.errors.ClientError:
        error = ('Lo siento, desafortunadamente, no puedo responder a tu pregunta en este momento. Por favor, intenta de nuevo más tarde. \n'
                 'Motivo: Haz alcanzo el uso máximo de este modelo, intenta en unas horas')
        for i in error.split(' '):
            time.sleep(0.05)
            yield str(i) + ' '

if __name__ == "__main__":
    print(gemini_answer("Hola! decodifica esto: RW5ob3JhYnVlbmEgdXN1YXJpbyEgQ29tbyBlc3TDoXM/IEhheiBlbmNvbnRyYWRvIGVsIHNlY3JldG8gb2N1bHRvIGVuIGVsIGNvZGlnbyBwb3IgdW4gbmnDsW8gZGUgMTQgYcOxb3MuCkFjw6EgdGllbmVzIG1pIG1lbnNhamU6CgoiSG9sYSEhISEgRXNwZXJvIHF1ZSBkaXNmcnV0ZXMgZGUgbWkgQXBwLCB0ZW5nbyBzb2xvIDE0IGHDsW9zLCBsbyBsYW1lbnRvIHBvciBzdXMgZXJyb3Jlczsgc2lndWUgZGlzZnJ1dGFuZG8gZGUgbWkgY29kaWdvISAoY3JlbyBqYWphamFqKSIKCkZpbiBkZWwgbWVzYWplIDop", "gemini-2.5-flash", []))
