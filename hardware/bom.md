# 購入部材一覧

数は装置1台に使う数です。袋やセットの入数とは異なります。
購入先は使用部品の照合用です。同じ型番でも仕様やセット内容を確認してください。

**固定ねじ57本・六角ナット24個・M3インサート26個。** USLL6本体のねじ3本、主電源スイッチとヒューズホルダーの付属ナットは別扱いです。USLL6を固定するM3ナット3個は、六角ナット24個の内数です。

[CSVでダウンロード](bom.csv) ／ [組立・取扱説明書](../docs/assembly-manual.pdf) ／ [印刷用STL一式](print-parts.zip)

## 機構

| 型番・仕様 | 部品名 | 必要数 | 取り付け場所・用途 |
| --- | --- | ---: | --- |
| [C-42STM01](https://jp.misumi-ec.com/vona2/detail/110310526769/?HissuCode=C-42STM01) | 42 mm角ステッピングモーター | 1 | 駆動フレームのU字開口から入れ、M3×8で4点固定 |
| [MTSRA8-120-S20-Q6](https://jp.misumi-ec.com/vona2/detail/110302642010/?HissuCode=MTSRA8-120-S20-Q6) | 送りねじ | 1 | 軸端φ6×20、ねじ部100、全長120 mm。軸受と黄銅ナットを通す |
| [MTSFR8](https://jp.misumi-ec.com/vona2/detail/110302641220/?HissuCode=MTSFR8) | 黄銅フランジナット | 1 | 黄銅ナット取付板の下面。M4×14とM4ナットで4点固定 |
| [SSEB8-100](https://jp.misumi-ec.com/vona2/detail/110302586530/?HissuCode=SSEB8-100) | リニアガイド（レール＋ブロック） | 1組 | レールはフレームへM2×12で4点、ブロックは取付板へM2×6で4点固定 |
| [CPL16-5-6](https://jp.misumi-ec.com/vona2/detail/110300126030/?HissuCode=CPL16-5-6) | カップリング | 1 | モーターのφ5軸と送りねじのφ6軸端を接続 |
| [696ZZ](https://jp.misumi-ec.com/vona2/detail/221301228090/?HissuCode=696ZZ) | 軸受（内径6×外径15×幅5 mm） | 1 | 駆動フレームの軸受座。上下に精密シムを入れ、蓋で押さえる |
| [PSCCJ6-5](https://jp.misumi-ec.com/vona2/detail/110302636320/?HissuCode=PSCCJ6-5) | セットカラー | 1 | 下シムの下で送りねじに固定 |
| [CIMR6-12-0.5](https://jp.misumi-ec.com/vona2/detail/110302677870/?HissuCode=CIMR6-12-0.5) | 精密シム（6×12×0.5 mm） | 2 | 軸受の上下へ各1枚。普通の座金へ置き換えない |
| [USLL6](https://jp.misumi-ec.com/vona2/detail/110302358850/?HissuCode=USLL6) | ウレタン先端の支持ねじ | 3 | ガラスホルダーへ底2本・横1本。M3ナットで固定 |
| 50×50×2.3 mm | ランダムドットガラス | 1 | ホルダーの溝へ挿入。溝幅2.9 mm、支持ねじで3点支持 |

## 検出・制御

| 型番・仕様 | 部品名 | 必要数 | 取り付け場所・用途 |
| --- | --- | ---: | --- |
| [SS-01GL13-E](https://jp.misumi-ec.com/vona2/detail/221000559138/?HissuCode=SS-01GL13-E) | OMRONリミットスイッチ | 2 | フレームの上下へ各1個。COM→GND、下NC→SCL、上NC→SDA |
| [Pololu 3130 / Tic T825](https://www.switch-science.com/products/3398) | USBモーター制御基板（端子実装済み） | 1 | 電子箱の底板へM2×6で2点固定 |
| 2.54 mm・1ピン・メス端子付き | 信号用リード線 | 4 | TicのSCL・SDA・信号GNDと、上下スイッチを接続。長さは現物で決める |

## 電装

| 型番・仕様 | 部品名 | 必要数 | 取り付け場所・用途 |
| --- | --- | ---: | --- |
| [XT60E-F](https://www.amazon.co.jp/dp/B0CQK1P1DP) | リード線付きパネル用XT60メス | 1 | 電源側板の下側。M2×8とM2ナット各2で固定 |
| [エーモン3214](https://www.amazon.co.jp/dp/B075SW22KP) | 主電源スイッチ（非照光） | 1 | 電源側板の上側。付属ナットで固定 |
| [OHM KIT-NR312](https://www.amazon.co.jp/dp/B0DSKS32YZ) | パネル用ヒューズホルダー | 1 | ヒューズ側板のφ13 mm穴。付属ナットで固定 |
| [5.2×20 mm・2 A](https://www.amazon.co.jp/dp/B086Z12VJF) | ガラス管ヒューズ | 1 | KIT-NR312内。エーモン3665セットの2 Aを使用 |
| [WAGO 221-412 / WFR-2BP](https://www.amazon.co.jp/dp/B01E577SMQ) | 2口レバー式中継コネクタ | 2 | 正極用と0 V用に各1個。専用の印刷台は使わない |
| [エーモン3311・250型](https://www.amazon.co.jp/dp/B086XFD4B8) | メス端子と絶縁スリーブ | 各2 | 3214の2端子へ接続。電線に合う圧着工具で加工 |
| [エーモン4942・0.50 sq](https://www.amazon.co.jp/dp/B07PSL1H4J) | 赤黒ダブルコード | 必要長 | 箱内のDC配線。側板を外す余長を確保して現物で切断 |
| [エーモン1196・φ4 mm](https://www.amazon.co.jp/dp/B001JBYGHC) | 熱収縮チューブ | 必要長 | ヒューズホルダーなどのはんだ端子を1本ずつ絶縁 |
| [U2C-AMB10BK](https://www.amazon.co.jp/dp/B005C8RVFM) | ELECOM USB-A–Micro-Bデータケーブル | 1 | パソコン→Tic。USB-CのみのPCはデータ対応変換アダプターも用意 |
| [XT60オス–4 mmバナナ・30 cm・14 AWG](https://www.amazon.co.jp/dp/B07RBKSFX4) | DC電源ケーブル | 1 | 赤を電源＋、黒を0 Vへ。2本組から1本使用 |
| 24 V以下に設定できるDC電源 | 直流安定化電源 | 1 | 装置のXT60へ接続。使用中の21.2 V出力で動作確認済み |

## 固定具

| 型番・仕様 | 部品名 | 必要数 | 取り付け場所・用途 |
| --- | --- | ---: | --- |
| [M3・外径4.6×長さ5.7 mm](https://www.amazon.co.jp/dp/B0G9L9RT4S) | 熱圧入インサート | 26 | 機構8個、USB側板8個、駆動側板8個、ヒューズ側板2個 |
| [M2×6](https://www.amazon.co.jp/dp/B0GVD68M67) | 六角穴付きねじ（長さは首下） | 6 | ガイドブロック4本、Tic基板2本 |
| [M2×8](https://www.amazon.co.jp/dp/B0GVD68M67) | 六角穴付きねじ（長さは首下） | 2 | XT60フランジ2本 |
| [M2×12](https://www.amazon.co.jp/dp/B0GVD68M67) | 六角穴付きねじ（長さは首下） | 7 | レール4本、軸受押さえ3本 |
| [M2×16](https://www.amazon.co.jp/dp/B0GVD68M67) | 六角穴付きねじ（長さは首下） | 4 | 上下リミット各2本 |
| [M3×8](https://www.amazon.co.jp/dp/B0GVD68M67) | 六角穴付きねじ（長さは首下） | 24 | モーター4本、ホルダー前枠4本、電子箱16本 |
| [M3×12](https://www.amazon.co.jp/dp/B0GVD68M67) | 六角穴付きねじ（長さは首下） | 10 | ベース接続4本、キャリア接続4本、ホルダー接続2本 |
| [M4×14](https://www.amazon.co.jp/dp/B0GVD68M67) | 六角穴付きねじ（長さは首下） | 4 | 黄銅フランジナット4本 |
| [M2・対辺4×厚さ1.6 mm](https://jp.misumi-ec.com/vona2/detail/110500137250/?HissuCode=NATTO-2-4-1.6) | 六角ナット | 13 | レール4個、軸受押さえ3個、リミット4個、XT60用2個 |
| [M3](https://www.amazon.co.jp/dp/B0GVD68M67) | 六角ナット | 7 | ホルダー前枠4個、USLL6用3個 |
| [M4](https://www.amazon.co.jp/dp/B0GVD68M67) | 六角ナット | 4 | 黄銅フランジナット用4個 |

## 消耗品

| 型番・仕様 | 部品名 | 必要数 | 取り付け場所・用途 |
| --- | --- | ---: | --- |
| PLAまたは採用した樹脂 | 3Dプリンター用フィラメント | 必要量 | 試験片と本体を同じ材料・造形条件で印刷 |
| 小型結束バンド・配線ラベル | 配線保持・識別用品 | 必要数 | 線束を保持。WAGOのレバーを押さえない |

## 用意する工具

六角レンチ（M2/M3/M4ねじ用）、小型スパナ、はんだごて・インサート用こて先、圧着工具、ワイヤーストリッパー、テスター、ノギスを使います。
M2ねじとナットは狭い場所へ入れるため、ピンセットもあると作業できます。

[READMEへ戻る](../README.md)
