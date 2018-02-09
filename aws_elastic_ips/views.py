import json

from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from extensions.views import tab_extension, TabExtensionDelegate
from infrastructure.models import Server
from resourcehandlers.models import ResourceHandler
from infrastructure.models import Environment
from utilities.decorators import dialog_view

class ElasticIPsTabDelegate(TabExtensionDelegate):
    def should_display(self):
        # Only show the Elastic IP magic for AWS Environments
        if self.instance.resource_handler.type_slug != "aws":
            return False
        return True

# Generic Method to connect to ec2
def get_ec2_handle(env_id):
    env = Environment.objects.get(id=env_id)
    rh = env.resource_handler
    aws = rh.cast()

    aws.connect_ec2(env.aws_region)
    ec2 = aws.resource_technology.work_class.ec2
    return ec2

@tab_extension(
    title='Elastic IPs',  # `title` is what end users see on the tab
    description='Manage Elastic IPs for AWS Providers',
    model=Environment, # Required: the model this extension is for
    delegate=ElasticIPsTabDelegate,
)
def aws_elastic_ips(request, obj_id):
    ec2 = get_ec2_handle(env_id=obj_id)
    addresses = ec2.get_all_addresses()
    for ad in addresses:
        ad.instance_name  = "Available" if ad.instance_id is None else ec2.get_all_instances(ad.instance_id)[0].instances[0].tags['Name']
    return render(request, 'aws_elastic_ips/templates/elastic_ips.html', dict(
        addresses=addresses, env_id=obj_id,
    ))

# aws_add_elastic_ip will add an ElasticIP address to a given environment
def aws_add_elastic_ip(request, env_id):
    ec2 = get_ec2_handle(env_id)
    ec2.allocate_address()
    messages.success(request, "Elastic IP Created")
    return HttpResponseRedirect(reverse('env_detail', args=[env_id]))

# aws_release_elastic_ip will remove an ElasticIP address given its allocation_id
def aws_release_elastic_ip(request, env_id, allocation_id):
    ec2 = get_ec2_handle(env_id)
    ec2.release_address(allocation_id=allocation_id)
    messages.success(request, "Elastic IP with allocation ID: {} Released".format(allocation_id))
    return HttpResponseRedirect(reverse('env_detail', args=[env_id]))

def aws_release_all_elastic_ip(request, env_id):
    ec2 = get_ec2_handle(env_id)
    addresses = ec2.get_all_addresses()
    count = 0
    for ad in addresses:
        if ad.association_id is None:
            ec2.release_address(allocation_id=ad.allocation_id)
            count += 1
    messages.warning(request, "{} Elastic IP have been Released".format(count))
    return HttpResponseRedirect(reverse('env_detail', args=[env_id]))
