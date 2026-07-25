"""GNN threat classifier (the QTD-HGNN core).

Two-layer GraphSAGE that classifies each transaction node as benign/malicious by
aggregating neighbour features across same-customer and same-payee edges. Consumes
the fused + topological node features. GraphSAGE (not plain GCN) for robustness on
the skewed-degree transaction graph.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv


class QTDGraphSAGE(torch.nn.Module):
    def __init__(self, in_channels: int, hidden_channels: int = 32, num_classes: int = 2,
                 dropout: float = 0.4):
        super().__init__()
        torch.manual_seed(12345)
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, hidden_channels)
        self.lin = torch.nn.Linear(hidden_channels, num_classes)
        self.dropout = dropout

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x, edge_index).relu()
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.conv2(x, edge_index).relu()
        x = F.dropout(x, p=self.dropout, training=self.training)
        return self.lin(x)   # logits [benign, malicious]
