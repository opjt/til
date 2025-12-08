# 리눅스 프로세스 권한

프로세스 관점에서 권한은 뭘 의미하는 것일까

프로세스가 시스템 자원에 접근할 때 어떤 권한을 사용할지 정의하는 사용자 식별자 개념이다.

## RUID(Real User ID)

> 내가 진짜야

`RUID` 는 프로세스르 시작한 사용자의 UID이다.

인간 사용자 관점의 프로세스 소유권을 나타낸다.

```bash
stat -c "%u %g" proc/$pid
```

## EUID(Effective User ID)

프로세스가 시스템 자원(포트, 파일)에 접근할 때 권한을 판별하는 데 사용되는 ID이다.

- 해당 프로세스가 어떤 권한으로 실행 중인가? 에 대한 값

```bash
ps -o pid,euid,ruid,cmd -p <pid>
```

## SUID(Set User ID)

[setuid](./rws.md) 프로그램이 원래 권한(EUID)로 돌아가도록 하기 위한 백업 슬롯이다

- `SUID` 프로그램 실행 시 `EUID`가 파일 Owner ID로 바뀜
- 그 순간의 `EUID` 값을 `Saved UID` 에 저장
- 프로세스가 권한을 낮췄다가 다시 올릴 필요가 있을 때 가져와서 사용.

`Saved UID`는 원래 `EUID`를 저장함.
