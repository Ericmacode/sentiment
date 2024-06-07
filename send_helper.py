import requests

def send_tg(msg):
    try:
        url = 'https://api.telegram.org/bot7072348120:AAHhHTZ3l_wg2Cc4PruCFLlReyYuOZCSpVI/sendMessage?chat_id=-4172094165&text=' + msg
        requests.get(url)
        print(msg)
        # print("message sent")
    except Exception as e:
        send_error(f"ERROR send_tg: {e}")
        pass

def send_error(error):
    try:
        url = 'https://api.telegram.org/bot6519888997:AAGPnihV-17TI8bHhp3e0DDLkcVOPcQgwDk/sendMessage?chat_id=-4116846653&text=' + error
        requests.get(url)
        print(error)
    except Exception as e:
        send_error(f"ERROR send_error:{e}")
        pass