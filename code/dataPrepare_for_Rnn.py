import torch
import torch.nn as nn
import openslide
from collections import OrderedDict
import torchvision.models as models
import torchvision.transforms as transforms
import torch.backends.cudnn as cudnn
import torch.nn.functional as F
import numpy as np
from time import time
import os



# 一些全部变量
model_path = 'output/CNN_checkpoint_best.pth'
batch_size = 256
top_k = 10    # 取 10 块 patch 作为 RNN 输入
patch_size = 224


# 并行模型串行化
def Parallel2Single(origin_state):
    converted = OrderedDict()

    for k, v in origin_state.items():
        name = k[7:]
        converted[name] = v
    return converted


# 读取数据
lib_train = torch.load('output/lib/cnn_train_data_lib.db')
lib_val = torch.load('output/lib/cnn_val_data_lib.db')

# transforms
normalize = transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.1, 0.1, 0.1])
trans = transforms.Compose([transforms.ToTensor(), normalize])

# 加载模型
model = models.resnet34(True)
model.fc = nn.Linear(model.fc.in_features, 2)
model = model.cuda()
ch = torch.load(model_path)
model.load_state_dict(Parallel2Single(ch['state_dict']))
model.eval()
cudnn.benchmark = True


# 处理 train 部分的数据
for i, slide_name in enumerate(lib_train['slides']):
    t0 = time()
    sl = openslide.OpenSlide(slide_name)

    sl_prob = []      # 存储当前 slide 中每个 patch 对应的 prob
    imgs_batch = []   # 存储当前 batch

    # 处理每个 patch
    for j, grid in enumerate(lib_train['grid'][i]):
        imgs_batch.append(trans(sl.read_region(grid, lib_train['level'], (patch_size, patch_size)).convert('RGB')).unsqueeze(0))

        if ((j + 1) == len(lib_train['grid'][i])) or ((j + 1) % batch_size == 0):
            imgs_batch = torch.cat(imgs_batch, 0).cuda()
            output = F.softmax(model(imgs_batch), dim=1).detach()
            sl_prob.extend(output[:, 1].cpu().tolist())
            imgs_batch = []
            print('Processing {} / {} slide, patch {} / {}'.format(i + 1, len(lib_train['slides']), j + 1, len(lib_train['grid'][i])))

    # 提取前 top_k 个 patch
    sl_prob = np.array(sl_prob)
    sorted_index = np.argsort(-sl_prob)

    grid_array = np.array(lib_train['grid'][i])
    lib_train['grid'][i] = grid_array[sorted_index[:top_k]].tolist()

    print('time for slide {} is '.format(i, time() - t0))
torch.save(lib_train, 'output/lib/rnn_train_data_lib.db')


# 处理 val 部分的数据
for i, slide_name in enumerate(lib_val['slides']):
    t0 = time()
    sl = openslide.OpenSlide(slide_name)

    sl_prob = []      # 存储当前 slide 中每个 patch 对应的 prob
    imgs_batch = []   # 存储当前 batch

    # 处理每个 patch
    for j, grid in enumerate(lib_val['grid'][i]):
        imgs_batch.append(trans(sl.read_region(grid, lib_val['level'], (patch_size, patch_size)).convert('RGB')).unsqueeze(0))

        if ((j + 1) == len(lib_val['grid'][i])) or ((j + 1) % batch_size == 0):
            imgs_batch = torch.cat(imgs_batch, 0).cuda()
            output = F.softmax(model(imgs_batch), dim=1).detach()
            sl_prob.extend(output[:, 1].cpu().tolist())
            imgs_batch = []
            print('Processing {} / {} slide, patch {} / {}'.format(i + 1, len(lib_val['slides']), j + 1, len(lib_val['grid'][i])))

    # 提取前 top_k 个 patch
    sl_prob = np.array(sl_prob)
    sorted_index = np.argsort(-sl_prob)

    grid_array = np.array(lib_val['grid'][i])
    lib_val['grid'][i] = grid_array[sorted_index[:top_k]].tolist()

    print('time for slide {} is '.format(i, time() - t0))
torch.save(lib_val, 'output/lib/rnn_val_data_lib.db')