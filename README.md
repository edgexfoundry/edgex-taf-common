<!--

 Copyright (C) 2019 Intel Corporation
 Copyright (C) 2019 IOTech Ltd
 SPDX-License-Identifier: Apache-2.0

-->

# EdgeX Test Automation Framework Common ( edgex-taf-common )

## Overview
Contains common code or scripts such as TUC which will be common for all the project specific TAF code.
TUC - Test Util Catalog.

# Usage

1. Create a edgex-taf project which contains a TAF folder.
2. Add edgex-taf-common as a submodule to your edgex-taf project and install required lib:
    ```shell script
    git submodule add git@github.com:edgexfoundry-holding/edgex-taf-common.git
    pip3 install robotbackgroundlogger
    pip3 install robotframework
    pip3 install configparser
    ```
    Then your project structure will be:
    ```
    edgex-taf-project
    └── edgex-taf-common
        ├── README.md
        ├── TAF-Manager
        └── TUC
    ├── TAF
    │   ├── README.md
    │   ├── __init__.py
    │   ├── config
    │   ├── testArtifacts
    │   ├── testCaseApps
    │   ├── testScenarios
    │   └── utils
    ├── .gitignore
    ├── .gitmodules
    ├── Jenkinsfile
    ├── README.md
    ```
3. Run test scripts via the edgex-taf-common:
    ```shell script
    # Run use cases
    python3 edgex-taf-common/TAF-Manager/trigger/run.py -u UC_coredata -u UC_metadata
    
    # Run test cases
    python3 edgex-taf-common/TAF-Manager/trigger/run.py -t UC_coredata/event.robot -t UC_metadata/device.robot
    ```
   
4. Develop with IDE

   In edgex-taf-common/TAF-Manager/trigger/run.py, Edgex-taf add the **edgex-taf-common** to the **system path**, so you should also add the path to the IDE. 

5. Build docker image
    ```shell script
    docker build .
    ```

## Community
- Chat: https://edgexfoundry.slack.com
- Mailing lists: https://lists.edgexfoundry.org/mailman/listinfo

## License
[Apache-2.0](LICENSE)
