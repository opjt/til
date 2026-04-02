# Go GC

많은 사람들이 알고있는 부분으로, Go는 Google에서 만든 언어이다.  
Google에 Go를 검색하면 유명한 Go 의 아버지들이 있다.

ken thompson, rob pike 등

문득 든 생각으로 왜 이런 사람들이 Go를 디자인할 때 GC를 넣기로 했을까?

그 이유를 알기 위해서는 Go의 탄생비화에 대해 알아야한다.

## Hello Go

<https://go.dev/talks/2012/splash.article#TOC_1.>

Go는 Google이 자사 문제를 해결하기 위해 설계한 프로그래밍 언어

구글은 몇가지 큰 문제들을 안고 있었다.

하드웨어 규모도 크고 소프트웨어 규모도 방대한 구글에서 c++ 바이너리 하나를 빌드하는 데 **45분**이나 걸리던 시절이 있었다.  
뿐만 아니라

- 서버 코드 대부분이 C++ 나머지는 Java ,Python
- 엔지니어 수천 명이 하나의 거대한 코드베이스를 공유
- C++ 소스 4.2MB가 전처리 후 컴파일러 입력 8GB로 팽창 (2000배)
- 전용 대규모 분산 컴파일 시스템을 만들었는데도 빌드가 수십분이 걸림

> Go의 목적은 프로그래밍 언어 연구가 아니라 설계자와 동료들의 개발 환경을 개선하는 것이다

## 왜 GC를 넣었나

Go를 만든 이유를 이해하면 GC를 도입한 이유가 자연스레 따라온다.

수천 명의 엔지니어가 협업하는 환경에서 메모리 관리는 여러 문제를 만든다

- 이 포인터는 누가 free해줘야 하지? 라는 소유권 문제가 시스템 설계에 스며들게 된다.
- **동시성 환경**에서 ownership 추적이 어려워진다

pike, thompson 은 Plan 9, unix 세대이며 이들은 이미 C로 수십년을 살아왔다.  
수동 메모리 관리의 고통을 누구보다 잘 안다

- 메모리 안전성을 언어가 보장하되, 프로그래머는 그걸 신경쓰지 않아도 되게 하자

[Complexity is multiplicative](https://commandcenter.blogspot.com/2023/12/simplicity.html)

소유권 모델을 없애는 대신 GC를 넣으면 언어 문법이 단순해지고, 동시성 모델도 단순해지고 결과적으로 팀 협업이 쉬워진다. (결국 엔지니어링 trade-off 라고 할 수
있다.)

## Go GC는 Java GC와 다르다

GC라고 하면 자바의 긴 Stop-the-world 를 떠올리는 사람이 많다.  
Go Team도 이 불신을 잘 알고 있었고, 설계 단계부터 다르게 접근했다

가장 큰 차이는 **Value Semantics(Go)** 와 **Reference Semantics(Java)** 에서 비롯된다.

Java는 객체를 다룰 때 항상 **참조(reference)** 를 통한다.  
필드 하나하나가 독립적인 힙 객체를 가리키는 포인터다.

Go는 기본이 **값(value)** 이다.  
struct 안에 데이터가 직접 들어간다.

이 차이가 GC 동작 방식 전체를 바꾼다.

```go
type X struct {
    a, b, c int
    buf [256]byte
}
```

Java였다면 `buf`는 별도 힙 객체로 할당되고 포인터로 참조된다.

```text
힙:
[ X 객체 ] ──→ [ byte[] 객체 ]
  할당 1번         할당 2번
  GC 추적 2개
```

Go는 `buf`가 struct 안에 직접 들어간다.

```text
힙:
[ X 전체 (a, b, c, buf 통째로) ]
  할당 1번
  GC 추적 1개
```

객체 100만 개를 만들면:

```text
Java: 힙 객체 200만 개 (X 100만 + buf 100만)
Go:   힙 객체 100만 개
```

- GC가 추적해야 할 대상이 절반으로 줄어든다.

### Interior Pointer

Go는 struct 내부 주소를 직접 참조할 수 있다.

```go
p := &x.buf[0]       // struct 중간을 직접 가리킴
f.Read(x.buf[:])     // 새 버퍼 할당 없이 직접 I/O에 넘김
```

Java는 이게 불가능하다.  
Java GC는 메모리 압축을 위해 객체를 **이동**시키는데,  
객체가 이동하면 내부를 가리키던 포인터 주소가 깨진다.  
그래서 언어 수준에서 아예 막아버렸다.

```text
Java GC (moving):
객체를 옮겨서 메모리 압축 → 단편화 없음
대신 interior pointer 불가

Go GC (non-moving):
객체를 옮기지 않음 → interior pointer 가능
대신 메모리 압축 없음
```

둘 다 trade-off다

### Go가 단편화를 버티는 이유

메모리 압축을 안 하면 단편화가 생길 수 있다.  
Go가 괜찮은 이유는 세 가지다.

**size class** — Go 런타임은 TCMalloc에서 가져온 아이디어로, 객체 크기별로 분류된 풀에서 할당한다.  
같은 크기끼리 모여있어서 해제 후에도 딱 맞게 재사용되어 단편화가 덜 심각하다.

**힙 객체 수 자체가 적다** — struct inline 덕분에  
Java보다 GC 추적 대상이 훨씬 적다.

**escape analysis** — 단명 객체는 애초에 스택에 올라간다.
