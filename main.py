# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 10:36:22 2023

@author: 3b13j
"""
import streamlit as st
from langchain_tools import build_chat_components, n_rounds, correct, create_chat_icon, optimize_prompt


if "cost" not in st.session_state : st.session_state.cost = 0 

# some quick displaying tools 
def l(text, position = "justify") :
    return st.markdown(just(text, position), unsafe_allow_html=True)
def just(text, position = "justify") :     
    return f'<div style="text-align: {position};">'+text+'</div>'


st.image("chat_fighters.jpeg")

l(" ")
l("A fun app to imagine the virtual clash between several public figures.", position = "center")
"___"


with st.sidebar :
    st.subheader("Configurate the app")
    
    "___"
    OPENAI_API_KEY = st.text_input("OpenAI API Key", "Provide key", type="password")
    st.session_state.OPENAI_API_KEY = OPENAI_API_KEY
    c, v = st.columns(2)
    fc = c.text_input('First Contestant', 'Plato')
    fat = c.text_input("Describe attitude", 'neutral')
    sc = v.text_input('Second Contestant', 'Aristotle')
    sat = v.text_input("Describe attitude", 'stubborn')
    
    
    
    theme = st.text_input('Ontological question', 'What is the meaning of life ?')
    
    n_r = st.number_input("Number of rounds", min_value=1, max_value=10, value=3)
    
    image = st.toggle("Display chat icons (more expensive)")
    
    f"cost of this session : {st.session_state.cost}" 
    
    if st.button( "Launch the debate !") :
        
        fconv, sconv, history , cost= build_chat_components(fc, sc,  fat, sat, theme, st.session_state.OPENAI_API_KEY)
        st.session_state.cost += cost
        if n_r > 1 : 
            fconv, sconv, history  , cost = n_rounds(fconv,sconv,history,n_r)
            st.session_state.cost += cost
        st.session_state.history= history
        if image :
            try :
                ficon = create_chat_icon(fc, st.session_state.OPENAI_API_KEY)
            except :
                l(f"Sorry Dallee refused to create an image for {fc} ")
            try :
                sicon = create_chat_icon(sc,st.session_state.OPENAI_API_KEY)
            except :
                l(f"Sorry Dallee refused to create an image for {sc} ")
            st.session_state.ficon = ficon
            st.session_state.cost += 0.016
            st.session_state.sicon = sicon
            st.session_state.cost += 0.016
            st.session_state.sentence, cost = correct(f"They are gonna debate on {theme}",st.session_state.OPENAI_API_KEY )
            st.session_state.cost+= cost
      
    
    #on = st.toggle('Speak with the figures yourself')
    
    
if OPENAI_API_KEY != "Provide key"  and "history" in st.session_state : 
        
    c, v = st.columns(2)
    with c :
        st.subheader ("Contestant number one is ...")
        st.header(fc)
        if "ficon" in st.session_state : 
            fim = st.session_state.ficon
            st.image(st.session_state.ficon)
        else : fim = None
        
        
    with v :
        st.subheader ("Contestant number two is ...")
        st.header(sc)
        if "sicon" in st.session_state : 
            sim = st.session_state.sicon
            st.image(st.session_state.sicon)
        else : sim = None
            
    "___"
    if 'sentence' in st.session_state : st.subheader(st.session_state.sentence)

    "___"
    
    
    for message in st.session_state.history: 
        if message[0] == fc : im = fim 
        else: im = sim
        with st.chat_message(message[0], avatar = im) :
           st.write(message[1])
        
        
        
    prompt = st.chat_input("Dont be shy")



else :  
    st.header("You must provide a valid key and click on the button for the app to run")