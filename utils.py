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