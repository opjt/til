# ioctl

ioctl은 I/O 컨트롤의 줄임말이다

- syscall 중 하나다
- 사용자 레벨에서 커널을 통해 하드웨어 장치를 컨트롤 하기 위해 도와주는 역할을 한다 (일종의 인터페이스 느낌임)

보통 `read`, `write`으로 표현하지 못하는 디바이스 제어를 위한 기능이라고 알려져 있다

- 유닉스의 기본철학은 모든 것은 파일로 관리한다 임
- 하지만 하드웨어 장치를 제어하다 보면 단순 데이터를 주고 받는 것 이상의 제어가 필요할 때가 생김

`man 2 ioctl` 을 입력하여 살펴보자

```c
#include <sys/ioctl.h>

ioctl(int fildes, unsigned long request, ...);
```

- fildes: 제어하려는 장치의 파일 디스크립터
- request: 드라이버에 보낼 명령 코드, 장치마다 정의된 코드가 있음

여기서 request code는 커널 코드에 정의된 상수(매크로)를 살펴보면 알 수 있다 <https://elixir.bootlin.com/linux/v6.19.8/source/include/uapi/linux/kvm.h#L696> 를
살펴보면

```c
#define KVMIO 0xAE
#define KVM_CREATE_VM             _IO(KVMIO,   0x01) /* returns a VM fd */
```

`KVM_CREATE_VM` 이라는 요청의 request값을 볼 수 있다 `_IO()`는 <https://github.com/torvalds/linux/blob/master/include/uapi/asm-generic/ioctl.h> 헤더를 살펴보면
구할 수 있다

```c
#define _IO(type,nr)        _IOC(_IOC_NONE,(type),(nr),0)
#define _IOC(dir,type,nr,size) \
    (((dir)  << _IOC_DIRSHIFT) | \    //     0 << 30
    ((type) << _IOC_TYPESHIFT) | \   //  0xAE << 8
    ((nr)   << _IOC_NRSHIFT) | \     //  0x01 << 0
    ((size) << _IOC_SIZESHIFT))      //     0 << 16
```

를 계산하면 0xAE00 | 0x01로 KVM_CREATE_VM = `0xAE01` 라는 것을 알 수 있다

ioctl 를 호출하고나서 리턴 형태는

- 값 자체를 리턴하거나
- 새 fd를 리턴하거나
- arg로 넘긴 구조체에 채워주거나 등등이 있다

```c
// 1. 값 자체를 리턴
int version = ioctl(fd_kvm, KVM_GET_API_VERSION, 0);
// → 12

// 2. 새 fd를 리턴
int fd_vm = ioctl(fd_kvm, KVM_CREATE_VM, 0);
// → 4 (파일 디스크립터)

// 3. arg로 넘긴 구조체에 채워줌, 리턴값은 0 (성공/실패)
struct kvm_regs regs;
ioctl(fd_vcpu, KVM_GET_REGS, &regs);
// → regs 안에 값이 채워짐
```
