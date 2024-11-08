<template>
  <div>
    <div class="pricing-header px-3 py-3 pt-md-5 pb-md-4 mx-auto text-center">
      <h1 class="display-5">DevOps Tools </h1>
      <p class="lead"></p>
    </div>
    <div class="container">
      <div class="row col-lg-12 form-group form-inline">
        <div class="col-lg-6 form-group">
          <label for="aws-account" class="col-lg-3 col-form-label">EKS Cluster</label>
          <select class="browser-default custom-select" id="aws-account">
            <option value="topzone-k8s" selected>topzone-k8s</option>
            <option value="tz-yyyyyyyyyyyy">tz-yyyyyyyyyyyy</option>
          </select>
          <div class="align-left loading">
            <img src="../assets/loading.gif"/>
          </div>
        </div>
      </div>
      <div class="col-lg-12">
        <div class="card card-default">
          <div class="card-body form-inline">
            <div class="col-sm-4"><h3>EKS Monitoring/Logging</h3></div>
            <div class="col-sm-8">
              <label class="col-sm-12 form-group">
                <h4><p class="cluster-link a-link" href="https://grafana.default.topzone-k8s.topzone.me"
                       target="_blank">Grafana</p></h4>
              </label><h5 class="text-center"></h5>
            </div>
          </div>
        </div>
        <div class="card card-default">
          <div class="card-body form-inline">
            <div class="col-sm-4"><h3>EKS Health Check</h3></div>
            <div class="col-sm-8">
              <label class="col-sm-12 form-group">
                <h4><p class="cluster-link a-link" href="https://prometheus.default.topzone-k8s.topzone.me"
                       target="_blank">Prometheus</p></h4>&nbsp;/&nbsp;
                <h4><p class="cluster-link a-link" href="https://alertmanager.default.topzone-k8s.topzone.me"
                       target="_blank">Alertmanager</p></h4>
              </label><h5 class="text-center"></h5>
            </div>
          </div>
        </div>
        <div class="card card-default">
          <div class="card-body form-inline">
            <div class="col-sm-4"><h3>CD</h3></div>
            <div class="col-sm-8">
              <label class="col-sm-12 form-group">
                <h4><p class="cluster-link a-link" href="https://argocd.default.topzone-k8s.topzone.me"
                       target="_blank">Argocd</p></h4>
              </label><h5 class="text-center"></h5>
            </div>
          </div>
        </div>
        <div class="card card-default">
          <div class="card-body form-inline">
            <div class="col-sm-4"><h3>Password Management</h3></div>
            <div class="col-sm-8">
              <label class="col-sm-12 form-group">
                <h4><p class="cluster-link a-link" href="https://vault.default.topzone-k8s.topzone.me"
                       target="_blank">Vault</p></h4>&nbsp;/&nbsp;
                <h4><p class="cluster-link a-link" href="https://consul.default.topzone-k8s.topzone.me"
                       target="_blank">Consul</p></h4>
              </label><h5 class="text-center"></h5>
            </div>
          </div>
        </div>
        <hr>
      </div>
      <div class="col-lg-12">
        <div class="card card-default">
          <div class="card-body form-inline">
            <div class="col-sm-4"><h3>Infra</h3></div>
            <div class="col-sm-8">
              <label class="col-sm-12 form-group">
                <h4><a href="https://github.com/topzone8713/tz-eks-main/blob/devops/terraform-aws-eks/workspace/base/main.tf" target="_blank">Terraform</a></h4>
              </label><h5 class="text-center"></h5>
            </div>
          </div>
        </div>
        <div class="card card-default">
          <div class="card-body form-inline">
            <div class="col-sm-4"><h3>CI</h3></div>
            <div class="col-sm-8">
              <label class="col-sm-12 form-group">
                <h4><a href="https://jenkins.default.topzone-k8s.topzone.me/" target="_blank">Jenkins</a></h4>
              </label><h5 class="text-center"></h5>
            </div>
          </div>
        </div>
        <div class="card card-default">
          <div class="card-body form-inline">
            <div class="col-sm-4"><h3>Docker Repo</h3></div>
            <div class="col-sm-8">
              <label class="col-sm-12 form-group">
                <h4><p class="cluster-link a-link"
                       href="https://ap-northeast-2.console.aws.amazon.com/ecr/repositories?region=ap-northeast-2"
                       target="_blank">ECR</p></h4>
              </label><h5 class="text-center"></h5>
            </div>
          </div>
        </div>
        <div class="card card-default">
          <div class="card-body form-inline">
            <div class="col-sm-4"><h3>Project Management</h3></div>
            <div class="col-sm-8">
              <label class="col-sm-12 form-group">
                <h4><a href="https://github.com/topzone8713/tz-argocd-repo/tree/main/tz-devops-admin">Argo Repo</a></h4>
              </label><h5 class="text-center"></h5>
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
  name: 'MainPage',
  components: {},
  data: function () {
    return {
      id: 'main',
    }
  },
  props: [],
  mounted() {
    $('.loading').hide();
    $('.cluster-link').click(function (e) {
      let url = $(e.currentTarget).attr('href');
      url = url.replaceAll('topzone-k8s', $('#aws-account').val());
// eslint-disable-next-line no-debugger
debugger;
      window.open(url, "_blank");
    });
  },
  methods: {
  }
};
</script>