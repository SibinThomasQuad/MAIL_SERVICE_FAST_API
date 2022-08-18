from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import hashlib
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Common:
    def tockens(self):
        
        #folder name to keep tockens
        
        return 'Tockens'
    
    def errors(self):
        
        #folder name to keep error logs
        
        return 'Errors'


#----------------------------------- LOGGING -----------------------------------------------------------------
class Log:
    def error(self,error):
        
        #function to log errors
        
        common = Common()
        error = str(error)
        error_code = hashlib.md5(error.encode())
        error_key = common.errors()+'/'+error_code.hexdigest()
        f = open(str(error_key), "a")
        f.write(error)
        f.close()
        return error_code.hexdigest()
        
#---------------------------------- MESSAGING ----------------------------------------------------------------
class Message:
    def sent_gmail(self,to,subject,body,html,signature,me,password):

        #SMTP Function for gmail

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = to
        text = body
        html = html+"<br></br>"+signature
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(me, password)
        mail.sendmail(me, to, msg.as_string())
        mail.quit()
    
    def sent_yahoomail(self,to,subject,body,html,signature,me,password):

        #SMTP Function for yahoo

        mail = smtplib.SMTP('smtp.mail.yahoo.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(me, password)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = to
        text = body
        html = html+"<br></br>"+signature
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        mail.sendmail(me, to, msg.as_string())
        mail.quit()

#---------------------------------- MODALS GMAIL--------------------------------------------------------------
class GmailBody(BaseModel):

    #Getting the post data to sent Gmail

    id: int
    to: str
    subject: str
    body: str
    html: str
    signature: str
    tocken : str

class GmailConfig(BaseModel):

    #Getting the post data to config Gmail

    id: int
    email: str
    password: str


#---------------------------------- MODALS YAHOO--------------------------------------------------------------
class YahooConfig(BaseModel):

    #Getting the post data to config Yahoomail

    id: int
    email: str
    password: str

class YahoomailBody(BaseModel):

    #Getting the post data to sent Yahoomail

    id: int
    to: str
    subject: str
    body: str
    html: str
    signature: str
    tocken : str

#---------------------------------- APP CONFIG ----------------------------------------------------------------
app = FastAPI()

#---------------------------------- ROUTES --------------------------------------------------------------------
@app.get("/")
def read_root():
    info = {
        "service":"EMAIL MICRO SERVICE",
        'Services':'Gmail,Yahoo',
        'Documentation':'domain/docs',
        'Version':'1.0','Creator':'Sibin Thomas'
        }
    return info

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post('/gmail/add/config',
description="Pass the gmail username and password to create configraion.Keep the tocken that return to sent the emails")
def AddConfigGmail(configInfo: GmailConfig):
    config_data = {}
    config_data['id'] = configInfo.id
    config_data['email'] = configInfo.email
    config_data['password'] = configInfo.password
    config_string = str(configInfo)
    key_result = hashlib.md5(config_string.encode())
    common = Common()
    key = common.tockens()+'/'+key_result.hexdigest()
    key_tocken = key_result.hexdigest()
    f = open(str(key), "a")
    f.write(str(json.dumps(config_data)))
    f.close()
    return {"status": True,"tocken":str(key_tocken)}

@app.post('/yahoo/add/config',
description="Pass the yahoo username and password to create configraion.Keep the tocken that return to sent the emails,in some servers like verizon use app password")
def AddConfigYahoo(configInfo: YahooConfig):
    config_data = {}
    config_data['id'] = configInfo.id
    config_data['email'] = configInfo.email
    config_data['password'] = configInfo.password
    config_string = str(configInfo)
    key_result = hashlib.md5(config_string.encode())
    common = Common()
    key = common.tockens()+'/'+key_result.hexdigest()
    key_tocken = key_result.hexdigest()
    f = open(str(key), "a")
    f.write(str(json.dumps(config_data)))
    f.close()
    return {"status": True,"tocken":str(key_tocken)}

@app.post('/gmail/sent/mail',
description="This is the api to sent the mail from your gmail account.use the tocken that you got at the time of configration")
def gmail_sent(message_info: GmailBody):
    common = Common()
    file_name = common.tockens()+'/'+message_info.tocken
    try:
        with open(file_name) as handle:
            dictdump = json.loads(handle.read())
            data =  dictdump
        message = Message()
        message.sent_gmail(message_info.to,message_info.subject,message_info.body,message_info.html,message_info.signature,data["email"],data["password"])
        return {"status": True,"message":"Email Sent"}
    except Exception as e:
        logs = Log()
        error = logs.error(e)
        return {"status": False,"message":"Email Not Sent(Check Token or passed data),Error Code : "+str(error)}

@app.post('/yahoo/sent/mail',
description="This is the api to sent the mail from your yahoo account.use the tocken that you got at the time of configration")
def yahoomail_sent(message_info: YahoomailBody):
    common = Common()
    file_name = common.tockens()+'/'+message_info.tocken
    try:
        with open(file_name) as handle:
            dictdump = json.loads(handle.read())
            data =  dictdump
        message = Message()
        message.sent_yahoomail(message_info.to,message_info.subject,message_info.body,message_info.html,message_info.signature,data["email"],data["password"])
        return {"status": True,"message":"Email Sent"}
    except Exception as e:
        logs = Log()
        error = logs.error(e)
        return {"status": False,"message":"Email Not Sent(Check Token or passed data),Error Code : "+str(error)}
    
