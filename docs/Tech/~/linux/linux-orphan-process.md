# Linux Orphan Process

`orphan`: 고아, 부모를 잃거나 부모가 없어진 아이.

```bash
root@pve:~# echo $$
824904
root@pve:~# ps -fp 824904
UID          PID    PPID  C STIME TTY          TIME CMD
root      824904  824898  0 20:32 pts/0    00:00:00 -bash
root@pve:~#
```

`ps` 명령어로 조회해보면 모든 프로세스에는 부모프로세스가 존재한다.

ssh로 접근하게 된다면

```bash
root@pve:~# echo $$
824904
root@pve:~# ps -fp 824904
UID          PID    PPID  C STIME TTY          TIME CMD
root      824904  824898  0 20:32 pts/0    00:00:00 -bash
root@pve:~# ps -fp 824898
UID          PID    PPID  C STIME TTY          TIME CMD
root      824898     939  0 20:32 ?        00:00:00 sshd: root@pts/0
root@pve:~# ps -fp 939
UID          PID    PPID  C STIME TTY          TIME CMD
root         939       1  0 Jul22 ?        00:16:52 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups
```

이처럼 부모를 타고타고 올라가면 결국 부모 프로세스가 `1`이 나온다.

만약 ssh로 접속 후 프로세스를 실행한다음 ssh 세션을 종료하면, 실행한 프로세스의 부모프로세스는 어떻게 될까?

- 실행된 프로세스가 종료되지 않고 살아 있다면, 해당 프로세스는 고아 프로세스가 되며, PPID는 `1`로 변경된다.

```bash
root@pve:~# ps -o pid,ppid,tty,cmd -p 828084
    PID    PPID TT       CMD
 828084       1 ?        ./main
```

## bash -c "exec ./main &"

`bash -c "exec ./main &"` 명령어를 실행하고 나면 main 프로세스의 ppid 는 무엇이 될까?

### `bash -c`의 의미

```bash
bash -c "..."
```

- 새로운 비대화형 bash 프로세스를 실행.
- 문자열 안의 명령을 실행한 뒤 즉시 종료

즉, 기존 SSH 세션의 bash가 아닌 하위 bash 프로세스가 잠깐 실행되었다가 종료되는 구조이다

### `exec` 커맨드

```bash
exec ./main
```

- 새로운 프로세스를 생성하지 않는다.
- 현재 bash 프로세스를 `./main`으로 치환(replace) 한다.(PID 유지)

```bash
login-bash (PID A)
└─ bash (pid B)
   └─ exec → main (pid B)
```

이런 구조가 됨.

### `&` 가 붙었을 때 흐름

exec 커맨드의 &가 붙으면?

PID B(`./main`)가 백그라운드에서 돌아가며, 다음 작업을 할 수 있도록 프롬포트를 반환하게 됨.

- PID A(로그인 쉘)는 자신이 시작한 명령(`bash -c "...`)이 성공적으로 완료되었다고 판단함
- 이시점에서 PID B는 부모(PID A)가 자신을 관리하지 않고 떠난 상태, 즉 고아 프로세스가 됨.
  - 명령 실행을 완료하였으니 PID B에 대한 관리 책임이 없기 때문.

### 결론

`bash -c "exec ./main &"` 으로 실행하게 되면 main의 PPID는 1이 된다.
