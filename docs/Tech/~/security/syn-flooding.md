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

원래 SYN 패킷에 옵션 정보(SACK, Window Scale, Timestamp 등)이 담긴다.  
SYN cookie는 SYN 패킷을 저장하지 않기 때문에 ACK가 돌아왔을 때 이옵션을 복원할 방법이 없다.

**Linux의 부분적 해결**

Timestamp 옵션은 예외적으로 매 패킷마다 echo back되는 구조(`TSval -> TSecr`)를 활용한다.  
서버가 SYN-ACK 의 TSval 필드에 WScale, SACK 같은 정보를 담아서 보내면 클라이언트가 ACK의 TSecr를 그대로 돌려주기 때문에 이를 사용한다

- 이 방법은 클라이언트가 Timestamp 옵션을 지원하는 경우에만 가능하다.

Timestamp 옵션 구조 (kind=8)

```text
+-------+-------+---------------------+---------------------+
| Kind=8| Len=10|       TSval         |       TSecr         |
+-------+-------+---------------------+---------------------+
  1byte   1byte        4byte                 4byte
```

- `TSval`: 보내는 쪽이 찍는 현재 시각 timestamp value
- `TSecr`: 상대방이 보낸 `TSval`을 그대로 돌려주는 값 timestamp echo reply
