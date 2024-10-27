# ai-shopping-buddy
An e-commerce conversational chatbot that gathers customer preferences to provide personalized product recommendations. 
Developed for "Generative AI World Cup 2024: So you think you can hack" by Databricks.

## 🚧 Early Development

This project is currently in early development. To minimize costs, 
Ollama local model is used instead of model serving on Databricks. 
We plan to transition to Databricks in the future.

## 🛠️ Local Setup

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


3. To interact with the chatbot, run
   ```bash
   python chatbots/shopping_buddy.py
   ```

## 🗂️ Dataset

The [Best Buy Products Dataset](https://dbc-dc755886-ab40.cloud.databricks.com/marketplace/consumer/listings/55c3365c-0a3b-403b-a8e0-73fca0469fff?o=2368250103410450)
is used. It is a sample dataset obtained from Databricks Marketplace.

### Data Fields
Here are the key fields in the dataset, omitting unused columns:
```
Schema({
    'product_id': Int64,
    'title': String,
    'images': String,
    'final_price': String,
    'discount': String,
    'initial_price': String,
    'root_category': String,
    'features_summary': String,
    'features': String,
    'product_specifications': String,
})
```

### Accessing the Dataset
To access the dataset on databricks, follow these steps:
1. Go to [Best Buy Products Dataset](https://dbc-dc755886-ab40.cloud.databricks.com/marketplace/consumer/listings/55c3365c-0a3b-403b-a8e0-73fca0469fff?o=2368250103410450)
2. Click `Get Instant Access`
3. Set Catelog name as `bright_data_best_buy_products_dataset`

The data will be available as `bright_data_best_buy_products_dataset.datasets.best_buy_products`

### Acknowledgments
This dataset is provided by Bright Data. All rights reserved. 

We would like to thank Bright Data for making this data available for research and development purposes. For more information about Bright Data, please visit their [official website](https://brightdata.com).
