# -*- coding: utf-8 -*-
"""
LSTM情感分析模型（规则增强版：加权词典 + 否定 + 程度）
"""
import os
import re
import math
import numpy as np
from collections import Counter
import pickle

# 可选导入jieba
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    print("警告: jieba未安装，将使用简单字符分割")

# 如果没有安装torch，使用基于规则的方法
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    nn = None
    TORCH_AVAILABLE = False
    print("警告: PyTorch未安装，将使用基于规则的情感分析")


if TORCH_AVAILABLE:
    class SentimentLSTM(nn.Module):
        """LSTM情感分析模型"""
        def __init__(self, vocab_size, embedding_dim=128, hidden_dim=256, num_layers=2, num_classes=2):
            super(SentimentLSTM, self).__init__()
            self.embedding = nn.Embedding(vocab_size, embedding_dim)
            self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True, dropout=0.3)
            self.fc = nn.Linear(hidden_dim, num_classes)
            self.dropout = nn.Dropout(0.3)
        
        def forward(self, x):
            embedded = self.embedding(x)
            lstm_out, _ = self.lstm(embedded)
            last_hidden = lstm_out[:, -1, :]
            output = self.dropout(last_hidden)
            output = self.fc(output)
            return output
else:
    SentimentLSTM = None


class SentimentAnalyzer:
    """情感分析器"""
    def __init__(self, model_path=None, vocab_path=None, max_length=100):
        self.max_length = max_length
        self.model = None
        self.vocab = {}
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.model_path = model_path
        self.vocab_path = vocab_path
        
        # 加载词汇表
        if vocab_path and os.path.exists(vocab_path):
            self.load_vocab(vocab_path)
        else:
            # 使用默认词汇表（基于常见中文情感词）
            self._build_default_vocab()
        
        # 加载模型
        if TORCH_AVAILABLE and model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def _build_default_vocab(self):
        """构建默认词汇表（与规则词典一致，便于后续训练）"""
        lex = self._get_rule_lexicon()
        positive_words = list(lex['pos_strong'] | lex['pos_normal'])
        negative_words = list(lex['neg_strong'] | lex['neg_normal'])
        all_words = list(dict.fromkeys(positive_words + negative_words))
        common_words = ['的', '了', '是', '我', '你', '他', '她', '这', '那', '商品',
                       '质量', '服务', '价格', '物流', '包装', '收到', '使用', '感觉', '东西', '产品']
        for w in common_words:
            if w not in all_words:
                all_words.append(w)
        for idx, word in enumerate(all_words):
            self.word_to_idx[word] = idx
            self.idx_to_word[idx] = word
        self.vocab_size = len(self.word_to_idx)
    
    def load_vocab(self, vocab_path):
        """加载词汇表"""
        try:
            with open(vocab_path, 'rb') as f:
                vocab_data = pickle.load(f)
                self.word_to_idx = vocab_data.get('word_to_idx', {})
                self.idx_to_word = vocab_data.get('idx_to_word', {})
                self.vocab_size = len(self.word_to_idx)
        except Exception as e:
            print(f"加载词汇表失败: {e}")
            self._build_default_vocab()
    
    def save_vocab(self, vocab_path):
        """保存词汇表"""
        vocab_data = {
            'word_to_idx': self.word_to_idx,
            'idx_to_word': self.idx_to_word
        }
        with open(vocab_path, 'wb') as f:
            pickle.dump(vocab_data, f)
    
    def load_model(self, model_path):
        """加载训练好的模型"""
        if not TORCH_AVAILABLE or SentimentLSTM is None:
            return False
        
        try:
            import torch
            self.model = SentimentLSTM(self.vocab_size)
            self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
            self.model.eval()
            return True
        except Exception as e:
            print(f"加载模型失败: {e}")
            return False
    
    def preprocess_text(self, text):
        """文本预处理：去噪、归一化、分词"""
        if not text:
            return []
        text = str(text).strip()
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 合并重复标点与空格，便于情感强度判断
        text = re.sub(r'[!！]{2,}', '！', text)
        text = re.sub(r'[?？]{2,}', '？', text)
        text = re.sub(r'\s+', ' ', text)
        # 保留中文、英文、数字（保留空格供分词）
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
        text = text.strip()
        if not text:
            return []
        # 分词
        if JIEBA_AVAILABLE:
            try:
                words = list(jieba.cut(text))
                words = [w.strip() for w in words if w.strip()]
            except Exception:
                words = [c for c in text if c.strip()]
        else:
            words = [c for c in text if c.strip()]
        return words
    
    def text_to_sequence(self, text):
        """将文本转换为序列"""
        words = self.preprocess_text(text)
        sequence = []
        for word in words:
            if word in self.word_to_idx:
                sequence.append(self.word_to_idx[word])
            else:
                # 未知词用0表示
                sequence.append(0)
        
        # 填充或截断到固定长度
        if len(sequence) > self.max_length:
            sequence = sequence[:self.max_length]
        else:
            sequence = sequence + [0] * (self.max_length - len(sequence))
        
        return np.array(sequence)
    
    def predict_with_model(self, text):
        """使用LSTM模型预测"""
        if not TORCH_AVAILABLE or self.model is None:
            return None
        
        try:
            import torch
            sequence = self.text_to_sequence(text)
            sequence_tensor = torch.LongTensor([sequence])
            
            with torch.no_grad():
                output = self.model(sequence_tensor)
                probabilities = torch.softmax(output, dim=1)
                predicted = torch.argmax(probabilities, dim=1).item()
                confidence = probabilities[0][predicted].item()
            
            # 0: 负面, 1: 正面
            sentiment = 'positive' if predicted == 1 else 'negative'
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'probability': {
                    'positive': probabilities[0][1].item(),
                    'negative': probabilities[0][0].item()
                }
            }
        except Exception as e:
            print(f"模型预测失败: {e}")
            return None
    
    def _get_rule_lexicon(self):
        """情感词典与否定/程度词（带权重，用于加权打分）"""
        # 强正面词权重 1.2，一般正面 0.9
        positive_strong = {'太好了', '完美', '超值', '物美价廉', '强烈推荐', '极力推荐', '非常满意',
                          '十分满意', '特别满意', '好评如潮', '五星好评', '物超所值', '货真价实',
                          '精工细作', '用心', '良心', '必买', '值得入手', '强烈推荐', '惊喜'}
        positive_normal = {'好', '棒', '赞', '优秀', '满意', '喜欢', '推荐', '不错', '很好',
                          '值得', '好评', '五星', '质量好', '服务好', '速度快', '包装好', '正品',
                          '靠谱', '划算', '实惠', '好用', '点赞', '种草', '回购', '感谢', '表扬',
                          '夸', '支持', '正确', '真实', '有效', '成功', '顺利', '简单', '容易',
                          '快速', '及时', '准确', '完整', '清晰', '新鲜', '干净', '安全', '健康',
                          '优质', '一流', '精品', '好货', '宝贝', '神器', '可以', '行', '佳', '美',
                          '还行', '挺好', '挺好用'}
        # 强负面词权重 1.2，一般负面 0.9
        negative_strong = {'垃圾', '太差', '非常失望', '千万别买', '强烈不推荐', '假货', '骗人',
                          '黑心', '坑人', '踩雷', '差评满天', '货不对板', '以次充好', '偷工减料',
                          '粗制滥造', '敷衍', '不负责任', '骗子', '废品', '烂货', '废物', '绝望'}
        negative_normal = {'差', '坏', '烂', '失望', '不好', '糟糕', '差评', '不值', '后悔',
                          '质量差', '服务差', '不推荐', '破损', '慢', '贵', '退货', '退款',
                          '假', '坑', '拔草', '吐槽', '骂', '批评', '抱怨', '投诉', '反对',
                          '错误', '虚假', '无效', '失败', '困难', '缓慢', '拖延', '残缺',
                          '模糊', '陈旧', '脏乱', '危险', '有害', '劣质', '次品', '烂货'}
        # 否定词（前 1～2 个词内出现则翻转情感）
        negation_words = {'不', '没', '非', '无', '未', '别', '莫', '勿', '难以', '从不', '绝不',
                          '并不', '毫不', '一点都不', '一点也不', '没有', '没啥', '没怎么', '都不', '也不',
                          '并不是', '也不是'}  # 双重否定语境
        # 程度副词：强化（乘 1.3）、减弱（乘 0.65）
        degree_strong = {'很', '非常', '特别', '太', '极', '十分', '相当', '格外', '极其', '超级', '真', '挺'}
        degree_weak = {'有点', '稍微', '略', '比较', '还算', '一般', '马马虎虎'}
        return {
            'pos_strong': positive_strong,
            'pos_normal': positive_normal,
            'neg_strong': negative_strong,
            'neg_normal': negative_normal,
            'negation': negation_words,
            'degree_strong': degree_strong,
            'degree_weak': degree_weak,
        }

    def predict_with_rules(self, text):
        """基于规则的情感分析（加权 + 否定 + 程度，提高准确度）"""
        lex = self._get_rule_lexicon()
        words = self.preprocess_text(text)
        if not words:
            return {'sentiment': 'neutral', 'confidence': 0.5, 'probability': {'positive': 0.5, 'negative': 0.5}}

        # 加权情感得分，正为正、负为负
        score = 0.0
        neg_window = 2  # 否定词向前看 2 个词

        for i, word in enumerate(words):
            # 检查否定：前 1～neg_window 位是否有否定词
            has_negation = False
            for j in range(1, neg_window + 1):
                if i - j < 0:
                    break
                prev = words[i - j]
                if prev in lex['negation']:
                    has_negation = True
                    break
                # 双字否定如 "一点 不"、"并不"
                if i - j - 1 >= 0:
                    two = words[i - j - 1] + words[i - j]
                    if two in lex['negation']:
                        has_negation = True
                        break

            # 双重否定：如 "并不是 不好" -> 正面
            if has_negation and i >= 2 and word in (lex['pos_strong'] | lex['pos_normal']):
                if words[i - 2] in ('并', '也', '都') or (i >= 3 and words[i - 3] + words[i - 2] in ('并不是', '也不是')):
                    has_negation = False

            # 程度系数
            degree = 1.0
            if i > 0:
                if words[i - 1] in lex['degree_strong']:
                    degree = 1.3
                elif words[i - 1] in lex['degree_weak']:
                    degree = 0.65

            # 正面词
            if word in lex['pos_strong']:
                s = 1.2 * degree
                score += -s if has_negation else s
            elif word in lex['pos_normal']:
                s = 0.9 * degree
                score += -s if has_negation else s
            # 负面词
            elif word in lex['neg_strong']:
                s = 1.2 * degree
                score += s if has_negation else -s
            elif word in lex['neg_normal']:
                s = 0.9 * degree
                score += s if has_negation else -s

        # 归一化到 [0, 1]，sigmoid 映射得到正/负概率
        cap = 5.0  # 得分绝对值上限
        raw = max(-cap, min(cap, score))
        # sigmoid 形式：prob_positive = 1/(1+exp(-raw))，再转为 confidence
        prob_positive = 1.0 / (1.0 + math.exp(-raw))
        prob_negative = 1.0 - prob_positive

        if prob_positive >= 0.6:
            sentiment = 'positive'
            confidence = min(0.98, 0.5 + (prob_positive - 0.5))
        elif prob_positive <= 0.4:
            sentiment = 'negative'
            confidence = min(0.98, 0.5 + (prob_negative - 0.5))
        else:
            sentiment = 'neutral'
            confidence = 0.5

        return {
            'sentiment': sentiment,
            'confidence': round(confidence, 4),
            'probability': {
                'positive': round(prob_positive, 4),
                'negative': round(prob_negative, 4)
            }
        }
    
    def predict(self, text):
        """预测文本情感"""
        if not text or not text.strip():
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'probability': {'positive': 0.5, 'negative': 0.5}
            }
        
        # 优先使用模型预测
        result = self.predict_with_model(text)
        if result is None:
            # 如果模型不可用，使用规则方法
            result = self.predict_with_rules(text)
        
        return result


# 全局情感分析器实例
_analyzer = None

def get_sentiment_analyzer():
    """获取情感分析器单例"""
    global _analyzer
    if _analyzer is None:
        # 模型路径（如果存在）
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, 'model_sentiment', 'lstm_sentiment.pt')
        vocab_path = os.path.join(base_dir, 'model_sentiment', 'vocab.pkl')
        
        # 确保目录存在
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        _analyzer = SentimentAnalyzer(model_path=model_path, vocab_path=vocab_path)
    return _analyzer


def analyze_sentiment(text):
    """分析文本情感（便捷函数）"""
    analyzer = get_sentiment_analyzer()
    return analyzer.predict(text)

