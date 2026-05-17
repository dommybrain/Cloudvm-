FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

RUN apt-get update && apt-get install -y \
    python3.10 python3.10-dev python3-pip \
    python3.14 python3.14-dev \
    git zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev \
    libncursesw5-dev cmake \
    libffi-dev libssl-dev \
    build-essential wget curl \
    && rm -rf /var/lib/apt/lists/*

# تثبيت legacy-cgi لـ Python 3.14
RUN pip3 install legacy-cgi

# تثبيت Cython وإصلاح _tempita.py
RUN pip3 install cython==0.29.36 buildozer==1.5.0 && \
    find / -name "_tempita.py" -path "*/Cython/*" 2>/dev/null | \
    xargs sed -i 's/^import cgi$/try:\n    import cgi\nexcept ImportError:\n    import html as cgi/' 2>/dev/null || true

RUN mkdir -p $ANDROID_HOME/cmdline-tools && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip && \
    unzip -q commandlinetools-linux-11076708_latest.zip -d $ANDROID_HOME/cmdline-tools && \
    mv $ANDROID_HOME/cmdline-tools/cmdline-tools $ANDROID_HOME/cmdline-tools/latest && \
    rm commandlinetools-linux-11076708_latest.zip

RUN yes | sdkmanager --licenses && \
    sdkmanager "build-tools;34.0.0" "platforms;android-33" "platform-tools"

# إصلاح _tempita.py في كل بيئة مؤقتة عند البناء
RUN echo '#!/bin/bash\n\
find /tmp -name "_tempita.py" -path "*/Cython/*" 2>/dev/null | \
xargs -I{} sed -i "s/^import cgi$/import sys\ntry:\n    import cgi\nexcept ImportError:\n    pass/" {} 2>/dev/null || true\n\
exec buildozer "$@"' > /usr/local/bin/buildozer-wrapper && \
    chmod +x /usr/local/bin/buildozer-wrapper

WORKDIR /app
