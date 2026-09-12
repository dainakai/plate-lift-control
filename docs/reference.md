# 操作と実験連携の詳細

[クイックスタート](../README.md#クイックスタート)の補足です。

## 原点復帰と終了

`up` と `down` は、位置が不明なら指定した側のリミットまで原点復帰して停止します。
既知の端からは終点の約2 mm手前まで通常速度で進み、残りを原点復帰の速度で探します。
停止後はモーターを無励磁にします。
スイッチを離すまで少し戻るため、終了時の `limit: none` は正常な場合があります。

`home` は記録済みの位置にかかわらず、下端の原点復帰をやり直します。
手回しや公式アプリで位置を変えた後など、位置の記録を取り直すときに使います。
`up` で上げた位置は、コマンド終了後もそのままです。

片付けるときは `shutdown` を実行し、`position: DOWN`、`motor: de-energized`、`fault: none`、`safe_to_unplug: true` を確認してから主電源とUSBを外します。
`shutdown` は下へ移動する終了処理です。
異常時は装置の主電源を切ってください。

## ストロークと複数台の指定

この公開版の既定値は **68 mm** です。
以前の配布ZIPと異なり、現在のR10/R11装置で毎回 `--travel-mm 68` を付ける必要はありません。
明示的に付けても同じ動作です。

旧50 mmストロークの装置では、すべての操作に `--travel-mm 50` を付けます。
このオプションは取り付け済み機構のストロークを指定するもので、任意の高さへ止めるためのものではありません。

```text
uv run platectl home --travel-mm 50
```

Ticが複数ある場合は、`ticcmd --list` に表示された番号を毎回 `--serial` に指定します。
次の番号は例なので実際の番号へ置き換えてください。

```text
uv run platectl status --serial 01234567
```

`ticcmd` が標準の検索パスにない場合は、`--ticcmd` に実行ファイルのフルパスを指定できます。
パスに空白がある場合は、全体をダブルクォートで囲みます。

## 実験スクリプトから使う

### 撮影シーケンスのサンプル

[examples/capture_sequence.py](../examples/capture_sequence.py) は、次の順序を実装したサンプルです。

1. 下端へ原点復帰する。
2. 上げて停止を確認し、校正画像の取得処理を呼ぶ。
3. 下げて停止を確認し、試料画像の取得処理を呼ぶ。
4. 通常終了時は下端で無励磁になっていることを確認する。

まず、USBを使わない模擬動作を試せます。

```text
uv run python examples/capture_sequence.py --cycles 2
```

既定は `mock` なので実機は動きません。
一時フォルダに模擬動作の状態を置き、実機の位置記録と分けています。
`UP / calibration capture goes here`、`DOWN / sample capture goes here`、最後に `finished: DOWN / motor off` が表示されます。

実機の上下操作を確認できたら、明示的に `--backend ticcmd` を指定します。

```text
uv run python examples/capture_sequence.py --backend ticcmd --cycles 1 --settle-seconds 0.5
```

**このコマンドは実機を動かします。撮影そのものはまだ行いません。**
ファイル内の `capture_calibration()` と `capture_sample()` を、使用するカメラの取得処理に置き換えてください。
`--settle-seconds` は停止後から撮影処理を呼ぶまでの待ち時間です。
必要な待ち時間は撮影画像で確認して調整します。
`--serial`、`--ticcmd`、`--travel-mm` も指定できます。

サンプルは、シーケンス全体で `platectl` と共通のロックを保持します。
別の `platectl` を同時に実行すると終了コード5で拒否されます。
撮影処理だけが失敗した場合は下端への終了処理を行いますが、移動異常、USB通信エラー、`Ctrl+C` のあとには自動で再移動しません。

### 別のプログラムからコマンドを呼ぶ場合

`platectl` は動作が終わるまで戻らない同期コマンドです。
`--json` を付けると、結果をプログラムから読めます。

| JSONの項目 | 意味 |
| --- | --- |
| `ok` | コマンド処理が例外なく完了したか。`status` の `ok: true` だけでは装置の異常なしを意味しません。 |
| `position` | `UP`、`DOWN`、`UNKNOWN` |
| `fault` | 現在の異常一覧。空の配列なら検出中の異常はありません。 |
| `motor_energized` | モーターが励磁中か |
| `safe_to_image` | 既知の端で停止し、無励磁で、異常が検出されていないか |
| `safe_to_unplug` | 上記の条件を満たし、下端にいるか |

撮影に進むときは終了コード0、期待する `position`、`safe_to_image: true` を確認します。
これらのフラグはTicの情報と原点復帰の記録に基づく判断です。
実際のガラス保持力や振動を測定するセンサーではありません。

| 終了コード | 意味 |
| --- | --- |
| 0 | コマンド完了 |
| 2 | 引数の誤り、ticcmdがない、USB通信エラーなど |
| 3 | リミットやTicの異常 |
| 4 | 移動または原点復帰のタイムアウト |
| 5 | 別の操作が実行中 |

`up` と `down` の途中では、1秒の通信タイムアウトを更新し続けます。
移動の期限は68 mm装置で20秒、50 mm装置で10秒です。
移動中の例外や中断では無励磁化を試み、位置の記録を無効にします。

## 更新する

ZIPを使う場合は、新しいZIPを別のフォルダへ展開して `uv sync` を実行します。
自分で編集した撮影処理とTicの設定バックアップは、更新前に保存してください。
アプリの位置記録はOSのユーザー用データ領域にあり、ソースコードのフォルダとは別です。
更新後は `home` から始めます。

Gitを使う場合は、次の方法でも導入できます。

```text
git clone https://github.com/dainakai/plate-lift-control.git
cd plate-lift-control
uv sync
```

以降は、変更を保存したうえで `git pull --ff-only` と `uv sync` を実行します。

## 開発とテスト

```text
uv sync --locked
uv run --locked pytest
uv run --locked ruff check .
```

テストはTicの代替バックエンドを使い、接続された実機へコマンドを送りません。
GitHub ActionsでもmacOS、Windows、Linuxで同じテストを実行します。
CADソフトは不要です。
変更点は [CHANGELOG.md](../CHANGELOG.md)、検証の範囲は [docs/validation.md](validation.md) に記載します。
