# WritePoem
**自动作诗系统**

=== 环境准备 ===

* Python 2.7
* Flask
* jieba
* sklearn

=== 使用方法 ===

第一次运行，则需要安装相关的库及生成初始数据：
* python preprocess.py
* python get_collocations.py
* python get_topic.py
* python get_start_words.py

以后只需要输入以下代码即可运行：
* python index.py

注：已在data文件夹中生成初始数据



本项目在[poem_generator](https://github.com/lijiancheng0614/poem_generator)的基础上修改而成