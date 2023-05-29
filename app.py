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

tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.add_special_tokens({"pad_token": "<PAD>", "bos_token": "<RECIPE_START>", "eos_token": "<RECIPE_END>"})
tokenizer.add_tokens(["<NER_START>", "<NEXT_NER>", "<NER_END>", "<INGR_START>", "<NEXT_INGR>", "<INGR_END>", "<DIR_START>", "<NEXT_DIR>", "<DIR_END>", "<TITLE_START>", "<TITLE_END>"])

generation_kwargs = {
    "max_length": 512,
    "min_length": 64,
    "top_k":  10,
    "pad_token_id": 50257,
    "do_sample": True, #for top k sampling
}

device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

def infer(inp, model):
    inp = tokenizer(inp, return_tensors="pt")
    X = inp["input_ids"].to(device)
    a = inp["attention_mask"].to(device)
    output = model.generate(X, attention_mask=a, **generation_kwargs )
    output = tokenizer.decode(output[0])
    return output

def postprocess_recipe(recipe):
    full_recipe = []
    recipe_words = recipe.split()

    for word in recipe_words:
        if word == "<RECIPE_END>":
            break
        else:
            full_recipe.append(word)

    title = full_recipe[full_recipe.index("<TITLE_START>")+1:full_recipe.index("<TITLE_END>")]
    ingredients = full_recipe[full_recipe.index("<INGR_START>")+1:full_recipe.index("<INGR_END>")]
    directions = full_recipe[full_recipe.index("<DIR_START>")+1:full_recipe.index("<DIR_END>")]

    full_title = ""
    ingredient = ""
    direction = ""

    for title_word in title:
        full_title = full_title + title_word + " "

    print(full_title)
    print("=" * 150)
    print("Ingredients:")

    for word in ingredients:
      if word == "<NEXT_INGR>":
          print(f"- {ingredient}")
          ingredient = ""
      else:
          ingredient = ingredient + word + " "

    print(f"- {ingredient}")
    print("-" * 150)
    print("Directions:")

    for word in directions:
      if word == "<NEXT_DIR>":
          print(f"- {direction}")
          direction = ""
      else:
          direction = direction + word + " "
    
    if direction != "":
      print(f"- {direction}")

training_model1 = GPT2LMHeadModel.from_pretrained(r"C:\Users\Weihan\OneDrive - Imperial College London\Desktop\School Work\Imperial College London\EIE\FYP\ML-Chef\recipe_model1")
training_model1 = training_model1.to(device)

input4 = "<RECIPE_START> <NER_START> flour <NEXT_NER> baking powder <NEXT_NER> bananas <NEXT_NER> eggs <NEXT_NER> vanilla extract <NEXT_NER> milk <NEXT_NER> butter <NER_END>"
postprocess_recipe(infer(input4, training_model1))

