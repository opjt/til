# OAuth

> OAuth는 권한 위임(Authorization)를 위한 개방형 표준 프로토콜이다.

**[관련 spec]**

- [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749) - The OAuth 2.0 Authorization Framework

## 왜 필요한가?

OAuth가 없던 시절에는 어떻게 하였나

먼저 이해하기 쉽게,

A 서비스에서 사용자의 구글 드라이브 접근권한이 필요하다고 가정해보자

- 사용자가 A서비스에 구글 패스워드를 직접 입력함
- 이후 A서비스가 -> 구글 API를 호출

A서비스가 사용자의 패스워드를 알게 됨, A서비스를 신뢰해야하고 A가 털리면 내 정보도 털리게 됨

OAuth가 해주는 것.

- 사용자 -> 구글한테만 비밀번호 입력 (A서비스는 개입 못 함)
- A서비스는 구글 드라이브 API만 호출 가능한 토큰을 받음 (패스워드는 모름)

A서비스가 털려도 token만 털림, token은 패스워드와 다르게 권한의 scope가 있고 + 만료 기간이 존재

이거에 대한 표준이 OAuth인 것이다

## Role

| 역할                 | 설명               | 예시                 |
| -------------------- | ------------------ | -------------------- |
| Resource Owner       | 진짜 주인 (사용자) | 나                   |
| Client               | 우리가 만드는 앱   | 내 서비스            |
| Authorization Server | 토큰 발급 서버     | Google, Kakao        |
| Resource Server      | 보호된 API 서버    | Drive API, Gmail API |

<!--
```mermaid
sequenceDiagram
    participant User
    participant Client
    participant AuthServer

    User->>Client: 로그인 클릭
    Client->>AuthServer: ?response_type=code&client_id=...
    AuthServer->>User: 로그인 + 동의 화면
    User->>AuthServer: 인증 완료
    AuthServer->>Client: redirect_uri?code=AUTH_CODE
    Client->>AuthServer: code + client_secret
    AuthServer->>Client: access_token, refresh_token
``` -->
