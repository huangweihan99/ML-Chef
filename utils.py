import streamlit as st

def format_input_ingredients(ingredients):
    full_ingredients = []
    ingredients_words = ingredients.split()

    for word in ingredients_words:
        if word == "<NER_END>":
            full_ingredients.append(word)
            break
        else:
            full_ingredients.append(word)

    input_ingredients = " ".join(full_ingredients)

    return input_ingredients

def postprocess_ingredients(ingredients):
    end_token_index = ingredients.find("<NER_END>")
    ingredients = ingredients[12:end_token_index-1]
    ingredients = ingredients.split(" <NEXT_NER> ")
    ingredients = ", ".join(ingredients)
    
    return ingredients

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

    st.subheader(full_title)
    st.markdown('___')
    st.markdown("##### **Ingredients:**")

    for word in ingredients:
      if word == "<NEXT_INGR>":
          st.markdown(f"* {ingredient}")
          ingredient = ""
      else:
          ingredient = ingredient + word + " "

    st.markdown(f"* {ingredient}")
    st.markdown('___')
    st.markdown("##### **Directions:**")
    
    i = 1
    
    for word in directions:
      if word == "<NEXT_DIR>":
          st.markdown(f"{i}. {direction}")
          direction = ""
          i +=1
      else:
          direction = direction + word + " "
    
    if direction != "":
      st.markdown(f"{i}. {direction}")
      
def get_title(recipe):
    full_recipe = []
    recipe_words = recipe.split()

    for word in recipe_words:
        if word == "<RECIPE_END>":
            break
        else:
            full_recipe.append(word)

    title = full_recipe[full_recipe.index("<TITLE_START>")+1:full_recipe.index("<TITLE_END>")]
    full_title = ""
    
    for title_word in title:
        full_title = full_title + title_word + " "
    
    return full_title
      
def recipe_to_txt(recipe):
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
    full_recipe = ""

    for title_word in title:
        full_title = full_title + title_word + " "

    full_recipe = full_title + "\n"
    full_recipe += "==========================================================================================================================================\n"
    full_recipe += "Ingredients:\n"

    for word in ingredients:
      if word == "<NEXT_INGR>":
          full_recipe += f"- {ingredient}\n"
          ingredient = ""
      else:
          ingredient = ingredient + word + " "

    full_recipe += f"- {ingredient}\n"
    full_recipe += "__________________________________________________________________________________________________________________________________________\n"
    full_recipe += "Directions:\n"
    
    i = 1
    
    for word in directions:
      if word == "<NEXT_DIR>":
          full_recipe += f"{i}. {direction}\n"
          direction = ""
          i +=1
      else:
          direction = direction + word + " "
    
    if direction != "":
      full_recipe += f"{i}. {direction}"
    
    return full_recipe