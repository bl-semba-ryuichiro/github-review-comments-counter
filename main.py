import argparse
import os
from github_review_counter.client import GitHubClient
from utils.env import get_env_var


def main():
    # 引数の定義
    parser = argparse.ArgumentParser(description="GitHub Pull Request Comment Analyzer")
    parser.add_argument("--owner", type=str, help="Repository owner", required=False)
    parser.add_argument("--repo", type=str, help="Repository name", required=False)
    parser.add_argument("--pr_number", type=int, help="Pull Request number", required=False)
    parser.add_argument("--excluded_users", type=str, nargs="*", help="Users to exclude from the analysis",
                        required=False, default=[])
    parser.add_argument("--excluded_keywords", type=str, nargs="*", help="Keywords to exclude from comments",
                        required=False, default=[])
    args = parser.parse_args()

    # パラメータを取得（優先順位: 引数 > 環境変数）
    owner = args.owner or get_env_var("GITHUB_OWNER")
    repo = args.repo or get_env_var("GITHUB_REPO")
    pr_number = args.pr_number or int(get_env_var("GITHUB_PR_NUMBER"))
    excluded_users = args.excluded_users or get_env_var("GITHUB_EXCLUDED_USERS", "").split(",")
    excluded_keywords = args.excluded_keywords or get_env_var("GITHUB_EXCLUDED_KEYWORDS", "").split(",")

    # 必須パラメータのチェック
    if not owner or not repo or not pr_number:
        print("Error: 必須パラメータ (owner, repo, pr_number) が不足しています。")
        parser.print_help()
        return

    # クライアントを初期化
    client = GitHubClient(
        excluded_users=[user.strip() for user in excluded_users if user.strip()],
        excluded_keywords=[keyword.strip() for keyword in excluded_keywords if keyword.strip()]
    )

    # コメント統計を取得
    try:
        comment_data = client.get_pr_comments(owner, repo, pr_number)

        parent_comments_num = comment_data['discussion']['parent_comments']
        child_comments_num = comment_data['discussion']['child_comments']
        issue_comments_num = comment_data['issue_comments']
        review_comments_num = comment_data['review_comments']

        print("\nコメント統計:")
        print("Discussion:")
        print(f"  - 親コメント数: {parent_comments_num} 件")
        print(f"  - 子コメント数: {child_comments_num} 件")
        print(f"Issue コメント: {issue_comments_num} 件")
        print(f"Review コメント: {review_comments_num} 件")
        print(f"総レビュー数（※子コメント以外）: {parent_comments_num + issue_comments_num + review_comments_num} 件")
    except Exception as e:
        print(f"エラー: {str(e)}")


if __name__ == "__main__":
    main()
