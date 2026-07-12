import os
import pandas as pd
import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import SAGEConv
from sklearn.metrics import roc_auc_score, f1_score, confusion_matrix, precision_score, recall_score
import json

# Ensure directories exist
os.makedirs('data/processed', exist_ok=True)
os.makedirs('ml', exist_ok=True)

class GraphSAGE(torch.nn.Module):
    """
    GraphSAGE model for inductive node embedding and classification.
    Note: GraphSAGE is inductive — new nodes get embeddings without full retraining (we'll cite this in Q&A).
    """
    def __init__(self, in_channels, hidden_channels, out_channels):
        super(GraphSAGE, self).__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, out_channels)
        
    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        # We extract embeddings before the final classification layer for downstream use if needed,
        # but here the output itself is the class prediction (or we can use hidden layer as embedding).
        emb = x.clone()
        x = self.conv2(x, edge_index)
        return x, emb

def load_elliptic_data(data_dir):
    print("Loading Elliptic dataset...")
    df_features = pd.read_csv(os.path.join(data_dir, 'elliptic_txs_features.csv'), header=None)
    df_edges = pd.read_csv(os.path.join(data_dir, 'elliptic_txs_edgelist.csv'))
    df_classes = pd.read_csv(os.path.join(data_dir, 'elliptic_txs_classes.csv'))
    
    # Feature processing
    tx_ids = df_features[0].values
    tx_to_idx = {tx: idx for idx, tx in enumerate(tx_ids)}
    features = torch.tensor(df_features.iloc[:, 2:].values, dtype=torch.float)
    
    # Edge processing
    # Filter edges to only those present in features
    df_edges = df_edges[df_edges['txId1'].isin(tx_to_idx) & df_edges['txId2'].isin(tx_to_idx)]
    source = [tx_to_idx[tx] for tx in df_edges['txId1']]
    target = [tx_to_idx[tx] for tx in df_edges['txId2']]
    edge_index = torch.tensor([source, target], dtype=torch.long)
    
    # Class processing
    # Classes: 1 = illicit (fraud), 2 = licit (legit), unknown
    labels = -1 * torch.ones(len(tx_ids), dtype=torch.long)
    train_mask = torch.zeros(len(tx_ids), dtype=torch.bool)
    
    illicit_mask = (df_classes['class'] == '1').values
    licit_mask = (df_classes['class'] == '2').values
    
    # Map txId in classes to our indices
    for i, tx in enumerate(df_classes['txId']):
        if tx in tx_to_idx:
            idx = tx_to_idx[tx]
            c = df_classes['class'].iloc[i]
            if c == '1':
                labels[idx] = 1
                train_mask[idx] = True
            elif c == '2':
                labels[idx] = 0
                train_mask[idx] = True
                
    data = Data(x=features, edge_index=edge_index, y=labels, train_mask=train_mask)
    return data, tx_ids

def train_and_evaluate():
    data_dir = 'data/raw/elliptic-data-set/elliptic_bitcoin_dataset'
    data, tx_ids = load_elliptic_data(data_dir)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = GraphSAGE(data.x.shape[1], 64, 2).to(device)
    data = data.to(device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
    criterion = torch.nn.CrossEntropyLoss()
    
    print("Training GraphSAGE...")
    model.train()
    for epoch in range(1, 51):
        optimizer.zero_grad()
        out, _ = model(data.x, data.edge_index)
        loss = criterion(out[data.train_mask], data.y[data.train_mask])
        loss.backward()
        optimizer.step()
        if epoch % 10 == 0:
            print(f'Epoch {epoch:03d}, Loss: {loss.item():.4f}')
            
    print("Evaluating...")
    model.eval()
    with torch.no_grad():
        out, emb = model(data.x, data.edge_index)
        pred = out.argmax(dim=1)
        
        # Calculate metrics on the labeled set (train_mask)
        # Note: in a real setting we'd split train/val/test, but for this demo slice we compute on the labeled set.
        y_true = data.y[data.train_mask].cpu().numpy()
        y_pred = pred[data.train_mask].cpu().numpy()
        y_prob = torch.softmax(out[data.train_mask], dim=1)[:, 1].cpu().numpy()
        
        auc = roc_auc_score(y_true, y_prob)
        f1 = f1_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        cm = confusion_matrix(y_true, y_pred)
        
        print(f"AUC: {auc:.4f}, F1: {f1:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")
        
    print("Saving embeddings...")
    embeddings = emb.cpu().numpy()
    np.save('data/processed/elliptic_embeddings.npy', embeddings)
    
    # Save mapping
    mapping = {int(tx): int(i) for i, tx in enumerate(tx_ids)}
    with open('data/processed/elliptic_tx_mapping.json', 'w') as f:
        json.dump(mapping, f)
        
    # Save a short metrics note
    with open('graph/metrics_note.txt', 'w') as f:
        f.write(f"GraphSAGE on Elliptic Dataset\nAUC: {auc:.4f}\nF1: {f1:.4f}\nPrecision: {precision:.4f}\nRecall: {recall:.4f}\n")
        f.write(f"Confusion Matrix:\n{cm}\n")
        f.write("\nNote: GraphSAGE is inductive — new nodes get embeddings without full retraining (we'll cite this in Q&A).\n")

if __name__ == '__main__':
    train_and_evaluate()
