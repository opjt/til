# 브라우저에서 웹사이트 접속 과정

> 브라우저에서 google.com 을 입력하면 일어나는 과정에 대해 설명해 주세요

- os적인 관점에서 설명하면 키보드 인터럽트부터 얘기할 수도 있겠지만 네트워크, 인프라적인 관점에서 정리한다

## DNS

`google.com` 은 사람이 보기 편하고 기억하기 쉽게 만든 도메인으로, 서버에 요청을 보내기 위해서는 IP가 필요함

리눅스의 경우 `/etc/nsswitch.conf` 를 보고 순서를 결정한다

```bash
pjt@lima-default:/Users/pjt$ cat /etc/nsswitch.conf | grep hosts
hosts:          files dns
```

여기서 files 는 `/etc/hosts` 를 의미하고 dns는 `/etc/resolv.conf`의 nameserver에 질의하는 것을 의미

1. `/etc/hosts` 파일 확인(있으면 DNS 조회 없이 바로 접근)
2. `/etc/resolv.conf` 의 nameserver에 질의

`/etc/resolv.conf`의 nameserver는 **Recursive Resolver**를 가리킴

- 8.8.8.8 (Google Public DNS), 1.1.1.1 (Cloudflare) 같은 서버
- 클라이언트 대신 Root -> TLD -> Authoritative DNS를 직접 찾아다니며 재귀 조회
- 조회 결과를 TTL 동안 캐시해서 다음 질의에 바로 반환

Recursive Resolver 가 캐시에 없으면 직접 찾아나선다

- `dig +trace google.com` 을 입력하면 찾는 과정을 트레이싱 가능

## Routing

ip를 얻었으면 ip로 패킷을 보내야 한다.  
OS가 라우팅 테이블을 확인하고 이 IP를 어디로 보낼지 결정함

```bash
pjt@lima-default:/Users/pjt$ ip route
default via 192.168.5.2 dev eth0 proto dhcp src 192.168.5.15 metric 200
10.4.0.0/24 dev nerdctl0 proto kernel scope link src 10.4.0.1
192.168.5.0/24 dev eth0 proto kernel scope link src 192.168.5.15 metric 200
192.168.5.2 dev eth0 proto dhcp scope link src 192.168.5.15 metric 200
```

목적지가 `142.251.23.100(google.com)` 이면?

- `10.4.0.4/24` 범위 x
- `192.168.5.0/24` 범위 x
- `default` -> 192.168.5.2 로 보낸다.
  - 라우팅 테이블은 가장 구체적인 것 부터 매칭을 한다

### ARP

게이트웨이 IP를 알았으면 실제 패킷을 전송하기 위해 MAC 주소가 필요하다.

- MAC 주소는 같은 LAN 구간에서만 사용하는 물리주소이다(NIC의 고유 주소임)

```bash
pjt@lima-default:/Users/pjt$ arp -n
Address                  HWtype  HWaddress           Flags Mask            Iface
192.168.5.2              ether   5a:94:ef:e4:0c:dd   C                     eth0
```

ip로 mac 주소를 얻기 위해 사용하는 프로토콜이 `ARP` 이고 `arp -n` 명령어를 통해 캐시 상태를 확인할 수 있다

캐시에 없으면 broadcast로 같은 LAN 전체에 물어본다

```bash
sudo tcpdump -n -i any arp

# 이후 다른 터미널에서 작업
# arp 캐시 비우기
sudo ip neigh flush all
ping -c 1 google.com
```

```bash
# arp tcpdump 결과
12:53:56.052927 eth0  Out ARP, Request who-has 192.168.5.2 tell 192.168.5.15, length 28
12:53:56.053082 eth0  In  ARP, Reply 192.168.5.2 is-at 5a:94:ef:e4:0c:dd, length 28
```

위처럼 게이트웨이인(192.168.5.2)가 자신의 MAC주소를 응답한다 (커널에서 처리) 이후 ARP 캐시에 저장되어 다음 질의부터는 브로드캐스트 없이 바로 사용한다

MAC 주소를 얻은 뒤에는 OS가 패킷을 이더넷 프레임으로 감싸서 NIC를 통해 물리신호로 변환하여 케이블로 보낸다.

```text
[ Ethernet Header        ] [ IP Header           ] [ TCP Header ] [ Data ]
  src MAC: 내 NIC MAC       src IP: 192.168.5.15
  dst MAC: 5a:94:ef:e4:0c:dd  dst IP: 142.251.x.x
```

프레임이 게이트웨이에 도착하면 아이피 패킷을 확인하여 목적지 아이피를 다시 확인 후 라우팅 테이블을 조회한다.  
이후 똑같에 arp를 요창하여 mac주소를 받고 다음 홉으로 요청을 보낸다. 이 과정을 dst IP에 닿을 때까지 반복한다

### NAT

공유기(사설망)을 벗어나 공인IP 대역으로 넘어갈 때 src IP가 교체된다.  
이때 변환전 source ip를 기록해 두어 응답할 때 본래의 IP를 찾아갈 수 있게 한다.

우리가 쓰는 사설IP(ex 192.168.x.x) 같은 대역은 사설망 전용으로 예약이 되어있고, 라우팅 테이블에 이 대역에 대한 경로가 존재하지 않는다.  
전세계 수백만 곳에서 사용하는 동일한 사설IP를 쓰기 때문에 목적지를 특정할 수 없기 때문
