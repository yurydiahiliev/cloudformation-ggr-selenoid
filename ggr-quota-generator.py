import glob
import json
import logging
import urllib.request
from collections import defaultdict
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import SubElement, Element

import boto3

ec2_tag_name = 'selenoid'
quota_dir_path = '/home/ec2-user/grid-router/quota/'
selenoid_port = '4444'

logger = logging.getLogger('quota')
handler = logging.FileHandler(quota_dir_path + 'quota.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s : %(funcName)s(): %(lineno)d')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)


# returns a dictionary with browser names, versions and overall count from all selenoid hosts
def get_selenoid_configs(hosts):
    browsers = defaultdict(defaultdict)
    count = ''
    for host in hosts:
        try:
            url = 'http://{}:{}/status'.format(host, selenoid_port)
            with urllib.request.urlopen(url) as response:
                config = json.loads(response.read().decode('utf-8'))
        except IOError as error:
            logger.error("Error getting selenoid status from {} : {}".format(host, error))
            continue

        count = str(config['total'])

        for browser in config['browsers'].keys():
            for version in config['browsers'][browser].keys():
                if version not in browsers[browser]:
                    browsers[browser][version] = []
                    browsers[browser][version].append(host)
                else:
                    browsers[browser][version].append(host)
    return {'browsers': browsers, 'count': count}


def generate_quota_xml(configs):
    config = configs['browsers']
    count = configs['count']
    root = Element('qa:browsers', attrib={'xmlns:qa': 'urn:config.gridrouter.qatools.ru'})

    for browser_name in config:
        versions = list(config[browser_name].keys())
        latest_ver = max(versions)
        browser = SubElement(root, 'browser', attrib={'name': browser_name, 'defaultVersion': latest_ver})

        for ver in config[browser_name]:
            version = SubElement(browser, 'version', attrib={'number': ver})
            region = SubElement(version, 'region', attrib={'name': aws_region})
            for host in config[browser_name][ver]:
                SubElement(region, 'host', attrib={'name': host, 'port': selenoid_port, 'count': count})

    return ElementTree.ElementTree(root)


# returns a dictionary with selenoid teams and corresponding hosts
def get_teams_and_hosts(tag_name):
    ec2 = boto3.resource('ec2', region_name=aws_region)
    filters = [{'Name': 'tag:{}'.format(tag_name), 'Values': ['*']},
               {'Name': 'instance-state-name', 'Values': ['running']}]
    instances = ec2.instances.filter(Filters=filters)

    teams_hosts = defaultdict(list)

    for instance in list(instances):
        host = instance.private_ip_address
        tags = instance.tags
        for tag in tags:
            if tag.get('Key') == tag_name:
                team = tag.get('Value')
                teams_hosts[team].append(host)

    return teams_hosts


def cleanup_quota_files(teams_hosts):
    teams = teams_hosts.keys()
    for file in glob.glob(quota_dir_path + "*.xml"):
        team = file.replace(quota_dir_path, '').replace('.xml', '')
        if len(teams) == 0 or team not in teams:
            root = Element('qa:browsers', attrib={'xmlns:qa': 'urn:config.gridrouter.qatools.ru'})
            try:
                with open(file, 'wb') as xml_quota:
                    ElementTree.ElementTree(root).write(xml_quota)
            except OSError as error:
                logger.error("Error cleaning up '{}' team xml quota file: {}".format(team, error))


def get_aws_region():
    metadata_url = 'http://169.254.169.254/latest/dynamic/instance-identity/document'
    with urllib.request.urlopen(metadata_url) as response:
        return json.load(response)['region']


def main():
    global aws_region
    aws_region = get_aws_region()

    teams_hosts = get_teams_and_hosts(ec2_tag_name)

    for team in teams_hosts:
        selenoid_hosts = teams_hosts.get(team)
        selenoid_configs = get_selenoid_configs(selenoid_hosts)
        quota_xml = generate_quota_xml(selenoid_configs)
        quota = minidom.parseString(ElementTree.tostring(quota_xml.getroot(), 'utf-8')).toprettyxml(indent=" ")

        try:
            with open('{}{}.xml'.format(quota_dir_path, team), 'w') as quota_file:
                quota_file.write(quota)
        except OSError as error:
            logger.error("Error writing '{}' team xml quota file: {}".format(team, error))

    cleanup_quota_files(teams_hosts)


if __name__ == '__main__':
    main()