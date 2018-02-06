# pet-chain-buyer
百度莱茨狗抢购，多线程，Google tesseract-ocr识别验证码和手动输入验证码

参考https://github.com/yanwii/pet-chain项目

# 使用方法
- 配置好需要的依赖库
- 用自己的headers替换config目录下headers.txt文件内容
- 编辑config/config.ini文件配置价格和是否自动填写验证码

### 1.手动输入验证码
先在命令行执行 `python pic.py`，加载验证码，当有新的验证码时会及时刷新
然后执行`python pet-chain.py`
### 2.自动输入验证码
直接执行`python pet-chain.py`
现在自动输入验证码正确率比较低，建议采用第一种方式，后续进行代码优化
