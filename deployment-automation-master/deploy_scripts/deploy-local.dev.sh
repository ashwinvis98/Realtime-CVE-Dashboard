#!/bin/sh
#
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

kubectl $OPERATION -f ../compose_files/backend/service.yaml

kubectl $OPERATION -f ../compose_files/frontend/deployment.yaml

kubectl $OPERATION -f ../compose_files/frontend/service.yaml
kubectl $OPERATION -f ../compose_files/ingress.yaml
