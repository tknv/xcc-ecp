# xcc-ecp
XCC External Captive Portal

XIQ-C Captive Portal (Hardcoded Redirect)

## 設定の変更箇所
`app.py` 内の以下の変数を必ず書き換えてください。

1. **`RADIUS_HOST`**: FreeRADIUSのIP。
2. **`REDIRECT_TARGET_URL`**: 
   ExtremeのコントローラーのIPアドレスを指定します。
   例: `http://10.0.0.1/web/login`
   ※XIQ-Cの設定でHTTPSを使用している場合は `https://...` にしてください。

## 実行手順

1. **イメージのビルド**
```bash
   docker build -t xiq-portal .
```

2. **コンテナの起動** 
```bash
docker run -d -p 80:80 --name my-portal xiq-portal
```

3. **コンテナの停止と削除**
```bash
docker stop my-portal
docker rm my-portal
```

4. **イメージの削除**
```bash
docker rmi xiq-portal
```