import os
import shutil
import time

import docker
import rich
import yaml

from logic import docker_snippets as ds

DOCKER_CLIENT = docker.APIClient(base_url='unix://var/run/docker.sock')
CONFIG = yaml.load(open("config/config.yaml", "r"), Loader=yaml.FullLoader)


class CreateWorkspace:
    def __init__(self, console, ws_name, ros_version, user, image, editor):
        self.console = console
        self.ws_name = ws_name
        self.ros_version = ros_version
        self.user = user
        self.base_image = image
        self.new_image = f"{self.ros_version}:{self.ws_name}-{self.user}"
        self.editor = editor
        self.ws_path = CONFIG["addu-workspaces-path"] + "/" + self.ws_name

    def setup_ws(self):
        self.create_workspace_config()
        self.create_workspace()
        self.create_dockerfile()
        self.build_image()
        ed = EditorDownloader(self.editor, self.console)
        ed.extract_editor(self.ws_path)
        self.create_startup()

    def create_workspace(self):
        os.chdir(CONFIG["addu-workspaces-path"])
        os.system(f"mkdir -p {self.ws_name}/editor-settings/share")
        os.system(f"mkdir -p {self.ws_name}/editor-settings/config")
        os.system(f"mkdir -p {self.ws_name}/editor-settings/local")
        os.system(f"mkdir -p {self.ws_name}/editor-settings/cache")
        os.system(f"mkdir -p {self.ws_name}/editor-settings/java")
        os.chdir(self.ws_name)

    def create_dockerfile(self):
        self.console.print(f"[bold blue]Creating Dockerfile...[/bold blue]", end="")
        with open("Dockerfile", "w") as dockerfile:
            lines = [
                f"FROM {self.base_image}",
                ds.install_packages(["python3-pip", "wget", "ranger"]),
                ds.create_user(self.user),
                ds.source_ros_in_user(self.user, self.ros_version),
                ds.grafical_support(),
                ds.share_devices()
            ]
            dockerfile.writelines(lines)
        self.console.print(f"[bold green] Done![/bold green]")

    def build_image(self, debug=True):
        build_path = str(os.path.join(CONFIG["addu-workspaces-path"], self.ws_name))
        print(build_path)
        response = DOCKER_CLIENT.build(path=build_path, tag=self.new_image, decode=True)
        self.console.print(f"[bold blue]Building image...[/bold blue]", end="")
        win = True
        if debug:
            for line in response:
                if 'stream' in line:
                    print(line['stream'].strip())
                    pass
                if 'error' in line:
                    self.console.print("Error:", line['error'].strip(), style="bold red")
                    win = False
                    break
        if win:
            self.console.print(f"[bold green] Done![/bold green]")

    def create_workspace_config(self):
        with open("config.yaml", "w") as config_file:
            yaml.dump({
                "name": self.ws_name,
                "user": self.user,
                "image": self.new_image,
                "distro": self.ros_version,
                "editor": self.editor
            }, config_file)

    def create_startup(self):
        match self.editor:
            case "vscode":
                editor_path = f"{self.ws_path}/VSCode-linux-x64"
                command = "./editor/code"
            case "pycharm-professional":
                editor_path = f"{self.ws_path}/pycharm-2023.3.3"
                command = "./editor/bin/pycharm.sh"
            case "pycharm-community":
                editor_path = f"{self.ws_path}/pycharm-community-2023.3.3"
                command = "./editor/bin/pycharm.sh"
            case _:
                editor_path = "your-editor-path-here"
                command = "bash"
        comando_docker_run = (
            f"docker run -it --privileged "
            f"--name {self.ws_name} "
            f"--user {self.user} "
            f"--workdir /home/{self.user} "
            f"--env DISPLAY=$DISPLAY "
            f"--volume /dev:/dev "
            f"--volume /tmp/.X11-unix:/tmp/.X11-unix "
            f"--volume {self.ws_path}/share:/home/{self.user}/share "
            f"--volume {editor_path}:/home/{self.user}/editor "
            f"--volume {self.ws_path}/editor-settings/config:/home/{self.user}/.config "
            f"--volume {self.ws_path}/editor-settings/cache:/home/{self.user}/.cache "
            f"--volume {self.ws_path}/editor-settings/local:/home/{self.user}/.local "
            f"--volume {self.ws_path}/editor-settings/java:/home/{self.user}/.java "
            f"--network host "
            f"--rm "
            f"{self.new_image} "
            f"{command}"
        )
        with open("startup.bash", "w") as file:
            file.write("#!/bin/bash\n")
            file.write(comando_docker_run + "\n")


class EditorDownloader:
    def __init__(self, editor):
        self.editor = editor
        self.editors_path = CONFIG["addu-editors-path"]
        if not os.path.exists(CONFIG["addu-editors-path"]):
            os.makedirs(CONFIG["addu-editors-path"])

        self.download_editor()

    def downloaded(self):
        match self.editor:
            case "vscode":
                return os.path.exists(f"{self.editors_path}/vscode.tar.gz")
            case "pycharm-professional":
                return os.path.exists(f"{self.editors_path}/pycharm-professional-2023.3.3.tar.gz")
            case "pycharm-community":
                return os.path.exists(f"{self.editors_path}/pycharm-community-2023.3.3.tar.gz")

    def download_editor(self):
        os.chdir(self.editors_path)
        match self.editor:
            case "vscode":
                os.system("wget -O vscode.tar.gz https://update.code.visualstudio.com/latest/linux-x64/stable")
            case "pycharm-professional":
                os.system("wget -q https://download.jetbrains.com/python/pycharm-professional-2023.3.3.tar.gz")
            case "pycharm-community":
                os.system("wget -q https://download.jetbrains.com/python/pycharm-community-2023.3.3.tar.gz")

    def extract_editor(self, ws_path):
        match self.editor:
            case "vscode":
                os.system(f"tar -xzf vscode.tar.gz -C {ws_path}")
            case "pycharm-professional":
                os.system(f"tar -xzf pycharm-professional-2023.3.3.tar.gz -C {ws_path}")
            case "pycharm-community":
                os.system(f"tar -xzf pycharm-community-2023.3.3.tar.gz -C {ws_path}")
        time.sleep(1)


def delete_ws(ws_name):
    ws_config = yaml.load(open(f"{CONFIG['addu-workspaces-path']}/{ws_name}/config.yaml", "r"), Loader=yaml.FullLoader)
    image_name = ws_config["image"]
    shutil.rmtree(f"{CONFIG['addu-workspaces-path']}/{ws_name}")
    DOCKER_CLIENT.remove_image(image_name)


if __name__ == '__main__':
    EditorDownloader("vscode")
    EditorDownloader("pycharm-community")
    EditorDownloader("pycharm-professional")
