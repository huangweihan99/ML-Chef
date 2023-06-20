import streamlit as st
import torch
import transformers
from transformers import AutoTokenizer, GPT2LMHeadModel
from utils import format_input_ingredients, postprocess_ingredients, postprocess_recipe, get_title, recipe_to_txt

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
def load_recipe_tokenizer():
    recipe_tokenizer = AutoTokenizer.from_pretrained("gpt2")
    recipe_tokenizer.add_special_tokens({"pad_token": "<PAD>", "bos_token": "<RECIPE_START>", "eos_token": "<RECIPE_END>"})
    recipe_tokenizer.add_tokens(["<NER_START>", "<NEXT_NER>", "<NER_END>", "<INGR_START>", "<NEXT_INGR>", "<INGR_END>", "<DIR_START>", "<NEXT_DIR>", "<DIR_END>", "<TITLE_START>", "<TITLE_END>"])
    
    return recipe_tokenizer

@st.cache_resource
def load_ingredient_model():
    ingredient_model = GPT2LMHeadModel.from_pretrained(r"C:\Users\Weihan\OneDrive - Imperial College London\Desktop\School Work\Imperial College London\EIE\FYP\ML-Chef\ingredient_model")
    ingredient_model = ingredient_model.to(device)
    
    return ingredient_model

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

def test(hehe):
    if hehe == 'Temperature':
        st.write('hi')

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
                
        if 'ingredient_count' not in st.session_state:
            st.session_state['ingredient_count'] = 0
            
        ingredient_input = ingredient_input.split(', ')
        
        st.session_state['ingredient_count'] = len(ingredient_input)
        
        new_tokens = 0
        
        if st.session_state['ingredient_count'] <= 4:
            new_tokens = 40
        elif st.session_state['ingredient_count'] <= 8:
            new_tokens = 20
        elif st.session_state['ingredient_count'] > 8:
            new_tokens = 10
        
        ingdt_generation_kwargs = {
            "max_new_tokens": new_tokens,
            "min_length": 9,
            "top_k":  5,
            "temperature": 1,
            "pad_token_id": 50257,
            "do_sample": True, #for top k sampling
        }
            
        ingredient_input = '<NER_START> ' + str.join(' <NEXT_NER> ', ingredient_input)
        
        augment = st.checkbox('**Augment Ingredient List**')
        
        if 'final_ingredient_input' not in st.session_state:
            st.session_state['final_ingredient_input'] = ''
            
        
        submit_ingredients = st.form_submit_button('Compile Ingredient List', use_container_width=True)
        
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
        if submit_ingredients and st.session_state['final_ingredient_input'] != '':
            st.write('The final ingredient list is: ', postprocess_ingredients(st.session_state['final_ingredient_input']))
            
        k = st.slider(
            label='**Select a value for the k**',
            min_value=1,
            max_value=20,
            value=5,
            step=1
        )
        
        temp = st.slider(
            label='**Select a value for the temperature**',
            min_value=0.00,
            max_value=1.00,
            value=0.90,
            step=0.05
        )
        
        generate_recipe = st.form_submit_button('Generate Recipe', use_container_width=True)
        
        if 'recipe' not in st.session_state:
            st.session_state['recipe'] = ''
            
        recipe_generation_kwargs = {
            "max_length": 512,
            "min_length": 64,
            "top_k":  k,
            "temperature": temp,
            "pad_token_id": 50257,
            "do_sample": True, #for top k sampling
        }
        
        if generate_recipe:
            if st.session_state['final_ingredient_input'] == '':
                st.error('Input ingredients and compile an ingredient list before generating a recipe', icon="🚨")
            else:
                st.session_state['recipe'] = infer_recipe('<RECIPE_START> ' + st.session_state['final_ingredient_input'])
                postprocess_recipe(st.session_state['recipe'])
    
    if st.session_state['recipe'] != '':
        st.download_button(
            label="Download Recipe",
            data=recipe_to_txt(st.session_state['recipe']),
            file_name=f"{get_title(st.session_state['recipe'])}.txt",
            use_container_width=True
        )
        
with st.sidebar:
    st.subheader('Temperature Conversion')
    col3, col4 = st.columns(2)
    
    with col3:
        temp_unit1 = st.selectbox(
            '**Select input unit**',
            ('', 'Fahrenheit', 'Degree Celsius')
        )
        
    with col4:
        temp_unit2 = st.selectbox(
            '**Select output unit**',
            ('', 'Fahrenheit', 'Degree Celsius')
        )
        
    temp_input = st.number_input('**Enter input temperature value**')
    
    if temp_unit1 == 'Fahrenheit' and temp_unit2 == 'Degree Celsius':
        temp_output = round(temp_input - 32 * (5/9), 2)
        st.write(f"{round(temp_input, 2)}F = {temp_output}" + u"\u2103")
        
    if temp_unit2 == 'Fahrenheit' and temp_unit1 == 'Degree Celsius':
        temp_output = round(temp_input / (5/9) + 32, 2)
        st.write(f"{round(temp_input, 2)}" + u"\u2103"  + f"= {temp_output}F")
    
    st.markdown('___')
    
    st.subheader('Mass Conversion')
    col5, col6 = st.columns(2)
    
    with col5:
        mass_unit1 = st.selectbox(
            '**Select input unit**',
            ('', 'Pound', 'Ounce', 'Kilogram', 'Gram')
        )
        
    with col6:
        mass_unit2 = st.selectbox(
            '**Select output unit**',
            ('', 'Pound', 'Ounce', 'Kilogram', 'Gram')
        )
        
    mass_input = st.number_input('**Enter input mass value**')
    
    st.markdown('___')
    
    st.subheader('Volume Conversion')
    col7, col8 = st.columns(2)
    
    with col7:
        vol_unit1 = st.selectbox(
            '**Select input unit**',
            ('', 'Cup', 'Tablespoon', 'Teaspoon', 'Liter', 'Milliliter')
        )
        
    with col8:
        vol_unit2 = st.selectbox(
            '**Select output unit**',
            ('', 'Cup', 'Tablespoon', 'Teaspoon', 'Liter', 'Milliliter')
        )
        
    vol_input = st.number_input('**Enter input volume value**')
    
    st.markdown('___')
    
    st.subheader('Length Conversion')
    col9, col10 = st.columns(2)
    
    with col9:
        len_unit1 = st.selectbox(
            '**Select input unit**',
            ('', 'Foot', 'Inch', 'Meter', 'Centimeter')
        )
        
    with col10:
        len_unit2 = st.selectbox(
            '**Select output unit**',
            ('', 'Foot', 'Inch', 'Meter', 'Centimeter')
        )
        
    len_input = st.number_input('**Enter input length value**')
    
    st.markdown('___')
    
    