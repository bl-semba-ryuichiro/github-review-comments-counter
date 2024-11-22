# github-review-comments-counter

このプログラムは、指定した GitHub Pull Request に関連するコメント（Issue コメント、Review コメント、Discussion コメント）を取得し、統計を出力するツールです。

## 機能

- Pull Request に紐づく Issue コメント の数を取得。
- Pull Request のコードレビューにおける Discussion コメント を「親コメント」「子コメント」に分けてカウント。
- Pull Request に対する Review コメント をカウント。
- 除外条件として、特定のユーザーやキーワード、内容が空のコメントをフィルタリング可能。

## プロジェクト構造

```text
github-review-comments-counter/
├── LICENSE                # プロジェクトのライセンスファイル
├── README.md              # プロジェクトの説明
├── pyproject.toml         # Python プロジェクト構成ファイル
├── .env                   # 環境変数ファイル
├── .env.example           # 環境変数ファイルのサンプル
├── github_review_counter/ # パッケージディレクトリ
│   ├── __init__.py        # パッケージ初期化ファイル
│   └── client.py          # GitHub API クライアント
├── utils/                 # ユーティリティ関連
│   ├── __init__.py        # パッケージ初期化ファイル
│   └── env.py             # 環境変数処理ヘルパー
└── main.py                # エントリポイントスクリプト
```

## 必要な環境

- Python 3.8 以上
- GitHub Personal Access Token（リポジトリへの読み取り権限が必要）

## インストール

### 1. リポジトリのクローン

```bash
git clone https://github.com/bl-semba-ryuichiro/github-review-comments-counter
```

### 2. 要な依存関係をインストール

```bash
pip install -e .
```

### 3. `.env` ファイルを作成し、必要な環境変数を設定

`.env.example` を元に `.env` ファイルを作成し、以下の環境変数を設定してください。

```shell
cp .env.example .env
```

```text
GITHUB_TOKEN=ghp_your_personal_access_token
```

なお、GitHub の Personal Access Token は `repo` スコープが必要です。

## 使い方

### 環境変数を使用する場合

```bash
python main.py
```

### コマンドライン引数を使用する場合

引数を指定しなかった場合は、環境変数から値が取得されます。

```bash
python main.py --owner your_repo_owner --repo your_repo_name --pr_number 123 \
    --excluded_users github-actions[bot] another-bot \
    --excluded_keywords LGTM "Looks good" Approved
```

## 結果例

プログラム実行時に次のような統計が出力されます。

```text
コメント統計:
Discussion:
  - 親コメント数: 3 件
  - 子コメント数: 7 件
Issue コメント: 4 件
Review コメント: 5 件

Issue コメント: 4 件
  - ユーザー: user1, 内容: このプルリクエストはバグ修正を...
  - ユーザー: user2, 内容: 質問があります。これはどのバ...

Discussion 親コメント: 3 件
  - ユーザー: reviewer1, 内容: この部分のロジックが複雑に...
  - ユーザー: reviewer2, 内容: インデントが崩れています。...

Discussion 子コメント: 7 件
  - ユーザー: user3, 内容: 確かに複雑ですね。リファクタ...
  - ユーザー: user4, 内容: 修正しました。ご確認くださ...

Review コメント: 5 件
  - ユーザー: reviewer3, 内容: 全体的に問題ないと思います...
```

