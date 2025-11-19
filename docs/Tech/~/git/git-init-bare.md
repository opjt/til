# git bare

일반적으로 git을 활용할 때 원격 저장소로 `github` 나 `gitlab` 을 사용하지만 그런 외부 서비스 없이도 git을 사용하는 방법이 있다

## 너 내 원격지가 되라

SSH로 접속가능한 서버에서 `git init --bare .` 를 입력하게 되면 현재 위치하고 있는 디렉토리가 원격지가 된다

```bash
ubuntu@cont:~/git$ ll
total 40
drwxrwxr-x 7 ubuntu ubuntu 4096 Nov 19 03:13 ./
drwxr-x--- 8 ubuntu ubuntu 4096 Nov 19 03:13 ../
drwxrwxr-x 2 ubuntu ubuntu 4096 Nov 19 03:11 branches/
-rw-rw-r-- 1 ubuntu ubuntu   66 Nov 19 03:12 config
-rw-rw-r-- 1 ubuntu ubuntu   73 Nov 19 03:11 description
-rw-rw-r-- 1 ubuntu ubuntu   21 Nov 19 03:12 HEAD
drwxrwxr-x 2 ubuntu ubuntu 4096 Nov 19 03:11 hooks/
drwxrwxr-x 2 ubuntu ubuntu 4096 Nov 19 03:11 info/
drwxrwxr-x 7 ubuntu ubuntu 4096 Nov 19 03:13 objects/
drwxrwxr-x 4 ubuntu ubuntu 4096 Nov 19 03:11 refs/
```

`git init` 명령어는 일반적으로 현재 디렉토리에 작업 디렉토리와 `.git` 폴더를 모두 포함하는 로컬 저장소를 생성하지만  
`--bare` 옵션을 사용하면 해당 디렉토리를 원격 저장소로 사용할 수 있음.

```bash
git clone ubuntu@192.168.50.203:git
```

clone시에는 scp 명령어를 이용하는 것처럼 위와 같이 사용하면 된다.

github 에서 clone시에 `HTTPS`, `SSH` 등 여러 방법이 있는데 `SSH`를 사용하는 방식과 동일하다.
