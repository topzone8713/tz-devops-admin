<template>
  <div>
    <div class="pricing-header px-3 py-3 pt-md-5 pb-md-4 mx-auto text-center">
      <h1 class="display-5">CI/CD & Monitoring</h1>
      <p class="lead"></p>
    </div>
    <div class="container">
      <div class="col-lg-12">
        <div class="card card-default">
          <div class="card-body form-inline">
            <div class="col-sm-2"><h3>CI / CD flow</h3></div>
            <div class="col-sm-10 text-center">
              <img src="../assets/jenkins-argocd.png" usemap="#jenkins-argocd"/>
              <map name="jenkins-argocd">
                <area shape="rect" coords="125,0,180,100" alt="Github" target="_blank" href="https://github.com/topzone8713/tz-devops-admin/tree/devops">
                <area shape="rect" coords="260,0,330,100" alt="Jenkins" target="_blank" href="https://jenkins.default.topzone-k8s.topzone.me">
                <area shape="rect" coords="430,0,500,100" alt="ECR" target="_blank" href="https://ap-northeast-2.console.aws.amazon.com/ecr/repositories">
                <area shape="rect" coords="510,0,590,100" alt="Vault" target="_blank" href="https://vault.default.topzone-k8s.topzone.me">
                <area shape="rect" coords="260,145,330,250" alt="Github" target="_blank" href="https://github.com/topzone8713/tz-devops-admin/tree/devops">
                <area shape="rect" coords="430,145,500,250" alt="ArgoCD" target="_blank" href="https://argocd.default.topzone-k8s.topzone.me">
                <area shape="rect" coords="620,145,700,250" alt="EKS" target="_blank" href="https://grafana.default.topzone-k8s.topzone.me">
              </map>
            </div>
          </div>
        </div>
        <div class="card card-default">
          <div class="card-body form-inline">
            <div class="col-sm-2"><h3>Log / Monitor</h3></div>
            <div class="col-sm-10 text-center">
              <img src="../assets/prometheus-grafana.png" usemap="#prometheus-grafana"/>
              <map name="prometheus-grafana">
                <area shape="rect" coords="5,30,70,100" alt="EKS" target="_blank" href="https://grafana.default.topzone-k8s.topzone.me">
                <area shape="rect" coords="155,30,220,100" alt="Prometheus" target="_blank" href="https://prometheus.default.topzone-k8s.topzone.me">
                <area shape="rect" coords="300,30,360,100" alt="AlertManager" target="_blank" href="https://alertmanager.default.topzone-k8s.topzone.me">
                <area shape="rect" coords="155,160,220,230" alt="Grafana" target="_blank" href="https://grafana.default.topzone-k8s.topzone.me/dashboards">
              </map>
            </div>
          </div>
        </div>
        <div class="card card-default">
          <div class="card-body form-inline">
            <div class="col-sm-2"><h3>ELK / metric</h3></div>
            <div class="col-sm-10 text-center">
              <img src="../assets/elk.png" usemap="#elk"/>
              <map name="elk">
                <area shape="rect" coords="5,12,75,90" alt="EKS" target="_blank" href="https://grafana.default.topzone-k8s.topzone.me">
                <area shape="rect" coords="350,9,420,87" alt="filebeat-1" target="_blank" href="https://grafana.default.topzone-k8s.topzone.me">
                <area shape="rect" coords="6,114,76,192" alt="ALB" target="_blank" href="https://ap-northeast-2.console.aws.amazon.com/ec2/home?region=ap-northeast-2">
                <area shape="rect" coords="115,101,185,179" alt="S3-1" target="_blank" href="https://s3.console.aws.amazon.com">
                <area shape="rect" coords="155,160,220,230" alt="SNS" target="_blank" href="https://ap-northeast-2.console.aws.amazon.com/sqs">
                <area shape="rect" coords="348,147,418,225" alt="filebeat-2" target="_blank" href="https://grafana.default.topzone-k8s.topzone.me">
                <area shape="rect" coords="231,152,301,230" alt="SNS" target="_blank" href="https://ap-northeast-2.console.aws.amazon.com/sqs">
                <area shape="rect" coords="454,6,524,84" alt="logstash" target="_blank" href="https://logstash.elk.topzone-k8s.topzone.me/">
                <area shape="rect" coords="565,9,635,87" alt="elasticsearch" target="_blank" href="https://es.elk.topzone-k8s.topzone.me/">
                <area shape="rect" coords="718,9,788,87" alt="kibana" target="_blank" href="https://kibana.elk.topzone-k8s.topzone.me">
                <area shape="rect" coords="7,209,77,287" alt="cloudfront" target="_blank" href="https://us-east-1.console.aws.amazon.com">
                <area shape="rect" coords="115,203,185,281" alt="S3-2" target="_blank" href="https://s3.console.aws.amazon.com">
              </map>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import $ from 'jquery';

export default {
  name: 'CICDPage',
  components: {},
  data: function () {
    return {
      id: 'cicd',
    }
  },
  props: [],
  mounted() {
    $('.loading').hide();
    $('.cluster-link').click(function (e) {
      let url = $(e.currentTarget).attr('href');
      url = url.replaceAll('topzone-k8s', $('#aws-account').val());
      window.open(url, "_blank");
    });
  },
  methods: {
  }
};
</script>