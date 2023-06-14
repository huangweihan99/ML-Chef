import streamlit as st
import evaluate 
import pandas as pd
import tqdm
import torch
import math
import transformers
from transformers import AutoTokenizer, GPT2LMHeadModel, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import Dataset, load_metric
from ast import literal_eval
from statistics import mean
from utils import format_input_ingredients, postprocess_ingredients

st.set_page_config(layout="wide")

st.title("ML-Chef Data Application :cook:")

device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

@st.cache_resource
def load_ingredient_tokenizer():
    ingredient_tokenizer = AutoTokenizer.from_pretrained("gpt2")
    ingredient_tokenizer.add_special_tokens({"pad_token": "<PAD>"})
    ingredient_tokenizer.add_tokens(["<NER_START>", "<NEXT_NER>", "<NER_END>"])
    
    return ingredient_tokenizer

@st.cache_resource
def load_ingredient_model():
    ingredient_model = GPT2LMHeadModel.from_pretrained(r"C:\Users\Weihan\OneDrive - Imperial College London\Desktop\School Work\Imperial College London\EIE\FYP\ML-Chef\ingredient_model")
    ingredient_model = ingredient_model.to(device)
    
    return ingredient_model

@st.cache_resource
def load_recipe_tokenizer():
    recipe_tokenizer = AutoTokenizer.from_pretrained("gpt2")
    recipe_tokenizer.add_special_tokens({"pad_token": "<PAD>", "bos_token": "<RECIPE_START>", "eos_token": "<RECIPE_END>"})
    recipe_tokenizer.add_tokens(["<NER_START>", "<NEXT_NER>", "<NER_END>", "<INGR_START>", "<NEXT_INGR>", "<INGR_END>", "<DIR_START>", "<NEXT_DIR>", "<DIR_END>", "<TITLE_START>", "<TITLE_END>"])
    
    return recipe_tokenizer

@st.cache_resource
def load_recipe_model():
    recipe_model = GPT2LMHeadModel.from_pretrained(r"C:\Users\Weihan\OneDrive - Imperial College London\Desktop\School Work\Imperial College London\EIE\FYP\ML-Chef\recipe_model")
    recipe_model = recipe_model.to(device)
    
    return recipe_model

    
ingredient_model = load_ingredient_model()
ingredient_tokenizer = load_ingredient_tokenizer()
ingredient_model.resize_token_embeddings(len(ingredient_tokenizer))

recipe_model = load_recipe_model()
recipe_tokenizer = load_recipe_tokenizer()
recipe_model.resize_token_embeddings(len(recipe_tokenizer))

ingdt_generation_kwargs = {
    "max_length": 48,
    "min_length": 9,
    "top_k":  5,
    "temperature": 1,
    "pad_token_id": 50257,
    "do_sample": True, #for top k sampling
}

recipe_generation_kwargs = {
    "max_length": 512,
    "min_length": 64,
    "top_k":  5,
    "temperature": 0.9,
    "pad_token_id": 50257,
    "do_sample": True, #for top k sampling
}

def infer_ingredients(inp):
    inp = ingredient_tokenizer(inp, return_tensors="pt")
    X = inp["input_ids"].to(device)
    a = inp["attention_mask"].to(device)
    output = ingredient_model.generate(X, attention_mask=a, **ingdt_generation_kwargs )
    output = ingredient_tokenizer.decode(output[0])
    return output

def infer_recipe(inp):
    inp = recipe_tokenizer(inp, return_tensors="pt")
    X = inp["input_ids"].to(device)
    a = inp["attention_mask"].to(device)
    output = recipe_model.generate(X, attention_mask=a, **recipe_generation_kwargs)
    output = recipe_tokenizer.decode(output[0])
    return output

col1, col2 = st.columns(2)

with col1:
    with st.form("ingredient_input"):
        st.header("Ingredient Input")
        pantry_ingredient_input = st.multiselect('**Select common pantry ingredients to use**', ['salt', 'pepper', 'sugar', 'olive oil', 'vegetable oil', 'garlic', 'onion', 'eggs', 'flour', 'milk', 'butter'])

        ingredient_input = st.text_input('**Enter other ingredients in CSV format e.g. *chicken, pasta, tomatoes***')

        for ingredient in pantry_ingredient_input:
            if ingredient_input == '':
                ingredient_input += ingredient
            else:
                ingredient_input = ingredient_input + ', ' + ingredient
                
        ingredient_input = ingredient_input.split(', ')
            
        ingredient_input = '<NER_START> ' + str.join(' <NEXT_NER> ', ingredient_input)
        
        augment = st.checkbox('**Augment ingredient list**')
        
        if 'final_ingredient_input' not in st.session_state:
            st.session_state['final_ingredient_input'] = ''
        
        submit_ingredients = st.form_submit_button('Compile Ingredients')
        
        if submit_ingredients and augment == True:
            if ingredient_input == '<NER_START> ':
                st.session_state['final_ingredient_input'] = ''
                st.error('Input ingredients before compiling an ingredient list', icon="🚨")
            else:
                st.session_state['final_ingredient_input'] = format_input_ingredients(infer_ingredients(ingredient_input))
                end_token_index = st.session_state['final_ingredient_input'].find('<NER_END>')
                st.session_state['final_ingredient_input'] = st.session_state['final_ingredient_input'][:end_token_index+9]
                st.write('The final ingredient list is: ', postprocess_ingredients(st.session_state['final_ingredient_input']))
            
        if submit_ingredients and augment == False:
            if ingredient_input == '<NER_START> ':
                st.session_state['final_ingredient_input'] = ''
                st.error('Input ingredients before compiling an ingredient list', icon="🚨")
            else:
                st.session_state['final_ingredient_input'] = ingredient_input + ' <NER_END>'
                st.write('The final ingredient list is: ', postprocess_ingredients(st.session_state['final_ingredient_input']))
    
with col2:
    with st.form("recipe_generation"):
        st.header("Recipe Generation")
        if submit_ingredients:
            st.write('The final ingredient list is: ', postprocess_ingredients(st.session_state['final_ingredient_input']))
        
        generate_recipe = st.form_submit_button('Generate Recipe')
        
        if generate_recipe:
            if st.session_state['final_ingredient_input'] == '':
                st.error('Input ingredients and compile an ingredient list before generating a recipe', icon="🚨")
            else:
                recipe = infer_recipe('<RECIPE_START> ' + st.session_state['final_ingredient_input'])
                st.write("recipe: ", recipe)