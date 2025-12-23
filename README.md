# gsat-major-helper

## 如何開啟
1. 先將資料庫建置好，進入到 `db` 資料夾中，接下來打以下指令
    ```
    docker compose up --build
    ```
2. 開新的 terminal，進到 `webapp` 資料夾中打以下指令，網站會在 `http://localhost:8000/`
    ```
    docker compose up --build
    ```
3. 若要結束則分別對這兩個 `Ctrl + C`，然後分別在終端機打
    ```
    docker compose down
    ```