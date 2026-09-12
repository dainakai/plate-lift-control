# plate-lift-control

校正用のガラスプレートを、MacまたはWindowsからUSBで上げ下げするソフトウェアです。
Pololu Tic T825を使った昇降装置で、校正時はプレートを上げ、撮影時は下げる用途を想定しています。

`platectl` コマンドで原点復帰、上昇、下降、状態確認、終了処理ができます。
実験の撮影処理と組み合わせるPythonのサンプルも含みます。
現在の装置（R10/R11、68 mmストローク）を既定値にしています。

**初回は、Pololuアプリの導入 → uvの導入 → このソフトの準備 → Tic設定の確認 → 原点復帰 → 上下操作、の順に進めてください。**
装置はPololuの公式アプリで動作確認済みです。
このリポジトリの自動テストはUSB機器を模擬するため、スクリプトと実機を組み合わせた確認は、下の初回操作手順で行います。

- [Macで準備する](#macで準備する)
- [Windowsで準備する](#windowsで準備する)
- [Ticの設定を確認する](#ticの設定を確認する)
- [初めてスクリプトで動かす](#初めてスクリプトで動かす)
- [普段の操作](#普段の操作)
- [実験スクリプトから使う](#実験スクリプトから使う)
- [困ったとき](#困ったとき)

## PCに入れるもの

| 名前 | 役割 |
| --- | --- |
| **Tic Control Center** | Pololuの公式アプリ。Ticの設定、手動操作、状態確認に使います。 |
| **ticcmd** | 公式アプリと一緒に入るUSB操作コマンド。このソフトが内部で呼び出します。 |
| **uv** | Pythonと必要なライブラリを用意し、操作スクリプトを実行します。 |
| **platectl** | このリポジトリの上下操作コマンド。Ticの状態を監視しながら移動します。 |

以下では、Gitを使わずZIPをダウンロードして始めます。
Pythonも個別にインストールする必要はありません。
初回の `uv sync` がPython 3.11とライブラリを準備します。
[uv公式のPython管理説明](https://docs.astral.sh/uv/guides/install-python/)

**コマンドは、装置をUSB接続するPCで実行します。**
別のサーバーへSSH接続したターミナルでは、手元のUSB機器を操作できません。

## Macで準備する

### 1. Pololuの公式アプリを入れる

1. [Pololu公式のmacOSインストールページ](https://www.pololu.com/docs/0J71/3.3)を開きます。
2. ページ内の **Tic Software for macOS** をダウンロードします。
3. ダウンロードした `.pkg` を開き、画面の案内に従ってインストールします。
4. アプリケーションフォルダの **Pololu Tic Stepper Motor Controller** を開けることを確認します。これがTic Control Centerです。

すでにこのアプリで装置を動かせている場合、再インストールは不要です。

### 2. uvを入れる

Spotlight（⌘ + スペース）で「ターミナル」を検索して開き、次の1行を実行します。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

これは[uv公式のインストール方法](https://docs.astral.sh/uv/getting-started/installation/)です。
完了したらターミナルを閉じ、新しく開き直して次を実行します。

```bash
uv --version
ticcmd --help
```

uvのバージョンとticcmdの使い方が表示されれば準備できています。
Pololuのインストーラによるコマンド検索パスの変更も、新しく開いたターミナルに反映されます。

### 3. このソフトをダウンロードして準備する

1. [ソースコードのZIP](https://github.com/dainakai/plate-lift-control/archive/refs/heads/main.zip)をダウンロードします。GitHubの緑色の **Code → Download ZIP** でも同じです。
2. ZIPを展開し、`plate-lift-control-main` フォルダを「ダウンロード」の直下に置きます。
3. ターミナルで次を1行ずつ実行します。

```bash
cd ~/Downloads/plate-lift-control-main
uv sync --locked --no-dev
uv run --locked --no-dev platectl --help
```

`pyproject.toml` と `README.md` があるフォルダで実行してください。
`uv sync` の初回実行にはインターネット接続が必要です。
最後に `up`、`down`、`home` などの使い方が表示されれば完了です。
ここまでのコマンドではモーターは動きません。

次は [Ticの設定を確認する](#ticの設定を確認する) へ進みます。

## Windowsで準備する

Windows 10/11のPowerShellで使う手順です。

### 1. Pololuの公式アプリを入れる

1. [Pololu公式のWindowsインストールページ](https://www.pololu.com/docs/0J71/3.1)を開きます。
2. **Tic Software and Drivers for Windows** をダウンロードして実行します。
3. ドライバーのインストール確認が表示されたら **Install** を選びます。
4. スタートメニューで「Tic」を検索し、**Tic Control Center** を起動できることを確認します。

すでにこのアプリで装置を動かせている場合、再インストールは不要です。

### 2. uvを入れる

スタートメニューで「PowerShell」を検索して開き、次を実行します。

```powershell
winget install --id=astral-sh.uv -e
```

`winget` が見つからない場合だけ、代わりに次の1行を使います。

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

どちらも[uv公式に掲載されているインストール方法](https://docs.astral.sh/uv/getting-started/installation/)です。
完了したらPowerShellを閉じ、新しく開き直します。

```powershell
uv --version
ticcmd --help
```

uvのバージョンとticcmdの使い方が表示されれば準備できています。
仮想環境の `Activate.ps1` を実行する作業はありません。

### 3. このソフトをダウンロードして準備する

1. [ソースコードのZIP](https://github.com/dainakai/plate-lift-control/archive/refs/heads/main.zip)をダウンロードします。
2. ZIPを右クリックして **すべて展開** を選びます。ZIPの中を表示しただけの状態では使えません。
3. `pyproject.toml` が入った `plate-lift-control-main` フォルダを「ダウンロード」の直下に置きます。同名フォルダが二重になった場合は、内側のフォルダを使います。
4. PowerShellで次を1行ずつ実行します。

```powershell
cd "$env:USERPROFILE\Downloads\plate-lift-control-main"
uv sync --locked --no-dev
uv run --locked --no-dev platectl --help
```

`uv sync` の初回実行にはインターネット接続が必要です。
Python 3.11とライブラリが入り、最後にコマンドの使い方が表示されれば完了です。
ここまでのコマンドではモーターは動きません。

ダウンロード先を変更している場合は、`cd` の移動先を実際の展開先へ読み替えてください。

## Ticの設定を確認する

### すでに公式アプリで動く装置の場合

**動作している設定を保存し、その設定を基に次の項目を確認します。**
このソフトを使うために、無条件で設定ファイル全体を上書きする必要はありません。

Tic Control CenterのFileメニューから現在の設定を保存するか、アプリを終了して次を実行します。

```text
ticcmd --get-settings tic-settings-backup.txt
```

このコマンドは設定をPCへ保存するだけで、モーターを動かしません。
保存したファイルは保管してください。

| 設定項目 | このソフトが想定する値 |
| --- | --- |
| Ticの機種 | T825 |
| Control mode | Serial / I²C / USB |
| モーターと送りねじ | 200フルステップ/回転、リード1.5 mm |
| Step mode | 1/8 |
| 正方向 | ガラスが上がる方向 |
| SCL | 下端のReverse limit、プルアップ有効、Active high |
| SDA/AN | 上端のForward limit、プルアップ有効、Active high |
| Command timeout | 有効、1000 ms |
| Soft error response | De-energize |
| Automatic homing | 無効 |
| Homing speed towards | `64000000`（6 mm/s） |
| Homing speed away | `16000000`（1.5 mm/s） |
| Max acceleration / deceleration | `3333333`（約31.25 mm/s²） |

通常移動の最大速度は、`platectl` が移動時に `150000000`（約14.06 mm/s）へ設定します。
原点復帰の速度、モーター電流、マイクロステップ、リミットの割り当てはTic側の設定を使います。
電源装置で観測した約0.27 Aは入力電流です。Ticのモーター各相の電流制限へそのまま転記する値ではありません。

### Ticを初期設定する場合

[config/tic-t825-settings.txt](config/tic-t825-settings.txt) に、この装置用の設定ひな型があります。
機構と配線が上表に一致する場合、Tic Control Centerの **File → Open settings file…** から開き、**Apply settings** で反映します。
ひな型のモーター電流上限は800 mAです。使用するモーターに合わせて確認し、すでに動作確認した電流値や回転方向の変更があれば引き継いでください。
[Pololuの設定ファイル説明](https://www.pololu.com/docs/0J71/5.7)、[モーター設定説明](https://www.pololu.com/docs/0J71/4.3)

リミットスイッチは、下端が **COM→GND、NC→SCL**、上端が **COM→GND、NC→SDA/AN** です。
NO端子は使いません。
モーター用電源を切った状態で、USBから状態を読みながら確認できます。

| スイッチの状態 | Forward limit active | Reverse limit active |
| --- | --- | --- |
| 両方離している | No | No |
| 下端だけ押している | No | Yes |
| 上端だけ押している | Yes | No |

ツメが機構の突き当たりより先にスイッチを押すことと、正方向で上がることも確認してから使います。
[Pololuのリミットスイッチ設定説明](https://www.pololu.com/docs/0J71/4.14)

## 初めてスクリプトで動かす

### 1. 公式アプリを終了し、USB通信を確認する

**Tic Control Centerを閉じてください。特にWindowsでは、公式アプリとticcmdが同時に同じUSB機器を使えません。**
[Pololu公式のUSB制御説明](https://www.pololu.com/docs/0J71/4.4)

装置をUSB接続し、動作確認に使ったモーター用電源を入れます。
ターミナルまたはPowerShellで、先ほど展開したフォルダへ移動して実行します。
以下のコマンドは両OSで共通です。

```text
ticcmd --list
uv run --locked --no-dev platectl status
```

`ticcmd --list` にT825のシリアル番号が表示されれば、USB接続を認識しています。
`status` は状態を読むコマンドで、移動しません。
初回の `position: UNKNOWN` は、スクリプトがまだ上下端を確定していないという意味です。

### 2. 下端へ原点復帰する

初回はガラスを外し、移動を目視できる状態で実行します。
方向とリミットを確認した装置で、下端の少し上から始めると確認しやすくなります。

```text
uv run --locked --no-dev platectl home
```

下へ動いて下端スイッチを押し、スイッチを離すまで少し戻って停止します。
終了時に次の表示を確認します。

```text
position: DOWN
motor: de-energized
fault: none
safe_to_unplug: true
```

戻った位置を下端として記録するため、終了時の `limit: none` は正常な場合があります。
`home` は保存されている位置にかかわらず、下端の原点復帰をやり直します。

### 3. 上げて、下げる

```text
uv run --locked --no-dev platectl up
uv run --locked --no-dev platectl down
```

1行目が完了して `position: UP` になったことを確認してから、2行目を実行します。
既知の端から移動するときは、終点の約2 mm手前まで通常速度で進み、残りを原点復帰の速度で探します。
停止後はモーターを無励磁にします。
通電なしでプレートを保持できる、この装置の送りねじ機構を前提としています。

異音、逆方向への移動、リミットを越えそうな動きがあれば、装置の主電源を切ってください。
`Ctrl+C` でもスクリプトは無励磁化を試みますが、USBが切れている場合は届きません。
`shutdown` は下へ移動する通常終了処理なので、異常時の停止には使いません。

## 普段の操作

新しいターミナルまたはPowerShellを開いたら、まず展開したフォルダへ `cd` します。
USBとモーター用電源を接続して `status` を確認し、電源投入後や公式アプリでの手動移動後は `home` から始めます。

| 目的 | コマンド |
| --- | --- |
| 状態を見る | `uv run --locked --no-dev platectl status` |
| 下端の原点復帰をやり直す | `uv run --locked --no-dev platectl home` |
| 上げる | `uv run --locked --no-dev platectl up` |
| 下げる | `uv run --locked --no-dev platectl down` |
| 下げて終了状態を確認する | `uv run --locked --no-dev platectl shutdown` |
| JSONで状態を読む | `uv run --locked --no-dev platectl status --json` |

`up` で上げた位置は、コマンド終了後もそのままです。
片付けるときは `shutdown` を実行し、`position: DOWN`、`motor: de-energized`、`fault: none`、`safe_to_unplug: true` を確認してから主電源とUSBを外します。

### ストロークと複数台の指定

この公開版の既定値は **68 mm** です。
以前の配布ZIPと異なり、現在のR10/R11装置で毎回 `--travel-mm 68` を付ける必要はありません。
明示的に付けても同じ動作です。

旧50 mmストロークの装置では、すべての操作に `--travel-mm 50` を付けます。
このオプションは取り付け済み機構のストロークを指定するもので、任意の高さへ止めるためのものではありません。

```text
uv run --locked --no-dev platectl home --travel-mm 50
```

Ticが複数ある場合は、`ticcmd --list` に表示された番号を毎回 `--serial` に指定します。
次の番号は例なので実際の番号へ置き換えてください。

```text
uv run --locked --no-dev platectl status --serial 01234567
```

`ticcmd` が標準の検索パスにない場合は、`--ticcmd` に実行ファイルのフルパスを指定できます。
パスに空白がある場合は、全体をダブルクォートで囲みます。

## 実験スクリプトから使う

### 撮影シーケンスのサンプル

[examples/capture_sequence.py](examples/capture_sequence.py) は、次の順序を実装したサンプルです。

1. 下端へ原点復帰する。
2. 上げて停止を確認し、校正画像の取得処理を呼ぶ。
3. 下げて停止を確認し、試料画像の取得処理を呼ぶ。
4. 通常終了時は下端で無励磁になっていることを確認する。

まず、USBを使わない模擬動作を試せます。

```text
uv run --locked --no-dev python examples/capture_sequence.py --cycles 2
```

既定は `mock` なので実機は動きません。
一時フォルダに模擬動作の状態を置き、実機の位置記録と分けています。
`UP / calibration capture goes here`、`DOWN / sample capture goes here`、最後に `finished: DOWN / motor off` が表示されます。

実機の上下操作を確認できたら、明示的に `--backend ticcmd` を指定します。

```text
uv run --locked --no-dev python examples/capture_sequence.py --backend ticcmd --cycles 1 --settle-seconds 0.5
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

## 困ったとき

| 症状 | 対応 |
| --- | --- |
| `uv` が見つからない | インストール後にターミナルまたはPowerShellを開き直します。 |
| `ticcmd` が見つからない | Pololuソフトをインストールし、ターミナルを開き直します。必要なら `--ticcmd` で場所を指定します。 |
| `pyproject.toml` が見つからない | ZIPを展開し、このファイルが入っているフォルダへ `cd` します。 |
| `uv sync --locked` が失敗する | まず通信エラーの有無を確認します。ファイルの組み合わせが違う場合はZIPを新しいフォルダへ展開し直します。 |
| 公式アプリでは動くがスクリプトから接続できない | 公式アプリを終了します。Windowsでは同時接続できません。 |
| `fault during homing: N; o; n; e` | 旧配布版の不具合です。このリポジトリから入れ直してください。エラーなしを示す `None` の誤判定は修正済みです。 |
| `Low VIN` | USBだけではモーターを動かせません。モーター用電源、主電源スイッチ、ヒューズ、Tic入力電圧を確認します。 |
| `both ... limits ... active` | NC線の抜け、SCL/SDAの割り当て、レバーの状態を確認します。 |
| 原点復帰がタイムアウトする | 主電源を切り、移動方向、ツメがレバーを押せるか、リミットの設定と配線を確認します。 |
| `another platectl process ... lock` | 実行中のコマンドまたは撮影サンプルが終わるまで待ちます。実行中にロックを消さないでください。 |
| 公式アプリや手回しで位置を変えた | 次に使う前に `home` で原点復帰をやり直します。手回しによる移動はソフトから検出できません。 |

詳しいTicの状態を読むには、公式アプリを閉じて次を実行します。

```text
ticcmd --status --full
uv run --locked --no-dev platectl status --json
```

## 更新する

ZIPを使う場合は、新しいZIPを別のフォルダへ展開して `uv sync --locked --no-dev` を実行します。
自分で編集した撮影処理とTicの設定バックアップは、更新前に保存してください。
アプリの位置記録はOSのユーザー用データ領域にあり、ソースコードのフォルダとは別です。
更新後は `home` から始めます。

Gitを使う場合は、次の方法でも導入できます。

```text
git clone https://github.com/dainakai/plate-lift-control.git
cd plate-lift-control
uv sync --locked --no-dev
```

以降は、変更を保存したうえで `git pull --ff-only` と `uv sync --locked --no-dev` を実行します。

## 開発とテスト

```text
uv sync --locked
uv run --locked pytest
uv run --locked ruff check .
```

テストはTicの代替バックエンドを使い、接続された実機へコマンドを送りません。
GitHub ActionsでもmacOS、Windows、Linuxで同じテストを実行します。
CADソフトは不要です。
変更点は [CHANGELOG.md](CHANGELOG.md)、検証の範囲は [docs/validation.md](docs/validation.md) に記載します。

## ライセンス

このリポジトリのコードと文書は [MIT License](LICENSE) です。
Pololuのアプリ本体は含めていません。公式サイトからインストールしてください。
