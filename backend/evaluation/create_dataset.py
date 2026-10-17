from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

client = Client()

examples = [
    {"inputs":{"question":"How many layers does the encoder have?"},
     "outputs":{"answer":"6 identical layers (N = 6)"}
    },
    { "inputs":{"question":"How many attention heads does the base model use?"},
     "outputs":{"answer":"8 (h = 8)"}
    
    },
    {"inputs":{"question":"What is the dimension d_model in the base model?"},
     "outputs":{"answer":"512"}},


    {"inputs":{"question":"Which optimizer was used for training?"},
         "outputs":{"answer":"Adam, β1 = 0.9, β2 = 0.98, ε = 10⁻⁹"}},

   { "inputs":{"question":"What hardware was used and how long did the base model train?"},
        "outputs":{"answer":"8 NVIDIA P100 GPUs, 100,000 steps, about 12 hours"}
       
       },
    { "inputs":{"question":"What dropout rate was used for the base model?"},
            "outputs":{"answer":"0.1"}
           
           },

    { "inputs":{"question":"What BLEU score does the big Transformer get on English-to-German (WMT 2014)?"},
            "outputs":{"answer":"28.4"}
           
           },

     { "inputs":{"question":"What is the training cost in FLOPs of the base Transformer?"},
                "outputs":{"answer":"3.3 × 10^18"}
               
               },

     { "inputs":{"question":"In the architecture diagram, what follows each Multi-Head Attention block?"},
            "outputs":{"answer":"An “Add & Norm” step (residual connection + layer normalization)"}
           
           },
    { "inputs":{"question":"What is the capital of France?"},
            "outputs":{"answer":"Should say it does not have enough information in the documents"}
           
           },

    ]

dataset = client.create_dataset(dataset_name="attention-paper-qa01")
client.create_examples(dataset_id=dataset.id,examples=examples)

