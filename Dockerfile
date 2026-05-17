FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

RUN apt-get update && apt-get install -y \
    python3.10 python3.10-dev python3-pip \
    git zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev \
    libncursesw5-dev cmake \
    libffi-dev libssl-dev \
    build-essential wget curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install legacy-cgi cython==0.29.36 buildozer==1.5.0

RUN mkdir -p $ANDROID_HOME/cmdline-tools && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip && \
    unzip -q commandlinetools-linux-11076708_latest.zip -d $ANDROID_HOME/cmdline-tools && \
    mv $ANDROID_HOME/cmdline-tools/cmdline-tools $ANDROID_HOME/cmdline-tools/latest && \
    rm commandlinetools-linux-11076708_latest.zip

RUN yes | sdkmanager --licenses && \
    sdkmanager "build-tools;34.0.0" "platforms;android-33" "platform-tools"

WORKDIR /app
