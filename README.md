# A.D.D.U - A Dumb Docker User

ADDU is a CLI tool to build ROS dockerimages and managing docker development environments.
<p align="center">
  <img src="images/addu_logo.png" alt="Texto alternativo" width="300">
</p>


## Features
- Create a new workspace from an available docker image
- Automatically build a new docker image for a workspace
- Install a code editor
- Manage your workspaces


## Installation and requirements
To use ADDU you must install docker and be able to use docker command without sudo.

You can install addu using pip:
```bash
pip install addu 
```

## Usage
Basic use of addu:
```bash
addu-cli
```
A terminal interface will appear, you can navigate through the options by inputting the available option.


## Future work
As it is, ADDU is not really a command line interface, but a cute terminal app, in any case addu should be available to
use as a true CLI, so future work will be to implement the same app with argparse or click like:
```bash
addu create 
addu run <workspace_name>
addu rm <workspace_name>
addu ls 
addu --help
```
