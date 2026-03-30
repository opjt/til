# syn-flooding

tcp-3way 핸드쉐이크 과정을 잠깐들여다 보면, 클라이언트의 커넥션 요청인 `SYN` 패킷이 들어오면 `SYN-Backlog`에 저장을 하고 이후 서버가 `SYN-ACK` 를 보낸뒤
클라이언트에서 `ACK`를 보내게 되면 해당 소켓은 `SYN-Backlog`에서 `Listen-Backlog`으로 이동된다

이후 `accept()` 시스템콜을 통해 Liten-Backlog(Accept-Backlog)에 있는 소켓을 꺼내간다.

만약 여기서 클라이언트가 `ACK`를 보내지 않는다면?

- `SYN-Backlog` 에 소켓이 계속 쌓이게 된다
- 설정된 큐크기 이상으로 요청이 올 경우 공간이 없어서 drop이 발생

이러한 `syn-flooding`를 막는 방법으로는 백로그의 사이즈를 키우거나 syn-cookie 기능을 사용한다

리눅스 기준으로

```bash
pjt@lima-default:/Users/pjt$ sysctl net.ipv4.tcp_syncookies
net.ipv4.tcp_syncookies = 1
```

`sysctl net.ipv4.tcp_syncookies` 명령어를 통해 활성여부를 확인할 수 있다

## syncookies

syncookies는 소켓을 `SYN-Backlog`에 저장하지 않아 근본적인 문제를 해결한다

큐에 데이터가 쌓이지 않는다면 고갈될 이유도 drop이 발생할 이유도 없기 때문.

**매커니즘**

1. 서버에서 SYN-ACK를 보낼때 아래 값을 HMAC으로 계산한 결과를 seq로 사용한다
   - HMAC(src_ip, src_port, dst_ip, dst_port, timestamp, 비밀키)
   - timestamp를 포함하여 오래된 ACK 재사용 공격을 방지한다
2. 클라이언트가 ACK를 보낸다. 서버는 ack - 1 값을 같은 방식으로 검증하여 정상 연결 여부를 확인한다

### 문제점

원래 SYN 패킷에 옵션 정보(SACK, Window Scale, Timestamp 등)가 담기는데  
syncookie는 seq 번호에 연결 정보를 우겨넣어야 해서 공간이 부족해 이 옵션들이 손실될 수 있다
