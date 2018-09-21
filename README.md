# iKing tools

本项目包括部分iKing相关的解析脚本等. 并不完善, 水平也堪忧. 凑活吧.

基于Python2.7, 并未测试Python3兼容性

## 依赖组件
Pillow(pip install Pillow)
progressive(pip install progressive)
pefile(pip install pefile)

## 组件安装直接使用
pip install -r requirements.txt

## 文件概要说明
- iking_data.py: 主要是一些数据对象的定义;
- iking_emotions.py: 表情相关的一些定义, 直接执行导出时, 所使用的iking版本为1.3.0.20, 其他版本所读取的表情tables的偏移量等可能会有不同;
- iking_magic.py: 魔法以及状态等的定义, 状态并未解析完全;
- iking_map.py: 关于地图上物体的一些定义和处理逻辑;
- iking_package.py: 主要收发数据包的解析等;
- iking_proxy.py: 代理服务, 主要用来协助解析数据;
- iking_render_map.py: 用来根据产生的地图数据文件来进行地图渲染, 目前渲染时暂不支持1.4.x.x开始使用的png资源, 请预先使用1.3.x.x导出zbm格式资源后进行渲染;
- iking_utils.py: 用到的工具类, 工具函数等;
- thai_keygen.py: 当初泰版zkok的keygen;
- dll_export.py: 从游戏的dll中导出图片资源(主要是地图渲染相关), 导出资源ID以RID开头的zbm资源和bitmap资源, 其中zbm资源会转换为bmp(1.3.x.x)或png(>=1.4.x.x), 以供iking_render_map进行渲染时使用;