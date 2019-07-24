**参考**

- https://mp.weixin.qq.com/s/I1mSPWuvSikE-ltS63PK4Q
- https://github.com/MSKCC-Computational-Pathology/MIL-nature-medicine-2019

****

![架构](images/架构.png)

# MIL

## 网络等定义

- `ResNet34` —— 最后一层改为二分类的全连接层
- `Criterion` —— 加权的 `CrossEntropyLoss`
- `optimizer` —— `Adam`

## 数据处理 MILdataset

### 初始化

> **以下 `slide` 即样本，表示整张病理图；`patch` 为一个样本内的切片。**
>
> **主要将所有样本的 `patch` 展开成一个 `vector` 进行存放**

- `slides`：`opslide` 打开的样本列表，长度为样本数

  ```shell
  [item1, item2,...itemn]
  ```

- `slidenames`：样本路径列表

- `targets`：样本的标记，0 正常，1 不正常

- `grid`：每个样本对应的 `patch` 坐标。长度为样本数 * 对应样本的 `patch` 数

  ```shell
  [(x,y), (),...,()]
  ```

- `slideIDX`：`patch` 对应的索引列表

  ```shell
  [0,0,...0, 1,1,...1,......n,n,...]
  ```

- `mode`：样本类别

- `mult`：`WSI` 缩放倍数，用于多尺度

- `size`：`patch` 尺寸，`224 * mult`，默认为 `1`

- `level`：`WSI` 分辨率等级，默认为 `0`，表示最高

- `t_data`：每个样本对应的非正常概率最大的 `patch` 列表，每个元素为一个 `tuple`，分别为 `slideIDX` 索引，`grid` 坐标，目标类别

### 网络输入

#### mode == 1

从对应样本中读取对应的 `patch`，并 `resize` 成 `224`，以及 `transform`。

#### mode == 2

依据 `t_data` 获取对应 `patch`，并 `resize` 成 `224`，以及 `transform`。

## 训练过程（every epoch）

### 训练（every epoch）

1. 在 `mode == 1` 下，对所有的 `patch` 进行推理，并保存所有 `patch` 的不正常的概率，得到列表 `probs`
2. 按照先 `slideIDX` ，再 `probs` 的顺序（降序），分别对 `slideIDX` 和 `probs` 进行排序。
3. 得到每个样本中，非正常概率最大的 `k` 个 `patch`，并构成列表 `t_data`
4. 在 `mode == 2` 下，从 `t_data` 列表中获取数据进行训练学习。

### 验证（指定 epoch 间隔）

1. 在 `mode == 1` 下，对所有的 `patch` 进行推理，并保存所有 `patch` 的不正常的概率，得到列表 `probs`
2. 按照先 `slideIDX` ，再 `probs` 的顺序（降序），分别对 `slideIDX` 和 `probs` 进行排序。
3. 得到每个样本中，非正常概率最大的 `k` 个，并构成列表 `maxs`
4. 以 `0.5` 为阈值，判定每个样本的预测结果，并计算误差

# RNN

## 网络等定义

### 模型

- **Encoder**： `resnet34` 网络修改，固定参数。应该是使用上一步中的 `MIL`

- **RNN**：单层 `RNN`

  ```python
      def forward(self, input, state):
          input = self.fc1(input)
          state = self.fc2(state)
          state = self.activation(state+input)
          output = self.fc3(state)
          return output, state
  ```

### 其他

- `Criterion` —— 加权的 `CrossEntropyLoss`
- `optimizer` —— `SGD`

## 数据准备 rnndata

### 初始化

- `slides`：`opslide` 打开的样本列表，长度为样本数

- `slidenames`：样本路径列表

- `targets`：样本的标记，0 正常，1 不正常

- `grid`：列表，每个元素对应一个样本，同样为一个列表。子列表的表示该样本中的 `patch` 坐标

  ```shell
  grid = [
          [(x1_1, y1_1),
  	 (x1_2, y1_2),
  	 (x1_3, y1_3)],
  	[(x2_1, y2_1),
  	 (x2_2, y2_2),
  	 (x2_3, y2_3),
  	 (x2_4, y2_4)],
  ]
  ```

- `mult`：`WSI` 缩放倍数，用于多尺度

- `size`：`patch` 尺寸，`224 * mult`，默认为 `1`

- `level`：`WSI` 分辨率等级，默认为 `0`，表示最高

- `s`：`RNN` 步长，即每个样本考虑的 `top-k` 个 `patch`

### 网络输入

1. 获取某一样本，并以随机顺序读取指定数目（默认为 `10`）的 `patch`，其 `target` 为对应 `slide` 的 `target`。以此组成一个 `RNN` 的输入

## 训练过程（every epoch）

### train(every epoch)

1. 获取输入
2. 初始化 `hidden state` 为 `0`
3. 使用 `RNN` 进行推理，`timestep = 10`，最后一个时间步得到输出概率，表示该样本（`slide`）非正常的概率。
4. 计算 `loss`，并进行 `bp`

### Test(指定 epoch 间隔)

与 `Train` 一样，只是无需 `bp`。