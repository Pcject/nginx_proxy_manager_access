# Project Description
[中文版](README_CN.md)

This project is a custom component for Home Assistant, integrating with Nginx Proxy Manager to support one-click switching of Access for a specific domain through Home Assistant's switch. Additionally, the component supports controlling internal and external network access by using different Access configuration files. The project is open-source under the Apache 2.0 license.

# Quick Start
## Installation
1. Download the code for this project and place it in the custom_components directory of Home Assistant.
2. Restart Home Assistant.
## Configuration
1. In `const.py` `DEFAULT_ACCESS_NAME_FOR_OFF`, configure the name of the Access to use when the switch is in the off position.
2. Add the Nginx Proxy Manager Access integration.
3. Enter the host, email, password, and other information.
4. A switch with the name of the domain will be automatically created.
Usage
5. Use Home Assistant's switch to toggle Access and control internal and external network access.

# License
This project is open-source under the Apache 2.0 license.