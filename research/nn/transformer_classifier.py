# Create a decoder only transformer classifier.
from typing import Any, Dict

import torch
from torch import nn


class TransformerClassifier(nn.Module):
    """Create a transformer classifier."""

    def __init__(self, config: Dict[str, Any], num_labels: int):
        super().__init__()
        self.config = config
        self.num_labels = num_labels

        self.embd = nn.Embedding(
            num_embeddings=config["vocab_size"],
            embedding_dim=config["hidden_size"],
        )

        self.decoder_layer = nn.TransformerDecoderLayer(
            d_model=config["hidden_size"],
            nhead=config["num_attention_heads"],
        )

        self.decoder = nn.TransformerDecoder(
            decoder_layer=self.decoder_layer,
            num_layers=config["num_hidden_layers"],
        )

        self.classifier = nn.Linear(config["hidden_size"], num_labels)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        embedded_seq = self.embd(input_ids)

        tgt_mask = nn.Transformer.generate_square_subsequent_mask(input_ids.size(1)).to(
            input_ids.device
        )

        x = self.decoder(embedded_seq, embedded_seq, tgt_mask=tgt_mask)
        x = self.classifier(x[:, -1, :])
        probs = torch.nn.functional.softmax(x, dim=-1)
        return probs


# example parameters
config = {
    "vocab_size": 1000,
    "hidden_size": 128,
    "num_attention_heads": 4,
    "num_hidden_layers": 2,
}

# create model
model = TransformerClassifier(config, num_labels=2)
# print(model)

# example input and target
input_ids = torch.randint(0, 1000, (10, 10))
targets = torch.randint(0, 2, (10,))
print("input_ids", input_ids.size())
print("targets", targets.size())


def train(x, y):
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    for i in range(10):
        optimizer.zero_grad()
        output = model(x)
        # print("output", output)
        loss = loss_fn(output, y)
        loss.backward()
        optimizer.step()
        print(loss.item())
        if i == 9:
            predicted_labels = torch.argmax(output, dim=-1)
            print("predicted_labels", predicted_labels)


train(input_ids, targets)
