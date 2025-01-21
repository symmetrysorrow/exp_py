import os

# フォルダのパスを指定
folder_path = "F:/tagawa/data/20241206/20241206/CH1_pulse/rawdata"  # フォルダパスを指定してください

# 変更後の開始番号を指定
start_number = 52481

try:
    # フォルダ内のファイルをリスト
    files = sorted(os.listdir(folder_path))  # ソートして順番を保つ

    # ファイルをリネーム
    for index, file_name in enumerate(files):
        # 拡張子とファイル名を分離
        base_name, extension = os.path.splitext(file_name)

        # "CH0_" のみ対象とする（条件を変更可能）
        if base_name.startswith("CH1_"):
            # 新しい番号を生成
            new_number = start_number + index
            new_name = f"CH1_{new_number}{extension}"
            old_path = os.path.join(folder_path, file_name)
            new_path = os.path.join(folder_path, new_name)
            
            # リネーム
            os.rename(old_path, new_path)
            print(f"Renamed: {file_name} -> {new_name}")

    print("すべてのファイル名を書き替えました！")
except Exception as e:
    print(f"エラーが発生しました: {e}")
