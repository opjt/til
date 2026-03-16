<!-- markdownlint-disable MD033 -->

# 컨테이너 런타임 레이어

## 레이어 정리

우리가 일상에서 컨테이너를 띄우는 것은 아주 고수준의 레이어인 docker 커맨드(cli)를 사용해서 띄우게 된다

하지만 hostOS의 cgroup을 조절하고 namespace를 설정하는 건 마법처럼 뚝딱되는 것이 아니다

컨테이너가 실행되기까지 여러 레이러를 거치는데 각 레이어가 무슨역할을 하는지 정리해본다

```bash
사용자 / 오케스트레이터 (docker, nerdctl)
        ↓
high-level runtime (containerd, CRI-O)
        ↓
shim (containerd-shim-runc-v2)
        ↓
OCI runtime (runc, crun)
        ↓
Linux kernel
```

**high-level runtime**: 이미지 pull, 스토리지, 네트워크 조율을 담당한다. 이미지를 rootfs + config.json으로 구성된 OCI bundle로 변환해서 shim을 통해 OCI
runtime(`runc`)에 넘긴다.

**shim**은 containerd 같은 하이레벨 런타임이 죽어도 컨테이너가 유지되도록 분리해주는 역할을 한다.

- 컨테이너 프로세스의 부모역할을 맡게 되는데, 만약 containerd 가 컨테이너들을 자식 프로세스로 지니고 있으면 containerd가 죽고나서 관리가 안된다

```bash
# shim이 없을 경우
containerd 죽음
    → 컨테이너 프로세스는 살아있음
    → 근데 exit code를 수거할 놈이 없음
    → stdio 연결이 끊김
    → 다시 살아난 containerd가 컨테이너 상태를 모름
# shim이 중간에 있으면?
containerd 죽음
    → shim은 살아있음
    → 컨테이너 프로세스의 부모 = shim
    → exit code, stdio 다 shim이 들고 있음
    → containerd 재시작 후 shim에 다시 연결
    → 컨테이너 상태 복구 가능
```

그 밑에 레이어가 `OCI runtime` 이다 (편하게 runc라고함)  
runc는 [OCI Runtime Spec](https://github.com/opencontainers/runtime-spec/blob/main/runtime.md)에 정의된 5개의 operation을 구현한다

```bash
create  → namespace, cgroup 설정. 프로세스는 블로킹 상태
start   → exec()으로 실제 프로세스 실행
state   → 현재 상태 JSON 출력
kill    → 시그널 전송
delete  → 리소스 정리
```

- start 후 runc는 종료된다. runc는 컨테이너를 띄우는 역할까지만 하고, 이후 컨테이너 프로세스의 부모는 shim이 맡는다.

```bash
runc create  → namespace, cgroup 설정. 프로세스 블로킹
runc start   → exec()으로 실제 프로세스 실행
runc exits   → runc 프로세스 자체는 종료
              이후 컨테이너 프로세스의 부모 = shim
```

runc는 리눅스 커널이 제공하는 기능들을 syscall로 호출하여 격리 환경을 구성한다.

```bash
namespaces   → 프로세스 격리
cgroups      → 리소스 제한
seccomp      → syscall 필터링
capabilities → root 권한 세분화
```

<style>
  svg text { font-family: sans-serif; }
  .t  { font-size: 14px; fill: #1a1a1a; }
  .ts { font-size: 12px; fill: #555550; }
  .th { font-size: 14px; font-weight: 500; fill: #1a1a1a; }

  /* color ramps */
  .c-gray   > rect, .c-gray   > circle { fill: #F1EFE8; stroke: #5F5E5A; }
  .c-gray   > text.th, .c-gray > text.t { fill: #444441; }
  .c-gray   > text.ts { fill: #5F5E5A; }

  .c-blue   > rect { fill: #E6F1FB; stroke: #185FA5; }
  .c-blue   > text.th, .c-blue > text.t { fill: #0C447C; }
  .c-blue   > text.ts { fill: #185FA5; }

  .c-amber  > rect { fill: #FAEEDA; stroke: #854F0B; }
  .c-amber  > text.th, .c-amber > text.t { fill: #633806; }
  .c-amber  > text.ts { fill: #854F0B; }

  .c-teal   > rect { fill: #E1F5EE; stroke: #0F6E56; }
  .c-teal   > text.th, .c-teal > text.t { fill: #085041; }
  .c-teal   > text.ts { fill: #0F6E56; }

  .c-purple > rect { fill: #EEEDFE; stroke: #534AB7; }
  .c-purple > text.th, .c-purple > text.t { fill: #3C3489; }
  .c-purple > text.ts { fill: #534AB7; }

  .c-green  > rect { fill: #EAF3DE; stroke: #3B6D11; }
  .c-green  > text.th, .c-green > text.t { fill: #27500A; }
  .c-green  > text.ts { fill: #3B6D11; }

  .c-coral  > rect { fill: #FAECE7; stroke: #993C1D; }
  .c-coral  > text.th, .c-coral > text.t { fill: #712B13; }
  .c-coral  > text.ts { fill: #993C1D; }

  .arr {
    stroke: #888780;
    stroke-width: 1.5;
    fill: none;
  }
</style>
<svg width="100%" viewBox="0 0 680 740" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="#888780" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- 1. 사용자 -->
  <g class="c-gray">
    <rect x="40" y="30" width="600" height="50" rx="10" stroke-width="0.5"/>
    <text class="th" x="340" y="50" text-anchor="middle" dominant-baseline="central">사용자 / 오케스트레이터</text>
    <text class="ts" x="340" y="68" text-anchor="middle" dominant-baseline="central">docker CLI · kubectl · 직접 호출</text>
  </g>

  <line x1="340" y1="80" x2="340" y2="108" class="arr" marker-end="url(#arrow)"/>
  <text class="ts" x="356" y="97" dominant-baseline="central" fill="#888780">명령</text>

  <!-- 2. High-level runtime -->
  <g class="c-blue">
    <rect x="40" y="108" width="600" height="50" rx="10" stroke-width="0.5"/>
    <text class="th" x="340" y="128" text-anchor="middle" dominant-baseline="central">high-level runtime</text>
    <text class="ts" x="340" y="146" text-anchor="middle" dominant-baseline="central">containerd · CRI-O — 이미지 pull, 스토리지, 네트워크 조율</text>
  </g>

  <line x1="340" y1="158" x2="340" y2="186" class="arr" marker-end="url(#arrow)"/>
  <text class="ts" x="356" y="175" dominant-baseline="central" fill="#888780">bundle 경로 + id</text>

  <!-- 3. shim -->
  <g class="c-amber">
    <rect x="40" y="186" width="600" height="50" rx="10" stroke-width="0.5"/>
    <text class="th" x="340" y="206" text-anchor="middle" dominant-baseline="central">shim</text>
    <text class="ts" x="340" y="224" text-anchor="middle" dominant-baseline="central">containerd-shim-runc-v2 — 데몬 죽어도 컨테이너 유지, stdio·exit code 관리</text>
  </g>

  <line x1="340" y1="236" x2="340" y2="264" class="arr" marker-end="url(#arrow)"/>
  <text class="ts" x="356" y="253" dominant-baseline="central" fill="#888780">OCI 커맨드 호출</text>

  <!-- 4. OCI runtime -->
  <g class="c-teal">
    <rect x="40" y="264" width="600" height="50" rx="10" stroke-width="0.5"/>
    <text class="th" x="340" y="284" text-anchor="middle" dominant-baseline="central">OCI runtime (low-level runtime)</text>
    <text class="ts" x="340" y="302" text-anchor="middle" dominant-baseline="central">runc · crun — create / start / state / kill / delete 구현체</text>
  </g>

  <line x1="340" y1="314" x2="340" y2="342" class="arr" marker-end="url(#arrow)"/>
  <text class="ts" x="356" y="331" dominant-baseline="central" fill="#888780">syscall</text>

  <!-- 5. Linux kernel -->
  <g class="c-purple">
    <rect x="40" y="342" width="600" height="50" rx="10" stroke-width="0.5"/>
    <text class="th" x="340" y="362" text-anchor="middle" dominant-baseline="central">Linux kernel</text>
    <text class="ts" x="340" y="380" text-anchor="middle" dominant-baseline="central">namespaces · cgroups · seccomp · capabilities</text>
  </g>

  <!-- 구분선 -->
  <line x1="40" y1="430" x2="640" y2="430" stroke="#B4B2A9" stroke-width="0.5" stroke-dasharray="4 3"/>
  <text class="ts" x="340" y="420" text-anchor="middle" fill="#888780">OCI runtime이 실행하는 순서</text>

  <!-- lifecycle: create -->
  <g class="c-gray">
    <rect x="40" y="440" width="108" height="44" rx="8" stroke-width="0.5"/>
    <text class="th" x="94" y="457" text-anchor="middle" dominant-baseline="central">create</text>
    <text class="ts" x="94" y="473" text-anchor="middle" dominant-baseline="central">bundle 읽기·fork</text>
  </g>

  <line x1="148" y1="462" x2="176" y2="462" class="arr" marker-end="url(#arrow)"/>

  <!-- CREATED -->
  <g class="c-blue">
    <rect x="176" y="440" width="120" height="44" rx="8" stroke-width="0.5"/>
    <text class="th" x="236" y="457" text-anchor="middle" dominant-baseline="central">CREATED</text>
    <text class="ts" x="236" y="473" text-anchor="middle" dominant-baseline="central">블로킹·hook 실행</text>
  </g>

  <line x1="296" y1="462" x2="324" y2="462" class="arr" marker-end="url(#arrow)"/>

  <!-- start -->
  <g class="c-teal">
    <rect x="324" y="440" width="108" height="44" rx="8" stroke-width="0.5"/>
    <text class="th" x="378" y="457" text-anchor="middle" dominant-baseline="central">start</text>
    <text class="ts" x="378" y="473" text-anchor="middle" dominant-baseline="central">exec() 실행</text>
  </g>

  <line x1="432" y1="462" x2="460" y2="462" class="arr" marker-end="url(#arrow)"/>

  <!-- RUNNING -->
  <g class="c-green">
    <rect x="460" y="440" width="108" height="44" rx="8" stroke-width="0.5"/>
    <text class="th" x="514" y="457" text-anchor="middle" dominant-baseline="central">RUNNING</text>
    <text class="ts" x="514" y="473" text-anchor="middle" dominant-baseline="central">프로세스 실행 중</text>
  </g>

  <line x1="514" y1="484" x2="514" y2="530" class="arr" marker-end="url(#arrow)"/>

  <!-- STOPPED -->
  <g class="c-coral">
    <rect x="460" y="530" width="108" height="44" rx="8" stroke-width="0.5"/>
    <text class="th" x="514" y="547" text-anchor="middle" dominant-baseline="central">STOPPED</text>
    <text class="ts" x="514" y="563" text-anchor="middle" dominant-baseline="central">종료·리소스 잔존</text>
  </g>

  <line x1="460" y1="552" x2="220" y2="552" class="arr" marker-end="url(#arrow)"/>

  <!-- delete -->
  <g class="c-gray">
    <rect x="112" y="530" width="108" height="44" rx="8" stroke-width="0.5"/>
    <text class="th" x="166" y="547" text-anchor="middle" dominant-baseline="central">delete</text>
    <text class="ts" x="166" y="563" text-anchor="middle" dominant-baseline="central">리소스 정리</text>
  </g>

  <line x1="166" y1="574" x2="166" y2="618" class="arr" marker-end="url(#arrow)"/>

  <!-- 소멸 -->
  <g class="c-gray">
    <rect x="112" y="618" width="108" height="44" rx="8" stroke-width="0.5"/>
    <text class="th" x="166" y="635" text-anchor="middle" dominant-baseline="central">소멸</text>
    <text class="ts" x="166" y="651" text-anchor="middle" dominant-baseline="central">non-existent</text>
  </g>

  <!-- state 조회 표시 -->
  <line x1="640" y1="462" x2="640" y2="552" stroke="#B4B2A9" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
  <text class="ts" x="655" y="508" text-anchor="middle" dominant-baseline="central" fill="#888780" transform="rotate(90,655,508)">state 조회 가능</text>
</svg>
