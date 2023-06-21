import streamlit as st

def format_input_ingredients(ingredients):
    """Clip input ingredient list at end token"""
    
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
    """Removes control tokens from ingredient list for display"""
    
    end_token_index = ingredients.find("<NER_END>")
    ingredients = ingredients[12:end_token_index-1]
    ingredients = ingredients.split(" <NEXT_NER> ")
    ingredients = ", ".join(ingredients)
    
    return ingredients

def postprocess_recipe(recipe):
    """Removes control tokens and formats recipe for markdown"""
    
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
    """Get title for file name"""
    
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
    """Convert recipe to format for .txt download file"""
    
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


def convert_temp(unit1, unit2, input):
    """Converts temperature units"""
    
    if unit1 == 'Fahrenheit' and unit2 == 'Degree Celsius':
        temp_output = round(input - 32 * (5/9), 2)
        st.write(f"{round(input, 2)}F = {temp_output}" + u"\u2103")
        
    if unit2 == 'Fahrenheit' and unit1 == 'Degree Celsius':
        temp_output = round(input / (5/9) + 32, 2)
        st.write(f"{round(input, 2)}" + u"\u2103"  + f"= {temp_output}F")
        
        
def convert_mass(unit1, unit2, input):
    """Converts mass units"""
    
    if unit1 == "Pound":
        if unit2 == "Ounce":
            output = round(input * 16, 2)
            st.write(f"{round(input, 2)}lbs = {output}oz")
        elif unit2 == "Kilogram":
            output = round(input * 0.45359237, 2)
            st.write(f"{round(input, 2)}lbs = {output}kg")
        elif unit2 == "Gram":
            output = round(input * 453.59237, 2)
            st.write(f"{round(input, 2)}lbs = {output}g")
    elif unit1 == "Ounce":
        if unit2 == "Pound":
            output = round(input / 16, 2)
            st.write(f"{round(input, 2)}oz = {output}lbs")
        elif unit2 == "Kilogram":
            output = round(input / 35.274, 2)
            st.write(f"{round(input, 2)}oz = {output}kg")
        elif unit2 == "Gram":
            output = round(input / 0.035274, 2)
            st.write(f"{round(input, 2)}oz = {output}g")
    elif unit1 == "Kilogram":
        if unit2 == "Pound":
            output = round(input / 0.45359237, 2)
            st.write(f"{round(input, 2)}kg = {output}lbs")
        elif unit2 == "Ounce":
            output = round(input * 35.274, 2)
            st.write(f"{round(input, 2)}kg = {output}oz")
        elif unit2 == "Gram":
            output = round(input * 1000, 2)
            st.write(f"{round(input, 2)}kg = {output}g")
    elif unit1 == "Gram":
        if unit2 == "Pound":
            output = round(input / 453.59237, 2)
            st.write(f"{round(input, 2)}g = {output}lbs")
        elif unit2 == "Ounce":
            output = round(input * 0.035274, 2)
            st.write(f"{round(input, 2)}g = {output}oz")
        elif unit2 == "Kilogram":
            output = round(input / 1000, 2)
            st.write(f"{round(input, 2)}g = {output}kg")
            

def convert_volume(unit1, unit2, input):
    """Converts volume units"""
    
    if unit1 == "Cup":
        if unit2 == "Tablespoon":
            output = round(input * 16, 2)
            st.write(f"{round(input, 2)} Cup = {output} Tablespoon")
        elif unit2 == "Teaspoon":
            output = round(input * 48, 2)
            st.write(f"{round(input, 2)} Cup = {output} Teaspoon")
        elif unit2 == "Litre":
            output = round(input / 4.2267528198649, 2)
            st.write(f"{round(input, 2)} Cup = {output}L")
        elif unit2 == "Millilitre":
            output = round(input * 236.588236, 2)
            st.write(f"{round(input, 2)} Cup = {output}ml")
    elif unit1 == "Tablespoon":
        if unit2 == "Cup":
            output = round(input / 16, 2)
            st.write(f"{round(input, 2)} Tablespoon = {output} Cup")
        elif unit2 == "Teaspoon":
            output = round(input * 3, 2)
            st.write(f"{round(input, 2)} Tablespoon = {output} Teaspoon")
        elif unit2 == "Litre":
            output = round(input / 67.628045, 2)
            st.write(f"{round(input, 2)} Tablespoon = {output}L")
        elif unit2 == "Millilitre":
            output = round(input * 14.7867648, 2)
            st.write(f"{round(input, 2)} Tablespoon = {output}ml")
    elif unit1 == "Teaspoon":
        if unit2 == "Cup":
            output = round(input / 48, 2)
            st.write(f"{round(input, 2)} Teaspoon = {output} Cup")
        elif unit2 == "Tablespoon":
            output = round(input / 3, 2)
            st.write(f"{round(input, 2)} Teaspoon = {output} Tablespoon")
        elif unit2 == "Litre":
            output = round(input / 202.884136, 2)
            st.write(f"{round(input, 2)} Teaspoon = {output}L")
        elif unit2 == "Millilitre":
            output = round(input * 4.928922, 2)
            st.write(f"{round(input, 2)} Teaspoon = {output}ml")
    elif unit1 == "Litre":
        if unit2 == "Cup":
            output = round(input * 4.2267528377, 2)
            st.write(f"{round(input, 2)}L = {output} Cup")
        elif unit2 == "Tablespoon":
            output = round(input * 67.628045, 2)
            st.write(f"{round(input, 2)}L = {output} Tablespoon")
        elif unit2 == "Teaspoon":
            output = round(input * 202.884136, 2)
            st.write(f"{round(input, 2)}L = {output} Teaspoon")
        elif unit2 == "Millilitre":
            output = round(input * 1000, 2)
            st.write(f"{round(input, 2)}L = {output}ml")
    elif unit1 == "Millilitre":
        if unit2 == "Cup":
            output = round(input / 236.588237, 2)
            st.write(f"{round(input, 2)}ml = {output} Cup")
        elif unit2 == "Tablespoon":
            output = round(input / 14.7867648, 2)
            st.write(f"{round(input, 2)}ml = {output} Tablespoon")
        elif unit2 == "Teaspoon":
            output = round(input / 4.928922, 2)
            st.write(f"{round(input, 2)}ml = {output} Teaspoon")
        elif unit2 == "Litre":
            output = round(input / 1000, 2)
            st.write(f"{round(input, 2)}ml = {output}L")
            
def convert_length(unit1, unit2, input):
    """Converts length units"""
    
    if unit1 == "Foot":
        if unit2 == "Inch":
            output = round(input * 12, 2)
            st.write(f"{round(input, 2)}ft = {output}in")
        elif unit2 == "Metre":
            output = round(input * 0.304800004, 2)
            st.write(f"{round(input, 2)}ft = {output}m")
        elif unit2 == "Centimetre":
            output = round(input * 30.4800004, 2)
            st.write(f"{round(input, 2)}ft = {output}cm")
    elif unit1 == "Inch":
        if unit2 == "Foot":
            output = round(input / 12, 2)
            st.write(f"{round(input, 2)}in = {output}ft")
        elif unit2 == "Metre":
            output = round(input / 39.3701, 2)
            st.write(f"{round(input, 2)}in = {output}m")
        elif unit2 == "Centimetre":
            output = round(input / 0.393701, 2)
            st.write(f"{round(input, 2)}in = {output}cm")
    elif unit1 == "Metre":
        if unit2 == "Foot":
            output = round(input / 0.304800004, 2)
            st.write(f"{round(input, 2)}m = {output}ft")
        elif unit2 == "Inch":
            output = round(input * 39.3701, 2)
            st.write(f"{round(input, 2)}m = {output}in")
        elif unit2 == "Centimetre":
            output = round(input * 100, 2)
            st.write(f"{round(input, 2)}m = {output}cm")
    elif unit1 == "Centimetre":
        if unit2 == "Foot":
            output = round(input / 30.4800004, 2)
            st.write(f"{round(input, 2)}cm = {output}ft")
        elif unit2 == "Inch":
            output = round(input * 0.393701, 2)
            st.write(f"{round(input, 2)}cm = {output}in")
        elif unit2 == "Metre":
            output = round(input / 100, 2)
            st.write(f"{round(input, 2)}cm = {output}m")