import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set seed for reproducibility
torch.manual_seed(42)
np.random.seed(42)

def prepare_data(filename="data_user500.csv"):
    df = pd.read_csv(filename)
    
    # Encode actions
    le_action = LabelEncoder()
    df['action_enc'] = le_action.fit_transform(df['action'])
    num_classes = len(le_action.classes_)
    
    # Normalize product_id (simplified)
    df['product_id_norm'] = df['product_id'] / 100.0
    
    sequences = []
    targets = []
    
    # Group by user and create sequences
    for user_id, group in df.groupby('user_id'):
        group = group.sort_values('timestamp')
        features = group[['product_id_norm', 'action_enc']].values
        
        # We have 8 behaviors per user, use first 7 as input, 8th action as target
        if len(features) == 8:
            sequences.append(features[:7])
            targets.append(features[7, 1]) # 1 is action_enc
            
    return np.array(sequences), np.array(targets), num_classes, le_action.classes_

# Models
class RNNModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(RNNModel, self).__init__()
        self.rnn = nn.RNN(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x):
        _, h = self.rnn(x)
        return self.fc(h.squeeze(0))

class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x):
        _, (h, c) = self.lstm(x)
        return self.fc(h.squeeze(0))

class BiLSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(BiLSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)
        
    def forward(self, x):
        _, (h, c) = self.lstm(x)
        # Concatenate forward and backward hidden states
        h_cat = torch.cat((h[-2,:,:], h[-1,:,:]), dim=1)
        return self.fc(h_cat)

def train_and_eval(model, train_loader, val_loader, epochs=50):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    train_losses = []
    val_accs = []
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for x_batch, y_batch in train_loader:
            optimizer.zero_grad()
            y_pred = model(x_batch.float())
            loss = criterion(y_pred, y_batch.long())
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        train_losses.append(total_loss / len(train_loader))
        
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for x_batch, y_batch in val_loader:
                y_pred = model(x_batch.float())
                _, predicted = torch.max(y_pred.data, 1)
                total += y_batch.size(0)
                correct += (predicted == y_batch).sum().item()
        
        val_accs.append(100 * correct / total)
        
    return train_losses, val_accs

if __name__ == "__main__":
    X, y, num_classes, class_names = prepare_data()
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    train_dataset = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train))
    val_dataset = TensorDataset(torch.from_numpy(X_val), torch.from_numpy(y_val))
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)
    
    input_dim = 2 # product_id and action
    hidden_dim = 64
    
    models = {
        "RNN": RNNModel(input_dim, hidden_dim, num_classes),
        "LSTM": LSTMModel(input_dim, hidden_dim, num_classes),
        "biLSTM": BiLSTMModel(input_dim, hidden_dim, num_classes)
    }
    
    results = {}
    
    plt.figure(figsize=(12, 5))
    
    for name, model in models.items():
        print(f"Training {name}...")
        losses, accs = train_and_eval(model, train_loader, val_loader)
        results[name] = {"losses": losses, "accs": accs, "final_acc": accs[-1]}
        
        plt.subplot(1, 2, 1)
        plt.plot(losses, label=name)
        plt.title("Training Loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.legend()
        
        plt.subplot(1, 2, 2)
        plt.plot(accs, label=name)
        plt.title("Validation Accuracy")
        plt.xlabel("Epoch")
        plt.ylabel("Accuracy (%)")
        plt.legend()
    
    plt.tight_layout()
    plt.savefig("model_comparison.png")
    print("Saved comparison plot to model_comparison.png")
    
    # Select best model
    best_model_name = max(results, key=lambda x: results[x]["final_acc"])
    print(f"\nBest model: {best_model_name} with {results[best_model_name]['final_acc']:.2f}% accuracy")
    
    # Save best model
    torch.save(models[best_model_name].state_dict(), "model_best.pth")
    print(f"Saved best model to model_best.pth")
    
    # Save class names for inference
    np.save("class_names.npy", class_names)
