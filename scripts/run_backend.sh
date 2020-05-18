#!/usr/bin/env bash
cd $(cd -P -- "$(dirname -- "$0")" && pwd -P)
image_name="rasberry_perception:$1"

# Docker Container = "$SHARE_TOKEN:$SHARE_PASSWORD"
declare -A docker_hub
docker_hub["rasberry_perception:detectron2"]="NAaW3EZzAKpzdRN"

echo "Looking for docker image '${image_name}' locally"

# Attempt to import docker image from a simulated hub hosted on nextcloud
if ! docker image inspect "$image_name" >/dev/null 2>&1 ; then
    echo "Docker image '${image_name}' does not exist locally"
    share_key=""
    share_name=""
    for key in "${!docker_hub[@]}"; do
        if [ $key == $image_name ]; then
            share_key=${docker_hub[$key]}
            share_name="$(echo "${key}" | tr : _).tar.gz"
        fi
    done

    if [ -z "${share_key}" ]; then
        echo "Docker image '${image_name}' also does not exist in the docker hub! Exiting"
        exit 1
    fi

    mkdir "/tmp/rasberry_perception/docker/" -p
    cd /tmp/rasberry_perception/docker/ || exit 1

    if ! [ -f "${share_name}" ]; then
        echo "Downloading ${share_name}"
        curl  -k -u "$share_key" https://lcas.lincoln.ac.uk/nextcloud/public.php/webdav/ -o "${share_name}"
    fi

    echo "Loading container /tmp/rasberry_perception/docker/${share_name} into docker"
    docker load < "${share_name}"

    if ! docker image inspect "$image_name" >/dev/null 2>&1 ; then
        echo "Docker load command has failed"
        exit 1
    fi
fi

# If container exists then launch, else exit
if docker image inspect "$image_name" >/dev/null 2>&1 ; then
    echo "Image '${image_name}' exists locally"
    echo "Starting $image_name"
    docker run --network host --gpus all --name $1_backend --rm -it $image_name
else
    echo "No valid container for backend ${image_name} can be started"
    exit 1
fi
