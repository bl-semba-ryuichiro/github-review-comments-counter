import os
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()

def get_env_var(key, default=None):
    """
    環境変数を取得し、存在しない場合はデフォルト値を返す。

    :param key: 環境変数のキー
    :param default: デフォルト値
    :return: 環境変数の値またはデフォルト値
    """
    return os.getenv(key, default)