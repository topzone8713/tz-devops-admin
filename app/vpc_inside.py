import logging
import boto3
from botocore.exceptions import ClientError, ProfileNotFound
from ujson import dumps

# logger config
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(message)s')


class VPC:

    def __init__(self):
        self.args = None
        self.session = None
        self.vpc_client = None
        self.elbV2_client = None
        self.elb_client = None
        self.lambda_client = None
        self.eks_client = None
        self.asg_client = None
        self.rds_client = None
        self.ec2 = None
        self.vpc_id = None

    def getVpcs(self, region, profile):
        try:
            print('getVpcs profile: {0}'.format(profile))
            session = boto3.Session(profile_name=profile)
            self.ec2 = session.resource('ec2', region_name=region)
        except ProfileNotFound as e:
            logger.warning("{}, please provide a valid AWS profile name".format(e))
            return "{}, please provide a valid AWS profile name".format(e)
        vpcs = []
        try:
            for t in list(self.ec2.vpcs.filter(Filters=[])):
                vpcs.append({'name': t.id if t.tags is None else t.tags[0]['Value'], 'id': t.id})
        except ClientError as e:
            logger.warning(e.response['Error']['Message'])
        return dumps(vpcs)

    def vpc_in_region(self):
        """
        Describes one or more of your VPCs.
        """
        str = ''
        vpc_exists = False
        try:
            vpcs = list(self.ec2.vpcs.filter(Filters=[]))
        except ClientError as e:
            str = str + e.response['Error']['Message'] + '\n'
            logger.warning(e.response['Error']['Message'])
            exit()
        str = str + "VPCs in region {}:".format(self.args['region']) + '\n'
        logger.info(str)
        for vpc in vpcs:
            str = str + vpc.id + '\n'
            logger.info(vpc.id)
            if vpc.id == self.vpc_id:
                vpc_exists = True
                break
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return vpc_exists, str

    def describe_asgs(self):
        str = "ASGs in VPC {}:".format(self.vpc_id) + '\n'
        logger.info(str)
        asgs = self.asg_client.describe_auto_scaling_groups()['AutoScalingGroups']
        for asg in asgs:
            asg_name = asg['AutoScalingGroupName']
            if self.asg_in_vpc(asg):
                str = str + asg_name + '\n'
                logger.info(str)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def asg_in_vpc(self, asg):
        subnets_list = asg['VPCZoneIdentifier'].split(',')
        for subnet in subnets_list:
            try:
                sub_description = self.vpc_client.describe_subnets(SubnetIds=[subnet])['Subnets']
                if sub_description[0]['VpcId'] == self.vpc_id:
                    logger.info("{} resides in {}".format(asg['AutoScalingGroupName'], self.vpc_id))
                    return True
            except ClientError:
                pass
        return False

    def describe_ekss(self):
        ekss = self.eks_client.list_clusters()['clusters']
        str = "EKSs in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("EKSs in VPC {}:".format(self.vpc_id))
        for eks in ekss:
            eks_desc = self.eks_client.describe_cluster(name=eks)['cluster']
            if eks_desc['resourcesVpcConfig']['vpcId'] == self.vpc_id:
                str = str + eks_desc['name'] + '\n'
                logger.info(eks_desc['name'])
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_ec2s(self):
        waiter = self.vpc_client.get_waiter('instance_terminated')
        reservations = self.vpc_client.describe_instances(Filters=[{"Name": "vpc-id",
                                                                    "Values": [self.vpc_id]}])['Reservations']

        # Get a list of ec2s
        ec2s = [ec2['InstanceId'] for reservation in reservations for ec2 in reservation['Instances']]
        str = "EC2s in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("EC2s in VPC {}:".format(self.vpc_id))
        for ec2 in ec2s:
            str = str + ec2 + '\n'
            logger.info(ec2)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_lambdas(self):
        lmbds = self.lambda_client.list_functions()['Functions']

        lambdas_list = [lmbd['FunctionName'] for lmbd in lmbds
                        if 'VpcConfig' in lmbd and lmbd['VpcConfig']['VpcId'] == self.vpc_id]
        str = "Lambdas in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("Lambdas in VPC {}:".format(self.vpc_id))
        for lmbda in lambdas_list:
            str = str + lmbda + '\n'
            logger.info(lmbda)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_rdss(self):
        rdss = self.rds_client.describe_db_instances()['DBInstances']

        rdsss_list = [rds['DBInstanceIdentifier'] for rds in rdss if rds['DBSubnetGroup']['VpcId'] == self.vpc_id]
        str = "RDSs in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("RDSs in VPC {}:".format(self.vpc_id))
        for rds in rdsss_list:
            str = str + rds + '\n'
            logger.info(rds)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_elbs(self):
        elbs = self.elb_client.describe_load_balancers()['LoadBalancerDescriptions']

        elbs = [elb['LoadBalancerName'] for elb in elbs if elb['VPCId'] == self.vpc_id]
        str = "Classic ELBs in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("Classic ELBs in VPC {}:".format(self.vpc_id))
        for elb in elbs:
            str = str + elb + '\n'
            logger.info(str)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_elbsV2(self):
        elbs = self.elbV2_client.describe_load_balancers()['LoadBalancers']

        elbs_list = [elb['LoadBalancerArn'] for elb in elbs if elb['VpcId'] == self.vpc_id]
        str = "ELBs V2 in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("ELBs V2 in VPC {}:".format(self.vpc_id))
        for elb in elbs_list:
            str = str + elb + '\n'
            logger.info(elb)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_nats(self):
        nats = self.vpc_client.describe_nat_gateways(Filters=[{"Name": "vpc-id",
                                                               "Values": [self.vpc_id]}])['NatGateways']

        nats = [nat['NatGatewayId'] for nat in nats]
        str = "NAT GWs in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("NAT GWs in VPC {}:".format(self.vpc_id))
        for nat in nats:
            str = str + nat + '\n'
            logger.info(nat)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_enis(self):
        enis = self.vpc_client.describe_network_interfaces(Filters=[{"Name": "vpc-id", "Values": [self.vpc_id]}])[
            'NetworkInterfaces']

        # Get a list of enis
        enis = [eni['NetworkInterfaceId'] for eni in enis]
        str = "ENIs in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("ENIs in VPC {}:".format(self.vpc_id))
        for eni in enis:
            str = str + eni + '\n'
            logger.info(eni)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_igws(self):
        """
      Describe the internet gateway
      """

        # Get list of dicts
        igws = self.vpc_client.describe_internet_gateways(
            Filters=[{"Name": "attachment.vpc-id",
                      "Values": [self.vpc_id]}])['InternetGateways']

        igws = [igw['InternetGatewayId'] for igw in igws]
        str = "IGWs in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("IGWs in VPC {}:".format(self.vpc_id))
        for igw in igws:
            str = str + igw + '\n'
            logger.info(igw)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_vpgws(self):
        """
      Describe the virtual private gateway
      """

        # Get list of dicts
        vpgws = self.vpc_client.describe_vpn_gateways(
            Filters=[{"Name": "attachment.vpc-id",
                      "Values": [self.vpc_id]}])['VpnGateways']

        vpgws = [vpgw['VpnGatewayId'] for vpgw in vpgws]
        str = "VPGWs in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("VPGWs in VPC {}:".format(self.vpc_id))
        for vpgw in vpgws:
            str = str + vpgw + '\n'
            logger.info(vpgw)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_subnets(self):
        # Get list of dicts of metadata
        subnets = self.vpc_client.describe_subnets(Filters=[{"Name": "vpc-id",
                                                             "Values": [self.vpc_id]}])['Subnets']

        # Get a list of subnets
        subnets = [subnet['SubnetId'] for subnet in subnets]
        str = "Subnets in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("Subnets in VPC {}:".format(self.vpc_id))
        for subnet in subnets:
            str = str + subnet + '\n'
            logger.info(subnet)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_acls(self):
        acls = self.vpc_client.describe_network_acls(Filters=[{"Name": "vpc-id",
                                                               "Values": [self.vpc_id]}])['NetworkAcls']

        # Get a list of subnets
        acls = [acl['NetworkAclId'] for acl in acls]
        str = "ACLs in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("ACLs in VPC {}:".format(self.vpc_id))
        for acl in acls:
            str = str + acl + '\n'
            logger.info(acl)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_sgs(self):
        sgs = self.vpc_client.describe_security_groups(Filters=[{"Name": "vpc-id",
                                                                 "Values": [self.vpc_id]}])['SecurityGroups']

        # Get a list of subnets
        # sgs = [sg['GroupId'] for sg in sgs]
        str = "Security Groups in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("Security Groups in VPC {}:".format(self.vpc_id))
        for sg in sgs:
            str = str + sg['GroupId'] + '\n'
            logger.info(sg['GroupId'])
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_rtbs(self):
        rtbs = self.vpc_client.describe_route_tables(Filters=[{"Name": "vpc-id",
                                                               "Values": [self.vpc_id]}])['RouteTables']
        # Get a list of Routing tables
        rtbs = [rtb['RouteTableId'] for rtb in rtbs]
        str = "Routing tables in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("Routing tables in VPC {}:".format(self.vpc_id))
        for rtb in rtbs:
            str = str + rtb + '\n'
            logger.info(rtb)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def describe_vpc_epts(self):
        epts = self.vpc_client.describe_vpc_endpoints(Filters=[{"Name": "vpc-id",
                                                                "Values": [self.vpc_id]}])['VpcEndpoints']

        # Get a list of Routing tables
        epts = [ept['VpcEndpointId'] for ept in epts]
        str = "VPC EndPoints in VPC {}:".format(self.vpc_id) + '\n'
        logger.info("VPC EndPoints in VPC {}:".format(self.vpc_id))
        for ept in epts:
            str = str + ept + '\n'
            logger.info(ept)
        str = str + "----------------------------------------------------------------------------------------\n"
        logger.info(str)
        return str

    def retrieveAll(self, region, profile, vpc):
        try:
            session = boto3.Session(profile_name=profile)
        except ProfileNotFound as e:
            logger.warning("{}, please provide a valid AWS profile name".format(e))
            return "{}, please provide a valid AWS profile name".format(e)
        self.args = {
            'region': region,
            'profile': profile,
            'vpc': vpc,
        }
        self.vpc_client = session.client("ec2", region_name=region)
        self.elbV2_client = session.client('elbv2', region_name=region)
        self.elb_client = session.client('elb', region_name=region)
        self.lambda_client = session.client('lambda', region_name=region)
        self.eks_client = session.client('eks', region_name=region)
        self.asg_client = session.client('autoscaling', region_name=region)
        self.rds_client = session.client('rds', region_name=region)
        self.ec2 = session.resource('ec2', region_name=region)

        self.vpc_id: str = vpc

        out = ''
        if self.vpc_in_region()[0]:
            out = out + self.describe_ekss()
            out = out + self.describe_asgs()
            out = out + self.describe_rdss()
            out = out + self.describe_ec2s()
            out = out + self.describe_lambdas()
            out = out + self.describe_elbs()
            out = out + self.describe_elbsV2()
            out = out + self.describe_nats()
            out = out + self.describe_vpc_epts()
            out = out + self.describe_igws()
            out = out + self.describe_vpgws()
            out = out + self.describe_enis()
            out = out + self.describe_sgs()
            out = out + self.describe_rtbs()
            out = out + self.describe_acls()
            out = out + self.describe_subnets()
        else:
            out = "The given VPC was not found in {}".format(region)
            logger.info(out)
        return out
