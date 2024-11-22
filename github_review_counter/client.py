import requests
from utils.env import get_env_var
import re

class GitHubClient:
    def __init__(self, excluded_users=None, excluded_keywords=None):
        """
        GitHub クライアントを初期化。

        :param excluded_users: 除外するユーザーのリスト（省略時は空リスト）
        :param excluded_keywords: 除外するキーワードを含むコメント（正規表現のリスト、例: ["LGTM", "Looks good"]）
        """
        self.token = get_env_var("GITHUB_TOKEN")
        self.excluded_users = excluded_users or []
        self.excluded_keywords = excluded_keywords or []

    def get_pr_comments(self, owner, repo, pr_number):
        """
        PR に関連するコメントを取得し、統計を出力。

        :param owner: リポジトリのオーナー
        :param repo: リポジトリ名
        :param pr_number: Pull Request 番号
        :return: コメント統計情報（dict）
        """
        # Issue コメントを取得
        issue_comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
        print(f"Fetching issue comments from: {issue_comments_url}")
        issue_comments = self._get_all_pages(issue_comments_url)
        filtered_issue_comments = self._filter_comments(issue_comments)

        # Review コメント（ディスカッション）を取得
        review_comments_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        print(f"Fetching review comments from: {review_comments_url}")
        review_comments = self._get_all_pages(review_comments_url)
        filtered_review_comments = self._filter_comments(review_comments)

        # Discussion の親コメントと子コメントをカウント
        parent_comments = [comment for comment in filtered_review_comments if not comment.get("in_reply_to_id")]
        child_comments = [comment for comment in filtered_review_comments if comment.get("in_reply_to_id")]

        # Review コメント（ディスカッション以外）をカウント
        review_feedback_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        print(f"Fetching review feedback from: {review_feedback_url}")
        review_feedback = self._get_all_pages(review_feedback_url)
        filtered_review_feedback = self._filter_comments(review_feedback)

        # コメント統計をログ出力
        self._log_comment_summary("Issue コメント", filtered_issue_comments)
        self._log_comment_summary("Discussion 親コメント", parent_comments)
        self._log_comment_summary("Discussion 子コメント", child_comments)
        self._log_comment_summary("Review コメント", filtered_review_feedback)

        # コメント統計をまとめる
        return {
            "discussion": {
                "parent_comments": len(parent_comments),
                "child_comments": len(child_comments),
            },
            "issue_comments": len(filtered_issue_comments),
            "review_comments": len(filtered_review_feedback),
        }

    def _log_comment_summary(self, category, comments):
        """
        コメントのサマリをログ出力。

        :param category: コメントカテゴリ（例: Issue コメント、Discussion 親コメントなど）
        :param comments: コメントのリスト
        """
        print(f"\n{category}: {len(comments)} 件")
        for comment in comments:
            user = comment.get("user", {}).get("login", "Unknown User")
            body_preview = (comment.get("body", "")[:30] + "...") if len(comment.get("body", "")) > 30 else comment.get("body", "")
            print(f"  - ユーザー: {user}, 内容: {body_preview}")

    def _get_all_pages(self, url):
        """
        ページネーション対応のコメント取得ヘルパー関数。

        :param url: コメントを取得する API エンドポイント
        :return: コメントのリスト（全ページ分）
        """
        headers = {"Authorization": f"token {self.token}"}
        all_comments = []

        while url:
            print(f"Sending GET request to: {url}")
            response = requests.get(url, headers=headers)

            # ステータスコードをデバッグ出力
            print(f"Response status code: {response.status_code}")
            if response.status_code != 200:
                print(f"Response content: {response.text}")
                response.raise_for_status()

            # レスポンスデータを取得
            comments = response.json()
            print(f"Fetched {len(comments)} comments from this page.")
            all_comments.extend(comments)

            # 次のページのリンクを確認
            url = self._get_next_page_url(response.headers)

        return all_comments

    def _filter_comments(self, comments):
        """
        指定したユーザーとキーワードを除外し、内容が空でないコメントリストを返す。

        :param comments: コメントのリスト
        :return: フィルタリングされたコメントのリスト
        """
        filtered = []
        for comment in comments:
            # ユーザーの除外
            if comment.get("user", {}).get("login") in self.excluded_users:
                continue

            # キーワードの除外
            if any(re.search(keyword, comment.get("body", ""), re.IGNORECASE) for keyword in self.excluded_keywords):
                continue

            # 空のコメントを除外
            if not comment.get("body", "").strip():
                continue

            filtered.append(comment)

        excluded_count = len(comments) - len(filtered)
        print(f"Excluded {excluded_count} comments based on users: {self.excluded_users}, keywords: {self.excluded_keywords}, or empty body.")
        return filtered

    def _get_next_page_url(self, headers):
        """
        次のページの URL を取得。

        :param headers: API レスポンスのヘッダー
        :return: 次のページの URL（存在しない場合は None）
        """
        link_header = headers.get("Link", "")
        if not link_header:
            return None

        links = link_header.split(",")
        for link in links:
            parts = link.split(";")
            if len(parts) == 2 and 'rel="next"' in parts[1]:
                # リンクから URL を抽出
                next_url = parts[0].strip()[1:-1]
                print(f"Next page URL found: {next_url}")
                return next_url
        return None