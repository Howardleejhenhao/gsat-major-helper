# PostgreSQL

## 建立 / 啟動
```bash
docker compose up -d --build
````

## 關閉 / 移除（清空資料）

```bash
docker compose down
```

## 進入資料庫

```bash
docker compose exec -it postgres psql -U app -d appdb
```

## 如何執行 `.sql` 檔案
在建立 container 後，跑以下指令，在這個資料夾底下有 `SQLExample1.sql`、`SQLExample2.sql`，可以直接拿來測試。
```bash
docker compose exec -T postgres psql -U app -d appdb < <file_name>.sql
```

## 列出所有資料表

```sql
\dt
```
如果你看到以下內容代表成功了
```
              List of relations
 Schema |        Name        | Type  | Owner
--------+--------------------+-------+-------
 public | admissionrecord    | table | app
 public | category           | table | app
 public | combinationdetail  | table | app
 public | department         | table | app
 public | examrequirement    | table | app
 public | examyear           | table | app
 public | standardlevel      | table | app
 public | subject            | table | app
 public | subjectcombination | table | app
 public | subjectperformance | table | app
 public | university         | table | app
```

## 退出 psql

```sql
\q
```