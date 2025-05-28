##############################################
# Created from template ros2.dockerfile.jinja
##############################################

###########################################
# Base image
###########################################
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04 AS base

ENV DEBIAN_FRONTEND=noninteractive

ARG USERNAME=ros2-humble
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd -g $USER_GID $USERNAME \
    && useradd -u $USER_UID -g $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

# Install language
RUN sudo apt-get update && sudo apt-get install -y \
  locales \
  && sudo locale-gen en_US.UTF-8 \
  && sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 \
  && sudo rm -rf /var/lib/apt/lists/*
ENV LANG=en_US.UTF-8

# Install timezone
RUN sudo ln -fs /usr/share/zoneinfo/UTC /etc/localtime \
  && export DEBIAN_FRONTEND=noninteractive \
  && sudo apt-get update \
  && sudo apt-get install -y tzdata \
  && sudo dpkg-reconfigure --frontend noninteractive tzdata \
  && sudo rm -rf /var/lib/apt/lists/*

RUN sudo apt-get update && sudo apt-get -y upgrade \
    && sudo rm -rf /var/lib/apt/lists/*

# Install common programs
RUN sudo apt-get update && sudo apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    lsb-release \
    sudo \
    software-properties-common \
    wget \
    unzip \
    net-tools \
    iproute2 \
    iputils-ping \
    && sudo rm -rf /var/lib/apt/lists/*

# Install ROS2
RUN sudo add-apt-repository universe \
  && sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \
  && sudo echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null \
  && sudo apt-get update && sudo apt-get install -y --no-install-recommends \
    ros-humble-ros-base \
    python3-argcomplete \
  && sudo rm -rf /var/lib/apt/lists/*

################
# Expose the nvidia driver to allow opengl
# Dependencies for glvnd and X11.
################
RUN sudo apt-get update \
 && sudo apt-get install -y -qq --no-install-recommends \
  libglvnd0 \
  libgl1 \
  libglx0 \
  libegl1 \
  libxext6 \
  libx11-6

# Env vars for the nvidia-container-runtime.
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute
ENV QT_X11_NO_MITSHM=1

ENV ROS_DISTRO=humble
ENV AMENT_PREFIX_PATH=/opt/ros/humble
ENV COLCON_PREFIX_PATH=/opt/ros/humble
ENV LD_LIBRARY_PATH=/opt/ros/humble/lib/x86_64-linux-gnu:/opt/ros/humble/lib
ENV PATH=/opt/ros/humble/bin:$PATH
ENV PYTHONPATH=/opt/ros/humble/local/lib/python3.10/dist-packages:/opt/ros/humble/lib/python3.10/site-packages
ENV ROS_PYTHON_VERSION=3
ENV ROS_VERSION=2
ENV ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
ENV DEBIAN_FRONTEND=
###########################################
#  Develop image
###########################################
FROM base AS dev

USER $USERNAME

ENV DEBIAN_FRONTEND=noninteractive
RUN sudo apt-get update && sudo apt-get install -y --no-install-recommends \
  bash-completion \
  build-essential \
  cmake \
  gdb \
  git \
  openssh-client \
  python3-argcomplete \
  python3-pip \
  ros-dev-tools \
  ros-humble-urdf-tutorial \
  ros-humble-ament-* \
  ros-humble-tf-transformations \
  ros-humble-moveit-configs-utils \
  ros-humble-moveit-ros-visualization \
  ros-humble-controller-manager \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui \
  ros-humble-robot-state-publisher \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-moveit-ros-move-group \
  ros-humble-moveit-ros-planning \
  ros-humble-moveit-ros-planning-interface \
  ros-humble-moveit-ros-robot-interaction \
  ros-humble-moveit-ros-occupancy-map-monitor \
  ros-humble-moveit-simple-controller-manager \
  ros-humble-moveit-ros-warehouse \
  ros-humble-moveit-setup-assistant \
  ros-humble-pilz-industrial-motion-planner \
  ros-humble-moveit-planners-chomp \
  ros-humble-moveit-planners-ompl \
  ros-humble-joint-trajectory-controller \
  ros-humble-position-controllers \
  ros-humble-effort-controllers \
  ros-humble-forward-command-controller \
  ros-humble-tf2-tools \
  ros-humble-kdl-parser \
  ros-humble-joint-limits \
  ros-humble-rqt \
  ros-humble-rqt-graph \
  ros-humble-rqt-joint-trajectory-controller \
  ros-humble-rqt-controller-manager \
  ros-humble-rqt-reconfigure \
  ros-humble-rqt-plot \

  vim \
  && sudo rm -rf /var/lib/apt/lists/*


RUN pip3 install websockets transformations

RUN rosdep init || echo "rosdep already initialized"

# Add sudo support for the non-root user
# RUN apt-get update && apt-get install -y sudo \
#   && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME\
#   && chmod 0440 /etc/sudoers.d/$USERNAME \
#   && rm -rf /var/lib/apt/lists/*

# Set up autocompletion for user
RUN sudo apt-get update && sudo apt-get install -y git-core bash-completion \
  && sudo echo "if [ -f /opt/ros/${ROS_DISTRO}/setup.bash ]; then source /opt/ros/${ROS_DISTRO}/setup.bash; fi" >> /home/$USERNAME/.bashrc \
  && sudo echo "if [ -f /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash ]; then source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash; fi" >> /home/$USERNAME/.bashrc \
  && sudo rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=
ENV AMENT_CPPCHECK_ALLOW_SLOW_VERSIONS=1

###########################################
#  Full image
###########################################
FROM dev AS full


ENV DEBIAN_FRONTEND=noninteractive
# Install the full release
RUN sudo apt-get update && sudo apt-get install -y --no-install-recommends \
  ros-humble-desktop \
  && sudo rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=
ENV LD_LIBRARY_PATH=/opt/ros/humble/lib

# necessary for xsens replay
RUN pip3 install pandas openpyxl xacro
RUN pip3 install --upgrade scipy

RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash && sudo apt-get install -y git-lfs

RUN echo "source /opt/ros/humble/setup.bash" >> /home/$USERNAME/.bashrc

###########################################
#  Full+Gazebo image
###########################################
FROM full AS gazebo

ENV DEBIAN_FRONTEND=noninteractive
# Install gazebo
RUN sudo wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null \
  && sudo apt-get update && sudo apt-get install -q -y --no-install-recommends \
    ros-humble-ros-gz \
  && sudo rm -rf /var/lib/apt/lists/*


ENV DEBIAN_FRONTEND=
