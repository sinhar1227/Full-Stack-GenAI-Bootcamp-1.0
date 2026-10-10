"""Run with: streamlit run app.py"""
import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from langgraph.types import Command
from deep_agent import build_agent, UserContext
from setup_data import DOCS, initialize

load_dotenv()
initialize()
st.set_page_config(page_title='Deep Agents Research Lab', page_icon='🧠', layout='wide')
st.title('Deep Agents — Research Lab')
st.caption('Real OpenAI model • Researcher + Analyst • Local docs + SQLite • Skills • Memory • Human approvals')

DEFAULT_QUESTION = ('Research LangChain, LangGraph and Deep Agents using local documents and '
                    'the database. Give a short summary, key findings, actual sources and confidence.')

if 'thread' not in st.session_state:
    st.session_state.thread = uuid.uuid4().hex
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'pending' not in st.session_state:
    st.session_state.pending = None
if 'report' not in st.session_state:
    st.session_state.report = None

with st.sidebar:
    st.header('Settings')
    model = st.text_input('OpenAI model', value=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'))
    st.caption('API key is read from .env. Model changes apply after New conversation.')
    if st.button('New conversation', use_container_width=True):
        st.session_state.thread = uuid.uuid4().hex
        st.session_state.messages = []
        st.session_state.pending = None
        st.session_state.report = None
        st.session_state.agent = None
        st.rerun()
    st.divider()
    st.subheader('Local source files')
    for file in sorted(DOCS.glob('*')):
        if file.suffix.lower() in {'.txt', '.md'}:
            st.code(file.name, language=None)
    upload = st.file_uploader('Add .txt / .md evidence', type=['txt', 'md'])
    if upload and st.button('Save document'):
        target = DOCS / upload.name
        target.write_bytes(upload.getvalue())
        st.success(f'Saved {target.name}')
        st.rerun()
    st.info('Email is a local outbox demo. Deletes require explicit approval and are confined to docs.')


def active_agent():
    if st.session_state.agent is None:
        st.session_state.agent = build_agent(model)
    return st.session_state.agent


def render_response(result):
    st.session_state.pending = None
    interrupts = result.get('__interrupt__', [])
    if interrupts:
        actions = []
        for intr in interrupts:
            payload = intr.value
            if not isinstance(payload, dict):
                raise RuntimeError(f'Unsupported interrupt payload: {payload!r}')
            actions.extend(payload.get('action_requests', []))
        if not actions:
            raise RuntimeError('An interruption occurred without recognized action_requests; no action performed.')
        st.session_state.pending = actions
        st.warning('Action requires your approval below.')
        return
    report = result.get('structured_response')
    if report is not None:
        data = report.model_dump() if hasattr(report, 'model_dump') else dict(report)
        st.session_state.report = data
        output = '### Summary\n' + str(data.get('summary', ''))
        output += '\n\n### Key findings\n' + '\n'.join('- ' + str(x) for x in data.get('key_findings', []))
        output += '\n\n**Sources:** ' + ', '.join(map(str, data.get('sources', [])))
        output += '\n\n**Confidence:** ' + str(data.get('confidence', ''))
    else:
        msgs = result.get('messages', [])
        output = str(msgs[-1].content) if msgs else 'No response returned.'
    st.session_state.messages.append({'role': 'assistant', 'content': output})
    st.rerun()


for entry in st.session_state.messages:
    with st.chat_message(entry['role']):
        st.markdown(entry['content'])

if st.session_state.pending:
    st.subheader('Human approval required')
    for i, action in enumerate(st.session_state.pending):
        with st.expander(f"Action {i+1}: {action.get('name', 'unknown')}", expanded=True):
            st.json(action.get('args', {}))
    col1, col2 = st.columns(2)
    decision = None
    if col1.button('✅ Approve all', use_container_width=True):
        decision = 'approve'
    if col2.button('❌ Reject all', use_container_width=True):
        decision = 'reject'
    if decision:
        decisions = [{'type': decision} for _ in st.session_state.pending]
        config = {'configurable': {'thread_id': st.session_state.thread}}
        with st.spinner('Resuming agent...'):
            try:
                result = active_agent().invoke(
                    Command(resume={'decisions': decisions}), config=config,
                    context=UserContext(user_id='demo-user', role='admin'))
                render_response(result)
            except Exception as exc:
                st.error(f'Unable to resume: {exc}')

prompt = st.chat_input('Ask a research question...', disabled=bool(st.session_state.pending))
if prompt:
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    config = {'configurable': {'thread_id': st.session_state.thread}}
    with st.chat_message('user'):
        st.markdown(prompt)
    with st.spinner('Researching with the real OpenAI model...'):
        try:
            result = active_agent().invoke(
                {'messages': [{'role': 'user', 'content': prompt}]}, config=config,
                context=UserContext(user_id='demo-user', role='admin'))
            render_response(result)
        except Exception as exc:
            st.error(f'Request failed: {exc}')
            st.caption('Check .env, model access, network connectivity, and installed package versions.')

if not st.session_state.messages:
    if st.button('▶ Run sample research'):
        st.session_state.messages.append({'role': 'user', 'content': DEFAULT_QUESTION})
        config = {'configurable': {'thread_id': st.session_state.thread}}
        with st.spinner('Running sample research...'):
            try:
                result = active_agent().invoke(
                    {'messages': [{'role': 'user', 'content': DEFAULT_QUESTION}]}, config=config,
                    context=UserContext(user_id='demo-user', role='admin'))
                render_response(result)
            except Exception as exc:
                st.error(f'Request failed: {exc}')
