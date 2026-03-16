# nerdctl

- [nerdctl.git](https://github.com/containerd/nerdctl)

nerdctl은 `Docker CLI`처럼 컨테이너를 쉽게 다룰 수 있는 CLI 도구입니다. 단, Docker와 달리 `dockerd` 없이 `containerd`를 직접 사용한다

## Docker와의 차이

Docker는 `dockerd`라는 중간 데몬을 거친다.

```bash
docker CLI → dockerd → containerd  → runc
```

nerdctl은 dockerd 없이 containerd를 직접 찌른다.

```bash
nerdctl → containerd → runc
```

명령어 인터페이스는 Docker와 호환되도록 설계되어 있어서 `docker` 를 `nerdctl` 로 바꿔써도 대부분 동작한다.

```bash
# 거의 동일하게 동작
docker run -it alpine sh
nerdctl run -it alpine sh
```

dockerd가 없으니 그만큼 가볍고, containerd를 직접 다루기 때문에 Kubernetes 환경과 동일한 런타임 스택을 로컬에서 쓸 수 있다는 장점이 있다

## Mac 에서 사용하는 방법

containerd 는 리눅스 커널 기능을 사용하기 때문에 nerdctl을 사용하기 위해서는 containerd가 돌아갈 수 있는 리눅스 환경이 필요합니다.

mac에서는 **lima** 를 사용하여 linux vm 을 마련할 수 있습니다.

```bash
# lima 설치
brew install lima
# lima vm 생성
limactl start
# lima vm 접속
limactl shell [name]
```

접속 이후 nerdctl 명령어를 사용할 수 있습니다

```bash
pjt@lima-default:/Users/pjt/.lima/default$ nerdctl run -it --rm hello-world
docker.io/library/hello-world:latest:                                             resolved       |++++++++++++++++++++++++++++++++++++++|
index-sha256:f7931603f70e13dbd844253370742c4fc4202d290c80442b2e68706d8f33ce26:    done           |++++++++++++++++++++++++++++++++++++++|
manifest-sha256:00abdbfd095cf666ff8523d0ac0c5776c617a50907b0c32db3225847b622ec5a: done           |++++++++++++++++++++++++++++++++++++++|
config-sha256:ca9905c726f06de3cb54aaa54d4d1eade5403594e3fbfb050ccc970fd0212983:   done           |++++++++++++++++++++++++++++++++++++++|
layer-sha256:198f93fd5094f85a71f793fb8d8f481294d75fb80e6190abb4c6fad2b052a6b6:    done           |++++++++++++++++++++++++++++++++++++++|
elapsed: 4.4 s                                                                    total:  16.6 K (3.8 KiB/s)

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (arm64v8)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

- limactl 로 vm 을 만들때 default 탬플릿 설정파일을 기반으로 설치한 경우입니다.

`~/.lima/default/lima.yaml` 를 살펴보면

```yaml
# default/lima.yaml
containerd:
  # Enable system-wide (aka rootful)  containerd and its dependencies (BuildKit, Stargz Snapshotter)
  # Note that `nerdctl.lima` only works in rootless mode; you have to use `lima sudo nerdctl ...`
  # to use rootful containerd with nerdctl.
  # 🟢 Builtin default: false
  system: null
  # Enable user-scoped (aka rootless) containerd and its dependencies
  # 🟢 Builtin default: true (for x86_64 and aarch64)
  user: null
#  # Override containerd archive
#  # 🟢 Builtin default: hard-coded URL with hard-coded digest (see the output of `limactl info | jq .defaultTemplate.containerd.archives`)
#  archives:
#  - location: "~/Downloads/nerdctl-full-X.Y.Z-linux-amd64.tar.gz"
#    arch: "x86_64"
#    digest: "sha256:..."
```

user 부분을 보면 default: true로 되어있는 부분을 통해 rootless로 containerd와 nerdctl을 사용할 수 있습니다.
