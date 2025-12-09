# Linux Capability

유닉스 시스템을 이어받은 리눅스에서는 ROOT 사용자가 프로세스를 실행할 때 아무런 제한이 없다.

리눅스는 모든 권한이 있거나, 아니거나 하는 이분법적 세계관을 지니고 있는데,  
커널 v2.2에 캐퍼빌리티 시스템 콜이 도입되면서 이런 세계관이 비틀어졌다.

## root 권한을 나눠줄게

리눅스 `Capability`는 root 권한을 더 세밀하게 분할하여, 특정 권한만을 프로세스에게 부여할 수 있게 하는 기능이다.

```bash
pjt@lima-default:/Users/pjt$ capsh --print
Current: =
Bounding set =cap_chown,cap_dac_override,cap_dac_read_search,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_linux_immutable,cap_net_bind_service,cap_net_broadcast,cap_net_admin,cap_net_raw,cap_ipc_lock,cap_ipc_owner,cap_sys_module,cap_sys_rawio,cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,cap_sys_admin,cap_sys_boot,cap_sys_nice,cap_sys_resource,cap_sys_time,cap_sys_tty_config,cap_mknod,cap_lease,cap_audit_write,cap_audit_control,cap_setfcap,cap_mac_override,cap_mac_admin,cap_syslog,cap_wake_alarm,cap_block_suspend,cap_audit_read,cap_perfmon,cap_bpf,cap_checkpoint_restore
Ambient set =
Current IAB:
... 생략
```

`capsh` 명령어로 현재 프로세스(쉘)의 캐퍼빌리티를 확인할 수 있다.

- `Current`: 현재 프로세스가 실제로 활성화된 캐퍼빌리티
- `Bounding set`

### 자주 사용하는 캐퍼빌리티

| 캐퍼빌리티 이름      | 허용작업                                                |
| -------------------- | ------------------------------------------------------- |
| CAP_NET_BIND_SERVICE | 1024번 미만의 특권 포트에 바인딩할 수 있도록 허용       |
| CAP_CHOWN            | 파일의 소유자(UID/GID)를 임의로 변경할 수 있도록 허용   |
| CAP_KILL             | 다른 사용자에게 속한 프로세스에 신호를 보낼 수 있게 함  |
| CAP_SYS_CHROOT       | chroot의 호출을 허용                                    |
| CAP_SYS_ADMIN        | 파일시스템 마운트를 포함한 시스템 관리 작업을 허용      |
| CAP_SETPCAP          | 실행 중인 프로세스의 캐퍼빌리티를 설정할 수 있도록 허용 |

### 사용 예

만약 당신이 포트 80을 리스닝하는 웹서비스를 올린다고 했을 때 일반 사용자의 경우 `permission denied` 이 뜰것이다.  
리눅스에서는 1024번 미만의 포트(well-known ports)를 특권 포트(privileged ports)로 지정해놨기 때문입니다.

```bash
cat /proc/sys/net/ipv4/ip_unprivileged_port_start
1024
```

- 특권포트 확인.

```bash
sudo stcap cap_net_bind_service=+ep ./myserver
```

로 권한을 주게 되면 정상적으로 실행할 수 있다.

```bash
getcap ./myserver
./myserver cap_net_bind_service=ep
```
