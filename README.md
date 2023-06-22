# ML-Chef

The ML-Chef data application consists of two GPT-2 models fine-tuned for the purpose of recipe generation and ingredient recommendation. These two models work in unison to take in a list of ingredients from the user, optionally recommend additional complementary ingredients, and generate customised recipes that maximally utilise the input ingredients. The high-level system diagram of the data application is shown below:

![data_app](https://github.com/huangweihan99/ML-Chef/assets/83905363/f89d272b-828c-4d96-93ca-768c157ecd21)

The ML-Chef data application was developed to achieve the following goals:

* Reduce food wastage
* Encourage culinary exploration

## User Guide

To launch and use the data application follow the steps listed below:
1. Clone the ML-Chef GitHub repository.
2. Replace the pre-trained model file paths in the functions `load_recipe_model` and `load_ingredient_model` to those corresponding to your local device:

```python
@st.cache_resource
def load_ingredient_model():
    """Loads ingredient recommendation model and caches it"""
    ingredient_model = GPT2LMHeadModel.from_pretrained(r"Replace with ingredient model file path")
    ingredient_model = ingredient_model.to(device)
    
    return ingredient_model

@st.cache_resource
def load_recipe_model():
    """Loads recipe generation model and caches it"""
    recipe_model = GPT2LMHeadModel.from_pretrained(r"Replace with recipe model file path")
    recipe_model = recipe_model.to(device)
    
    return recipe_model
```

3. Install the necessary libraries such as streamlit and transformers.

```python
pip install streamlit
pip install transformers
```

4. Navigate to the ML-Chef directory in your terminal and enter the command `streamlit run main.py` to launch the data app.
5. Select common pantry ingredients to use from the drop-down menu.
6. Enter other input ingredients in the text-entry field in **CSV format**.
7. Use the ingredient recommendation model to recommend additional complementary ingredients by selecting the **Augment Ingredient List** option.
8. Finalize the input ingredients to the recipe generation model by clicking the **Compile Ingredient List** button.

![ingdt_entry](https://github.com/huangweihan99/ML-Chef/assets/83905363/cd8ca45f-2d8f-4108-827c-b482e7202ca9)

9. After compiling the ingredient list, you can adjust the generation hyperparameters using the sliders and then click the **Generate Recipe** button. This process takes a while (∼ 35s).
10. After the recipe has been generated, you have the option to save the recipe to your local device by clicking the **Download Recipe** button.

![recipe_generation2](https://github.com/huangweihan99/ML-Chef/assets/83905363/821c5647-43ee-42e1-8839-c040b916327f)

11. When following the recipe, use the unit conversion widget located in the side bar to convert any quantities.

## Training and Validation

The training and validation pipeline used for both models are essentially identical. A high-level overview is provided below:

![recipe_training_pipeline](https://github.com/huangweihan99/ML-Chef/assets/83905363/dccd0b1c-32de-4d9e-8e68-a180370f887a)

The pre-trained models were sourced from the [Hugging Face library](https://huggingface.co/) that also provided the high-level components used to formulate the pipelines. The models were trained using filtered versions of the [RecipeNLG](https://recipenlg.cs.put.poznan.pl/). The detailed code and guidance for the training and validation processes can be found in the two Jupyter notebooks within the **`colab_training`** file.

## Evaluation

The recipe generation and ingredient recommendation models were tested using datasets that contained 246,895 full recipes and 326,865 ingredient lists respectively. The losses incurred and generation metrics scores produced during the evaluation runs are tallied in the table below:

|Model                          | Cross-Entropy Loss|BLEU    |ROUGE-2 |METEOR  |SBERT   |WER     |
|:-----------------------------:|:-----------------:|:------:|:------:|:------:|:------:|:------:|
|Recipe Generation Model        |1.449741           |0.481800|0.424000|0.573900|0.971600|0.659600|
|Ingredient Recommendation Model|1.740500           |0.518000|0.352800|0.522300|0.851000|0.843300|

**Note:** the output logits were sampled using a greedy search, thus the generation metric scores in the table reflect the similarity between the **most-likely outputs** and the labels.



