<template>
  <div>
    <div class="pricing-header px-3 py-3 pt-md-5 pb-md-4 mx-auto text-center">
      <h1 class="display-5">RI Calculator</h1>
      <p class="lead">If Left is (-), need to add RI.</p>
    </div>
    <div class="container">
      <div class="row col-lg-12 form-group form-inline">
        <div class="col-lg-4 form-group">
          <label for="profile" class="col-lg-5 col-form-label">AWS Profile</label>
          <select class="browser-default custom-select" id="profile">
            <option value="topzone-k8s" selected>topzone-k8s</option>
            <option value="tz-yyyyyyyyyyyy">tz-yyyyyyyyyyyy</option>
          </select>
        </div>
        <div class="col-lg-4 form-group">
          <label for="region" class="col-lg-5 col-form-label">Region</label>
          <select class="browser-default custom-select" id="region">
            <option value="ap-northeast-1">ap-northeast-1</option>
            <option value="ap-northeast-2" selected>ap-northeast-2</option>
          </select>
        </div>
        <div class="col-lg-4 form-group">
          <label for="riType" class="col-lg-5 col-form-label">RI Type</label>
          <select class="browser-default custom-select" id="riType">
            <option value="ec2" selected>EC2</option>
            <option value="db">DB</option>
            <option value="cache">Cache</option>
          </select>
          <div class="align-left loading">
            <img src="../assets/loading.gif"/>
          </div>
        </div>
      </div>
      <fieldset>
        <legend><a class="p-2" id="ri_link" href="#">RI</a>:</legend>
        <hr>
        <div class="col-lg-12">
          <table class="data table table-bordered table-sm table-responsive-sm table-striped"
                 id="ri-table"
                 data-search="true">
            <thead>
            <tr>
              <th data-field="itemClass">Item Class</th>
              <th data-field="itemType">Item Type</th>
              <th data-field="startDt">Start Dt</th>
              <th data-field="count">Count</th>
              <th data-field="left">Left</th>
            </tr>
            </thead>
          </table>
        </div>
      </fieldset>
      <fieldset>
        <legend>Usage:</legend>
        <hr>
        <div class="col-lg-12">
          <table class="data table table-bordered table-sm table-responsive-sm table-striped"
                 id="usage-table"
                 data-search="true">
            <thead>
            <tr>
              <th data-field="itemClass">Item Class</th>
              <th data-field="itemType">Item Type</th>
              <th data-field="count">Count</th>
            </tr>
            </thead>
          </table>
        </div>
      </fieldset>
    </div>
  </div>
</template>

<script>

import $ from 'jquery';

export default {
  name: 'RIPage',
  components: {},
  data: function () {
    return {
      id: 'ri',
    }
  },
  props: [],
  mounted() {
    let _this = this;
    $('.loading').show();
    _this.ajaxRequest();
    $('#profile').change(function () {
      _this.ajaxRequest();
    });
    $('#region').change(function () {
      _this.ajaxRequest();
    });
    $('#riType').change(function () {
      _this.ajaxRequest();
    });
    $('#ri_link').click(function () {
      let url = '';
      if ($('#riType').val() === 'db') {
        url = 'https://ap-northeast-2.console.aws.amazon.com/rds/home?region=ap-northeast-2#reserved-instances:';
      } else if ($('#riType').val() === 'ec2') {
        url = 'https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#ReservedInstances';
      } else if ($('#riType').val() === 'cache') {
        url = 'https://ap-northeast-2.console.aws.amazon.com/elasticache/home?region=ap-northeast-2#/reserved-nodes';
      }
      url = url.replaceAll('ap-northeast-2', $('#region').val());
      window.open(url, "_blank");
    });
  },
  methods: {
    ajaxRequest() {
      let _this = this;
      $('.loading').show();
      let url = _this.$parent.url + 'awsri?profile=' + $('#profile').val() + '&region=' + $('#region').val() + '&type=' + $('#riType').val();
      $.get(url).then(function (res) {
        res = JSON.parse(res);
        _this.RI = res['RI'];
        _this.Usage = res['Usage'];
        $('#ri-table').DataTable({
          data: res['RI'],
          columns: [
            {title: 'Item Class', data: 'itemClass'},
            {title: 'Item Type', data: 'itemType'},
            {title: 'Start Dt', data: 'startDt'},
            {title: 'Count', data: 'count'},
            {title: 'Left', data: 'left'}
          ],
          select: true,
          paging: true,
          destroy: true,
          lengthMenu: [
            [25, 50, -1],
            [25, 50, 'All'],
          ],
        });
        $('#usage-table').DataTable({
          data: res['Usage'],
          columns: [
            {title: 'Item Class', data: 'itemClass'},
            {title: 'Item Type', data: 'itemType'},
            {title: 'Count', data: 'count'},
          ],
          select: true,
          paging: true,
          destroy: true,
          lengthMenu: [
            [25, 50, -1],
            [25, 50, 'All'],
          ],
        });
        $('.loading').hide();
      })
    }
  },
};
</script>