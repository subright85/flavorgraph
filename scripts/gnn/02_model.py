"""
Simple-HGN encoder + DistMult decoder.

Simple-HGN (arXiv:2112.14936, KDD 2021):
- GAT attention with learnable type-level embeddings
- Residual connection per layer
- L2 normalization on output embeddings

DistMult decoder:
- score(i,j) = eᵢᵀ W eⱼ  (W = diagonal, so element-wise product + sum)
- Symmetric → appropriate for undirected ingredient pairing
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import HeteroConv, GATConv


class SimpleHGNLayer(nn.Module):
    def __init__(self, in_dim, out_dim, num_node_types, num_edge_types, num_heads=4, dropout=0.1):
        super().__init__()
        self.out_dim = out_dim
        self.num_heads = num_heads
        head_dim = out_dim // num_heads

        # Type-specific linear transforms (one per node type)
        self.type_transforms = nn.ModuleDict()

        # GAT convolutions per relation
        self.convs = HeteroConv({
            ('ingredient', 'pairs_with', 'ingredient'): GATConv(
                in_dim, head_dim, heads=num_heads, dropout=dropout,
                add_self_loops=False, concat=True
            ),
            ('ingredient', 'contains', 'compound'): GATConv(
                (in_dim, in_dim), head_dim, heads=num_heads, dropout=dropout,
                add_self_loops=False, concat=True
            ),
            ('compound', 'in', 'ingredient'): GATConv(
                (in_dim, in_dim), head_dim, heads=num_heads, dropout=dropout,
                add_self_loops=False, concat=True
            ),
        }, aggr='sum')

        # Learnable type embedding added to output (Simple-HGN key innovation)
        self.type_emb = nn.Embedding(num_node_types, out_dim)

        # Residual projection (in_dim → out_dim if they differ)
        self.res_proj = nn.Linear(in_dim, out_dim, bias=False) if in_dim != out_dim else nn.Identity()

        self.dropout = nn.Dropout(dropout)
        self.norm_ing = nn.LayerNorm(out_dim)
        self.norm_cmp = nn.LayerNorm(out_dim)

    def forward(self, x_dict, edge_index_dict, type_ids):
        out_dict = self.convs(x_dict, edge_index_dict)

        result = {}
        for ntype, out in out_dict.items():
            res = self.res_proj(x_dict[ntype])
            type_id = type_ids[ntype]
            te = self.type_emb(torch.tensor(type_id, device=out.device))
            h = out + te + res
            if ntype == 'ingredient':
                h = self.norm_ing(h)
            else:
                h = self.norm_cmp(h)
            h = F.elu(h)
            h = self.dropout(h)
            result[ntype] = h

        return result


class SimpleHGN(nn.Module):
    """
    2-layer Simple-HGN with learnable input embeddings (no pre-computed features).
    Node types: ingredient=0, compound=1
    """

    def __init__(self, n_ingredient, n_compound, hidden_dim=128, num_layers=2,
                 num_heads=4, dropout=0.1):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.type_ids = {'ingredient': 0, 'compound': 1}

        # Learnable node embeddings (initial features)
        self.ing_emb = nn.Embedding(n_ingredient, hidden_dim)
        self.cmp_emb = nn.Embedding(n_compound, hidden_dim)

        self.layers = nn.ModuleList([
            SimpleHGNLayer(
                in_dim=hidden_dim,
                out_dim=hidden_dim,
                num_node_types=2,
                num_edge_types=3,
                num_heads=num_heads,
                dropout=dropout,
            )
            for _ in range(num_layers)
        ])

    def forward(self, data):
        x_dict = {
            'ingredient': self.ing_emb.weight,
            'compound': self.cmp_emb.weight,
        }
        edge_index_dict = {
            ('ingredient', 'pairs_with', 'ingredient'): data['ingredient', 'pairs_with', 'ingredient'].edge_index,
            ('ingredient', 'contains', 'compound'): data['ingredient', 'contains', 'compound'].edge_index,
            ('compound', 'in', 'ingredient'): data['compound', 'in', 'ingredient'].edge_index,
        }

        for layer in self.layers:
            x_dict = layer(x_dict, edge_index_dict, self.type_ids)

        # L2 normalize ingredient embeddings
        x_dict['ingredient'] = F.normalize(x_dict['ingredient'], dim=-1)
        x_dict['compound'] = F.normalize(x_dict['compound'], dim=-1)

        return x_dict


class DistMultDecoder(nn.Module):
    """
    Symmetric DistMult: score(i,j) = eᵢ ⊙ W ⊙ eⱼ summed.
    W is a learnable diagonal (hidden_dim vector).
    """

    def __init__(self, hidden_dim):
        super().__init__()
        self.W = nn.Parameter(torch.ones(hidden_dim))

    def forward(self, ei, ej):
        # ei, ej: [batch, hidden_dim]
        return (ei * self.W * ej).sum(dim=-1)


class FlavorHGN(nn.Module):
    """Full model: encoder + decoder."""

    def __init__(self, n_ingredient, n_compound, hidden_dim=128, num_layers=2,
                 num_heads=4, dropout=0.1):
        super().__init__()
        self.encoder = SimpleHGN(n_ingredient, n_compound, hidden_dim, num_layers, num_heads, dropout)
        self.decoder = DistMultDecoder(hidden_dim)

    def encode(self, data):
        return self.encoder(data)

    def score_pair(self, x_dict, ing_i, ing_j):
        """Score ingredient pair (i, j). Both are index tensors."""
        ei = x_dict['ingredient'][ing_i]
        ej = x_dict['ingredient'][ing_j]
        return self.decoder(ei, ej)

    def forward(self, data, ing_i, ing_j):
        x_dict = self.encode(data)
        return self.score_pair(x_dict, ing_i, ing_j)
