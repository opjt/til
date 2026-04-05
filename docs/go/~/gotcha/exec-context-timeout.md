# TIL: exec.CommandContext에서 `signal: killed` vs `context deadline exceeded`

## 현상

`exec.CommandContext`로 timeout을 걸었을 때, `cmd.Run()`이 반환하는 `err`는 `context.DeadlineExceeded`가 **아니다**.

```go
ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
defer cancel()

cmd := exec.CommandContext(ctx, "sleep", "10")
err := cmd.Run()

fmt.Println(err) // "signal: killed"
```

## 왜 그런가

`exec.CommandContext`는 context가 cancel되면 내부적으로 **프로세스에 `SIGKILL`을 보낸다**.

그래서 `cmd.Run()`이 반환하는 에러는 OS 레벨의 시그널 에러인 `*exec.ExitError`  
즉 `"signal: killed"` 다.

`context.DeadlineExceeded`는 ctx 자체에 담겨 있고, `cmd.Run()`의 반환값에는 담기지 않는다.

```text
ctx.Err()   → context.DeadlineExceeded
cmd.Run()   → "signal: killed"          ← OS가 프로세스를 죽인 결과
```

## 올바른 timeout 감지 방법

`cmd.Run()` 에러만 보지 말고, **`ctx.Err()`도 함께 체크**해야 한다.

```go
err := cmd.Run()

if err != nil {
    if errors.Is(ctx.Err(), context.DeadlineExceeded) {
        fmt.Println("timeout으로 인한 종료")
    } else {
        fmt.Println("다른 에러:", err)
    }
}
```

## 에러 흐름 정리

```text
timeout 발생
    └─▶ ctx 내부에 DeadlineExceeded 저장  →  ctx.Err() == DeadlineExceeded
    └─▶ exec이 프로세스에 SIGKILL 전송    →  cmd.Run() == "signal: killed"
```

## 관련 타입

| 확인 대상   | 타입              | 값                         |
| ----------- | ----------------- | -------------------------- |
| `ctx.Err()` | `error`           | `context.DeadlineExceeded` |
| `cmd.Run()` | `*exec.ExitError` | `"signal: killed"`         |

## 참고

- `errors.Is(err, context.DeadlineExceeded)`로 체크할 것 (`==` 비교 금지)
- Go 1.20+에서는 `exec.CommandContext`에 `cmd.WaitDelay`를 설정해 SIGKILL 전에 grace period를 줄 수도 있음
