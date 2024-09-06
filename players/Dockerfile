# Use the official Python 3.10 image as the base
FROM python:3.10-slim

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies, OpenJDK 17, and Android SDK dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    curl \
    lzma \
    zip \
    zlib1g-dev \
    libssl-dev \
    libffi-dev \
    libsqlite3-dev \
    libgmp-dev \
    libncurses5-dev \
    libtool \
    libltdl-dev \
    libopenblas-dev \
    openjdk-17-jdk \
    unzip \
    wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME to use OpenJDK 17
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Install Buildozer and Cython
RUN pip3 install --upgrade pip && pip3 install buildozer cython python-for-android

# Download and install the Android SDK command-line tools
RUN mkdir -p /usr/src/android-sdk/cmdline-tools && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip -O cmdline-tools.zip && \
    unzip cmdline-tools.zip -d /usr/src/android-sdk/cmdline-tools && \
    mv /usr/src/android-sdk/cmdline-tools/cmdline-tools /usr/src/android-sdk/cmdline-tools/latest && \
    rm cmdline-tools.zip

# Set ANDROID_HOME environment variable and add SDK tools to PATH
ENV ANDROID_HOME=/usr/src/android-sdk
ENV PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH

# Install Android SDK components (platform-tools and Android API 31)
RUN yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "platforms;android-31"

# Expose the port the app runs on
EXPOSE 8000

# Define the default command to run when starting the container
CMD ["bash"]
