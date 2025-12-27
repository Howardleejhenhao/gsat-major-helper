# gsat-major-helper
## 如何開啟網站

1. 先啟動資料庫（db）

```bash
cd db
docker compose up --build
```


2. 再開一個新的 Terminal，啟動網站（webapp）

```bash
cd webapp
docker compose up --build
```

網站會在：

* `http://localhost:8000/`