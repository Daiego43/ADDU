def create_user(name, uid=1000):
    snippet = f"""
ARG USER={name}
ARG UID={uid}
ARG GID=$UID
RUN groupadd --gid $GID $USER && \\
    useradd -m -s /bin/bash --uid $UID --gid $GID $USER && \\
    echo "$USER:$USER" | chpasswd && \\
    usermod -aG sudo $USER && \\
    echo "$USER ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER 
RUN mkdir -p /home/$USER/share
    """
    return snippet


def source_ros_in_user(user, ros_version):
    snippet = f"""
RUN echo "source /opt/ros/{ros_version}/setup.bash" >> /home/{user}/.bashrc
RUN echo "source /home/{user}/share/ros_ws/install/setup.bash" >> /home/{user}/.bashrc
    """
    if ros_version == "noetic":
        snippet = f"""
RUN echo "source /opt/ros/{ros_version}/setup.bash" >> /home/{user}/.bashrc
RUN echo "source /home/{user}/share/ros_ws/devel/setup.bash" >> /home/{user}/.bashrc
"""
    return snippet


def install_packages(packages_list):
    snippet = f"""
RUN apt-get update && \\
    apt-get install -y \\
"""
    for pkg in packages_list:
        if packages_list[-1] == pkg:
            snippet += f"    {pkg}"
        else:
            snippet += f"    {pkg} \\\n"
    return snippet


def grafical_support(display=":0"):
    snippet = f"""
ENV DISPLAY {display}
VOLUME /tmp/.X11-unix:/tmp/.X11-unix:rw
RUN apt-get install -y \\
    libx11-6 \\
    libxext-dev \\
    libxrender-dev \\
    libxtst6 \\
    x11-apps \\
    x11-utils \\
    libgl1-mesa-glx \\
    libgl1-mesa-dri \\
    libgtk2.0-0 \\
    libgtk-3-0\n
    """
    return snippet


def share_devices():
    snippet = f"""
VOLUME /dev:/dev\n
    """
    return snippet
