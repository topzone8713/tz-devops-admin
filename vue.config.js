const { defineConfig } = require('@vue/cli-service');
module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    devtool: 'source-map',
  },
  productionSourceMap: true,
  devServer: {
     allowedHosts: ['all'],
     proxy: 'http://localhost:8000/',
  }
});
