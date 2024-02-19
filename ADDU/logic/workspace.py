import yaml
import os
from logic import docker_snippets as ds
import docker

CONFIG = yaml.safe_load(open('config/config.yaml'))
WORKSPACES_PATH = CONFIG['addu-workspaces-path']


class Workspace:
    def __init__(self, workspace_name=None, user=None, distro=None, base_image=None, editor=None):
        self.workspace_name = workspace_name
        self.workspace_path = os.path.expanduser(f"{WORKSPACES_PATH}/{workspace_name}")
        print(self.workspace_path)
        self.user = user
        self.distro = distro
        self.base_image = base_image
        self.image_name = f"{self.distro}:{self.workspace_name}-{self.user}"
        self.container_name = f"{self.workspace_name}-{self.user}"
        self.editor = editor

    def create_workspace(self):
        # Settings dirs
        os.makedirs(f"{self.workspace_path}/settings/java", exist_ok=True)
        os.makedirs(f"{self.workspace_path}/settings/config", exist_ok=True)
        os.makedirs(f"{self.workspace_path}/settings/local", exist_ok=True)
        os.makedirs(f"{self.workspace_path}/settings/cache", exist_ok=True)
        # Shared Volume dir
        os.makedirs(f"{self.workspace_path}/shared", exist_ok=True)
        # Dockerfile, config.yaml and startup.sh
        self.create_dockerfile()
        self.create_config_yaml()
        match self.editor:
            case "vscode":
                self.create_startup(command="code")
            case "pycharm-professional":
                self.create_startup(command="pycharm.sh")
            case "pycharm-community":
                self.create_startup(command="pycharm.sh")

    def create_config_yaml(self):
        with open(f"{self.workspace_path}/config.yaml", "w") as config:
            config.write(f"workspace_name: {self.workspace_name}\n")
            config.write(f"user: {self.user}\n")
            config.write(f"distro: {self.distro}\n")
            config.write(f"base_image: {self.base_image}\n")
            config.write(f"image_name: {self.image_name}\n")
            config.write(f"container_name: {self.container_name}\n")
            config.write(f"editor: {self.editor}\n")

    def create_dockerfile(self):
        with open(f"{self.workspace_path}/Dockerfile", "w") as dockerfile:
            lines = [
                f"FROM {self.base_image}",
                ds.install_packages(["python3-pip", "wget", "ranger", "git", "libxrender1", "libxtst6", "libxi6"]),
                ds.create_user(self.user),
                ds.source_ros_in_user(self.user, self.distro),
                ds.grafical_support(),
                ds.install_editor(self.editor)
            ]
            dockerfile.writelines(lines)

    def create_startup(self, command="bash"):
        with open(f"{self.workspace_path}/startup.sh", "w") as startup:
            lines = (
                f"docker run -it --privileged "
                f"--name {self.workspace_name} "
                f"--user {self.user} "
                f"--workdir /home/{self.user} "
                f"--env DISPLAY=$DISPLAY "
                f"--volume /dev:/dev "
                f"--volume {self.workspace_path}/shared:/home/{self.user}/shared "
                f"--volume {self.workspace_path}/settings/config:/home/{self.user}/.config "
                f"--volume {self.workspace_path}/settings/cache:/home/{self.user}/.cache "
                f"--volume {self.workspace_path}/settings/local:/home/{self.user}/.local "
                f"--volume {self.workspace_path}/settings/java:/home/{self.user}/.java "
                f"--network host "
                f"--rm "
                f"{self.image_name} "
                f"{command}"
            )
            startup.writelines(lines)

    def run_workspace(self):
        os.system(f"bash {self.workspace_path}/startup.sh")

    def build_image(self):
        client = docker.from_env()
        client.images.build(path=self.workspace_path, tag=self.image_name, rm=True, forcerm=True)


if __name__ == '__main__':
    w = Workspace("test", "test", "noetic", "ros:noetic", "pycharm-professional")

