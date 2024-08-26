import math

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


class SelfAttention(nn.Module):
    def __init__(self, embdim, dropout):
        super().__init__()
        self.wq = nn.Linear(embdim, embdim)
        self.wk = nn.Linear(embdim, embdim)
        self.wv = nn.Linear(embdim, embdim)
        self.dropout = nn.Dropout(dropout)
        self.scale = math.sqrt(embdim)

    def forward(self, x, mask=None):
        q = self.wq(x)
        k = self.wk(x)
        v = self.wv(x)

        attn = torch.matmul(q, k.transpose(-2, -1)) / self.scale

        if mask is not None:
            attn = attn.masked_fill(mask == 0, float("-inf"))

        attn = F.softmax(attn, dim=-1)
        attn = self.dropout(attn)
        out = torch.matmul(attn, v)

        return out


class MultiHeadAttention(nn.Module):
    def __init__(self, embdim, block_size, nh, dropout, mask=False):
        super().__init__()
        self.nh = nh
        self.embdim = embdim
        self.dk = embdim // nh
        self.wq = nn.Linear(embdim, embdim)
        self.wk = nn.Linear(embdim, embdim)
        self.wv = nn.Linear(embdim, embdim)
        self.fc_out = nn.Linear(embdim, embdim)
        self.dropout = nn.Dropout(dropout)
        self.mask = None
        if mask:
            self.mask = torch.tril(torch.ones(block_size, block_size)).view(
                1, 1, block_size, block_size
            )

    def split_heads(self, x):
        batch_size, block_size, d_model = x.size()
        return x.view(batch_size, block_size, self.nh, self.dk).transpose(1, 2)

    def combine_heads(self, x):
        batch_size, _, block_size, d_k = x.size()
        return x.transpose(1, 2).contiguous().view(batch_size, block_size, self.embdim)

    def forward(self, q, k, v):
        q = self.split_heads(self.wq(q))  # (B, nh, T, dk)
        k = self.split_heads(self.wk(k))  # (B, nh, T, dk)
        v = self.split_heads(self.wv(v))  # (B, nh, T, dk)

        attn = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.dk)

        if self.mask is not None:
            attn = attn.masked_fill(self.mask == 0, float("-inf"))

        attn = F.softmax(attn, dim=-1)
        attn = self.dropout(attn)
        out = torch.matmul(attn, v)  # (B, nh, T, dk)

        out = self.combine_heads(out)  # (B, T, C)
        out = self.fc_out(out)

        return out


class PositionwiseFeedForward(nn.Module):
    def __init__(self, embdim, d_ff, dropout=0.1):
        super().__init__()
        self.fc1 = nn.Linear(embdim, d_ff)
        self.fc2 = nn.Linear(d_ff, embdim)
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x


class EncoderLayer(nn.Module):
    def __init__(self, embdim, block_size, d_ff, nh, dropout):
        super().__init__()
        self.attention = MultiHeadAttention(embdim, block_size, nh, dropout)
        self.ff = PositionwiseFeedForward(embdim, d_ff, dropout)
        self.norm1 = nn.LayerNorm(embdim)
        self.norm2 = nn.LayerNorm(embdim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        attn_out = self.attention(x, x, x)
        x = self.norm1(x + self.dropout(attn_out))
        ff_out = self.ff(x)
        out = self.norm2(x + self.dropout(ff_out))
        return out


class DecoderLayer(nn.Module):
    def __init__(self, embdim, block_size, d_ff, nh, dropout):
        super().__init__()
        self.masked_attn = MultiHeadAttention(
            embdim, block_size, nh, dropout, mask=True
        )
        self.attention = MultiHeadAttention(embdim, block_size, nh, dropout)
        self.ff = PositionwiseFeedForward(embdim, d_ff, dropout)
        self.norm1 = nn.LayerNorm(embdim)
        self.norm2 = nn.LayerNorm(embdim)
        self.norm3 = nn.LayerNorm(embdim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, enc_out):
        attn_out = self.masked_attn(x, x, x)
        x = self.norm1(x + self.dropout(attn_out))
        attn_out = self.attention(x, enc_out, enc_out)
        x = self.norm2(x + self.dropout(attn_out))
        ff_out = self.ff(x)
        out = self.norm3(x + self.dropout(ff_out))
        return out


class Transformer(nn.Module):
    def __init__(
        self, srcvoc_size, tgtvoc_size, block_size, embdim, d_ff, nh, dropout, n_layers
    ):
        super().__init__()
        self.encoder_emb = nn.Embedding(srcvoc_size, embdim)
        self.decoder_emb = nn.Embedding(tgtvoc_size, embdim)
        self.pos_emb = nn.Embedding(block_size, embdim)
        self.encoder_layers = nn.ModuleList(
            [
                EncoderLayer(embdim, block_size, d_ff, nh, dropout)
                for _ in range(n_layers)
            ]
        )
        self.decoder_layers = nn.ModuleList(
            [
                DecoderLayer(embdim, block_size - 1, d_ff, nh, dropout)
                for _ in range(n_layers)
            ]
        )
        self.fc_out = nn.Linear(embdim, tgtvoc_size)

    def forward(self, src, tgt):
        src_block_size, tgt_block_size = src.size(1), tgt.size(1)
        src_positions = torch.arange(0, src_block_size).unsqueeze(0).to(src.device)
        tgt_positions = torch.arange(0, tgt_block_size).unsqueeze(0).to(tgt.device)

        src = self.encoder_emb(src) + self.pos_emb(src_positions)
        tgt = self.decoder_emb(tgt) + self.pos_emb(tgt_positions)

        enc_out = src
        for layer in self.encoder_layers:
            enc_out = layer(enc_out)

        out = tgt
        for layer in self.decoder_layers:
            out = layer(out, enc_out)

        out = self.fc_out(out)
        return out


def train(transformer, src, tgt, epoch=10, lr=1e-4):
    optimizer = optim.Adam(transformer.parameters(), lr=lr)
    loss_func = nn.CrossEntropyLoss(ignore_index=0)

    transformer.train()  # Set model to training mode

    for ep in range(epoch):
        optimizer.zero_grad()

        # Forward pass
        out = transformer(src, tgt[:, :-1])  # Input sequence (excluding last token)

        # Reshape output and target for loss computation
        out = out.contiguous().view(
            -1, transformer.fc_out.out_features
        )  # Flatten output
        tgt_flat = (
            tgt[:, 1:].contiguous().view(-1)
        )  # Flatten target (excluding first token)

        # Compute loss
        loss = loss_func(out, tgt_flat)

        # Backward pass and optimization
        loss.backward()
        optimizer.step()

        # Print training progress
        if (ep + 1) % 10 == 0 or ep == 0:
            print(f"Epoch [{ep + 1}/{epoch}], Loss: {loss.item():.4f}")


# Define the parameters
src_vocab_size = 5000
tgt_vocab_size = 5000
block_size = 10
epoch = 100
embdim = 32
d_ff = 64
nh = 4
dropout = 0.1
n_layer = 2
lr = 0.001

# Generate random sample data
src_data = torch.randint(
    1, src_vocab_size, (64, block_size)
)  # (batch_size, block_size)
tgt_data = torch.randint(
    1, tgt_vocab_size, (64, block_size)
)  # (batch_size, block_size)
# Instantiate the model
transformer = Transformer(
    src_vocab_size, tgt_vocab_size, block_size, embdim, d_ff, nh, dropout, n_layer
)

# Train the model
train(transformer, src_data, tgt_data, epoch=epoch, lr=lr)
