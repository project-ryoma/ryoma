
# Quick Start

This guide will walk you through setting up Aita and start coding with Aita.

## Prerequisites

Before you start, make sure you have the following installed:

- Python 3.9 or higher

## Installation

To install Aita, run the following command:

{% code title="bash" %}
```bash
pip install aita
```
{% endcode %}

## Getting Started

To start using Aita, you can run the following code:

{% code title="python" %}
```python

from aita.agent.pandas import PandasAgent
import pandas as pd

df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'purchase_amount': [100, 200, 300, 400, 500]
})
pandas_agent = PandasAgent("gpt-3.5-turbo") \
    .add_dataframe(df)

print(pandas_agent.stream("I want to get the top customer which making the most purchases"))
```
{% endcode %}

This code will create a new agent that uses the GPT-3.5-turbo model and has a confidence threshold of 0.8.

## Next Steps

Now that you have successfully set up Aita, you can start exploring more features and functionalities. Check out the [documentation](https://docs.aita.dev) for more information.
