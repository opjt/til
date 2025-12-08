# Defer

`defer`는 연기하다, 지연되다 라는 뜻으로 go에서는 함수가 리턴되기 전까지 실행을 지연시키는 문법으로 사용됩니다.

- [A Tour of Go(defer)](https://go.dev/tour/flowcontrol/12) 참고.

몇 가지 특이사항으론

- `LIFO` 처리, 맨마지막에 등록된 `defer`부터 처리됨

## defer로 panic 핸들링

- [Don't Panic](https://go.dev/wiki/CodeReviewComments#dont-panic)

함수에서 만약 패닉을 일으킬 수 있을 때 해당 패닉을 잡아서 에러로 리턴할 수가 있음.

```go
package main

import "fmt"

func main() {

	if err := test(); err != nil {
		fmt.Printf("hi, %v", err)
	}
}

func test() (err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("error here")
		}
	}()

	// some logic
	panic("hi")

	return nil

}
```

- go의 named return을 사용하여 처리할 수 있다.
- 라이브러리에서 panic을 유발한다면 유용하게 사용할 수 있음.

## 인자 즉시 평가

`defer`는 함수 호출 자체는 지연시키지만, 그 함수에 전달되는 값은 `defer` 코드를 만나는 순간 확정(평가)됨.

```go
package main

import "fmt"

func main() {
	a := 10

	// 1. defer 선언 시점의 a 값(10)이 복사되어 저장됨
	defer fmt.Println("defer된 값:", a)

	// 2. a의 값을 변경함
	a = 20

	fmt.Println("현재 값:", a)

	// 3. 함수 종료 -> defer 실행
}
```

결과값

```bash
현재 값: 20
defer된 값: 10
```

### 익명 함수(Closure)로 미루기

만약 평가 시점을 나중으로 미루고 싶다면 익명함수로 감싸서 사용할 수 있습니다.  
이 경우 인자 전달이 아니라 변수 캡처가 이뤄지기 때문입니다.

```go
package main

import "fmt"

func main() {
    a := 10

    // 익명 함수로 감쌈 (인자로 넘기지 않음)
    defer func() {
        // 이 함수가 '실행되는 시점'에 a를 참조함
        fmt.Println("defer된 값:", a)
    }()

    a = 20
    fmt.Println("현재 값:", a)
}
```

결과

```bash
현재 값: 20
defer된 값: 20
```
