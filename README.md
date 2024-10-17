# ai-shopping-buddy
An e-commerce conversational chatbot that gathers customer preferences to provide personalized product recommendations. 
Developed for "Generative AI World Cup 2024: So you think you can hack" by Databricks.

## 🚧 Early Development

This project is currently in early development. To minimize costs, 
Ollama local model is used instead of model serving on Databricks. 
We plan to transition to Databricks in the future.

## 🛠️ Setup

Follow these steps to set up the environment.

1. Install Dependencies
    ```bash
    pip install -r requirement-dev.txt
    ```

2. Pull the Ollama Model
    ```bash
    ollama pull mistral
    ```
   The [mistral](https://ollama.com/library/mistral) model is used as it is small and runs fast locally. 
   It can be easily switch to other models in the Ollama library.
