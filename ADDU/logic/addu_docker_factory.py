import os

import docker
import yaml

from ADDU.logic import docker_snippets as ds
from rich.progress import track
DOCKER_CLIENT = docker.APIClient(base_url='unix://var/run/docker.sock')
CONFIG = yaml.load(open("ADDU/config/config.yaml", "r"), Loader=yaml.FullLoader)


class CreateWorkspace:
    def __init__(self, console, ws_name, ros_version, user, image, editor):
        self.console = console
        self.ws_name = ws_name
        self.ros_version = ros_version
        self.user = user
        self.image = image
        self.editor = editor
        self.create_workspace()
        self.create_dockerfile()
        self.build_image()
        self.create_startup_script()
        self.create_workspace_config()

    def create_workspace(self):
        if not os.path.exists(CONFIG["addu-workspaces-path"]):
            os.system(f"mkdir {CONFIG['addu-workspaces-path']}")
            os.chdir(CONFIG["addu-workspaces-path"])
        else:
            os.chdir(CONFIG["addu-workspaces-path"])
        os.system(f"mkdir -p {self.ws_name}/share")
        os.chdir(self.ws_name)

    def create_dockerfile(self):
        self.console.print(f"[bold blue]Creating Dockerfile...[/bold blue]", end="")
        with open("Dockerfile", "w") as dockerfile:
            lines = [
                f"FROM {self.image}",
                ds.install_packages(["python3-pip", "wget", "ranger"]),
                ds.create_user(self.user),
                ds.source_ros_in_user(self.user, self.ros_version),
                ds.grafical_support(),
                ds.share_devices(),
                ds.install_code_editor(self.editor)
            ]
            dockerfile.writelines(lines)
        self.console.print(f"[bold green] Done![/bold green]")

    def build_image(self):
        build_path = os.path.join(CONFIG["addu-workspaces-path"], self.ws_name)
        resulting_image = f"{self.ros_version}:{self.ws_name}"
        response = DOCKER_CLIENT.build(path=os.getcwd(), tag=self.image, decode=True)
        self.console.print(f"[bold blue] Building image...[/bold blue]", end="")
        for line in track(response, description=f"[bold blue]Building image...[/bold blue]"):
            if 'error' in line:
                print("Error:", line['error'].strip())
                break
        self.console.print(f"[bold green] Done![/bold green]")

    def create_startup_script(self):
        with open(f'startup.bash', "w") as entrypoint:
            command = f"""
docker run -it --privileged \\
    --name {self.ws_name} \\
    --user {self.user} \\
    --workdir /home/{self.user} \\
    --volume /dev:/dev \\
    --volume /{self.ws_name}/share:/home/ros2/share \\
    --network host \\
    {self.image} \\
    pycharm.sh
        """
            entrypoint.write(command)

    def create_workspace_config(self):
        with open("config.yaml", "w") as config_file:
            yaml.dump({
                "name": self.ws_name,
                "user": self.user,
                "image": self.image,
                "ros_version": self.ros_version,
                "editor": self.editor
            }, config_file)

def create_workspace(ws_name):
    if not os.path.exists(CONFIG["addu-workspaces-path"]):
        os.system(f"mkdir {CONFIG['addu-workspaces-path']}")
        os.chdir(CONFIG["addu-workspaces-path"])
    else:
        os.chdir(CONFIG["addu-workspaces-path"])
    os.system(f"mkdir -p {ws_name}/share")
    os.chdir(ws_name)


def build_image(path, image_name):
    response = DOCKER_CLIENT.build(path=path, tag=image_name, decode=True)
    for line in response:
        if 'stream' in line:
            print(line['stream'].strip())
        if 'error' in line:
            print("Error:", line['error'].strip())
            break


def run_container(image_name, container_name, shared_volume, user):
    DOCKER_CLIENT.create_container(image_name, name=container_name, user=user, volumes=[shared_volume])


def create_dockerfile(ros_version, user, image, editor):
    with open("Dockerfile", "w") as dockerfile:
        lines = [
            f"FROM {image}",
            ds.install_packages(["python3-pip", "wget", "ranger"]),
            ds.create_user(user),
            ds.source_ros_in_user(user, ros_version),
            ds.grafical_support(),
            ds.share_devices(),
            ds.install_code_editor(editor)
        ]
        dockerfile.writelines(lines)


def create_startup_script(user, ws_name, tag_name, container_name):
    with open(f'startup.bash', "w") as entrypoint:
        command = f"""
docker run -it --privileged \\
    --name {container_name} \\
    --user {user} \\
    --workdir /home/{user} \\
    --volume /dev:/dev \\
    --volume /{ws_name}/share:/home/ros2/share \\
    --network host \\
    {tag_name} \\
    pycharm.sh
        """
        entrypoint.write(command)


if __name__ == '__main__':
    run_container("noetic:haru", )
