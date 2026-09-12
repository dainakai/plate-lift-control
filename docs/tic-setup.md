# Ticを交換または初期化したときの設定

通常の利用では、このページの操作は不要です。
Ticを交換、初期化した場合や、モーターと配線を変更した場合に参照してください。
`platectl` は通常移動の速度を設定しますが、リミット、マイクロステップ、モーター電流などはTicに保存済みの値を使います。

## 設定を変更する前に

設定を変更する場合は、先に現在の設定を保存してください。

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

## 設定を適用する

[config/tic-t825-settings.txt](../config/tic-t825-settings.txt) に、この装置用の設定ひな型があります。
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

[クイックスタートへ戻る](../README.md#クイックスタート)
