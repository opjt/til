# 도커의 컨테이너 구성 방법

본 글은 [이게 돼요? 도커 없이 컨테이너 만들기 / if(kakao)2022](https://www.youtube.com/watch?v=mSD88FuST80) 영상을 보고 난 후 알게 된 점을 정리한 내용입니다.

## chroot

아주 먼 옛날 최초의 격리 기술이라고 할 수 있는 chroot가 존재하였습니다 **chroot** 는 change root direcotry,말 그대로 루트 디렉토리를 변경하는 것이다

실제 도커 이미지를 통해 chroot 실습

```bash
docker export $(docker create nginx) | tar -C nginx-root -xvf -;
chroot nginx-root /bin/bash
```

하지만 현대 컨테이너 기술에서는 **chroot** 를 사용하지 않는다

- 왜냐? > chroot는 격리된 파일 시스템을 제공하긴 하지만, 가장 큰 문제로 탈옥이 가능하였음
- 그리고 다른 프로세스들이 보임.(파일적으로만 격리된 환경이기 때문)

이러한 문제들을 리눅스의 네임스페이스 기능을 사용하여 해결해보자

## namespace

> 리눅스 커널에서 프로세스들을 서로 격리하기 위해 만든 기능. 각자의 그룹내에서 독립적인 환경을 구성하게 해준다

docker를 사용할때 컨테이너 안에서 ps 를 하면 내 컨테이너의 안의 프로세스들만 보이는데 이러한 부분이 namespace 를 사용해서 격리된 컨테이너 환경을 만드는 것.

unshare 명령어를 통한 마운트 격리 실습

```bash
unshare --mount bin/sh
mkdir new_root
mount -t tmpfs none new_root
mkdir testdir
```

이렇게 명령어를 입력하면 다른 쉘에서는 `testdir`이 보이지 않는 것을 확인 가능.

이렇게 되면 디렉토리가 격리는 되었지만 컨테이너에서 호스트의 루트 디렉토리에 접근할 수 있다

### pivot_root

pivot_root는 루트 디렉토리를 바꾸는 역할이다. 어? 그러면chroot랑 똑같은 거 아닌가요?

- 아님. `pivot_root`는 루트파일 시스템을 완전히 교체한다
- 이는 커널 system call로 `chroot`같은 눈속임 형태와 완전히 다름.

pivot_root 실습

```bash
unshare -m /bin/sh
mount -t tmpfs none new_root
cp -r myroot/* new_root # 리눅스 기본 명령어가 설치된 루트 디렉토리
cd new_root
mkdir old_root
pivot_root . old_root # pivot_root {새로운 루트디렉토리} {기존 루트파일 시스템이 부착될 곳}
cd /

ls / # 격리된 공간과 호스트os에서 비교.
```

이렇게 `pivot_root`를 통해 루트 디렉토리를 바꾸고 old_root를 삭제하게 되면 완전히 격리된 공간이 되는 것.

## Overlay File system

컨테이너 이미지들은 일반적으로 **read-only** 상태로 배포가 된다하지만 컨테이너를 실행하면, 그 이미지 위에 생성되는 변경사항은 유지가 되어야하는데

이때 사용하는 것이 오버레이 파일 시스템이다.

- 오버레이 파일 시스템은 리눅스 커널에 내장된 `합성`파일 시스템이다
- 여러개의 디렉토리를 겹쳐서 하나의 디텍토리처럼 보여주고 싶을 때 사용함 (포토샵의 레이어 개념과 비슷)

overlayFs 실습

```bash
mkdir -p rootfs/{lower_base,lower,upper,merge,work}
echo base > lower_base/base
echo test > lower/file1
mount -t overlay overlay -o lowerdir=lower_base/:lower/,upperdir=upper/,workdir=work/ merge/
ls rootfs/merge
```

이 상태에서

- merge디렉토리에 있는 file1 을 지우게 되면 upper디렉토리에 노란색 글씨로 file1이 생기게 된다
- 이걸 `whute out`이라고 하는데 lower 디렉토리에 있는 원본 파일을 지우지 않고 삭제된 정보가 upper dir에 쓰여지게 되는 것.
- 이런식으로 원본 파일을 지우지 않고 보장할 수 있다.

## Cgroup (Control groups)

지금까지 격리된 공간을 구성하는데 집중하였지만 이제는 hostOS에서 컨테이너 자원을 어떻게 보장할 수 있을까? 에 대해 알아보자

우선 Cgroup에 대해 간단히 알아보면

- 리눅스 커널 기능으로 프로세스들의 리소스 사용랴을 제한하는 기능
- namespace만으로는 리소스를 통제할 수 없음.

만약 특정 컨테이너가 자원을 무한정 끌어다 쓰게 되면 ? 나머지 컨테이너들은 자원을 못받으면서 시스템의 문제가 생김

`mount | grep cgroup` 명령어를 통해 현재 어떤 버전의 cgroup을 사용하는지 알 수 있다.

Cgroup실습

```bash
# 실습에 필요한 패키지 설치
apt install -y cgroup-tools
apt install -y stress

cgcreate -a root -g cpu:mycgroup
tree /sys/fs/cgroup/mycgroup/

cgset -r cpu.max=30000 mycgroup
cgexec -g cpu:mycgroup stress -c 1
# 이후 다른 터미널에서
top
```

- `/sys/fs/cgroup/mycgroup` 경로에 들어가면 `cpu.max` 라는 파일에 `30000 100000` 라고 적혀져 있는 모습을 볼 수 있다
- 이는 100,000 마이크로초(0.1초) 중 30,000 마이크로초(0.03초) 동안만 CPU 사용을 허용한다는 뜻으로, 즉 약 30% CPU 사용 제한을 의미한다
- 이 설정 덕분에 해당 Cgroup에 속한 프로세스들은 cpu자원을 지정한 비율 이상 사용하지 못하게 되어 시스템 자원 과다 사용을 방지할 수 있음
