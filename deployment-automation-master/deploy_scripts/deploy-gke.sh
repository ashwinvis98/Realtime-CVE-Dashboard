#!/bin/sh

if [ $1 -eq 1 ]; then
    #gcloud config set project bda-project-05012023
    gcloud container clusters create-auto bda-cluster --region=us-west1
    gcloud container clusters get-credentials bda-cluster --region=us-west1
fi

me=`basename "$0"`
usage() {
    echo "Usage: $me APPLY"
    echo "APPLY - [0-1]"
    exit $1
}

fatal() {
    echo error: $*
    usage 1
}

[ "$1" = -h ] && usage 0
[ $# -lt 1 ] && fatal "$me: No argument provided"

if [ $1 -eq 0 ]; then
    OPERATION=delete
else
    OPERATION=apply

    set -a
    source ./backend.env
    set +a
fi
echo $OPERATION



envsubst < ../compose_files/backend/deployment.yaml > backend-deployment.tmp.yaml
kubectl $OPERATION -f backend-deployment.tmp.yaml
rm backend-deployment.tmp.yaml

kubectl $OPERATION -f ../compose_files/backend/service-gke.yaml

kubectl $OPERATION -f ../compose_files/frontend/deployment.yaml

kubectl $OPERATION -f ../compose_files/frontend/service-gke.yaml
kubectl $OPERATION -f ../compose_files/ingress-gke.yaml

if [ $1 -eq 0 ]; then
    gcloud container clusters delete bda-cluster --region=us-west1
fi