#!/usr/bin/env bash
#set -x

shopt -s expand_aliases
alias trace_on='set -x'
alias trace_off='{ set +x; } 2>/dev/null'

WORKING_HOME=/var/lib/jenkins

# 기본 클러스터 이름 설정
CLUSTER_NAME=${CLUSTER_NAME:-"topzone-k8s"}
CONFIG_FILE=$(echo ${CLUSTER_NAME} | sed 's/eks-main/project/')

# 로그 파일에 환경 변수 기록
{
    echo "AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}"
    echo "AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}"
    echo "AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION}"
    echo "APP_NAME: ${APP_NAME}"
    echo "GIT_BRANCH: ${GIT_BRANCH}"
    echo "BUILD_NUMBER: ${BUILD_NUMBER}"
    echo "NAMESPACE: ${NAMESPACE}"
    echo "STAGING: ${STAGING}"
    echo "ACCOUNT_ID: ${ACCOUNT_ID}"
    echo "CLUSTER_NAME: ${CLUSTER_NAME}"
    echo "DOMAIN: ${DOMAIN}"
    echo "GITHUP_ID: ${GITHUP_ID}"
    echo "GITHUP_TOKEN: ${GITHUP_TOKEN}"
    echo "VAULT_TOKEN: ${VAULT_TOKEN}"
    echo "ARGOCD_ID: ${ARGOCD_ID}"
    echo "ARGOCD_PASSWORD: ${ARGOCD_PASSWORD}"
} >> log

ACTION=${1}

# ACTION 인자 확인
if [[ -z "${ACTION}" ]]; then
    echo "ACTION is none!"
    exit 1
fi

# Vault 관련 작업
if [[ "${ACTION}" == "vault" ]]; then
  export VAULT_ADDR=http://vault.vault.svc.cluster.local
  login_out=$(vault login ${VAULT_TOKEN})
  vault_secret_key=$2
  fields=($(echo "$3" | tr ',' '\n'))
  for item in "${fields[@]}"; do
    rslt=$(vault kv get -field=${item} ${vault_secret_key})
    echo ${rslt}
  done
  exit 0
fi

if [[ "${ACTION}" == "vault_config" ]]; then
  export VAULT_ADDR=http://vault.vault.svc.cluster.local
  login_out=$(vault login ${VAULT_TOKEN})
  vault_secret_key=$2
  vault_secret_key2=$3
  tmp=tmp_$(shuf -i 0-1000 -n 1)
  echo "" > .env
  echo "" > ${tmp}
  if [[ "${vault_secret_key2}" != "" ]]; then
#    echo "====================${vault_secret_key2}====================" >> ${tmp}
    vault kv get -format=json secret/${vault_secret_key}/${vault_secret_key2} | jq -r .data.data >> ${tmp}
    echo "" >> ${tmp}
  else
    vault kv get -format=json secret/${vault_secret_key} | jq -r .data.data >> ${tmp}
  fi
  if [[ "${4}" == "-json" ]]; then
    cp -Rf ${tmp} .env
  else
    cat ${tmp} | jq -r 'keys_unsorted[] as $key|"\($key)=\(.[$key])"' >> .env
  fi
  cat .env && rm -Rf ${tmp}
  exit 0
fi

# AWS STS 호출
echo "================================================"
echo "aws sts get-caller-identity"
aws sts get-caller-identity
echo "================================================"
echo "****** ACTION: $1"
echo "================================================"

# 필수 환경 변수 확인
for var in WORKSPACE APP_NAME BUILD_NUMBER; do
    if [[ -z "${!var}" ]]; then
        echo "${var} is none!"
        exit 1
    fi
done

# GIT_BRANCH 변환
export ORI_GIT_BRANCH=${GIT_BRANCH}
export GIT_BRANCH=$(echo ${ORI_GIT_BRANCH} | sed 's/\//-/g' | cut -b1-21 | tr '[:upper:]' '[:lower:]')
echo "GIT_BRANCH: ${GIT_BRANCH}"

# STAGING 환경 변수 설정
if [[ "${FORCED_PROD}" == "true" ]]; then
  export STAGING=prod
else
  if [[ "${FORCED_STAGING}" == "true" ]]; then
    export STAGING=staging
  elif [[ "${FORCED_QA}" == "true" ]]; then
    export STAGING=qa
  else
    if [[ "${GIT_BRANCH}" == "master" || "${GIT_BRANCH}" == "main" ]]; then
      export STAGING=prod
    elif [[ "${STAGING}" == "" ]]; then
      export STAGING=dev
    fi
  fi
fi

# TAG_ID 및 IMAGE_TAG 설정
if [[ "${TAG_ID}" != "latest" ]]; then
    TAG_ID=$(echo ${GIT_BRANCH} | md5sum | cut -b1-5)-${TAG_ID}
fi
echo "TAG_ID: ${TAG_ID}"
if [[ -z "${IMAGE_TAG}" ]]; then
  IMAGE_TAG="${DOCKER_NAME}:${TAG_ID}"
fi
echo "IMAGE_TAG: ${IMAGE_TAG}"
if [[ -z "${REPO_HOST}" ]]; then
  REPO_HOST="${ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
fi
echo "REPO_HOST: ${REPO_HOST}"
if [[ -z "${REPOSITORY_TAG}" ]]; then
  export REPOSITORY_TAG="${REPO_HOST}/${IMAGE_TAG}"
fi
echo "REPOSITORY_TAG: ${REPOSITORY_TAG}"

# K8S 파일 및 APP_NAME 설정
SOURCE_K8S_FILE=${WORKSPACE}/k8s.yaml
SOURCE_DOCKER_FILE=${WORKSPACE}/Dockerfile
ORI_APP_NAME=${APP_NAME}
if [[ "${STAGING}" == "prod" ]]; then
  APP_NAME=${ORI_APP_NAME}
  K8S_FILE=${K8S_FILE/-dev/}
  if [[ "${K8S_DIR}" != "" ]]; then
    SOURCE_K8S_FILE=${WORKSPACE}/${K8S_DIR}/k8s.yaml
  fi
else
  if [[ "${BRANCH_ROLLOUT}" == "true" ]]; then
    if [[ "${K8S_DIR}" != "" ]]; then
      if [[ "${STAGING}" == "staging" ]]; then
        APP_NAME=${ORI_APP_NAME}-staging
        SOURCE_K8S_FILE=${WORKSPACE}/${K8S_DIR}/k8s-staging.yaml
      elif [[ "${STAGING}" == "qa" ]]; then
        APP_NAME=${ORI_APP_NAME}-qa
        SOURCE_K8S_FILE=${WORKSPACE}/${K8S_DIR}/k8s-qa.yaml
      else
        APP_NAME=${ORI_APP_NAME}-${GIT_BRANCH}
        SOURCE_K8S_FILE=${WORKSPACE}/${K8S_DIR}/k8s-dev.yaml
      fi
    fi
  elif [[ "${BRANCH_ROLLOUT}" == "false" ]]; then
    APP_NAME=${ORI_APP_NAME}
    if [[ "${K8S_DIR}" != "" ]]; then
      if [[ "${STAGING}" == "staging" ]]; then
        SOURCE_K8S_FILE=${WORKSPACE}/${K8S_DIR}/k8s-staging.yaml
      elif [[ "${STAGING}" == "qa" ]]; then
        SOURCE_K8S_FILE=${WORKSPACE}/${K8S_DIR}/k8s-qa.yaml
      else
        SOURCE_K8S_FILE=${WORKSPACE}/${K8S_DIR}/k8s.yaml
      fi
    fi
  fi
fi
echo "ORI_APP_NAME: ${ORI_APP_NAME}"
echo "APP_NAME: ${APP_NAME}"
if [[ "${STAGING}" == "prod" || "${STAGING}" == "staging" || "${STAGING}" == "qa" ]]; then
  NAMESPACE=${NAMESPACE/-dev/}
  NAMESPACE=${NAMESPACE/-prod/}
  PROJECT=${NAMESPACE}
else
  if [[ $NAMESPACE != *-dev ]]; then
    NAMESPACE=${NAMESPACE}"-dev"
  else
    NAMESPACE=${NAMESPACE}
  fi
  PROJECT=${NAMESPACE/-dev/}
fi
KUBECTL="kubectl -n ${NAMESPACE} --kubeconfig ${WORKSPACE}/resources/kubeconfig_eks-main"
echo "================================================"

# Kubernetes 초기화 함수
function k8s_init {
  echo "#######################################"
  echo k8s init
  echo "#######################################"
  REPO_IMAGE=$(aws ecr list-images --repository-name ${DOCKER_NAME})
  if [[ $? != 0 ]]; then
    aws ecr create-repository \
        --repository-name ${DOCKER_NAME} \
        --image-tag-mutability IMMUTABLE
    sleep 3
  fi
}

# Kubernetes 파일 처리 함수
function k8s_file {
  TARGET_K8S_FILE="${WORKSPACE}/k8s_file.yaml"
  echo "#######################################"
  echo "envsubst < ${SOURCE_K8S_FILE} > ${TARGET_K8S_FILE}"
  echo "#######################################"
  envsubst < "${SOURCE_K8S_FILE}" > "${TARGET_K8S_FILE}"
  echo "========================"
  cat ${TARGET_K8S_FILE}
  echo "========================"
}

# ArgoCD 초기화 함수
function argocd_init {
  if [[ "${USE_ARGOCD}" != "true" ]]; then
    return
  fi
  echo "#######################################"
  echo apply to argocd
  echo "#######################################"
  pwd
  echo argocd login argocd-server.argocd.svc.cluster.local:443 --username ${ARGOCD_ID} --password ${ARGOCD_PASSWORD} --insecure
  argocd login argocd-server.argocd.svc.cluster.local:443 --username ${ARGOCD_ID} --password ${ARGOCD_PASSWORD} --insecure
  trace_on
  argocd app create ${APP_NAME} \
    --project ${PROJECT} \
    --repo https://github.com/${GITHUP_ID}/tz-argocd-repo.git \
    --path ${APP_NAME} \
    --dest-namespace ${NAMESPACE} \
    --dest-server https://kubernetes.default.svc --directory-recurse --upsert --grpc-web
  if [[ $? != 0 ]]; then
    echo "Error occurred!"
    alert_slack
    exit 1
  fi
  argocd app sync ${APP_NAME}
  trace_off
}

# ArgoCD 삭제 함수
function argocd_delete {
  if [[ "${USE_ARGOCD}" != "true" ]]; then
    return
  fi
  echo "#######################################"
  echo apply to argocd
  echo "#######################################"
  pwd
  echo argocd login argocd-server.argocd.svc.cluster.local:443
  argocd login argocd-server.argocd.svc.cluster.local:443 --username ${ARGOCD_ID} --password ${ARGOCD_PASSWORD} --insecure
  trace_on
  argocd app delete ${APP_NAME3} -y
  trace_off
}

# Slack 알림 함수
#SLACK_DEVOPS=https://hooks.slack.com/services/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 # eks_alert
SLACK_DEVOPS=https://hooks.slack.com/services/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 # devop
function alert_slack {
  echo ""
#  curl -X POST -H 'Content-type: application/json' --data '{"text":"build error '${APP_NAME}' - '${BUILD_URL}'"}' ${SLACK_DEVOPS}
}

# ACTION에 따른 작업 수행
if [[ "${ACTION}" == "init" ]]; then
  k8s_init
elif [[ "${ACTION}" == "argocd_init" ]]; then
  argocd_init
elif [[ "${ACTION}" == "argocd_delete" ]]; then
  argocd_delete
elif [[ "${ACTION}" == "build" ]]; then
  echo "#######################################"
  echo "BUILD_CMD: ${BUILD_CMD}"
  echo "#######################################"

  echo "AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION}"
  echo "CLUSTER_NAME: ${CLUSTER_NAME}"
  echo "ACCOUNT_ID: ${ACCOUNT_ID}"
  aws ecr get-login-password --region ${AWS_DEFAULT_REGION} \
      | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com

  if [[ "${BUILD_CMD}" != "" ]]; then
    ${BUILD_CMD}
  fi
  if [[ "${BUILD_CMD_ONLY}" != "yes" ]]; then
    trace_on
    pwd
    if [[ "${STAGING}" == "prod" && "${OUTPUT}" == "out" ]]; then
      rm -Rf out && mkdir out
      export DOCKER_BUILDKIT=1
      docker build -f Dockerfile -t ${REPOSITORY_TAG} . \
        --build-arg NODE_ENV=${NODE_ENV} \
        --build-arg STAGING_ENV=${STAGING_ENV} \
        --build-arg FONT_AWESOME_TOKEN=${FONT_AWESOME_TOKEN} \
        --output out
    fi
    # docker build --no-cache -f Dockerfile -t ${REPOSITORY_TAG} . --build-arg NODE_ENV=${NODE_ENV} --build-arg STAGING_ENV=${STAGING_ENV} --build-arg FONT_AWESOME_TOKEN=${FONT_AWESOME_TOKEN} --output out
    docker build --no-cache -f Dockerfile -t ${REPOSITORY_TAG} . \
      --build-arg NODE_ENV=${NODE_ENV} \
      --build-arg STAGING_ENV=${STAGING_ENV} \
      --build-arg FONT_AWESOME_TOKEN=${FONT_AWESOME_TOKEN}
    if [[ $? != 0 ]]; then
      echo "Error occurred!"
      alert_slack
      exit 1
    fi
    IMG_TAG=(${REPOSITORY_TAG//:/ })
    if [[ "${STAGING}" == "prod" ]]; then
      echo docker image tag ${REPOSITORY_TAG} ${IMG_TAG[0]}:latest
      docker image tag ${REPOSITORY_TAG} ${IMG_TAG[0]}:latest
    elif [[ "${STAGING}" == "staging" || "${STAGING}" == "qa" ]]; then
      echo docker image tag ${REPOSITORY_TAG} ${IMG_TAG[0]}:qa
      docker image tag ${REPOSITORY_TAG} ${IMG_TAG[0]}:qa
    fi
    trace_off
  fi
elif [[ "${ACTION}" == "push" ]]; then
  k8s_init
  echo "#######################################"
  echo Push image
  echo "#######################################"
  trace_on
  aws ecr get-login-password --region ${AWS_DEFAULT_REGION} \
    | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com
  docker push ${REPO_HOST}/${IMAGE_TAG}
  if [[ $? != 0 ]]; then
    echo "Error occurred!"
    alert_slack
    exit 1
  fi
  IMG_TAG=(${REPOSITORY_TAG//:/ })
  if [[ "${STAGING}" == "prod" ]]; then
    echo docker push ${IMG_TAG[0]}:latest
    docker push ${IMG_TAG[0]}:latest
  elif [[ "${STAGING}" == "staging" || "${STAGING}" == "qa" ]]; then
    echo docker push ${IMG_TAG[0]}:qa
    docker push ${IMG_TAG[0]}:qa
  fi
  trace_off
elif [[ "${ACTION}" == "apply" ]]; then
  echo "#################################"
  echo "APP_NAME: ${APP_NAME}"
  echo "STAGING: ${STAGING}"
  echo "BRANCH_ROLLOUT: ${BRANCH_ROLLOUT}"
  echo "SOURCE_K8S_FILE: ${SOURCE_K8S_FILE}"
  echo "NAMESPACE: ${NAMESPACE}"
  echo "PROJECT: ${PROJECT}"
  echo "KUBECTL: ${KUBECTL}"
  env
  echo "#################################"
  k8s_file

  echo "#######################################"
  echo apply to k8s
  echo "#######################################"
  trace_on
  ${KUBECTL} apply -f ${TARGET_K8S_FILE}
  trace_off

  if [[ "${USE_ARGOCD}" == "true" ]]; then
    echo "#######################################"
    echo commit and push the char to git repo
    echo "#######################################"
    pwd

    git clone "https://${GITHUP_ID}:${GITHUP_TOKEN}@github.com/${GITHUP_ID}/tz-argocd-repo.git" tz-argocd-repo
    argocd_init_yn='true'
    if [ -d tz-argocd-repo/${APP_NAME} ]; then
      argocd_init_yn='false'
    fi
    rm -Rf tz-argocd-repo/${APP_NAME}
    mkdir -p tz-argocd-repo/${APP_NAME}
    trace_on
    cp ${TARGET_K8S_FILE} tz-argocd-repo/${APP_NAME}
    trace_off

    pushd `pwd`
    cd tz-argocd-repo
    git add .
    git config user.email ${GIT_COMMITTER_EMAIL}
    git config --global --add safe.directory /home/jenkins/agent/workspace/${APP_NAME}
    git commit -m 'Update chart'
    git remote set-url origin "https://${GITHUP_ID}:${GITHUP_TOKEN}@github.com/${GITHUP_ID}/tz-argocd-repo.git"
    git push origin main -f
    echo "#######################################"
    echo remove working dirs
    echo "#######################################"
    rm -Rf tz-argocd-repo

#    if [[ "${argocd_init_yn}" == "true" ]]; then
      echo "argocd_init"
      argocd_init
#    else
      echo "argocd app sync ${APP_NAME}"
      argocd app sync ${APP_NAME}
#    fi
    pushd
  fi

  if [[ "$(kubectl get csr -o name)" != "" ]]; then
    kubectl get csr -o name | xargs kubectl certificate approve
  fi

  if [[ "${BACKUP}" == "true" && "${BACKUP_LABEL}" != "" ]]; then
    echo "#######################################"
    echo velero backup create
    echo "#######################################"
    BACKUP_LABEL=(`echo ${BACKUP_LABEL} | tr ',' ' '`)
    selector=""
    for label in "${BACKUP_LABEL[@]}"; do
      selector="${selector} --selector ${label}"
    done
    cmd="velero backup create ${APP_NAME} ${selector} -n velero"
    echo ${cmd}
    export KUBECONFIG="${WORKSPACE}/resources/kubeconfig_eks-main"
    `${cmd}`
    velero schedule create ${APP_NAME} --schedule="@every 10m" \
      --include-namespaces ${APP_NAME} \
      --ttl 24h0m0s \
      -n velero
  fi

elif [[ "${ACTION}" == "delete" ]]; then
  echo "#######################################"
  echo delete in k8s
  echo "#######################################"
  k8s_file

  trace_on
  ${KUBECTL} delete -f ${TARGET_K8S_FILE}
  if [[ $? != 0 ]]; then
    echo "Error occurred!"
  fi
  trace_off

#  if [[ "${USE_ARGOCD}" == "true" ]]; then
#    echo "#######################################"
#    echo delete in argocd
#    echo "#######################################"
#    argocd app delete ${APP_NAME}
#  fi
elif [[ "${ACTION}" == "verify" ]]; then
  trace_on
  DEPLOYMENT=${APP_NAME}
  if [[ "$2" != "" ]]; then
    DEPLOYMENT=${2}
  fi
  ${KUBECTL} rollout status deployment/${DEPLOYMENT} --timeout=120s
  if [[ $? != 0 ]]; then
    echo "Failed to deploy in k8s!!!"
    alert_slack
    exit 1
  fi
  trace_off
elif [[ "${ACTION}" == "s3" ]]; then
  echo "#######################################"
  echo "DIST: ${DIST}"
  echo "S3_BUCKET: ${S3_BUCKET}"
  echo "DIST_DOCKER: ${DIST_DOCKER}"
  echo "CLOUDFRONT_ID: ${CLOUDFRONT_ID}"
  echo "#######################################"
  trace_on

  # aws s3 rm s3://${S3_BUCKET} --recursive
  if [[ "${DIST}" != "" && "${S3_BUCKET}" != "" ]]; then
    aws s3 cp --recursive ./${DIST}/ s3://${S3_BUCKET} --region ${AWS_DEFAULT_REGION}
    if [[ $? != 0 ]]; then
      echo "Failed to push to s3!!!"
      alert_slack
      exit 1
    fi
  elif [[ "${DIST_DOCKER}" != "" && "${S3_BUCKET}" != "" ]]; then
    docker run -d --rm ${REPOSITORY_TAG}
    sleep 10
    DOCKER_ID=`docker ps | grep ${REPOSITORY_TAG} | awk '{print $1}'`
    docker cp ${DOCKER_ID}:${DIST_DOCKER} dist_docker
    ls -al dist_docker
    docker kill ${DOCKER_ID}
    aws s3 cp --recursive ./dist_docker/ s3://${S3_BUCKET} --region ${AWS_DEFAULT_REGION}
    if [[ $? != 0 ]]; then
      echo "Failed to push to s3!!!"
      alert_slack
      exit 1
    fi
  fi

  if [[ "${CLOUDFRONT_ID}" != "" ]]; then
    aws cloudfront create-invalidation --distribution-id ${CLOUDFRONT_ID} --paths '/*' --region ${AWS_DEFAULT_REGION}
    if [[ $? != 0 ]]; then
      echo "Failed to invalidate Cloudfront Cache!!!"
      alert_slack
      exit 1
    fi
  fi
  trace_off
elif [[ "${ACTION}" == "slack" ]]; then
  if [[ "${SLACK_HOOK}" == "" ]]; then
    echo "NO SLACK_HOOK!!!"
    exit 1
  fi
  trace_on
  curl -X POST -H 'Content-type: application/json' --data '{"text":"build done '${APP_NAME}': '${BUILD_URL}'"}' ${SLACK_HOOK}
  if [[ $? != 0 ]]; then
    echo "Failed to send message by slack!!!"
    alert_slack
    exit 1
  fi
  trace_off
fi

exit 0
