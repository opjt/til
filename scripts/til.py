#!/usr/bin/env python3

import os
import sys
import re
from pathlib import Path


def parse_args():
    if len(sys.argv) < 3:
        print("사용법: ./til.py newpost <category> <filename> [description]")
        print('예: ./til.py newpost linux sysctl "커널 파라미터"')
        sys.exit(1)

    category = sys.argv[2].lower()
    filename = sys.argv[3].lower()
    description = sys.argv[4] if len(sys.argv) > 4 else ""

    return category, filename, description


def create_post_file(category, filename):
    """포스트 파일 생성"""
    category_dir = Path("docs/Tech/~") / category
    category_dir.mkdir(parents=True, exist_ok=True)

    post_file = category_dir / f"{filename}.md"

    if post_file.exists():
        print(f"! 파일이 이미 존재합니다: {post_file}")
        return False

    post_file.touch()
    print(f"✓ 파일 생성: {post_file}")
    return True


def format_category_header(category):
    """카테고리 헤더 포맷 (첫 글자 대문자)"""
    return f"### {category.capitalize()}"


def link_already_exists(index_content, category, filename):
    """링크가 이미 존재하는지 확인"""
    link_pattern = rf"\[{filename}\]\({category}/{filename}\.md\)"
    return bool(re.search(link_pattern, index_content))


def update_index(category, filename, description):
    """index.md 업데이트"""
    index_file = Path("docs/Tech/tech_index.md")

    if not index_file.exists():
        print("! index.md 파일을 찾을 수 없습니다")
        return False

    content = index_file.read_text(encoding="utf-8")

    # 이미 존재하는 링크 확인
    if link_already_exists(content, category, filename):
        print(f"! 이미 존재하는 링크입니다: [{filename}]({category}/{filename}.md)")
        return False

    # 링크 생성
    link_text = f"- [{filename}]({category}/{filename}.md)"
    if description:
        link_text += f" - {description}"

    category_header = format_category_header(category)

    # 카테고리 섹션이 있는지 확인
    lines = content.split("\n")
    category_index = -1
    next_category_index = -1

    for i, line in enumerate(lines):
        if re.match(r"^### ", line):
            if line == category_header:
                category_index = i
            elif category_index != -1 and next_category_index == -1:
                next_category_index = i
                break

    # 카테고리가 없으면 맨 앞에 추가
    if category_index == -1:
        content = f"{category_header}\n{link_text}\n\n" + content
        print(f"✓ 카테고리 추가: {category_header}")
    else:
        # 기존 카테고리의 바로 아래에 링크 추가 (맨 위)
        # 헤더 다음 줄 확인
        if category_index + 1 < len(lines) and lines[category_index + 1].strip() == "":
            # 이미 공백이 있으면 그 다음에 삽입
            insert_index = category_index + 2
        else:
            # 공백이 없으면 헤더 바로 다음에 삽입
            insert_index = category_index + 1
        lines.insert(insert_index, link_text)
        content = "\n".join(lines)

    index_file.write_text(content, encoding="utf-8")
    print(f"✓ index.md에 링크 추가")

    return True


def main():
    if len(sys.argv) < 2 or sys.argv[1] != "newpost":
        print("사용법: ./til.py newpost <category> <filename> [description]")
        sys.exit(1)

    category, filename, description = parse_args()

    # 포스트 파일 생성
    create_post_file(category, filename)

    # index.md 업데이트
    if update_index(category, filename, description):
        print("")
        print("✓ 완료! 다음 파일이 준비되었습니다:")
        print(f"  - {category}/{filename}.md")
        print(f"  - index.md 업데이트됨")
    else:
        print("")
        print("! 작업이 취소되었습니다")
        sys.exit(1)


if __name__ == "__main__":
    main()
