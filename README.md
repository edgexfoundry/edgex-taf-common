<!--

 Copyright (C) 2019 Intel Corporation
 Copyright (C) 2019-2025 IOTech Ltd
 SPDX-License-Identifier: Apache-2.0

-->

# EdgeX Test Automation Framework Common ( edgex-taf-common )
[![Build Status](https://jenkins.edgexfoundry.org/view/EdgeX%20Foundry%20Project/job/edgexfoundry/job/edgex-taf-common/job/main/badge/icon)](https://jenkins.edgexfoundry.org/view/EdgeX%20Foundry%20Project/job/edgexfoundry/job/edgex-taf-common/job/main/) [![GitHub Latest Dev Tag)](https://img.shields.io/github/v/tag/edgexfoundry/edgex-taf-common?include_prereleases&sort=semver&label=latest-dev)](https://github.com/edgexfoundry/edgex-taf-common/tags) ![GitHub Latest Stable Tag)](https://img.shields.io/github/v/tag/edgexfoundry/edgex-taf-common?sort=semver&label=latest-stable) [![GitHub License](https://img.shields.io/github/license/edgexfoundry/edgex-taf-common)](https://choosealicense.com/licenses/apache-2.0/) [![GitHub Pull Requests](https://img.shields.io/github/issues-pr-raw/edgexfoundry/edgex-taf-common)](https://github.com/edgexfoundry/edgex-taf-common/pulls) [![GitHub Contributors](https://img.shields.io/github/contributors/edgexfoundry/edgex-taf-common)](https://github.com/edgexfoundry/edgex-taf-common/contributors) [![GitHub Committers](https://img.shields.io/badge/team-committers-green)](https://github.com/orgs/edgexfoundry/teams/edgex-taf-committers/members) [![GitHub Commit Activity](https://img.shields.io/github/commit-activity/m/edgexfoundry/edgex-taf-common)](https://github.com/edgexfoundry/edgex-taf-common/commits)

## Overview
Contains common code or scripts such as TUC which will be common for all the project specific TAF code.
TUC - Test Util Catalog.

> **BREAKING CHANGE:**  
> In **v1.0**, edgex-taf-comand options have been updated.
> Please review the new options by running:
> ```bash
> python3 -m TUC -h
> ```
> and for **rebot** sub command:
> ```bash
> python3 -m TUC rebot -h
> ```
> Additionally, the following variables has changed:
> - environment variable **PROFILE** -> **TAF_CONFIG**
> - **SettingsInfo().profile** -> **SettingsInfo().tafConfig**
> - **SettingsInfo().profile_constant** -> **SettingsInfo().config_constant**

# Usage

1. Install required lib:
    ```shell script
    git clone git@github.com:edgexfoundry/edgex-taf-common.git
    pip3 install edgex-taf-common
    pip3 install -r edgex-taf-common/requirements.txt
    ```

2. Create a edgex-taf project which contains a TAF folder.

    ```
    edgex-taf-project
    ├── TAF
    │   ├── README.md
    │   ├── __init__.py
    │   ├── config
    │   │   ├──global_variables.py
    │   │   └── default
    │   │       └── configuration.py
    │   ├── testArtifacts
    │   │   ├── logs
    │   │   └── reports
    │   ├── testCaseModules
    │   ├── testScenarios
    │   └── utils
    ├── .gitignore
    ├── .gitmodules
    ├── Jenkinsfile
    ├── README.md
    ```
   
3. Run test scripts via the edgex-taf-common:
    ```shell script
    cd edgex-taf-project
   
    # Run tests
    python3 -m TUC -t functionalTest/API/core-data -t functionalTest/API/core-metadata/info/GET.robot
    ```

Default report location:
```
TAF/testArtifacts/reports
├── log.html
├── report.html
└── report.xml
```
   
4. Develop with IDE

   Since we use edgex-taf-common as module, we need to add it to the IDE. [For the pycharm example, add interpreter paths.](https://www.jetbrains.com/help/pycharm/installing-uninstalling-and-reloading-interpreter-paths.html)

5. Build docker image
    ```shell script
    docker build .
    ```

# Reports aggregation
Specify the reports directory and output directory

`python3 -m TUC rebot path/to/report/dir path/to/output/dir` 

Then TUC will fetch robot XML reports from **inputdir** and regenerate new report to **outputdir**
```
path/to/output/dir
├── log.html
├── report.html
└── result.xml (xUnit compatible XML format)
```

## Community
- Discussion: https://github.com/orgs/edgexfoundry/discussions
- Mailing lists: https://lists.edgexfoundry.org/mailman/listinfo

## License
[Apache-2.0](LICENSE)
