# Telegram CN Archive Bot

Telegram 机器人：将网页转录为 Telegraph。

基于 [telegraph_export_bot](https://github.com/gaoyunzhi/telegraph_export_bot) 进行了中文本地化，并优化了一些性能。

你可以访问 [@CNArchiveBot](https://t.me/CNArchiveBot) 来体验该项目。  
有问题可通过 [Issues](https://github.com/NullPointerMaker/telegram_cn_archive_bot/issues) 或 [@NPDev](https://t.me/NPDev) 反馈。

## 特性

* 后续编辑
* 繁简转换

## 部署

1. 使用 [@BotFather](https://t.me/botfather) 生成一个机器人。  
   将 API Token 填入 `config.py` 文件。  
   其它配置按需修改。
2. 在操作系统中安装 Python 3 运行环境。
3. 安装依赖库：  
   ```
   pip3 install -r requirements.txt
   ```
4. Windows 执行 `Telegram-CNArchiveBot.Cmd` 文件。  
   其它操作系统执行 `telegram-cn-archive-bot.bash` 文件。

## 使用

向机器人发送链接，机器人会将该网页转录为 Telegraph 并将其链接回复给你。
