import json
from tempfile import _TemporaryFileWrapper

import requests
import streamlit as st

def ask_api(
    lcserve_host: str,
    url: str,
    file: _TemporaryFileWrapper,
    question: str,
    openAI_key: str,
) -> str:
    if not lcserve_host.startswith('http'):
        return '[ERROR]: Invalid API Host'

    if url.strip() == '' and file == None:
        return '[ERROR]: Both URL and PDF is empty. Provide atleast one.'

    if url.strip() != '' and file != None:
        return '[ERROR]: Both URL and PDF is provided. Please provide only one (eiter URL or PDF).'

    if question.strip() == '':
        return '[ERROR]: Question field is empty'

    _data = {
        'question': question,
        'envs': {
            'OPENAI_API_KEY': openAI_key,
        },
    }

    if url.strip() != '':
        r = requests.post(
            f'{lcserve_host}/ask_url',
            json={'url': url, **_data},
        )

    else:
        with open(file.name, 'rb') as f:
            r = requests.post(
                f'{lcserve_host}/ask_file',
                params={'input_data': json.dumps(_data)},
                files={'file': f},
            )

    if r.status_code != 200:
        raise ValueError(f'[ERROR]: {r.text}')

    return r.json()['result']

def main():
    st.set_page_config(page_title="PDF GPT", page_icon="📚")

    title = 'PDF GPT'
    description = """ PDF GPT allows you to chat with your PDF file using Universal Sentence Encoder and Open AI. It gives hallucination free response than other tools as the embeddings are better than OpenAI. The returned response can even cite the page number in square brackets([]) where the information is located, adding credibility to the responses and helping to locate pertinent information quickly."""

    st.markdown(f'<center><h1>{title}</h1></center>', unsafe_allow_html=True)
    st.markdown(description)

    lcserve_host = st.text_input(
        'Enter your API Host here',
        value='http://localhost:8080',
    )
    openAI_key = st.text_input(
        'Enter your OpenAI API key here',
        type='password',
        help='Get your Open AI API key here: https://platform.openai.com/account/api-keys',
    )
    pdf_url = st.text_input('Enter PDF URL here')
    file = st.file_uploader(
        'Upload your PDF/ Research Paper / Book here',
        type=['pdf'],
    )
    question = st.text_input('Enter your question here')
    submit = st.button('Submit')

    if submit:
        try:
            answer = ask_api(lcserve_host, pdf_url, file, question, openAI_key)
            st.success(f'The answer to your question is: {answer}')
        except ValueError as e:
            st.error(str(e))

if __name__ == '__main__':
    main()
