# Telegram CN Archive Bot

将网页转录为 Telegraph。

该项目在 [telegraph_export_bot](https://github.com/gaoyunzhi/telegraph_export_bot) 的基础上进行了中文本地化，并优化了一些性能。

你可以访问 [@CNArchiveBot](https://t.me/CNArchiveBot) 来体验该项目。  
有问题可通过 [Issues](https://github.com/NullPointerMaker/telegram_cn_archive_bot/issues) 或 [@NPDev](https://t.me/NPDev) 反馈。

## 如何使用

向机器人发送链接，机器人会将该网页转录为 Telegraph 并将其链接回复给你。

## 附加功能

用户可以编辑生成的 Telegraph。

## 如何部署

请先使用 [@BotFather](https://t.me/botfather) 生成一个机器人并获得 API Token。  
再将 API Token 填入 `token` 文件。然后运行 `python setup.py`。  
机器人将会在部署完成后自动运行。