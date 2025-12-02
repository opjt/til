# go snippet

> 알고리즘 문제 풀 때 자주 사용하는 인아웃풋 스닛펫

## n개 숫자 입력 받기

```go
package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	r := bufio.NewReader(os.Stdin)
	w := bufio.NewWriter(os.Stdout)
	defer w.Flush()

	nums := make([]int, n)
	const n = 9

	for i := range nums {
		fmt.Fscan(r, &nums[i])
 	}
 	fmt.Fprintln(w, nums)
}
```
