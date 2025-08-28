FROM ubuntu:24.04

# 设置时区避免 tzdata 卡住
ENV DEBIAN_FRONTEND=noninteractive TZ=Asia/Shanghai

# 更新软件源并安装 g++, python3, openjdk
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    python3 \
    openjdk-17-jdk \
    time \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 默认命令（判题时会被 docker run 覆盖）
CMD ["/bin/bash"]