# AWS Cloudformation-GGR-Selenoid

**Introduction**
---
This is a AWS Cloudfomation template for using in set up test automation infrastructure via AWS Cloudformation Stack with AWS spot fleet instances for browser tests using Aerokube GGR and Selenoid docker containers

**Stack schema**
---

![alt text](https://github.com/yurydiahiliev/cloudformation-ggr-selenoid/blob/main/img/stack_schema.png)

**Pre-requisites**
---
Access to AWS account, installed aws-cli, generated AWS API keys


**Prepare AWS stack**
---

1. Specify your own parameters in params.json file to use them in stack creation
Available Options:

| Parameter                 | Default Value                | Description                                |
| --------------------------|:----------------------------:| ------------------------------------------:|
| AvailabilityZone          | `us-east-1a`                 | Set AWS Region                             |
| VpcId                     | `vpc-05322bf757c9b2f06`      | VPC in your AWS Account                    |
| KeyName                   | `test`                       | AWS EC2 Key pair name                      |
| LaunchGgr                 | `Yes`                        | Launch Aerokube Go Grid Router             |
| LaunchSelenoid            | `Yes`                        | Launch Aerokube Selenoid                   |
| LaunchSelenoidUi          | `Yes`                        | Launch Aerokube Selenoid UI                |
| GgrArgs                   | `-guests-allowed`            | Specify GGR Args                           |
| GgrInstanceType           | `t2.micro`                   | AWS Instance Type                          |
| GgrSpotInstance           | `Yes`                        | Create GGR spot instance                   |
| GgrVersion                | `latest`                     | GGR version                                |
| SelenoidInstanceType      | `t2.micro`                   | AWS Instance Type                          |
| SelenoidSpotInstance      | `Yes`                        | Create Selenoid spot instance              |
| SelenoidVersion           | `latest`                     | Aerokube Selenoid version                  |
| InstancesCount            | `1`                          | Selenoid instances count                   |
| SelenoidArgs              | `-timeout 3m`                | Additional Selenoid args                   |
| TmpfsSize                 | `128`                        | TmpfsSize (128, 512, 1024)                 |
| Browsers                  | `chrome:111.0;firefox:111.0` | List of browsers with versions             |
| BrowsersLimit             | `4`                          | Count of browsers per 1 selenoid instance  |
| CountLatestBrowserVersions| `1`                          | Count of latest browser verions            |
| CmVersion                 | `1.5.7`                      | Aerokube CM version                        |
| DockerComposeVersion      | `1.23.2`                     | Docker compose version                     |

Note:
All incoming network traffic to ports `22, 4444, 8888, 8080` is allowed inside template

**How to create AWS Cloudformation Stack**
---

To create AWS Cloudformation Stack use the following command:
```console
$ sh create_stack.sh 
```

Example of successfull script response:
```
{
    "StackId": "arn:aws:cloudformation:us-east-1:211622251997:stack/ggr-selenoid/23f28670-d4b1-11ed-98bf-0a5a344d9477"
}

Waiting for [ggr-selenoid] stack creation...
Stack with name ggr-selenoid was created successfully!
After 5 minutes and 11 seconds.
Retriving GGR URL...
```
Note: 
- Script returns GGR URL output which is using in RemoteWebDriver object creation in test automation framework as a entry point to run all browser tests.
- All GGR and Selenoid node instances can be found in AWS EC2 Dashboard names with stack name suffix.
- Stack creation time depends on different factors such as count of requested Selenoid instances, AWS instance types and etc.
- This approach can be used in CI/CD process as a part of 'infrastructure as a code' pipelines

**Autoscaling**
---
If you're using EC2 on-demand instances in params.json file, not spot instances, in case of termination some of selenoid nodes, new nodes will be initialising and added to GGR quota.xml using Python cron job, average uptime ~ 2 min

**Stack Cleanup**
---

When AWS Cloudformation stack deleted, all spot fleet requests and EC2 instances will be terminated as well

```console
$ sh cleanup_stack.sh 
```
Successfull stack delete response

```
Starting to delete AWS Cloudformation Stack with name: ggr-selenoid
Waiting for deleting AWS Cloudformation Stack with name: ggr-selenoid
Deleted stack successfully!
```
 