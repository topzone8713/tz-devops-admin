<template>
  <div id="app">
    <div class="d-flex flex-column flex-md-row align-items-center p-3 px-md-4 mb-3 bg-white border-bottom shadow-sm">
      <h5 class="my-0 mr-md-auto font-weight-normal">
        <router-link class="p-2 text-dark" to="/">DevOps Admin Tool</router-link>
      </h5>
      <nav class="my-2 my-md-0 mr-md-3">
<!--        <router-link class="p-2 text-dark" to="/s3">S3 Repo</router-link>-->
<!--          <a href="https://repo.devops.topzone.me/" target="_blank">S3 Repo</a>-->
      </nav>
<!--      <nav class="my-2 my-md-0 mr-md-3">-->
<!--        <router-link class="p-2 text-dark" to="/ri">RI calculator</router-link>-->
<!--      </nav>-->
      <nav class="my-2 my-md-0 mr-md-3">
        <router-link class="p-2 text-dark" to="/cicd">CI/CD</router-link>
      </nav>
      <nav class="my-2 my-md-0 mr-md-3">
        <router-link class="p-2 text-dark" to="/vpc">VPC Resource Search</router-link>
      </nav>
    </div>
    <router-view/>
    <footer class="pt-4 my-md-5 pt-md-5 border-top">
      <div class="row">
      </div>
    </footer>
  </div>
</template>

<script>
require('datatables.net-bs4');
require('datatables.net-bs4/css/dataTables.bootstrap4.css');
require('datatables.net-responsive-bs4');
require('datatables.net-responsive-bs4/css/responsive.bootstrap4.css');
require('datatables.net-select-bs4');
require('datatables.net-select-bs4/css/select.bootstrap4.min.css');

export default {
  name: 'App',
  components: {
  },
  metaInfo: {
    script: [
      { src: 'https://cdn.datatables.net/v/dt/dt-1.12.1/datatables.min.css', async: true, defer: true },
      { src: 'https://cdn.datatables.net/v/dt/dt-1.12.1/datatables.min.js', async: true, defer: true }
    ],
  },
  data: function() {return {
    url: '' // http://localhost:8000/
  }},
};
</script>