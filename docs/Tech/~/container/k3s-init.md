# k3s 설치

- k3s는 경량화된 쿠버네티스 배포판이다.
- 설치가 복잡한 k8s와 달리 매우 간단하게 셋업이 가능하다.

## install script

```bash
curl -sfL https://get.k3s.io | sh -

sudo chmod 644 /etc/rancher/k3s/k3s.yaml # kubectl을 위한 권한

# 설치 확인
kubectl get nodes
```

## 내 mac에서 kubectl로 관리

```bash
# 서버에서 입력
sudo cat /etc/rancher/k3s/k3s.yaml # 내용 복사

# my mac
touch ~/.kube/k3s_config.yaml # 붙여넣기.

# 환경변수 수정
vi ~/.zshrc
export KUBECONFIG=~/.kube/config:~/.kube/k3s_config.yaml
source ~/.zshrc

kubectl config get-contexts # 등록된 컨텍스트 표시
kubectl config rename-context default klab # 이름 헷갈리지 않게 수정.
kubectl config use-context klab # 현재 컨텍스트 수정.
```
