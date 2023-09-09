# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 10:54:29 2023

@author: 3b13j
"""
import os 

import openai

from diffusers import DiffusionPipeline 


from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from stqdm import stqdm 





llm_model = "gpt-3.5-turbo"




""" The goal of this program is to have a language model dialogue with itself.
Therefore the names "User" and "AI" do not really make sense and we would like to replace them with the names of 
our two contestants. 
To the best of my limited knowledge, langchain doesn't allow in the prebuilt components to change information about the speaker.
A first idea to implement the conversation will be to build two concurrent conversation chains feeding each other and a combined memory 
that will be the one displayed via the streamlit interface.


"""

def build_chat_components(fc, sc, fat, sat, theme, key) :
    
    llm = ChatOpenAI(temperature=0.5, model=llm_model, openai_api_key= key)
    """
    builds the 3 components we need, i.e. two conversationnal chains, one for each competitor, and a shared
    """
    
    fmemory = ConversationBufferMemory()
    smemory = ConversationBufferMemory()
    
    # fc is asked si he answers first
    init_prompt = f"Hello {sc}, What do you think about {theme}"
    smemory.save_context({"input": "Hi"}, 
                    {"output": init_prompt})
    
    # Instead of creating a first prompt and then injecting it in the PromptTemplate Constructor, we could have created a custom ConversationChain subclass that accepts a prompt with two more inputs, fc and sc, but this would have been more technical 
    fsent =  f'The following is a thorought conversation between {sc} and you. You are {fc}.You are {fat}. Do not start your answer with {fc} name. Your answer must move the conversation forward and you disagree with {sc} but stay coherent in your argumentation.'
    fprompt = PromptTemplate(
        input_variables=['history', 'input'],
        output_parser=None,
        partial_variables={},
        template=fsent+'\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:', 
        template_format='f-string',
        validate_template=True
        )
    
    ssent =  f'The following is a thorought conversation between {fc} and you. You are {sc}.You are {sat}.Do not provide paratext.Do not start your answer with {sc} name. Your answer must move the conversation forward.'
    sprompt = PromptTemplate(
        input_variables=['history', 'input'],
        output_parser=None,
        partial_variables={},
        template=ssent+'\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:', 
        template_format='f-string',
        validate_template=True
        )
    
    fconversation = ConversationChain(
        llm=llm, 
        memory = fmemory,
        prompt = fprompt,
        verbose=True
        )
    
    sconversation = ConversationChain(
        llm=llm, 
        memory = smemory,
        prompt = sprompt,
        verbose=True
        )
    
    
    
    common_memory = [[fc,init_prompt]] 
    sanswer = sconversation.predict(input =init_prompt)
    common_memory.append([sc, sanswer])
    fanswer = fconversation.predict(input = sanswer)
    common_memory.append([fc, fanswer])
    
    
    return fconversation, sconversation, common_memory
    
def one_round(fconversation, sconversation, common_memory) :
    
    sc = common_memory[-2][0]
    fc = common_memory[-1][0]
    finput = common_memory[-1][1]
    sanswer = sconversation.predict(input = finput)
    common_memory.append([sc, sanswer])
    fanswer = fconversation.predict(input = sanswer)
    common_memory.append([fc, fanswer])
    
    
    return fconversation, sconversation, common_memory
    
    
def n_rounds(fconversation, sconversation, common_memory, n) : 
    for i in range(int(n)) :
        fconversation, sconversation, common_memory = one_round(fconversation, sconversation, common_memory)
    return fconversation, sconversation, common_memory 
    


def create_chat_icon(name, key) :
    openai.api_key = key
    pr = f"A small portrait of {name}"
    response = openai.Image.create(
    prompt=pr,
    n=1,
    size="256x256",
    )

    return response["data"][0]["url"]
     