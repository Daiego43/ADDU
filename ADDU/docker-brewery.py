import os

import docker

import snippets.docker_snippets as ds

client = docker.APIClient(base_url='unix://var/run/docker.sock')
client.info()


def create_dockerfile(ros_version, user, image, tag, editor="pycharm"):
    with open("Dockerfile", "w") as dockerfile:
        lines = [
            f"FROM {image}:{tag}",
            ds.install_packages(["python3-pip", "wget", "ranger"]),
            ds.create_user(user),
            ds.source_ros_in_user(user, ros_version),
            ds.grafical_support(),
            ds.share_devices(),
            ds.install_code_editor(editor, download=False)
        ]
        dockerfile.writelines(lines)


def create_entrypoint(entrypoint_name, user, shared_volume, tag_name, gpu=False):
    with open(f'{entrypoint_name}.bash', "w") as entrypoint:
        command = f"""
docker run -it --privileged \\
    --user {user} \\
    --workdir /home/{user} \\
    --volume /dev:/dev \\
    --volume {shared_volume}:/home/ros2/ros_ws \\
    --network host \\
    {tag_name} \\
    pycharm.sh
        """
        entrypoint.write(command)


def create_workspace():
    os.system("mkdir -p /home/daiego/workspaces/ros2-humble-ws")


if __name__ == '__main__':
    images = {
        'osrf/ros': [
            "noetic-desktop-full",
            "humble-desktop-full"
        ],
        'ros': [
            "noetic-ros-base",
            "humble-ros-base"
        ]
    }

    try:
        os.chdir("pycharm-ros2")
    except FileNotFoundError:
        os.system("mkdir pycharm-ros2")
        os.chdir("pycharm-ros2")

    image_name = "ros:humble-pycharm-developer"
    create_dockerfile("humble", "ros2", "osrf/ros", "humble-desktop-full")

    print("Iniciando la construcción de la imagen...")
    response = client.build(path='.', tag=image_name, decode=True)
    for line in response:
        if 'stream' in line:
            print(line['stream'].strip())

        if 'error' in line:
            print("Error:", line['error'].strip())
            break

    create_entrypoint("pycharm_ros2", "ros2", "/home/daiego/workspaces/ros2-humble-ws", image_name)