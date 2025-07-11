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

from mistralai import Mistral
from Gemini.GeminiAPI import get_bondol_prompt
import streamlit as st


client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])  # Make sure that is your valid API key!!!
def mistral_answer(question, model, historial):
    complete_answer = ''
    # This is the final prompt for the ai, it contains the bondol prompt, the historial and the user question
    final_question = [{"role": "information", "content": get_bondol_prompt()},
                      {"role": "system", "content": "context: " + str(historial)},
                      {"role": "user", "content": question},
                      {"role": "assistant", "content": "(respond in utf-8)"}]

    stream_response = client.chat.stream(
        model = model,
        messages = [
            {
                "role": "user",
                "content": str(final_question),
            },
        ]
    )

    for chunk in stream_response:
        complete_answer += chunk.data.choices[0].delta.content
        yield chunk.data.choices[0].delta.content
    return complete_answer