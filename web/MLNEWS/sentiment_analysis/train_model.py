# -*- coding: utf-8 -*-
"""
训练LSTM情感分析模型（可选）
如果需要训练自己的模型，可以使用此脚本
"""
import os
import pickle
import jieba
import numpy as np
from collections import Counter
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from lstm_model import SentimentLSTM, SentimentAnalyzer

class SentimentDataset(Dataset):
    """情感分析数据集"""
    def __init__(self, texts, labels, word_to_idx, max_length=100):
        self.texts = texts
        self.labels = labels
        self.word_to_idx = word_to_idx
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        # 文本转序列
        words = jieba.cut(text)
        sequence = []
        for word in words:
            if word in self.word_to_idx:
                sequence.append(self.word_to_idx[word])
            else:
                sequence.append(0)  # 未知词
        
        # 填充或截断
        if len(sequence) > self.max_length:
            sequence = sequence[:self.max_length]
        else:
            sequence = sequence + [0] * (self.max_length - len(sequence))
        
        return torch.LongTensor(sequence), torch.LongTensor([label])


def build_vocab(texts, min_freq=2):
    """构建词汇表"""
    word_counter = Counter()
    for text in texts:
        words = jieba.cut(text)
        word_counter.update(words)
    
    # 过滤低频词
    vocab = {word: count for word, count in word_counter.items() if count >= min_freq}
    word_to_idx = {word: idx + 1 for idx, word in enumerate(vocab.keys())}
    word_to_idx['<PAD>'] = 0  # 填充符
    word_to_idx['<UNK>'] = len(word_to_idx)  # 未知词
    
    return word_to_idx


def train_model(train_texts, train_labels, val_texts=None, val_labels=None, 
                epochs=10, batch_size=32, learning_rate=0.001):
    """训练模型"""
    print("构建词汇表...")
    word_to_idx = build_vocab(train_texts)
    vocab_size = len(word_to_idx)
    print(f"词汇表大小: {vocab_size}")
    
    # 创建数据集
    train_dataset = SentimentDataset(train_texts, train_labels, word_to_idx)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    val_loader = None
    if val_texts and val_labels:
        val_dataset = SentimentDataset(val_texts, val_labels, word_to_idx)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # 创建模型
    model = SentimentLSTM(vocab_size)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    # 训练
    print("开始训练...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for sequences, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(sequences)
            loss = criterion(outputs, labels.squeeze())
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels.squeeze()).sum().item()
        
        accuracy = 100 * correct / total
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
        
        # 验证
        if val_loader:
            model.eval()
            val_correct = 0
            val_total = 0
            with torch.no_grad():
                for sequences, labels in val_loader:
                    outputs = model(sequences)
                    _, predicted = torch.max(outputs.data, 1)
                    val_total += labels.size(0)
                    val_correct += (predicted == labels.squeeze()).sum().item()
            
            val_accuracy = 100 * val_correct / val_total
            print(f"验证准确率: {val_accuracy:.2f}%")
    
    # 保存模型和词汇表
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'model_sentiment')
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'lstm_sentiment.pt')
    vocab_path = os.path.join(model_dir, 'vocab.pkl')
    
    torch.save(model.state_dict(), model_path)
    with open(vocab_path, 'wb') as f:
        pickle.dump({'word_to_idx': word_to_idx}, f)
    
    print(f"模型已保存到: {model_path}")
    print(f"词汇表已保存到: {vocab_path}")
    
    return model, word_to_idx


if __name__ == '__main__':
    # 示例：使用示例数据训练
    # 实际使用时，应该从数据库或文件中加载真实的评论数据
    
    # 示例正面评论
    positive_texts = [
        "这个商品质量很好，非常满意！",
        "物流很快，包装也很好，推荐购买！",
        "物美价廉，值得推荐！",
        "五星好评，非常棒！",
        "质量不错，服务也很好！"
    ]
    
    # 示例负面评论
    negative_texts = [
        "质量很差，不推荐购买",
        "物流太慢，包装也破了",
        "商品和描述不符，很失望",
        "服务态度很差，差评",
        "质量有问题，后悔购买"
    ]
    
    train_texts = positive_texts + negative_texts
    train_labels = [1] * len(positive_texts) + [0] * len(negative_texts)
    
    print("注意：这只是示例数据，实际训练需要大量真实数据")
    print("训练模型...")
    train_model(train_texts, train_labels, epochs=5)

