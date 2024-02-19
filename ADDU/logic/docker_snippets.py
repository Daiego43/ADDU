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
RUN mkdir -p /home/$USER/shared
    """
    return snippet


def source_ros_in_user(user, ros_version):
    snippet = f"""
RUN echo "source /opt/ros/{ros_version}/setup.bash" >> /home/{user}/.bashrc
RUN echo "source /home/{user}/shared/ros_ws/install/setup.bash" >> /home/{user}/.bashrc
    """
    if ros_version == "noetic":
        snippet = f"""
RUN echo "source /opt/ros/{ros_version}/setup.bash" >> /home/{user}/.bashrc
RUN echo "source /home/{user}/shared/ros_ws/devel/setup.bash" >> /home/{user}/.bashrc
"""
    return snippet


def install_editor(editor):
    if editor == "vscode":
        snippet = f"""
RUN wget -O vscode.tar.gz https://update.code.visualstudio.com/latest/linux-x64/stable
RUN tar -xvf vscode.tar.gz -C /opt/
ENV PATH="/opt/VSCode-linux-x64:${{PATH}}"
    """
    if editor == "pycharm-professional":
        snippet = f"""
RUN wget -q "https://download.jetbrains.com/python/pycharm-professional-2023.3.3.tar.gz"
RUN tar -xvf pycharm-professional-2023.3.3.tar.gz -C /opt/
ENV PATH="/opt/pycharm-2023.3.3/bin:${{PATH}}"
"""
    if editor == "pycharm-community":
        snippet = f"""
RUN wget -q https://download.jetbrains.com/python/pycharm-community-2023.3.3.tar.gz
RUN tar -xvf pycharm-community-2023.3.3.tar.gz -C /opt/
ENV PATH="/opt/pycharm-community-2023.3.3/bin:${{PATH}}"
"""
    return snippet


def grafical_support():
    snippet = f"""
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
