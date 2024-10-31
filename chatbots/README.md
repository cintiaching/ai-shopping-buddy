# Agent Graph
The graph below illustrates the implemented logic of the shopping buddy's agentic service. Additional elements will be included to finalize the graph and provide a complete product recommendation.

Currently, the graph captures the process of obtaining customer preferences.

```mermaid
%%{init: {'flowchart': {'curve': 'linear'}}}%%
graph TD;
	__start__([<p>__start__</p>]):::first
	get_preference(get_preference)
	manage_state(manage_state)
	greeting(greeting)
	gather_preference(gather_preference)
	match_products(match_products)
	recommend(recommend)
	find_related_products(find_related_products)
	recommend_related_product(recommend_related_product)
	__end__([<p>__end__</p>]):::last
	__start__ --> manage_state;
	find_related_products --> recommend_related_product;
	gather_preference --> match_products;
	manage_state --> greeting;
	match_products --> recommend;
	recommend_related_product --> __end__;
	greeting -.-> __end__;
	greeting -.-> get_preference;
	get_preference -.-> gather_preference;
	get_preference -.-> __end__;
	recommend -.-> find_related_products;
	recommend -.-> __end__;
	get_preference -.-> get_preference;
	classDef default fill:#1e1e1e, stroke:#ffffff, color:#ffffff;
    classDef first fill:#4a4a4a, color:#ffffff;
    classDef last fill:#3b3b3b, color:#ffffff;
    classDef node fill:#2c2c2c, stroke:#ffffff, color:#ffffff;
```
