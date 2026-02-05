# 근사 타입

go에는 원래 제네릭 문법이 존재하지 않았지만 1.18 버전부터 정식 기능이 됨.

[https://go.dev/blog/intro-generics](https://go.dev/blog/intro-generics)

go의 제네릭에서 `~` 기호는 underlying type이 특정 타입인 모든 타입을 의미한다.

- `~string` 은 underling type이 `string`인 모든 타입을 의미함.
- 이는 `string` 타입 자체뿐 아니라 `type MyString string`으로 선언된 모든 사용자정의 타입도 포함.

```go
package main

import (
	"fmt"
)

type nostring string

type rootString interface {
	~string
}

func foo[T string](s T) {
	fmt.Println(s)
}
func bar[T rootString](s T) {
	fmt.Println(s)
}
func main() {
	var s1 nostring = "hi1"
	foo(s1) // <-- nostring does not satisfy string (possibly missing ~ for string in string)
	bar(s1)
}
```

해당 코드를 보면 왜 ~를 사용하는지 알 수 있다.

추가로 `"golang.org/x/exp/constraints"` 패키지를 사용하면

```go
type Unsigned interface {
	~uint | ~uint8 | ~uint16 | ~uint32 | ~uint64 | ~uintptr
}
```

처럼 잘 정리되어 있는 타입들이 많기 때문에 적절히 임포트해서 사용하는 것도 좋아보임
