FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
# USER root

# 设置工作目录
WORKDIR /app

COPY . /app

CMD ["/bin/bash"]
RUN apt-get update && \
apt-get install --fix-broken -y && \
apt-get install apt-utils -y && \
apt-get install -y --no-install-recommends ffmpeg libsm6 libxext6 libffi-dev python3.8 python3-pip python3-dev build-essential vim telnet iputils-ping curl ca-certificates && \
apt-get clean && \
rm -rf /var/lib/apt/lists/* /etc/systemd/system/timers.target.wants/apt-daily*  &&  \
rm -rf /root/.cache/*

# # 更新软件源列表
# RUN apt-get update

# # 安装必要的工具
# RUN apt-get install -y ffmpeg libsm6 libxext6 \
#     libffi-dev \
#     build-essential \
#     libssl-dev \
#     zlib1g-dev \
#     libncurses5-dev \
#     libncursesw5-dev \
#     libreadline-dev \
#     libsqlite3-dev \
#     libgdbm-dev \
#     libdb5.3-dev \
#     libbz2-dev \
#     libexpat1-dev \
#     liblzma-dev \
#     tk-dev \
#     wget \
#     curl

# # 安装 Python
# RUN wget https://mirrors.huaweicloud.com/python/3.7.9/Python-3.7.9.tgz && \
#     tar xvf Python-3.7.9.tgz && \
#     cd Python-3.7.9 && \
#     ./configure && \
#     make && \
#     make install

# # 更新 pip
# RUN python3.7 -m ensurepip --upgrade

# # 设置默认Python版本
# RUN update-alternatives --install /usr/bin/python python /usr/local/bin/python3.7 1
# RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.7 1
# RUN update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.7 1
# RUN update-alternatives --install /usr/bin/pip3 pip3 /usr/local/bin/pip3.7 1

# # 清理
# RUN rm -rf Python-3.7.9 && rm Python-3.7.9.tgz

# # 验证安装
# RUN python3 --version
# RUN pip3 --version

# COPY codemeter_7.50.5271.500_amd64.deb /codemeter.deb
# CMD ["/bin/bash"]
# RUN apt-get update && \
# apt-get install --fix-broken -y && \
# apt-get install apt-utils -y && \
# apt-get install -y --no-install-recommends ffmpeg libsm6 libxext6 python3 python3-pip vim telnet systemd iputils-ping curl ca-certificates && \
# apt-get clean && \
# rm -rf /var/lib/apt/lists/* /etc/systemd/system/timers.target.wants/apt-daily*  &&  \
# rm -rf /root/.cache/* 

# RUN apt-get update && \
#     apt-get install -y libsndfile1 sox

# 设置工作目录为 /root
# WORKDIR /root

# 复制当前目录下的所有文件到 /root
# COPY . /root

ENV LD_LIBRARY_PATH=/app/tsdk-core/lib/linux/release_x64/:$LD_LIBRARY_PATH

# 安装依赖
# RUN pip3 install --upgrade pip -i https://mirrors.cloud.tencent.com/pypi/simple
RUN pip3 install --no-cache-dir -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple

# 容器对外暴露的端口
EXPOSE 8000

# 启动应用程序
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
