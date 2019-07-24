> **全球首个临床级病理 AI 系统源码及复现。**

- **介绍**：[首个临床级病理AI诞生，4万余真实世界病理切片准确率超98%，用于筛查可减少医生75%工作量](https://mp.weixin.qq.com/s/I1mSPWuvSikE-ltS63PK4Q)
- **官方 Github**：https://github.com/MSKCC-Computational-Pathology/MIL-nature-medicine-2019

****

> **个人新增部分**
1. 数据集下载。自己申请的，可直接使用，`50G` 左右，下载脚本见 `dataset/download_dataset.py`
2. 数据集准备。官方接口需要指定格式，参考 `code/README.md`。这里我自己写了一个脚本，见 `code/dataParser.py`，改一下相关路径就好。
3. 训练及测试。将官方代码改成单机数据并行训练，加速训练，单 `GPU` 也无需更改代码。具体运行命令，参考 `code/README.md`

****

> **原理图贴一张**

![](doc/images/架构.png)