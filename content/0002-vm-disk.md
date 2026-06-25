---
title: "VM 디스크 이미지 포맷(qcow2, raw, vmdk)은 무엇이 다른가?"
preview: "Lima가 시작할 때 .img 파일을 다운로드하고 qcow2로 변환한다. 이 변환이 왜 필요한지, 각 포맷의 trade-off가 무엇인지 알아야 imgutil 코드가 이해된다."
tags: [vm]
---

## 핵심 개념

| 포맷       | 특징                               |
| ---------- | ---------------------------------- |
| `raw`      | 섹터 1:1 매핑. 빠르지만 큼         |
| `qcow2`    | Copy-on-Write, sparse, 스냅샷 지원 |
| `vmdk`     | VMware 포맷, 이식성                |
| `vhd/vhdx` | Microsoft 포맷, Hyper-V/WSL2       |

**Sparse file**: 파일 시스템이 실제 기록된 블록만 디스크에 저장한다. `du -sh` vs `ls -lh` 값이 다른 이유.
