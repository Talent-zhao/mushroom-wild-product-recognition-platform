import os
from sklearn.model_selection import train_test_split
from shutil import copyfile
from tqdm import tqdm

def split_datasets(dataset_root,train_dir,test_dir):
    # 获取所有类别文件夹
    categories = os.listdir(dataset_root)

    # 遍历每个类别文件夹
    for category in tqdm(categories):

        category_path = os.path.join(dataset_root, category)

        # 获取该类别下的所有图像文件
        images = [f for f in os.listdir(category_path) if f.endswith('.jpg') or f.endswith('.png')]

        # 划分训练集和测试集
        train_images, test_images = train_test_split(images, test_size=0.2, random_state=42)

        # 创建保存训练集和测试集的目录
        os.makedirs(os.path.join(train_dir, category), exist_ok=True)
        os.makedirs(os.path.join(test_dir, category), exist_ok=True)

        # 复制图像到对应目录
        for image in train_images:
            src_path = os.path.join(category_path, image)
            dst_path = os.path.join(train_dir, category, image)
            copyfile(src_path, dst_path)

        for image in test_images:
            src_path = os.path.join(category_path, image)
            dst_path = os.path.join(test_dir, category, image)
            copyfile(src_path, dst_path)


# 设置数据集根目录
dataset_root = r'data/蘑菇是否有毒'
# 设置保存划分结果的目录
split_path = r'data/蘑菇是否有毒训练数据集'
train_dir = os.path.join(split_path,'train')
test_dir =  os.path.join(split_path,'test')
split_datasets(dataset_root,train_dir,test_dir)