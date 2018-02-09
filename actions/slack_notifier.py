#!/usr/local/bin/python

"""
Sample hook to Send Notification to Slack.
Expects a connection object named 'slack'
Action input slack_endpoint should be the service endpoint in format T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
Action input user_name should be the slack username to send the message from.
"""

import sys
import requests
import json

if __name__ == '__main__':
    import django
    django.setup()

from infrastructure.models import Server
from jobs.models import Job
from utilities.logger import ThreadLogger
from utilities.models import ConnectionInfo


def run(job, hook_point=None, order=None, logger=None, **kwargs):
    if not logger:
        logger = ThreadLogger(__name__)

    # if this is called in the Post Order Hook then we need to get the job context from the order.
    if hook_point == 'post_order_execution':
        job = order.list_of_jobs()[0]

    # When executed in the context of a Server or Service Action then this won't have an order so report job name and status instead.
    if order:
        order_name = order.name
        order_status = order.status
    else:
        order_name = job.get_action().name
        order_status = job.status

    server = job.server_set.last()  # prov job only has one server in set

    # Connection object for slack must be created.
    conn = ConnectionInfo.objects.get(name='slack')
    assert isinstance(conn, ConnectionInfo)

    #Load the slack endpoint from an action parameter... because unfortunaltey connection object doesnt support paths, and i don't want to hardcode my key.
    slack_url = "{}://{}/services/{}".format(conn.protocol, conn.ip, '{{ slack_endpoint }}')


    job.set_progress('Sending Slack Notification for server {}'.format(server.hostname))

    # Handle Servers without services
    service_name = 'N/A'
    if server.service:
        serviceName = server.service.name

    # Custom emoji and color based on Order Status!
    emoji = ':party:'
    slack_colour = '#1AA993'
    if order_status == "FAILURE":
        slack_colour = '#8B0000'
        emoji = ':failed:'

    # Use some nested attachments for a cleaner slack message.
    request_body =    {
      'text': 'Your Order: {} has status: {}! {} \n Below are your Service Details:'.format(order_name, order_status, emoji),
      'attachments': [
      {
      'text':  '*Service Name:* {} \n *Hostname:* {} \n *OS Build:* {} \n *IP Address:* {}\n *Environment:* {}'.format(service_name, server.hostname, server.os_build.name, server.ip, server.environment.name),
      'color': slack_colour,
      }
      ],
      'username': '{{ user_name }}'
    }

    json_data = json.dumps(request_body)

    # Dump the slack messages to the console
    job.set_progress('Slack URL is: {}'.format(slack_url))
    job.set_progress('Slack RequestBody: {}'.format(json_data))
    # Send the Slack Message
    response = send_slack_message(json_data, conn, slack_url, logger=logger)
    if response.status_code > 299 or response.status_code < 200:
        err = (
            'Failed to create Slack Message, response from '
            'Slack:\n{}'.format(response.content)
        )
        return "FAILURE", "", err
    else:
        msg = 'Response: {}, HTTP Code: {}'.format(response.content, response.status_code)
    return "SUCCESS", msg, ""


def send_slack_message(data, conn, url, logger=None):
    """
    Make REST call and return the response
    """
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.post(
        url=url,
        data=data,
        headers=headers
    )
    logger.info('Response from Slack:\n{}'.format(response.content))
    return response


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('  Usage:  {} <job_id>'.format(sys.argv[0]))
        sys.exit(1)

    job = Job.objects.get(id=sys.argv[1])
    print(run(job))
