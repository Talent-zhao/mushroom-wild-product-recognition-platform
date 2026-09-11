# LSTM情感分析模块使用说明

## 功能概述

本模块实现了基于LSTM的评论情感分析功能，可以自动识别评论的正负面评价。

## 安装依赖

```bash
pip install jieba numpy
# 可选：如果需要使用LSTM模型（需要GPU支持）
pip install torch torchvision
```

## 使用方法

### 1. 基本使用

```python
from sentiment_analysis import analyze_sentiment

# 分析文本情感
result = analyze_sentiment("这个商品质量很好，非常满意！")
print(result)
# 输出: {'sentiment': 'positive', 'confidence': 0.85, ...}
```

### 2. 在Django视图中使用

情感分析已经集成到评论功能中，当用户提交评论时会自动进行情感分析。

### 3. 训练自己的模型（可选）

如果需要训练自己的LSTM模型：

```python
from sentiment_analysis.train_model import train_model

# 准备训练数据
train_texts = ["正面评论1", "正面评论2", ...]
train_labels = [1, 1, ...]  # 1表示正面，0表示负面

# 训练模型
train_model(train_texts, train_labels, epochs=10)
```

## 工作原理

1. **LSTM模型**：若已安装 PyTorch 且存在训练好的模型，优先使用 LSTM 进行预测。
2. **规则增强方法**（无模型时的默认方案）：
   - **加权情感词典**：强/一般正面词与强/一般负面词分别赋予 1.2 / 0.9 权重。
   - **否定处理**：前 1～2 个词内出现否定词（不、没、并不、并不是、也不是等）时翻转该情感词极性。
   - **双重否定**：如「并不是不好」会识别为正面。
   - **程度副词**：很/非常/特别等强化词使权重 ×1.3，有点/稍微/一般等减弱词 ×0.65。
   - **得分归一化**：加权得分经 sigmoid 映射为 [0,1] 正/负概率，再判定 positive / negative / neutral 及置信度。

## 模型文件位置

- 模型文件：`model_sentiment/lstm_sentiment.pt`
- 词汇表：`model_sentiment/vocab.pkl`

## 数据库迁移

添加情感分析字段后，需要执行数据库迁移：

```bash
python manage.py makemigrations
python manage.py migrate
```

## 注意事项

1. 首次使用时会自动创建默认词汇表
2. 如果没有训练好的模型，系统会自动使用基于规则的方法
3. 建议使用jieba分词库以获得更好的中文分词效果

