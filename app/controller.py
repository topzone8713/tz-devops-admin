import subprocess
from urllib import parse
from vpc_inside import VPC
import os
import requests
import json
import logging

APP_VERSION = '0.2'
# logger config
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(message)s')


class Controller:
    tracer = None

    def _html(self, message):
        return message.enapp("utf8")

    def do_GET(self, httpd):
        query = requests.utils.urlparse(httpd.path).query
        httpd.send_response(200)
        logger.info(f"self.path: {httpd.path}")
        if '/awsri' in httpd.path:
            params = dict(x.split('=') for x in query.split('&'))
            if 'profile' not in params or 'region' not in params or 'type' not in params:
                out = "{\"error\": \"profile or region or type is required.\"}"
            else:
                out = self.get_ri(params.get('profile'), params.get('region'), params.get('type'), 'GET')
            httpd.end_headers()
            httpd.wfile.write(bytes(out, 'utf-8'))
            return
        if '/awss3' in httpd.path:
            params = dict(x.split('=') for x in query.split('&'))
            if 's3repo' not in params:
                out = "{\"error\": \"s3repo is required.\"}"
            else:
                out = self.get_s3(params.get('s3repo'), 'GET')
            httpd.end_headers()
            httpd.wfile.write(bytes(out, 'utf-8'))
            return
        if '/awsvpc?' in httpd.path:
            params = dict(x.split('=') for x in query.split('&'))
            if 'profile' not in params or 'region' not in params or 'vpc' not in params:
                out = "{\"error\": \"profile or region or vpc is required.\"}"
            else:
                out = self.get_vpc(params.get('profile'), params.get('region'), params['vpc'], 'GET')
            httpd.end_headers()
            httpd.wfile.write(bytes(out, 'utf-8'))
            return
        elif '/awsvpcs?' in httpd.path:
            params = dict(x.split('=') for x in query.split('&'))
            if 'profile' not in params or 'region' not in params:
                out = "{\"error\": \"profile or region is required.\"}"
            else:
                out = self.get_vpcs(params.get('profile'), params.get('region'), 'GET')
            httpd.end_headers()
            httpd.wfile.write(bytes(out, 'utf-8'))
            return
        elif httpd.path == '/health':
            out = "{\"version\": \"" + APP_VERSION + "\"}"
            httpd.end_headers()
            httpd.wfile.write(bytes(out, 'utf-8'))
            return

        root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dist')
        logger.info(httpd.path)
        if httpd.path == '/':
            filename = root + '/index.html'
        else:
            filename = root + httpd.path
        httpd.send_response(200)
        if filename[-4:] == '.css':
            httpd.send_header('Content-type', 'text/css')
        elif filename[-5:] == '.json':
            httpd.send_header('Content-type', 'application/javascript')
        elif filename[-3:] == '.js':
            httpd.send_header('Content-type', 'application/javascript')
        elif filename[-4:] == '.ico':
            httpd.send_header('Content-type', 'image/x-icon')
        else:
            httpd.send_header('Content-type', 'text/html')
        httpd.end_headers()
        with open(filename, 'rb') as fh:
            html = fh.read()
            httpd.wfile.write(html)

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self, httpd):
        logger.info(f"self.path: {httpd.path}")
        if httpd.path == '/awsri':
            content_length = int(httpd.headers['Content-Length'])
            post_data = httpd.rfile.read(content_length)
            httpd._set_headers()
            params = parse.parse_qs(parse.urlsplit(str(post_data, 'utf-8')).path)
            if 'type' not in params:
                out = 'type is required.'
            else:
                out = self.get_ri(params.get('type')[0], 'POST')
        elif httpd.path == '/awsvpc':
            content_length = int(httpd.headers['Content-Length'])
            post_data = httpd.rfile.read(content_length)
            httpd._set_headers()
            params = parse.parse_qs(parse.urlsplit(str(post_data, 'utf-8')).path)
            if 'vpc' not in params:
                out = 'vpc is required.'
            else:
                out = self.get_vpc(params['vpc'][0], 'POST')
        else:
            out = 'Not found!'
        httpd.wfile.write(bytes("{\'result\': '" + out + "'}", 'utf-8'))

    def get_s3(self, s3repo='', exec_type='GET'):
        if s3repo == '':
            return 's3repo is required.'
        out = ''
        S3Arry = []
        if exec_type == 'POST':
            return out
        elif exec_type == 'GET':
            s3_cmd = "aws s3api list-objects-v2 --bucket " + s3repo + " --query 'Contents[*].[Key,LastModified,Size]' --output text"
            logger.info(f"s3_cmd: {s3_cmd}")
            process = subprocess.Popen(
                s3_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True)
            for out1 in iter(process.stdout.readline, b''):
                if out1 == '':
                    break
                out1 = out1.replace('\n', '')
                outArry = out1.split('\t')

                S3 = {
                    'fileName': outArry[0],
                    'filePath': "http://" + s3repo + ".s3-website.ap-northeast-2.amazonaws.com/" + outArry[0],
                    'updatedDt': outArry[1],
                    'size': int(outArry[2]),
                }
                S3Arry.append(S3)
            S3Arry = sorted(S3Arry, key=lambda d: d['updatedDt'])
        return "{\"S3\": " + json.dumps(S3Arry) + "}"

    def get_ri(self, profile='', region='', type='', exec_type='GET'):
        if profile == '':
            return 'profile is required.'
        if region == '':
            return 'region is required.'
        if type == '':
            return 'type is required.'
        out = ''
        if exec_type == 'POST':
            return out
        elif exec_type == 'GET':
            if type == 'db':
                ri_cmd = "aws rds describe-reserved-db-instances --query 'ReservedDBInstances[*].[ProductDescription,DBInstanceClass,State,StartTime,DBInstanceCount]' --profile " + profile + " --region " + region + " --output text | grep active"
                usage_cmd = "aws rds describe-db-instances --query 'DBInstances[*].[Engine,DBInstanceClass,DBInstanceStatus,DBInstanceIdentifier]' --profile " + profile + " --region " + region + " --output text | grep available"
                return self.ri_cal(ri_cmd, usage_cmd)
            elif type == 'ec2':
                ri_cmd = "aws ec2 describe-reserved-instances --query 'ReservedInstances[*].[ProductDescription,InstanceType,State,Start,InstanceCount]' --profile " + profile + " --region " + region + " --output text | grep active"
                usage_cmd = "aws ec2 describe-instances --query \"Reservations[*].Instances[*].[Platform,InstanceType,Tags[?Key=='Name']|[0].Value,State.Name,InstanceLifecycle]\" --filters \"Name=instance-state-name,Values=running\" --profile " + profile + " --region " + region + " --output text"
                return self.ri_cal(ri_cmd, usage_cmd)
            elif type == 'cache':
                ri_cmd = "aws elasticache describe-reserved-cache-nodes --query 'ReservedCacheNodes[*].[ProductDescription,CacheNodeType,State,StartTime,CacheNodeCount]' --profile " + profile + " --region " + region + " --output text | grep active"
                usage_cmd = "aws elasticache describe-cache-clusters --query 'CacheClusters[*].[Engine,CacheNodeType,CacheClusterStatus,CacheClusterId]' --profile " + profile + " --region " + region + " --output text | grep available"
                return self.ri_cal(ri_cmd, usage_cmd)
        return out

    def ri_cal(self, ri_cmd, usage_cmd):
        # 1. get RI infos
        logger.info(f"ri_cmd: {ri_cmd}")
        process = subprocess.Popen(
            ri_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True)
        RIArry = []
        for out1 in iter(process.stdout.readline, b''):
            if out1 == '':
                break
            out1 = out1.replace('\n', '')
            outArry = out1.split('\t')
            key = outArry[0] + ' ' + outArry[1]
            RI = {
                'key': key,
                'itemClass': outArry[0],
                'itemType': outArry[1],
                'startDt': outArry[3][0: outArry[3].index('T')],
                'count': int(outArry[4]),
                'left': int(outArry[4]),
            }
            RIArry.append(RI)

            # 2. get Current usage
            process = subprocess.Popen(
                usage_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True)
            UseArry = []
            for out1 in iter(process.stdout.readline, b''):
                if out1 == '':
                    break
                out1 = out1.replace('\n', '')
                outArry = out1.split('\t')
                if len(outArry) == 5 and outArry[4] != 'None':
                    continue
                if 'aurora' == outArry[0]:
                    outArry[0] = 'aurora-mysql'
                if 'None' == outArry[0]:
                    outArry[0] = 'Linux/UNIX'
                if 'windows' == outArry[0]:
                    outArry[0] = 'Windows'
                key = outArry[0] + ' ' + outArry[1]
                Use = {
                    'key': key,
                    'itemClass': outArry[0],
                    'itemType': outArry[1],
                    'count': 1,
                }
                if len(UseArry) == 0:
                    UseArry.append(Use)
                else:
                    chk = False
                    for t in UseArry:
                        if t.get('key') == key:
                            t['count'] = t['count'] + 1
                            chk = True
                            break
                    if chk is False:
                        UseArry.append(Use)

            # 3. RIArry - UseArry
            for t in UseArry:
                chk = False
                for r in RIArry:
                    if t['key'] == r['key']:
                        r['left'] = r['left'] - t['count']
                        chk = True
                        break
                if chk is False:
                    RI = {
                        'key': t['key'],
                        'itemClass': t['itemClass'],
                        'itemType': t['itemType'],
                        'startDt': '',
                        'count': 0,
                        'left': t['count'] * -1,
                    }
                    RIArry.append(RI)
            RIArry = sorted(RIArry, key=lambda d: d['key'])
            UseArry = sorted(UseArry, key=lambda d: d['key'])
        return "{\"RI\": " + json.dumps(RIArry) + ", \"Usage\": " + json.dumps(UseArry) + "}"

    def get_vpcs(self, profile='', region='', exec_type='GET'):
        if profile == '':
            return 'profile is required.'
        if region == '':
            return 'region is required.'
        print('get_vpcs profile: ' + profile)
        print('get_vpcs region: ' + region)
        vpcIns = VPC()
        out = vpcIns.getVpcs(region, profile)
        if exec_type == 'POST':
            return out
        elif exec_type == 'GET':
            return out

    def get_vpc(self, profile='', region='', vpc='', exec_type='GET'):
        if profile == '':
            return 'profile is required.'
        if region == '':
            return 'region is required.'
        if vpc == '' or vpc == 'null':
            return 'vpc is required.'
        print('get_vpc profile: ' + profile)
        print('get_vpc region: ' + region)
        print('get_vpc vpc: ' + vpc)
        vpcIns = VPC()
        out = vpcIns.retrieveAll(region, profile, vpc)
        if exec_type == 'POST':
            return out
        elif exec_type == 'GET':
            return out
