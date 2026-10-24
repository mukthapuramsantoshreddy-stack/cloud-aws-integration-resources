# Student Management System on AWS

## Project Overview

The **Student Management System** is a cloud-based web application deployed on Amazon Web Services (AWS). It allows users to enter student details and upload images through a web browser. The application runs on an Amazon EC2 instance, while Amazon S3 provides object storage for uploaded images.

The project demonstrates practical experience in AWS infrastructure provisioning, identity and access management, application deployment, cloud storage, serverless automation, monitoring, and alerting.

I provisioned the AWS infrastructure and configured the required services, then used Git and GitHub to manage the source code and deploy the application onto EC2.

## Project Objectives

- Build and deploy a Student Management System on AWS.
- Create a custom VPC and configure subnets, an Internet Gateway, a NAT Gateway, and route tables.
- Manage AWS resources using an IAM user, IAM policies, and IAM roles.
- Store user-uploaded images in Amazon S3.
- Deploy the application on Amazon EC2.
- Use Git and GitHub for source-code management and deployment.
- Automate EC2 instance shutdown using AWS Lambda and Amazon EventBridge.
- Monitor EC2 CPU utilization using Amazon CloudWatch.
- Receive SNS notifications when CPU utilization exceeds the configured 30% threshold.

## Technologies and AWS Services

| Technology / Service | Purpose |
|---|---|
| AWS IAM | User access, policies, and roles |
| Amazon VPC | Isolated virtual network |
| Public and private subnets | Network segmentation |
| Internet Gateway | Internet connectivity for eligible resources in public subnets |
| NAT Gateway | Outbound internet connectivity for resources in private subnets |
| Route tables | Control network traffic routing |
| Amazon EC2 | Hosts the web application |
| Amazon S3 | Stores uploaded student images |
| AWS Lambda | Executes the EC2 shutdown automation |
| Amazon EventBridge | Triggers Lambda according to a schedule |
| Amazon CloudWatch | Monitors EC2 CPU utilization |
| Amazon SNS | Sends CPU-utilization alert notifications |
| Git | Version control |
| GitHub | Source-code repository |
| PuTTY | SSH connection to the EC2 instance |
| Python and Flask | Application runtime and web framework |

## Architecture

```text
                    AWS ROOT ACCOUNT
                           |
                           v
                    Create IAM User
                           |
                           v
                 Login as IAM User
                           |
                           v
                    Amazon VPC
                           |
               +-----------+-----------+
               |                       |
          Public Subnet           Private Subnet
               |                       |
        Internet Gateway          NAT Gateway
               |
          EC2 Instance
          Flask Application
               |
         User accesses app
          via public IP
          and port 5000
               |
       Student details form
       and image upload
               |
               v
          Amazon S3 Bucket
        Uploaded student images


 EC2 Scheduled Shutdown:

 Amazon EventBridge
        |
        | Scheduled trigger
        v
    AWS Lambda
        |
        | Stop EC2 instance
        v
    Amazon EC2


 EC2 CPU Monitoring:

 EC2 CPU Utilization
        |
        v
 Amazon CloudWatch Alarm
     Threshold: 30%
        |
        v
      Amazon SNS
        |
        v
 Email Notification
```

*The diagram represents the configured workflow described in this project. The exact subnet placement of the EC2 instance and the S3 access method should be documented according to the final AWS configuration.*

## Project Implementation

### 1. IAM User Creation and Access Management

I created an IAM user from the AWS root account and used that IAM user for my project implementation.

I configured the required IAM policies and roles to manage access to AWS resources, including EC2 and S3.

**Purpose:**
- Separate day-to-day project activities from the root account.
- Control access to AWS resources.
- Allow the application to access the required AWS services through appropriate IAM permissions.

**Security practice:** The root account should be reserved for tasks that specifically require it. Routine AWS administration should use an appropriately permissioned IAM identity or IAM Identity Center.

### 2. VPC and Network Configuration

I created my own Amazon VPC and configured the required networking resources.

The network configuration included:
- VPC
- Public and private subnets
- Internet Gateway (IGW)
- NAT Gateway
- Route tables

**Purpose:**

The VPC provides a logically isolated network for AWS resources. Subnets divide the network into smaller segments, while route tables determine where network traffic is sent.

The Internet Gateway provides internet connectivity for appropriately routed resources in public subnets. The NAT Gateway enables eligible resources in private subnets to initiate outbound internet connections without requiring direct inbound internet connectivity.

### 3. Source Code Management Using Git and GitHub

I obtained the Student Management System source code and saved it in my local file system.

I then created a new GitHub repository and uploaded the project source code using Git.

The general workflow was:

```bash
git init
git add .
git commit -m "Initial project commit"
git branch -M main
git remote add origin <GITHUB_REPOSITORY_URL>
git push -u origin main
```

This made the application source code available in GitHub for deployment onto EC2.

**Purpose:**
- Maintain source-code history.
- Store the project in a remote repository.
- Make application files available for deployment.
- Track and manage future changes.

### 4. Amazon S3 Bucket Configuration

I created an Amazon S3 bucket to store images uploaded by users through the Student Management System.

When a user uploads an image through the application, the application sends the file to the configured S3 bucket.

**Workflow:**

1. The user opens the application in a browser.
2. The user enters student details and selects an image.
3. The Flask application processes the upload.
4. The application uses its configured AWS permissions to send the image to S3.
5. Amazon S3 stores the uploaded image as an object.

The application requires the appropriate IAM permissions to perform the necessary S3 operations.

**Purpose:** Store uploaded images separately from the EC2 application server, using scalable object storage.

*Note: S3 does not automatically receive an image merely because it is selected in the browser. The application must upload the file through the AWS SDK or another configured upload mechanism.*

### 5. IAM Roles and Policies for EC2 and S3

I created IAM policies and roles to support the required access between the EC2-hosted application and Amazon S3.

The EC2 instance uses its attached IAM role to obtain AWS credentials and perform authorized operations.

This approach avoids embedding long-term AWS access keys directly in the application source code.

**Purpose:**
- Authorize application access to S3.
- Control which bucket and objects can be accessed.
- Improve security through permission-based access.

The recommended approach is to grant only the actions and resources required by the application.

### 6. EC2 Instance Creation and Connection

I created an Amazon EC2 instance to host the Student Management System.

I connected to the instance using its public IP address through PuTTY over SSH.

After connecting, I prepared the environment by installing the required dependencies and tools.

Typical commands for an Amazon Linux 2023 instance include:

```bash
sudo dnf update -y
sudo dnf install -y python3 python3-pip git
```

The actual packages installed depend on the application requirements.

### 7. Application Deployment on EC2

After preparing the EC2 environment, I cloned the GitHub repository onto the instance.

```bash
git clone <GITHUB_REPOSITORY_URL>
cd <PROJECT_DIRECTORY>
```

I installed the required Python dependencies and followed the application setup steps to run the Flask application.

For example, if the project uses `requirements.txt`:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The application was then started using its configured entry point.

For an application whose entry point is `app.py`, this may be:

```bash
python app.py
```

The exact command depends on the project's source code.

### 8. Accessing the Application Through a Browser

Once the Flask application was running, I accessed it using the EC2 public IP address and port 5000.

The endpoint follows this general format:

```text
http://<EC2_PUBLIC_IP>:5000
```

I opened the application in a browser, entered student details, and uploaded images through the form.

The application then stored the uploaded images in the configured Amazon S3 bucket.

**Result:** The application could be accessed remotely, and the image-upload workflow could be tested through the web interface.

**Security consideration:** Port 5000 is commonly used by Flask's development server. For a production deployment, use a production WSGI server, HTTPS, appropriate network access restrictions, and application authentication rather than exposing the development server directly to the internet.

### 9. Scheduled EC2 Shutdown Using Lambda and EventBridge

I configured AWS Lambda and Amazon EventBridge to automate EC2 instance shutdown at a specified time.

**Workflow:**

1. I created a Lambda function containing the logic to stop the target EC2 instance.
2. I configured an EventBridge schedule to trigger the function at the required time.
3. I configured the necessary Lambda execution permissions to allow the function to stop the intended EC2 instance.
4. When the schedule triggers, EventBridge invokes Lambda.
5. Lambda requests the EC2 stop operation using its execution role.

This reduces the need to stop the instance manually and can help control compute costs.

**Important:** EventBridge schedules must be configured with the intended time zone or UTC schedule correctly. Stopping an EC2 instance does not delete it, but attached storage and other resources may continue to incur charges. A stop operation can also fail if the instance or its configuration does not support it.

### 10. EC2 CPU Monitoring Using CloudWatch and SNS

I configured Amazon CloudWatch monitoring for the EC2 instance and used an alarm threshold of 30% CPU utilization.

The notification workflow uses Amazon SNS to deliver alerts.

**Workflow:**

1. CloudWatch collects EC2 CPU utilization metrics.
2. A CloudWatch alarm evaluates the metric against the configured 30% threshold.
3. When the alarm meets its configured conditions, it enters the corresponding alarm state.
4. The alarm publishes a notification to the configured SNS topic.
5. SNS sends the notification to its subscribed endpoint, such as a confirmed email subscription.

**Purpose:**
- Monitor EC2 resource utilization.
- Identify when CPU usage exceeds the selected threshold.
- Receive notifications without continuously checking the AWS console.

The alarm's evaluation period, number of evaluation periods, comparison operator, and SNS subscription configuration determine exactly when and how notifications are delivered.

## End-to-End Project Workflow

The overall project workflow is:

1. Create an IAM user and use it for AWS project administration.
2. Create a VPC and configure the required networking resources.
3. Store the application source code in a GitHub repository.
4. Create the S3 bucket for uploaded images.
5. Configure IAM roles and policies for EC2 and S3 access.
6. Launch an EC2 instance and connect through PuTTY.
7. Install the required software and dependencies.
8. Clone the source code from GitHub.
9. Run the Flask application on EC2.
10. Access the application through the EC2 public IP and port 5000.
11. Enter student information and upload images to S3.
12. Use EventBridge and Lambda to stop EC2 according to a schedule.
13. Use CloudWatch and SNS to monitor CPU utilization and send notifications when the configured 30% threshold is reached.

## Security Considerations

- Use the root account only for tasks that require it.
- Apply least-privilege permissions to IAM users, roles, and policies.
- Keep AWS access keys, private keys, and application secrets out of GitHub.
- Keep the S3 bucket private unless public access is explicitly required.
- Restrict SSH access to trusted IP addresses.
- Avoid exposing port 5000 to all internet users in a production environment.
- Implement authentication and authorization before storing real student information.
- Use HTTPS for production traffic.
- Verify CloudWatch alarm conditions and SNS subscriptions.
- Give the Lambda execution role permission to stop only the intended EC2 instance.
- Review EC2 and networking costs, especially NAT Gateway charges.

## Key Learning Outcomes

Through this project, I gained practical experience with:

- AWS account access management using IAM.
- VPC networking, subnetting, gateways, and route tables.
- EC2 provisioning and Linux server administration.
- Deploying a Python application from GitHub.
- Storing user-uploaded files in Amazon S3.
- Configuring IAM-based service access.
- Automating EC2 shutdown using Lambda and EventBridge.
- Monitoring CPU utilization with CloudWatch.
- Configuring SNS-based notifications.
- Understanding the relationship between application deployment, cloud infrastructure, automation, and monitoring.

## Conclusion

The Student Management System demonstrates how an application can be deployed and operated using multiple AWS services.

Amazon EC2 hosts the web application, Amazon S3 stores uploaded images, and IAM manages access permissions. A custom VPC provides the network foundation, while Git and GitHub support source-code management and deployment. AWS Lambda and EventBridge automate scheduled EC2 shutdown, and CloudWatch with SNS provides CPU monitoring and notifications.

This project provides hands-on experience in AWS infrastructure, Linux administration, cloud deployment, object storage, IAM security, serverless automation, and operational monitoring.

## Author

**Student Management System — AWS Cloud Project**

Technologies: AWS | EC2 | S3 | IAM | VPC | Lambda | EventBridge | CloudWatch | SNS | Python | Flask | Git | GitHub
