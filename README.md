# mm100_visualizer

起動まで時間がかかることがあります
オープンソースです(sourceフォルダーにあります)

- mac
  - mm100_visualizer をダウンロード
- windows
  - mm100_visualizer.exe をダウンロード

## 使い方

1. ファイルを選択
2. show_each_region だけを選択
![Alt text](<data/スクリーンショット 2024-02-01 10.43.19.png>)
3. Confirm
4. 下のボックスにdoneが出るまで待つ
どこかの`imgs`フォルダーに画像が出力されます

全体とそれぞれの領域が5分づつ、**時間 (s)-z軸の高さ (mm)** のグラフが表示されています

![Alt text](data/240116_110145.887552.png)

電極がこうなってればいいのですが、
![Alt text](<data/240116_110145.887552 2.png>)

たまにこうなっていることがあります。これは片側の電極の掘り方が壊れているのでRhinoで作り直しましょう
![Alt text](data/240116_110227.513188.png)

あとはz軸が -6.1\~0.0 mmの間を掘っているか
領域がちゃんと5つあるか（セパレーター、大円、、、）
compare_nc、xyだけにチェックを入れConfirmして掘る範囲が 0\~100 mm以内に収まっているかなどをお好みで確認します。

## 詳しい使い方

- compare_nc
  - wz
![Alt text](data/240201_104703.889885.png)

  - xy
![Alt text](data/240201_104653.560343.png)

  - wxy
![Alt text](data/240201_104704.638398.png)

- show_each_region
![Alt text](data/240201_104705.563297.png)

- show_index
上から時間に対するx,y,zのどれか、ミルの動くスピード、ncファイル上での行数（region (s)は 60秒程度がおすすめ）
  - region:空白, zのみ
![Alt text](data/240201_104707.824710.png)
  - region:0-60, zのみ
![Alt text](data/240201_104713.888910.png)

## 複数ファイル

ブラウズの時ファイルを複数選択するとcompare_ncで出力される画像が変わります

show_each_region, show_indexは変わりません

![Alt text](<data/スクリーンショット 2024-01-16 10.42.41.png>)

- compare_nc
  - wz, single_graph あり
![Alt text](data/240201_105143.840541.png)

  - wz, single_graph なし
![Alt text](data/240201_105153.893352.png)


## versions

25/3/18 2.1.2
- エラー文がわかりやすくなりました。

24/3/11 1.3.1
- ミルに名前をつけれるようになりました。

24/1/31 1.2.3
- グラフにミルの番号を書き込むようにしました。

24/1/30 1.2.1

24/1/24 1.1

23/10/29 1.0

## 動作確認

mac Ventura 13.6
windows 22H2
