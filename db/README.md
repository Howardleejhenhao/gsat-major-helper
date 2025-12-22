# PostgreSQL

## 建立 / 啟動
```bash
docker compose up -d
````

## 關閉 / 移除（清空資料）

```bash
docker compose down
```

## 進入資料庫

```bash
docker compose exec -it postgres psql -U app -d appdb
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