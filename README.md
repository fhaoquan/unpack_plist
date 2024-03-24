代码使用python3

1、安装依赖
1、方法一：使用pip命令在线安装。

输入以下命令可以直接安装：

pip install PyQt5
由于安装默认使用国外的镜像，可能因为网络问题会导致下载慢或者失败的现象。所以我们可以使用国内的镜像，比如豆瓣提供的镜像。只需要加上“-i https://pypi.douban.com/simple”参数。

pip install PyQt5 -i https://pypi.douban.com/simple


python3 -m pip install Pillow
python3 -m pip install PyQt5
或者

pip install -r requirements.txt

2、运行

python3 unpack_plist.py ./test/Sprite.plist 

3、根据界面提示解析
界面:
python3 unpack_plist_ui.py
