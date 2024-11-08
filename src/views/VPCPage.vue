<template>
  <div>
    <div class="pricing-header px-3 py-3 pt-md-5 pb-md-4 mx-auto text-center">
      <h1 class="display-5">VPC Resource Search</h1>
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
          <label for="vpc" class="col-lg-3 col-form-label">VPC</label>
          <select class="browser-default custom-select" id="vpc">
          </select>
          <div class="align-left loading">
            <img src="../assets/loading.gif"/>
          </div>
        </div>
      </div>
      <fieldset>
        <div class="col-lg-12">
              <textarea id="result" name="result" rows="50" cols="123">
              </textarea>
        </div>
      </fieldset>
    </div>
  </div>
</template>

<script>

import $ from 'jquery';

export default {
  name: 'VPCPage',
  components: {},
  data: function () {
    return {
      id: 'vpc',
    }
  },
  props: [],
  mounted() {
    $('.loading').hide();
    let _this = this;
    _this.ajaxRegion(function () {
        _this.ajaxRequest2();
    });
    $('#profile').change(function () {
      _this.ajaxRegion();
    });
    $('#region').change(function () {
      _this.ajaxRegion();
    });
    $('#vpc').change(function () {
      _this.ajaxRequest2();
    });
  },
  methods: {
    ajaxRegion(cb) {
      let url = this.$parent.url + 'awsvpcs?profile=' + $('#profile').val() + '&region=' + $('#region').val();
      $.ajax(url, {
        method: 'GET',
        success: function (res) {
          let vpcs = JSON.parse(res);
          $("#vpc").empty();
          for (let v of vpcs) {
            $('#vpc').append($('<option>').val(v.id).text(v.name));
          }
          if (cb) cb();
        },
        error: function () {
        }
      });
    },
    ajaxRequest2() {
        // eslint-disable-next-line no-debugger
        debugger;
      $('.loading').show();
      let url = this.$parent.url + 'awsvpc?profile=' + $('#profile').val() + '&region=' + $('#region').val() + '&vpc=' + $('#vpc').val();
      $.ajax(url, {
        method: 'GET',
        success: function (res) {
          $('#result').val(res);
          $('.loading').hide();
        },
        error: function () {
        }
      });
    }
  },
};
</script>