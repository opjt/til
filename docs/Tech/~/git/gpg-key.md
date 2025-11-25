# GPG KEY

GPG(GNU Privacy Guard)는 암호화와 전자 서명을 위한 도구.

git에서도 커밋에 서명을 하기 위해 사용 가능.

Github를 보면 커밋에 `Verified` 라고 표시된 부분을 볼 수 있는데 이게 GPG로 서명한 경우이다.

## GPG 키 만들기

우선 GPG를 설치하겠습니다.

```bash
brew install gpg
```

그다음 key를 생성하겠습니다.

```bash
gpg --full-generate-key
```

명령어를 입력하면 인터렉티브 프롬포트가 활성되는데

키 설정 선택하고, 사용자 정보, 이메일 등을 입력하면 됩니다.

```bash
$ gpg --list-secret-keys --keyid-format LONG

[keyboxd]
---------
sec   ed25519/8BA288F0AB5A68A5 2025-11-24 [SC]
      5A3F2BB8D86D730CC660799B8BA288F0AB5A68A5
uid                 [ultimate] Park jungtae (opjt) <jtpark1957@gmail.com>
ssb   cv25519/C8059F498A8A5664 2025-11-24 [E]
```

위 결과를 기준으로 ed25519 뒤에 있는 8BA288F0AB5A68A5가 KEY 입니다.

git config를 설정하겠습니다.

```bash
git config --global user.signingkey 8BA288F0AB5A68A5
git config --global commit.gpgsign true
# gpgsign을 true로 할경우 매 커밋마다 자동으로 서명됩니다
git config --global gpg.program gpg
```

이제 github에 GPG Public KEY를 등록하기 위해서 공개키를 추출하겠습니다.

```bash
gpg --armor --export 8BA288F0AB5A68A5 # 앞서 확인한 키
```

GPG 키에 passphrase가 설정되어 있는 경우 `GPG_TTY` 환경변수를 설정해주지 않으면 암호를 묻는 화면이 출력되지 않아서 커밋이 찍히지 않을 수도 있습니다.

`export GPG_TTY=$TTY`
