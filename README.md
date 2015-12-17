# RootZoneCollector/根区采集模块

This tool used to get root zone information periodically from IANA   

## 概述
-----
根区采集模块工具，用于采集IANA发布的根区数据，并对采集的数据采用PGP校验，本工具实现了以下功能:   

1. **下载进程**的下载动作由Python内置的Schedule工具进行调度，不进行下载任务时，下载进程Sleep
2. 下载完成后，**验证进程**对**下载进程**得到的数据进行真实性和完整性校验，校验工具采用开源的GunPG软件
3. **验证进程**完成后，由**迁移进程**将通过校验的文件迁移至目标文件夹   
	   
## 文件及目录列表
-----
### 目录
   
   
   
   
+ /Old_Code   
	存储重要的历史版本代码片段
+ /script   
	与前端网页的交互脚本都在这里
+ /Test_Code   
	测试功能使用的用例代码
   
### 文件
   
+ /ZoneCollector.py   
	主功能模块，实现了数据下载、数据校验、文件迁移的功能
+ /Configuration.in   
	配置文件，主功能模块启动前需要的参数都在这里了
+ /PGPVarifyPublicKey.pub   
	校验数字签名时使用的公钥文件(文件来源自MIT公钥数据库)
+ /root.zone/root.zone.sig   
	测试数据文件和测试签名文件，正式版本会将上述测试文件一出
   
## 使用方法
---
	python ZoneCollect.py -c /.../Configuration.in

	python ZoneCollect.py -b
	
	python ZoneCollect.py -p 3600

