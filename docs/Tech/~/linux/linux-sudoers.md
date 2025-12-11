# Linux sudoers

[su](./linux_su.md) 명령어로 root 사용자로 전환할 수도 있지만,

`sudo -i` 로도 루트 환경에 진입할 수 있다.

하지만 두 명령어의 차이가 있는데, `sudo -i` 명령어는 사용자의 비밀번호로 루트 권한을 얻을 수 있다는 것.

- 이러면 보안적으로 문제가 되는 것이 아닌가?
- 하지만 일반 사용자에게 루트 비밀번호를 알려주는 게 더 취약함.

일반 사용자가 어디까지 sudo 권한을 얻을 수 있는지 설정하는 것이 `sudoers`다

## visudo

`visudo` 는 sudoers 파일을 수정할 수 있는 명령어다.

직접 `/etc/sudoers` 를 수정하면 안되나요?

- `visudo` 명령어로 수정할 경우 저장 시 문법검사가 이루어짐.
- 애초에 `r` 권한만 있는 경우도 있음.

## sudoers 예시

`username ALL=(ALL) ALL`

- `username`은 모든 호스트=(어떤 사용자/그룹 권한) 모든 명령어 사용 가능의 의미다

`username ALL=(root) /usr/bin/systemctl restart nginx`

- `username`은 루트 권한으로 위 명령어만 사용 가능.
