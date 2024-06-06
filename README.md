Для запуска на винде 
py -m venv .venv

source venv/Scripts/activate

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\activate

sudo systemctl restart my_telegram_bot.service

sudo systemctl start my_telegram_bot.service
sudo systemctl start support_bot.service

sudo systemctl start gunicorn
sudo systemctl status gunicorn
sudo systemctl restart gunicorn
sudo systemctl stop gunicorn

systemctl daemon-reload

sudo systemctl restart nginx

ps aux | grep python

sudo systemctl edit --full my_telegram_bot.service
sudo systemctl edit --full support_bot.service