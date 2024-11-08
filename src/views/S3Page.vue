<template>
  <div>
    <div class="pricing-header px-3 py-3 pt-md-5 pb-md-4 mx-auto text-center">
      <h1 class="display-5">S3 Repo</h1>
    </div>
    <div class="container">
      <div class="row col-lg-12 form-group form-inline">
        <div class="col-lg-4 form-group">
          <label for="s3repo" class="col-lg-5 col-form-label">S3 Repo</label>
          <select class="browser-default custom-select" id="s3repo">
            <option value="unity-repo.topzone.me" selected>unity-repo.topzone.me</option>
          </select>
        </div>
      </div>
      <fieldset>
        <hr>
        <div class="col-lg-12">
          <table class="data table table-bordered table-sm table-responsive-sm table-striped"
                 id="s3-table"
                 data-search="true">
            <thead>
            <tr>
              <th data-field="fileName">File Name</th>
              <th data-field="updatedDt">Updated Dt</th>
              <th data-field="size">Size</th>
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
  name: 'S3Page',
  components: {},
  data: function () {
    return {
      id: 's3',
    }
  },
  props: [],
  mounted() {
    let _this = this;
    $('.loading').show();
    _this.ajaxRequest();
    $('#s3repo').change(function () {
      _this.ajaxRequest();
    });
    $('#s3-table').on('click', 'tbody tr', function() {
        let url = "https://" + $('#s3repo').val() + "/" + this.cells[0].innerText;
        window.open(url, '', 'width=300, height=300');
    });
  },
  methods: {
    ajaxRequest() {
      let _this = this;
      $('.loading').show();
      // let url = 'http://localhost:8000/awss3?s3repo=' + $('#s3repo').val();
      let url = _this.$parent.url + 'awss3?s3repo=' + $('#s3repo').val();
      $.get(url).then(function (res) {
        res = JSON.parse(res);
        _this.S3 = res['S3'];
        $('#s3-table').DataTable({
          data: res['S3'],
          columns: [
            {title: 'File Name', data: 'fileName'},
            {title: 'Updated Dt', data: 'updatedDt'},
            {title: 'Size', data: 'size'}
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