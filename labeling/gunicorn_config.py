#####################
###gunicorn配置文件###
####################

# 监听内网端口
bind = '0.0.0.0:9090'

# 并行工作进程数
workers = 1

# 指定每个工作者的线程数
threads = 1

# 超时时间，单位为s
timeout = 120

worker_class = 'gevent'

daemon = False

# 工作模式协程
worker_class = 'uvicorn.workers.UvicornWorker'

# 查看系统当前各进程信息
# pstree -ap|grep gunicorn

# 杀掉进程
# kill -9 <PID>