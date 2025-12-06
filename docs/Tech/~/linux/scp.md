# SCP

> SCP(Secure COPY)

> 사실 리눅스 카테고리 라고 하기엔 좀 그렇지만, 리눅스 환경에서 제일 많이 쓰기 때문에 리눅스 카테고리로 넣음.

SCP가 원격지에 파일을 보내거나 가져올 때 사용하는 파일 전송 프로토콜 , 명령어 이다

## SCP 와 SSH

`SCP`는 `SSH` 위에서 동작한다는 점.

- [https://www.openssh.org/txt/release-9.0](https://www.openssh.org/txt/release-9.0) , 9.0 이전에는.

openSSH 9.9 버전부터는 `SCP` 명령어를 실행하면 내부적으로 구식 SCP 프로토콜이 아닌 SFTP 프로토콜을 사용한다.

```bash
scp -O file user@host:/path
```

만약 옛날 형식의 scp를 사용하려면 `-O` 옵션을 사용하면 된다.

## 구형 scp 동작 방식

- [openssh-scp.c](https://github.com/openssh/openssh-portable/blob/master/scp.c)

상세 코드는 위 github에서 볼 수 있다.

```bash

[Client scp]
    |
    | 1. SSH 연결 생성
    |
[Server sshd]
    |
    | 2. scp -t /path 실행
    |
[Server scp -t]
    |
    | 3. 서버 → 클라: \0 (준비됨)
    |
[Client scp]
    |
    | 4. 파일 헤더 전송: "C0644 11 file.txt\n"
    |
    | 5. 파일 내용 전송: "<바이트>"
    |
    | 6. 파일 끝: "\0"
    |
    | 7. 서버 → OK "\0"
```

`SCP` 는 `SSH` 연결 후 stdin/stdout으로 통신하는 구조다 (SSH는 단순히 파이프의 역할을 수행)
