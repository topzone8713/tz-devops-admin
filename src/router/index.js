import Vue from 'vue'
import VueRouter from 'vue-router'
import MainPage from '../views/MainPage.vue'
import CICDPage from '../views/CICDPage.vue'
import RIPage from '../views/RIPage.vue'
import S3Page from '../views/S3Page.vue'
import VPCPage from '../views/VPCPage.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: MainPage
  },
  {
    path: '/',
    name: 'home',
    component: MainPage
  },
  {
    path: '/cicd',
    name: 'cicd',
    component: CICDPage
  },
  {
    path: '/ri',
    name: 'ri',
    component: RIPage
  },
  {
    path: '/s3',
    name: 's3',
    component: S3Page
  },
  {
    path: '/vpc',
    name: 'vpc',
    component: VPCPage
  },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
