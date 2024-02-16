import yaml
import os
from logic import docker_snippets as ds
import docker

CONFIG = yaml.safe_load(open('config/config.yaml'))
WORKSPACES_PATH = CONFIG['addu-workspaces-path']


class Workspace:
    def __init__(self, workspace_name=None, user=None, distro=None, base_image=None, editor=None):
        self.workspace_name = workspace_name
        self.workspace_path = f"{WORKSPACES_PATH}/{workspace_name}"
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
        with open(f"{self.workspace_path}/config.yaml", "w"): pass
        self.create_startup()

    def create_dockerfile(self):
        with open(f"{self.workspace_path}/Dockerfile", "w") as dockerfile:
            lines = [
                f"FROM {self.base_image}",
                ds.install_packages(["python3-pip", "wget", "ranger", "git"]),
                ds.create_user(self.user),
                ds.source_ros_in_user(self.user, self.distro),
                ds.grafical_support(),
                ds.install_editor(self.editor)
            ]
            dockerfile.writelines(lines)

    def create_startup(self):
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
                f"bash"
            )
            startup.writelines(lines)

    def run_workspace(self):
        os.system(f"bash {self.workspace_path}/startup.sh")

    def run_workspace_docker(self):
        client = docker.from_env()

        command = "bash"

        volumes = {
            "/dev": {"bind": "/dev", "mode": "rw"},
            f"{self.workspace_path}/shared": {"bind": f"/home/{self.user}/shared", "mode": "rw"},
            f"{self.workspace_path}/settings/config": {"bind": f"/home/{self.user}/.config", "mode": "rw"},
            f"{self.workspace_path}/settings/cache": {"bind": f"/home/{self.user}/.cache", "mode": "rw"},
            f"{self.workspace_path}/settings/local": {"bind": f"/home/{self.user}/.local", "mode": "rw"},
            f"{self.workspace_path}/settings/java": {"bind": f"/home/{self.user}/.java", "mode": "rw"},
        }

        network_mode = "host"

        container = client.containers.run(
            image=self.image_name,
            command=command,
            name=self.workspace_name,
            user=self.user,
            working_dir=f"/home/{self.user}",
            environment=["DISPLAY=$DISPLAY"],
            volumes=volumes,
            network_mode=network_mode,
            remove=True,
            privileged=True,
            tty=True
        )

    def build_image(self):
        client = docker.from_env()
        client.images.build(path=self.workspace_path, tag=self.image_name, rm=True, forcerm=True)


if __name__ == '__main__':
    w = Workspace("test", "test", "noetic", "ros:noetic", "pycharm-professional")
    w.create_workspace()
    w.build_image()
    w.run_workspace_docker()
