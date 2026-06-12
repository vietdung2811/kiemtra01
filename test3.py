import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

np.random.seed(42)
N = 100

X_academic = np.random.randint(4, 10, (N, 5))
peer = np.random.randint(4, 10, (N, 10))
X = np.hstack([X_academic, peer])
X = torch.tensor(X, dtype=torch.float32)

edges = []
for i in range(N):
    for j in range(N):
        if i != j:
            sim = np.linalg.norm(X_academic[i] - X_academic[j])
            if sim < 6:
                edges.append([i, j])

edges = torch.tensor(edges, dtype=torch.long)
A = torch.zeros((N, N))
for i, j in edges:
    A[i, j] = 1.0

A = A / (A.sum(dim=1, keepdim=True) + 1e-6)
peer_mean = peer.mean(axis=1)

y = (
    0.3 * X_academic[:, 0] +
    0.2 * X_academic[:, 1] +
    0.1 * X_academic[:, 2] +
    0.15 * X_academic[:, 3] +
    0.1 * X_academic[:, 4] +
    0.15 * peer_mean +
    np.random.normal(0, 0.3, N)
)
y = torch.tensor(y, dtype=torch.float32)

class GraphSAGE(nn.Module):
    def __init__(self, in_dim, hidden=64):
        super().__init__()
        self.fc1 = nn.Linear(in_dim * 2, hidden)
        self.fc2 = nn.Linear(hidden, 32)
        self.out = nn.Linear(32, 1)

    def forward(self, x, adj):
        neigh = torch.matmul(adj, x)
        h = torch.cat([x, neigh], dim=1)
        h = F.relu(self.fc1(h))
        h = F.relu(self.fc2(h))
        return self.out(h).squeeze()

model = GraphSAGE(X.shape[1])
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.L1Loss()

for epoch in range(200):
    optimizer.zero_grad()
    pred = model(X, A)
    loss = loss_fn(pred, y)
    loss.backward()
    optimizer.step()

print("Final prediction:", model(X, A)[0].item())