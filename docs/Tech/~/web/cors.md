# CORS 정책

> Cross-Origin Resource Sharing

웹 브라우저가 보안을 위해 기본적으로 적용하는 동일 출처정책(SOP)을 완화하여 다른 출처간의 리소스 공유를 허용하는 매커니즘이다.

- 여기서 출처는 `Origin`을 의미하는데 이는 프로토콜, 도메인, 포트 까지 포함하는 개념이다.
- 프론트와 백엔드 서버가 각각 존재한다면 반드시 마주치는 문제이다.

## 사전 요청

[https://developer.mozilla.org/ko/docs/Glossary/Preflight_request](https://developer.mozilla.org/ko/docs/Glossary/Preflight_request)

`preflight` 요청이라고도 하는데, 브라우저가 실제 요청을 보내기 전에 서버가 지원하는 http method를 확인하기 위해 보내는 요청이다.

### OPTIONS METHOD

`options` 요청을 보낼 때

- `Access-Control-Request-Headers`: 본 요청 시 헤더
- `Access-Control-Request-Method`: 본 요청 시 메소드

헤더를 포함하여 보냄.

그러면 서버에서는 `Access-Control-Allow-Methods` 헤더를 실어서 응답.

## Access-Control-Allow-Origin

[mdn](https://developer.mozilla.org/ko/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Origin)

서버가 브라우저에게 보내는 허가증이다.

A.com에서 B.com에 요청하는 경우 B.com에서 `Access-Control-Allow-Origin` 헤더에 A.com 을 명시해야함 만약 `*` 로 할 경우 모든 도메인에서 해당 자원에 대해 접근할
수 있도록 허용.

## credentials 옵션

[mdn](https://developer.mozilla.org/ko/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Credentials)

JS 진영에서 `fetch`로 요청을 날리는 경우 `credentials` 옵션을 수정할 수가 있다

- include: 도메인이 달라도 무조건 쿠키를 주고받음
- same-origin: (기본값) 같은 origin끼리만 주고받음
- omit: 어떤 상황에서도 주고받지 않음.

만약 `include` 로 설정할 경우 `Access-Control-Allow-Origin`를 `*`로 설정하면 안됨.

서버쪽에선 `Access-Control-Allow-Credentials` 를 true로 설정해야 쿠키를 처리할 수가 있다.

- 브라우저단에서 `OPTIONS` 메서드 돌 때 헤더를 검사하고 false로 되어있으면 요청을 보내지 않음.
