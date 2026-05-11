"""
SimGRACE contrastive pre-training (WWW 2022).

Key idea: generate two views by adding Gaussian noise to encoder weights
→ no graph augmentation, preserves PMI structure.

Loss: NT-Xent (normalized temperature-scaled cross-entropy)
- Positive pairs: same node, two noisy encoder views
- Negatives: all other nodes in the batch
"""

import torch
import torch.nn.functional as F
import os
import sys
import copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from scripts.gnn.model import FlavorHGN


GRAPH_PATH = os.path.join(os.path.dirname(__file__), 'graph.pt')
PRETRAIN_CKPT = os.path.join(os.path.dirname(__file__), 'pretrain.pt')


def perturb_encoder(model, noise_std=0.01):
    """Return a deep copy of model with Gaussian noise on all encoder params."""
    model_copy = copy.deepcopy(model)
    with torch.no_grad():
        for param in model_copy.encoder.parameters():
            param.add_(torch.randn_like(param) * noise_std)
    return model_copy


def nt_xent_loss(z1, z2, temperature=0.5):
    """NT-Xent contrastive loss. z1, z2: [N, D]."""
    z1 = F.normalize(z1, dim=-1)
    z2 = F.normalize(z2, dim=-1)
    N = z1.size(0)
    z = torch.cat([z1, z2], dim=0)
    sim = torch.mm(z, z.T) / temperature
    mask = torch.eye(2 * N, dtype=torch.bool, device=z.device)
    sim.masked_fill_(mask, float('-inf'))
    labels = torch.cat([torch.arange(N) + N, torch.arange(N)], dim=0).to(z.device)
    return F.cross_entropy(sim, labels)


def pretrain(
    hidden_dim=128,
    num_layers=2,
    num_heads=4,
    dropout=0.1,
    noise_std=0.01,
    temperature=0.5,
    lr=1e-3,
    epochs=200,
    device='cpu',
    verbose=True,
):
    data = torch.load(GRAPH_PATH, weights_only=False)
    data = data.to(device)

    n_ing = data['ingredient'].num_nodes
    n_cmp = data['compound'].num_nodes

    model = FlavorHGN(n_ing, n_cmp, hidden_dim, num_layers, num_heads, dropout).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_loss = float('inf')
    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()

        # View 1: current model
        x1 = model.encode(data)

        # View 2: noisy encoder copy (no grad)
        noisy_model = perturb_encoder(model, noise_std=noise_std).to(device)
        noisy_model.train(False)  # inference mode — disables dropout
        with torch.no_grad():
            x2 = noisy_model.encode(data)

        loss_ing = nt_xent_loss(x1['ingredient'], x2['ingredient'], temperature)
        loss_cmp = nt_xent_loss(x1['compound'], x2['compound'], temperature)
        loss = loss_ing + 0.5 * loss_cmp

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()

        if loss.item() < best_loss:
            best_loss = loss.item()
            torch.save(model.state_dict(), PRETRAIN_CKPT)

        if verbose and epoch % 20 == 0:
            print(f"Epoch {epoch:3d} | loss {loss.item():.4f} (ing {loss_ing.item():.4f}, cmp {loss_cmp.item():.4f})")

    print(f"\nPre-training done. Best loss: {best_loss:.4f}")
    print(f"Checkpoint: {PRETRAIN_CKPT}")
    return model


if __name__ == '__main__':
    pretrain(epochs=200, verbose=True)
