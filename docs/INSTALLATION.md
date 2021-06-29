## Installation
The installation steps cover guide to set up a CPU Utilization alarm for AWS Elastic Container Service (ECS). If you want to set up a different alarm, you just need to tweak the Step 2 below.

Create a Discord notification system to monitor your AWS infrastructure in 4 easy steps. The steps below assume you already have Elastic Container Service (ECS) running as mentioned in our other repositories. However, you can re-use the steps for any AWS service that you want to monitor.

### 1. Set up AWS SNS Topic
1. Go to your SNS dashboard and click on `Topics`.
2. Click on `Create topic` button.
3. Select topic `type` to be "Standard"
4. Set the name of the topic. For example: `plio-staging-ecs-alert`
5. Set a display name of the topic.
6. Enable access logs for your SNS topic (optional, recommended for production)
   1. Go to `Delivery status logging` section
   2. Select `AWS Lambda` from the list of protocols.
   3. Set `Success sample rate` as 100%.
   4. For IAM roles, select `Create new service role` and click on `Create new roles` button.
   5. You will see IAM role are pre-selected. Inside the policy name, select the option that starts with `oneClick_`. These are the default policies.
   6. Click on `Allow` button. It should take you back to the SNS screen and you should see the new roles configured.
   7. When this topic publishes a message, you can access the logs from CloudWatch.
7. Click on `Create topic` button.

### 2. Set up AWS Cloudwatch Alarm
1. Go to your Cloudwatch dashboard and click on `Alarms`.
2. Click on `Create Alarm` button.
3. In the `Specify metric and conditions`, select the metric.
   1. Select ECS service and then the ECS cluster.
   2. Select the metric you want. For example, CPU utilization for staging backend.
   3. Click on `Select metric` button.
   4. In the metric options, set `Statistic` to "Maximum"
   5. Set period to `1 minute`.
   6. Leave the other options like metric name, service name etc as default.
4. In the `Conditions` section:
   1. Choose threshold type to be `Static`
   2. When CPU utilization is `Greater` or `Greater/Equal`
   3. Threshold value to 70 (or whatever you want).
   4. Click on `Next` button
5. In the `Notification` section:
   1. `Alarm state trigger` to be "Alert"
   2. Select an existing SNS topic
   3. Inside the send notification to, select the SNS topic `plio-staging-ecs-alert` you created in previous step.
   4. Click on `Next` button
6. Set the alarm name. For example: `plio-staging-ecs-backend-cpu-70`
7. Add alarm description.
8. Finally, click on `Create alarm` button after reviewing your configurations.

#### Note for auto-scaling
For production ECS, you may already see existing alarms if you have enabled auto-scaling.
- You may wish to create new alarms by following the steps mentioned above or can update the existing ones that were automatically created.
- If you're editing them, you can simply go to Notification section and add the SNS topic.
- **Note:** PLEASE MAKE SURE YOU DO NOT UPDATE ANYTHING ELSE AS THIS MAY IMPACT THE AUTO-SCALING FUNCTIONALITY.

### 3. Set up Discord Webhook
1. Create a new Channel on your Discord. Name it as `plio-logs`.
2. Go to `Channel settings > Integrations > Webhooks`
3. Create a new webhook.
4. Name the webhook as `AWS`.
5. Set the webhook channel to `plio-logs`.
6. Copy the webhook URL for later use.

### 4. Set up AWS Lambda function
1. Go to your Lambda dashboard and click on `Create function` button.
2. Name the lambda function. For example: `plio-staging-discord-alerts`.
4. Choose `Runtime` to "Python 3.8"
5. In the execution role section, select `Create a new role with basic Lambda permissions` option.
6. Click on `Create function` button at the bottom. You will see the function in your lambda function list.
5. Go to the `Code` tab. You will see a file named `lambda_function.py`.
6. Replace all the code inside that file with our [lambda_function.py](./lambda_function.py) file.
7. Deploy the code changes.
8. Go to `Configuration` tab and switch to `Environment variables`.
9. Add a new environment variable:
   1. Key should be `WEBHOOK_URL`
   2. In value, paste the webhook url you copied from Discord.
10. Next, go to `Triggers` page within the `Configuration` tab
   3. Click on `Add Trigger`.
   4. `Select trigger` to be "SNS".
   5. `SNS topic` to be "plio-staging-ecs-alert" that you had created above.
   6. Click on `Add`.
   7. After adding this, if you go to SNS dashboard and see open the SNS topic, you will see an entry in the subscribers list for the AWS Lambda and marked as confirmed subscription.


### Testing
The easiest way for testing is to invert the Alarm condition.
1. Go to your Cloudwatch dashboard.
2. Edit the alarm you created before `plio-staging-ecs-backend-cpu-70`.
3. In the conditions section, invert the alarm condition by selecting "Lower/Equal" option.
4. After some time, the alarm status should change to "In Alarm" and you should receive a Discord notification.
5. Switch back the alarm condition after testing.
