# GO의 TCP 소켓 backlog 이야기

c 언어를 통해 소켓 프로그래밍을 하다 보면 `listen()` 함수 호출 시 두번째 파라미터는 `backlog` 에 대한 값이다.

하지만 **go** 에서는 이러한 백로그 설정을 할 수 없다?

댓츠노노 그렇지 않다

go는 개발자가 직접 설정할 필요 없이 운영체제가 허용하는 최대 백로그 값을 가져와 자동으로 사용합니다.

## net 패키지로 살펴보자

Go의 `net` 패키지 소스 코드를 통해 Go가 이 최대 백로그 값을 어떻게 결정하는지 살펴보자.

`net/sock_posix.go` 를 보면 `listenerBacklog()`를 호출하여 백로그를 넘겨줌.

```go
// net.go

func listenerBacklog() int {
	listenerBacklogCache.Do(func() { listenerBacklogCache.val = maxListenerBacklog() })
	return listenerBacklogCache.val
}
```

여기서 핵심은 각 플랫폼(운영체제) 별로 다르게 작성된 `maxListenerBacklog()` 함수이다.  
이 함수가 해당 OS에서 허용하는 최대 백로그 값을 가져오는 역할을 함

리눅스의 경우

```go
// sock_linux.go

func maxListenerBacklog() int {
	fd, err := open("/proc/sys/net/core/somaxconn")
	if err != nil {
		return syscall.SOMAXCONN
	}
	defer fd.close()
	l, ok := fd.readLine()
	if !ok {
		return syscall.SOMAXCONN
	}
	f := getFields(l)
	n, _, ok := dtoi(f[0])
	if n == 0 || !ok {
		return syscall.SOMAXCONN
	}

	if n > 1<<16-1 {
		return maxAckBacklog(n)
	}
	return n
}
```

- `/proc/sys/net/core/somaxconn` 에 값에 따라 설정됨을 알 수 있다.
- 만약 값을 읽는 데 실패하거나 0이면 Go에서 정의된 기본값을 사용

그 외에도

```go
//sock_bsd.go

func maxListenerBacklog() int {
	var (
		n   uint32
		err error
	)
	switch runtime.GOOS {
	case "darwin", "ios":
		n, err = syscall.SysctlUint32("kern.ipc.somaxconn")
	case "freebsd":
		n, err = syscall.SysctlUint32("kern.ipc.soacceptqueue")
	case "netbsd":
		// NOTE: NetBSD has no somaxconn-like kernel state so far
	case "openbsd":
		n, err = syscall.SysctlUint32("kern.somaxconn")
	}
    ...
```

BSD 계열 운영체제는 파일 시스템 대신 `sysctl` 시스템 호출을 통해 커널 변수에서 제한 값을 읽어옴.

## 말고도 다른 방법

- 만약 `net` 패키지가 제공하는 자동 설정(OS의 최대치 사용)을 원치 않고 특정한 백로그 값을 직접 설정하고 싶다면  
  유닉스 소켓을 저수준에서 직접 구현할 수도 있다.
