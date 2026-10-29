# 叮当观察 · jcvpn.blog

这是可直接发布的静态博客，无需安装前端依赖或运行构建服务。正式地址为 **https://jcvpn.blog/**。GitHub 仓库用于保存及同步网站文件，连接仓库本身不会自动开通网站托管。

## 本次交付

- 60篇文章、200条通用FAQ、6个专题及5个品牌页面。
- 78个唯一页面允许收录，旧的`01-首页框架.html`保留跳转并排除收录。
- 全站统一页头与完整页脚，提供关于本站、联系我们、内容导航及品牌记录入口。联系页使用站长确认的Telegram与邮箱。
- 每个正式页面使用对应的绝对canonical网址，首页统一指向`https://jcvpn.blog/`。
- 正式内页网址与Cloudflare Pages一致，例如`https://jcvpn.blog/contact`，不带`.html`；本地文件仍保留`.html`以便编辑和预览。
- 提供真正的`404.html`，让不存在的路径返回404，不会误显示首页。
- `sitemap.xml`、`robots.txt`、IndexNow根目录验证文件和提交工具。
- 网站地图按页面内容指纹保留真实修改时间；未改动的页面不会每次打包都刷新日期。
- IndexNow默认仅生成待提交清单，只有手动提交时才访问线上网站并通知搜索引擎。

## 上传与提交Bing

1. 将交付的`jcvpn-blog-upload.zip`解压，**把里面的文件上传到网站根目录**。根目录直接有`index.html`、`sitemap.xml`、`robots.txt`、一份长文件名的`.txt`验证文件，以及`assets/`和`data/`目录。不要再多套一层文件夹。
2. 将`jcvpn.blog`绑定到你的托管服务，并启用HTTPS。服务器/CDN需允许公开访问，不应额外发送`X-Robots-Tag: noindex`。
3. 确认首页、品牌页、`https://jcvpn.blog/sitemap.xml`和`https://jcvpn.blog/robots.txt`可以正常打开。统一使用不带www的HTTPS域名；HTTP及www入口应由托管服务重定向到正式域名。首页`/index.html`可由服务器301跳转到`/`，页面本身已设置首页canonical。
4. 在[Bing站长工具](https://www.bing.com/webmasters/)添加`https://jcvpn.blog/`。按Bing实际给出的DNS、HTML文件或meta标签方案验证所有权。本项目没有伪造Bing验证码；IndexNow验证文件也不能替代Bing站长账号验证。
5. 在Bing站长工具的网站地图栏目提交：**https://jcvpn.blog/sitemap.xml**。
6. 线上文件上传完整后，在本地双击`上线后提交IndexNow.cmd`。它会先检查线上验证文件、此次变动页面、网站地图及robots是否与这份文件一致；不一致则停止。需要本机安装Python 3。首次提交78个页面，收到HTTP 200后记录成功批次；再次提交仅处理新增、修改或删除的网址。HTTP 202表示收到但验证仍在处理中，会保留待提交状态。

IndexNow的提交成功表示搜索引擎收到通知，不代表已经收录，也不保证排名。工具没有绑定定时提交，也不会在每个访客打开网页时发送请求。

## 明天新增内容

先修改或新增文章HTML，并补上文章目录、专题和FAQ里的相关入口。然后双击`更新网站地图并打包.cmd`，将新生成的压缩包上传覆盖网站，最后再双击`上线后提交IndexNow.cmd`。

这两个命令分别负责“准备与打包”和“确认线上文件后提交”。修改本地文件不会自动改变线上网站，GitHub推送也只有在你另外配置托管自动部署后才会发布网站。

如果原有内容生成脚本重新输出了本地预览页面，在最后再运行准备工具即可重新应用正式收录设置。复制站点或从GitHub重新下载后，保留`data/publication-manifest.json`和现有验证文件，避免重建修改日期或更换验证密钥。

博客公开联系方式在`data/site-contact.json`维护。更新后运行准备工具，会重新生成`contact.html`、`about.html`以及全站页头、页脚。联系按钮直接打开邮件应用或Telegram，没有伪造表单提交和客服在线状态。

## 从GitHub部署到Cloudflare Pages

Cloudflare项目的“构建和部署”设置应填写：

| 设置 | 内容 |
| --- | --- |
| 生产分支 | `main` |
| 框架预设 | `None` / 无 |
| 构建命令 | `npm run build` |
| 构建输出目录 | `dist` |
| 根目录 | 留空，使用仓库根目录 |

仓库已提供`package.json`和无第三方依赖的构建脚本。`npm run build`会检查现有正式页面，再把网站文件复制到`dist`；不需要React、Vite或其他框架。制作记录、维护脚本与仓库配置不会进入`dist`。

若之前出现`Could not read package.json`或`ENOENT`，是旧版本尚未提供npm构建入口。请使用本次修复后的提交，确认以上设置后重新部署。不要仅重试旧提交。构建通过后，仍需在Cloudflare中绑定自定义域名并完成Bing验证。

自动部署连接已开启时，今后推送GitHub可能触发Cloudflare部署。部署完成后再运行IndexNow提交工具；npm构建本身不会向搜索引擎提交网址。

## 命令行等价操作

```text
python tools/prepare_site.py
python tools/validate_site.py
python tools/indexnow.py
python tools/prepare_site.py --zip ../jcvpn-blog-upload.zip
```

上传后检查但不提交：`python tools/indexnow.py --check-live`。

上传后正式提交：`python tools/indexnow.py --submit`。

线上校验会识别Cloudflare自动追加的Web Analytics统计脚本；其余正文与链接仍需匹配发布文件。核对多个页面时会显示进度。

`site.config.json`保存域名及IndexNow配置。IndexNow验证文件须可公开访问；这份配置不是GitHub令牌或账户密码。不得向仓库提交账号密码、私有订阅地址或其他服务密钥。

## 上传包与仓库的区别

压缩包只包含网站实际使用的HTML、资源、数据、两份页面引用的编辑说明、网站地图、robots及IndexNow验证文件。历史预览截图、原始素材、制作过程文档、本地提交状态、Git元数据和维护工具不会装入公开上传包。

仓库另保留编辑文案、维护工具和说明，方便后续更新。部署时请使用上传包，或配置托管平台按相同范围打包，避免把制作记录当成网站内容发布。

## 官方参考

- [Bing：添加并验证网站](https://www.bing.com/webmasters/help/add-and-verify-site-12184f8b)
- [Bing：网站地图与内容发现](https://blogs.bing.com/webmaster/2025/7/Keeping-Content-Discoverable-with-Sitemaps-in-AI-Powered-Search/)
- [IndexNow协议、验证方式和返回码](https://www.indexnow.org/documentation)
- [Sitemap协议与lastmod含义](https://www.sitemaps.org/protocol.html)
