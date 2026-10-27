"""テストの点数を読み込んで、科目ごとの平均点を表示する。"""

import csv

SUBJECTS = ["国語", "数学", "英語"]


def load_scores(path):
    """CSV を読んで、1行を1人分の辞書にして返す。"""
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def average_by_subject(rows):
    """科目ごとの平均点を計算する。"""
    averages = {}
    for subject in SUBJECTS:
        total = 0
        for row in rows:
            total += int(row[subject])
        averages[subject] = total / len(rows)
    return averages


def main():
    rows = load_scores("scores.csv")
    print(f"{len(rows)}人分の点数を読み込みました。")
    print("--- 科目ごとの平均点 ---")
    for subject, average in average_by_subject(rows).items():
        print(f"{subject}: {average:.1f}点")


if __name__ == "__main__":
    main()
