# CPP code snippet

## boilerplate

```cpp

#include <bits/stdc++.h>
using namespace std;

int main() {
	ios_base::sync_with_stdio(false);
	cin.tie(nullptr);
}
```

- `#include <bits/stdc++.h>`: GNU g++ 전용 올인원 헤더, 표준 라이브러리를 거의 전부 포함
- `ios_base::sync_with_stdio(false)`: c표준 IO와 c++ IO의 동기화를 끔, 속도 증가를 위해 사용
- `cin.tie(nullptr)`: cin과 cout 의 tie(묶음)을 해제
  - 기본적으로 cin을 쓰기 전에 cout이 flush되도록 묶여 있는데, 이걸 풀어서 속도를 올림.
