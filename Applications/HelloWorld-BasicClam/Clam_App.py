# -*- coding: utf-8 -*-
"""
Main Page - Basic Clam Test Bed

@author: aolabs.ai
"""

# 3rd Party Modules
import numpy as np
import streamlit as st
import requests


# Returns json, result stored in json as Agent's 'story'
def agent_api_call(agent_id, input_data, label=None, deployment="Local"):

    if deployment == "API":
        url = "https://7svo9dnzu4.execute-api.us-east-2.amazonaws.com/v0dev/kennel/agent"
    
        payload = {
            "kennel_id": "v0dev/TEST-BedOfClams",
            "agent_id": agent_id,
            "INPUT": input_dat,
            "control": {
                "US": True
            }
        }
        if label != None:
            payload["LABEL"] = label
    
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-API-KEY": "buildBottomUpRealAGI" # st.secrets["aolabs_api_key"]
        }
    
        response = requests.post(url, json=payload, headers=headers)
        print(response)    
        response = response.json()['story']  # we can print the HTTP response here, too
        return response

    if deployment == "Local":
        if label == None:
            label = []
        if agent_id not in st.session_state['Local_Agents']:
            agent = st.session_state.Local_Core( st.session_state.Local_Arch )
            st.session_state["Local_Agents"][agent_id] = agent
        else:
            agent = st.session_state['Local_Agents'][agent_id]
        agent.reset_state()
        agent.next_state( list(input_data), [label], unsequenced=True)
        response = agent.story[ agent.state-1, agent.arch.Z__flat ]
        response = "".join(list(response.astype(str)))
        print("from api call func" + response)
        return response

if "Local_Agents" not in st.session_state:
    # to construct and store Local Agents as needed
    st.session_state.Local_Agents = {}

    # preparing Arch Netbox Device Discovery locally 
    from Arch import Arch
    arch = Arch([1, 1, 1], [1], [], "full_conn", "Clam Agent created locally!")
    st.session_state.Local_Arch = arch
    
    # retrieving Agent class locally from Core
    # from github import Github, Auth    
    # github_auth = Auth.Token(st.secrets["aolabs_github_auth"])
    # github_client = Github(auth=github_auth)
    # ao_core = github_client.get_repo("aolabsai/ao_core")
    # content = ao_core.get_contents("ao_core/ao_core.py")
    # exec(content.decoded_content, globals())
    # st.session_state.Local_Core = Agent
    import ao_core as ao
    st.session_state.Local_Core = ao.Agent

st.set_page_config(
    page_title="AO Labs Demo App",
    page_icon="https://i.imgur.com/j3jalQE.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': "mailto:ali@aolabs.ai",
        'Report a bug': "mailto:ali@aolabs.ai",
        'About': "This is a demo of our AI features. Check out www.aolabs.ai and www.docs.aolabs.ai for more. Thank you!"
    }
)

# App Front End
st.title('AO Labs v0.1.0 Clam Demo')
st.image("https://i.imgur.com/cTHLQYL.png")
st.markdown("*Note: This app is not yet a standalone experience; please visit [this guide for more context](https://docs.google.com/document/d/1cUmTXsf7bCIMGKm3RHn001Qya-tZcFTvgCPj4Ynu2_M/edit).*")

# side bar content
st.session_state.side_bar_content = """
if "Agents" not in st.session_state:
    st.session_state["Agents"] = {}
if 'agent_id' not in st.session_state:
    active_agent = "**Current Agent:** :red[*No Agent(s) Yet*]"
    agent_deployment = ""
else:
    active_agent = "**Current Agent:** :violet["+st.session_state.agent_id+"]"
    agent_deployment = "Agent deployed :blue["+st.session_state.Agents[st.session_state.agent_id]['deployment']+"]"
with st.sidebar:    
    st.write(active_agent)
    st.write(agent_deployment)
st.sidebar.image("https://raw.githubusercontent.com/netbox-community/netbox/develop/docs/netbox_logo.svg", use_column_width=True)"""
exec(st.session_state.side_bar_content)

st.write("")
st.write("")
st.write("")
st.write("First, name your Clam Agent.")
st.write(" Agents maintain persistant state and are auto-provisioned through our API (or you can also try a version of this demo with the Agent loaded in the browser session.")
def New_Agent(deployment):
    st.session_state.agent_trials = 0
    st.session_state.agent_id = st.session_state.agent_id_field
    st.session_state.agent_results = np.zeros( (100,  5), dtype='O')

    Agent = {
        'deployment': deployment,
        'trials': str(0),
        'last_trial': "",
        'state' : str(0),
        '%_closed' : str(0),
        # 'tested (bulk)': str(st.session_state.tested)+" - "+str(test_size),
        # 'accuracy (bulk)': "",
        # 'no guesses (bulk)': "",
        # 'recs (autocomplete)': str(0),
        # 'mistakes (autocomplete)': str(0),
        }
    st.session_state.Agents[ st.session_state.agent_id ] = Agent       

st.session_state.agent_id_field = st.text_input("First, name your Clam Agent.", value="1st of Clams")
st.button("Create Agent Locally", on_click=New_Agent, args=("Local",))
st.button("Create Agent via API", on_click=New_Agent, args=("API",))
if "agent_id" not in st.session_state: st.write("Load up an Agent!")
else: st.write("Current Agent:  " + st.session_state.agent_id)
st.write("")
st.markdown('#')
st.markdown('##')
st.write("STEP 0) Activate learning:")
instincts_ONOFF = st.checkbox('Instincts On')
labels_ONOFF = st.checkbox('Labels On')
if labels_ONOFF & instincts_ONOFF is True: st.write('Note: the presence of labels overrides any instinctual learning.')
LABEL = None
if labels_ONOFF is True:
    labels_CHOICE = st.radio('Pick one', ['OPEN the Clam', 'CLOSE the Clam'])
    if labels_CHOICE == 'OPEN the Clam': LABEL = 1
    if labels_CHOICE == 'CLOSE the Clam': LABEL = 0
st.write("")

user_INPUT = st.multiselect("STEP 1) Show the Clam this input pattern:", ['FOOD', 'A-CHEMICAL', 'C-CHEMICAL'])
user_STATES = st.slider('This many times:', 1, 10)
st.write("")
st.write("")

if "agent_id" not in st.session_state: st.write("Connect an Agent to start")
else: st.write("STEP 2) Run Trial: "+str(st.session_state.agent_trials))
if user_STATES == 1:button_text= 'Expose Clam ONCE'
if user_STATES > 1: button_text= 'Expose Clam '+str(user_STATES)+' times'

# Run the Agent Trial
def run_agent():
    Agent = st.session_state.Agents[ st.session_state.agent_id ]
    
    # INPUTS
    INPUT = [0, 0, 0]
    if 'FOOD'       in user_INPUT: INPUT[0] = 1
    if 'A-CHEMICAL' in user_INPUT: INPUT[1] = 1
    if 'C-CHEMICAL' in user_INPUT: INPUT[2] = 1
    
    responses = []
    for x in np.arange(user_STATES):
        response= agent_api_call(st.session_state.agent_id, INPUT, label=LABEL)        
        print(response)
        responses += [int(response)]

    # save trial results for dispplaying to enduser    
    final_totals = sum(responses) / user_STATES * 100
    if labels_ONOFF == True: Label_Insti = "LABEL"
    elif instincts_ONOFF == True: Label_Insti = "INSTI"
    else: Label_Insti ="NONE"
    
    st.session_state.agent_results[st.session_state.agent_trials, :] = ["Trial #"+str(st.session_state.agent_trials), INPUT, user_STATES, Label_Insti, str(final_totals)+"%"]
    st.session_state.agent_trials += 1
    Agent['trials'] = str(st.session_state.agent_trials)
    Agent['last_trial'] = "Trial #"+str(st.session_state.agent_trials)+"with input"+str(INPUT)+" repeated "+str(user_STATES)+" with learning:"+Label_Insti+" for "+ str(final_totals)+"% opening"

    
if user_STATES == 1: button_text= 'Expose Clam ONCE'
if user_STATES > 1: button_text= 'Expose Clam '+str(user_STATES)+' times'
st.button(button_text, on_click=run_agent)

# Display Trial Log Results
if "agent_id" not in st.session_state: st.write("Load up an Agent!")
else:
    display_trial = st.session_state.agent_trials-1
    print(display_trial)
    if display_trial == -1: pass
    else:
        st.write("**Trial #"+str(display_trial)+" Results Summary**: You exposed the Clam Agent to "+str(st.session_state.agent_results[display_trial, 1])+' as input for '+str(st.session_state.agent_results[display_trial, 2])+'   times with learning mode '+str(st.session_state.agent_results[display_trial, 3])+'.')
        if (st.session_state.agent_results[display_trial, -1]) == "0%":
            if LABEL == 0: st.write("As you commanded, the Clam remained CLOSED, and learned to do so for the input you set.")
            else: st.write("The Clam didn't open at all. :(  Give it some food with this chemical and see how its behavior changes.")
        else:
            if LABEL == 1: st.write("As you ordered, the Clam was OPEN, and learned to do so for the input you set.")
            else: st.write('The Clam OPENED  '+st.session_state.agent_results[display_trial, -1]+' of the time.')
    st.write("")
    st.write('## Trial Results')
    st.text(str(st.session_state.agent_results[0:st.session_state.agent_trials, :]))  