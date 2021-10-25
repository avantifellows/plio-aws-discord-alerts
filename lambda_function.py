import json
import os
import urllib3

http = urllib3.PoolManager()


def parse_service_event(event, service="Service"):
    """Formats the event details as Discord alert"""
    return [
        {
            "name": service,
            "value": event["Trigger"]["Dimensions"][0]["value"],
            "inline": True,
        },
        {"name": "Alarm", "value": event["AlarmName"], "inline": True},
        {
            "name": "Description",
            "value": event.get("AlarmDescription", ""),
            "inline": True,
        },
        {"name": "Old State", "value": event["OldStateValue"], "inline": True},
        {"name": "Trigger", "value": event["Trigger"]["MetricName"], "inline": True},
        {"name": "Event", "value": event["NewStateReason"], "inline": True},
    ]


def lambda_handler(event, context):
    """Retrieves the SNS event details and makes HTTP call to Discord webhook"""
    webhook_url = os.getenv("WEBHOOK_URL")
    users_to_notify = os.getenv("USER_IDS_TO_NOTIFY")
    parsed_message = []
    for record in event.get("Records", []):
        # convert SNS message component into JSON
        sns_message = json.loads(record["Sns"]["Message"])

        is_alarm = sns_message.get("Trigger", None)
        if is_alarm:
            parsed_message = parse_service_event(sns_message, is_alarm["Namespace"])

        if not parsed_message:
            parsed_message = [
                {
                    "name": "Something happened that cannot be parsed! Please check logs.",
                    "value": json.dumps(sns_message),
                }
            ]

        # prepare discord data
        discord_data = {
            "username": "AWS",
            "avatar_url": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
            "embeds": [
                {"color": 16711680, "fields": parsed_message}  # red to highlight error
            ],
        }

        if users_to_notify:
            users_to_notify = users_to_notify.split(',')
            users_to_notify = [f"<@{user_id}>" for user_id in users_to_notify if user_id]
            discord_data["content"] = "".join(users_to_notify)

        headers = {"content-type": "application/json"}

        # make the webhook call
        http.request(
            "POST", webhook_url, body=json.dumps(discord_data), headers=headers
        )
