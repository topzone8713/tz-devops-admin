# tz-devops-admin

tz-devops-admin은 `tz-eks-main`으로 구성된 Kubernetes 클러스터를 관리하고 시각화하는 웹 애플리케이션입니다. 이 앱은 다양한 개발 환경을 통합하여 CI/CD 파이프라인, 로깅, 모니터링 시스템을 모니터링할 수 있는 사용자 인터페이스를 제공하며, 각 기능으로의 링크를 제공합니다. 또한 특정 AWS 계정과 VPC 내 생성된 리소스를 확인할 수 있습니다.

이 앱은 백엔드는 Python, 프론트엔드는 Vue로 작성되어 있으며, 하나의 앱으로 빌드됩니다.


* tz-devops-admin: [https://github.com/topzone8713/tz-devops-admin](https://github.com/topzone8713/tz-devops-admin)
* tz-eks-main: [https://github.com/topzone8713/tz-eks-main/tree/devops](https://github.com/topzone8713/tz-eks-main/tree/devops)

## 사용방법
강의를 들으면서 이 앱을 활용하기 위해서는 다음 순서를 따르세요.

1. 본인의 GitHub 계정에서 프로젝트를 fork합니다.
2. fork한 프로젝트를 private 프로젝트로 변경합니다.
3. 아래 내용을 수정합니다.
   https://github.com/xxxxxx/tz-devops-admin/tree/devops/resources

- resources/.env
  ```
  auth_realm=devops-admin
  user=admin
  password=DevOps!323
  dev=developer
  dev_password=Dev!323
  aws_account_id=084828581538     => 수정 필요
  aws_region=ap-northeast-2
  ```

- resources/config
  ```
  [default]
  region = ap-northeast-2
  output = json

  [profile tz-xxxxxxxxx]       => 수정 필요
  region = ap-northeast-2
  output = json
  ```

- resources/credentials
  ``
  [default]
  aws_access_key_id = xxxxxxxxx       => 수정 필요
  aws_secret_access_key = xxxxxxxxx   => 수정 필요

  [tz-xxxxxxxxx]                      => 수정 필요
  aws_access_key_id = xxxxxxxxx       => 수정 필요
  aws_secret_access_key = xxxxxxxxx   => 수정 필요
  ```

- resources/kubeconfig_eks-main
  이 파일은 `tz-eks-main`을 구성하여 생성된 `resources/kubeconfig_topzone-k8s` 파일을 이 위치에 덮어 씁니다.

4. 변경된 내용을 commit/push하면 Jenkins에서 빌드할 수 있는 상태가 됩니다.

### CI/CD 관련 자원 개요

- k8s/Jenkinsfile: Jenkins 빌드 시 사용되는 스크립트
- k8s/k8s.sh: `kubectl`, `argocd` 등의 명령어 실행을 돕는 유틸리티
- k8s/k8s-dev.yaml: 개발 환경에서 사용할 k8s 자원을 생성하기 위한 yaml 파일
- Dockerfile: Docker 환경 구성 파일

Dockerfile은 AWS CLI를 실행할 수 있도록 미리 설정된 환경을 제공합니다.

```
FROM topzone8713/devops-utils2:latest
```

참고로 이 이미지는 Jenkinsfile의 빌드용 컨테이너에서도 사용됩니다.

```
containers:
- name: devops2
  image: topzone8713/devops-utils2:latest
```

아래 내용은 이 앱을 로컬에서 구성하고자 할 경우에 필요한 사항입니다. (강의에서 불필요)

## Prerequisites

To set up the environment for developing this application, follow these steps

1. Install Vue CLI (if not already installed):
   ```bash
   npm uninstall -g @vue/cli
   npm install -g @vue/cli
   ```

2. Create the project with Vue CLI using a preset:
   ```bash
   npx @vue/cli create --inlinePreset='{ 
     "useConfigFiles": false, 
     "plugins": { 
       "@vue/cli-plugin-babel": {}, 
       "@vue/cli-plugin-eslint": { 
         "config": "base", 
         "lintOn": ["save"] 
       } 
     }, 
     "router": true, 
     "routerHistoryMode": true 
   }' tz-devops-admin
   ```

3. Install additional dependencies:
   ```bash
   npm install bootstrap bootstrap-vue
   npm install
   ```

## Project Setup

To set up the project and install required packages:

```bash
pip3 install -r requirements.txt
npm install
```

## Building for Production

To compile and minify the application for production:

```bash
npm run build
```

## Linting

To lint and auto-fix files:

```bash
npm run lint
```

## Running the Application

To start the development server:

```bash
python3 app/server.py
```

Once running, open the app in your browser at [http://localhost:8000/](http://localhost:8000/).


