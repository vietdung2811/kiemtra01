import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

class GNNStyleModel(nn.Module):
    def __init__(self, in_dim):
        super().__init__()
        self.fc1 = nn.Linear(in_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.out = nn.Linear(32, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.out(x)

np.random.seed(42)
N = 500
X = np.random.randint(4, 10, (N, 15))
peer_mean = X[:, 5:15].mean(axis=1, keepdims=True)
peer_std = X[:, 5:15].std(axis=1, keepdims=True)
y = (
    0.25 * X[:, 0] +
    0.2 * X[:, 1] +
    0.1 * X[:, 2] +
    0.15 * X[:, 3] +
    0.1 * X[:, 4] +
    0.2 * peer_mean.squeeze() +
    np.random.normal(0, 0.25, N)
)
X_full = np.hstack([X, peer_mean, peer_std])
X_tensor = torch.tensor(X_full, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.float32).view(-1, 1)

model = GNNStyleModel(X_tensor.shape[1])
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.L1Loss()

for epoch in range(200):
    optimizer.zero_grad()
    pred = model(X_tensor)
    loss = loss_fn(pred, y_tensor)
    loss.backward()
    optimizer.step()

print("Final MAE:", loss.item())