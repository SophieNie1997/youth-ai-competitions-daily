# GitHub Pages 发布说明

这个项目已经准备为 GitHub Pages 静态站发布。

## 本地构建

```bash
python3 -m unittest discover -s tests -v
python3 scripts/generate_daily_site.py
```

## 首次发布

1. 初始化本地 Git 仓库并切到 `main`。
2. 添加远端：

```bash
git remote add origin https://github.com/SophieNie1997/youth-ai-competitions-daily.git
git push -u origin main
```

3. 在 GitHub 仓库页面进入 `Settings` -> `Pages`。
4. 将 `Build and deployment` 的 `Source` 设置为 `GitHub Actions`。
5. 打开 `Actions` 页面，等待 `Deploy GitHub Pages` workflow 成功。

成功后，站点 URL 通常是：

```text
https://sophienie1997.github.io/youth-ai-competitions-daily/
```
