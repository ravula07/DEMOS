import numpy as np
from PIL import Image
import streamlit as st
import tensorflow as tf
from langchain.memory import ConversationBufferWindowMemory
from langchain import Cohere, ConversationChain, LLMChain, PromptTemplate
from keras.applications.vgg16 import preprocess_input, decode_predictions, VGG16

st.set_page_config(page_title="CHIRP CHAT",
                  page_icon="🐥",
                  layout="wide",
                  initial_sidebar_state="expanded")

#st.title(':orange[CHIRP CHAT]')
#st.markdown("<h1 style='text-align: center;'>:orange[CHIRP CHAT]</h1>", unsafe_allow_html=True,)
st.markdown("<h1 style='text-align: center; color: orange;'>CHIRP CHAT 🐥 </h1> ", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["CHAT HERE 💬", " Uploaded Documents 📄"])

# Creating Sidebar for Utilites
with st.sidebar:
    st.title("Upload Your Birdie")
    uploaded_file = st.file_uploader("Choose a file", type=["png", "jpg"])
    clear_button = st.button("Clear Conversation", key="clear") 
    
#with tab1:
    #user_input = st.text_area(label=":green[Welcome to CHIRP CHAT! Type in your bird-brained questions]")
     
with tab2:
   if uploaded_file is not None:
    uploaded_image = Image.open(uploaded_file)
    x = preprocess_input(np.array(uploaded_image))
    model = VGG16(weights='imagenet')
    #img = uploaded_file
    #x = np.array(img)
    x = np.expand_dims(x, axis=0)
    preds = model.predict(x)
    
    decoded_preds = decode_predictions(preds, top=1)[0]
    for pred in decoded_preds:
      result = pred[1]
    st.image(uploaded_file, caption=result)

with tab1:
    if uploaded_file is not None:
        tab1.markdown("<h3 style='text-align: center;'>Now you're chirping about the bird "
        + result
        + "</h3>",
        unsafe_allow_html=True,)

def Img_DataGen(Input):
  cohere_api_key= st.secrets["cohere_apikey"]
  LLM = Cohere(cohere_api_key=cohere_api_key , model="command-xlarge-nightly")
  
  prompt1 = PromptTemplate(
  input_variables=["product"],
  template="Generate a paragraph about {product} as if an Ornithologist is saying it.")
  chain = LLMChain(llm=LLM, prompt=prompt1)
  var = chain.run(result)
  
  prompt = PromptTemplate(
  input_variables=["result","var"], 
  template=template)
  var = prompt.format(result=result, var = var)
  
  var = var + """{history}
  Human: {human_input}
  Assistant:"""
  
  prompt = PromptTemplate(
  input_variables=["history", "human_input"], 
  template=var)

  chat_chain = LLMChain(
  llm = Cohere(cohere_api_key= COHERE_API_KEY, model="command-xlarge-nightly"), 
  prompt=prompt, 
  verbose=True, 
  memory=ConversationBufferWindowMemory(k=8)
  )
  return "Ready"

# Session State
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
   
def generate_response(query):
    result = chat_chain({"query": query})

# Creating Containers
response_container = tab1.container()
container = tab1.container()

with container:
    with st.form(key="my_form", clear_on_submit=True):
        user_input = st.text_input("You:", key="input")
        submit_button = st.form_submit_button(label="Send")

    if user_input and submit_button:
        if uploaded_file is not None:
            output = generate_response(user_input)
            print(output)
            st.session_state["past"].append(user_input)
            st.session_state["generated"].append(output)
            st.session_state["chat_history"] = [(user_input, output)]
        else:
            st.session_state["past"].append(user_input)
            st.session_state["generated"].append(
                "Hey, you there! Don't be a bird-brain and upload a picture of a birdie in the sidebar."
            )

if st.session_state["generated"]:
    with response_container:
        for i in range(len(st.session_state["generated"])):
            message(
                st.session_state["past"][i],
                is_user=True,
                key=str(i) + "_user",
                avatar_style="adventurer",
                seed=123,
            )
            message(st.session_state["generated"][i], key=str(i))

# Enabling Clear button

if clear_button:
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["chat_history"] = []
