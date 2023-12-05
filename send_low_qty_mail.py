import json,falcon,sys
import pymysql
from datetime import datetime
import os,ssl
from email.message import EmailMessage
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


conn = pymysql.connect( 
		host='cs5721-project-suhasmkumar66-35d6.a.aivencloud.com', 
		user='avnadmin',  
		password = "AVNS_9ZVRUDfaIDQXFi0H9r1",  
		port=27477,
		cursorclass=pymysql.cursors.DictCursor
		)
cur = conn.cursor()


def create_html_table(data):
	table_html = "<table border='1'><tr><th>Product Name</th><th>Product Description</th><th>Required Quantity</th></tr>"
	for row in data:
		table_html += f"<tr><td>{row['product_name']}</td><td>{row['product_description']}</td><td>{row['quantity']*10}</td></tr>"
	table_html += "</table>"
	return table_html
	
	
	
def send_mail(row,toAddress):
	table_html = create_html_table(row)
	print(table_html)
	email_sender = "suhasmkumar66@gmail.com"
	email_password = 'mzal hfmd cvle vbft'
	email_receiver = toAddress

	subject = 'Out of Stock Pharm E Cart'
	body = """
Dear Vendor,
<br>
<br>
Below Products are out of stock and to be supplied Immediately
<br>
<br>
{0}
<br>
<br>
Regards,
<br>
Pharm-E-cart
""".format(table_html)
	em = MIMEMultipart('multipart')
	em['From'] = email_sender
	em['To'] = email_receiver
	em['Subject'] = subject
	# em.set_content(body)
	part1 = MIMEText(body, 'html')
	em.attach(part1)


	context = ssl.create_default_context()
	with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
		smtp.login(email_sender,email_password)
		smtp.sendmail(email_sender,email_receiver,em.as_string())


if __name__ == "__main__":
	sQry = "select * from `products`.product_list where quantity <= '5'"
	cur = conn.cursor()
	cur.execute(sQry)
	result = cur.fetchall()
	result_list = []
	for row in result:
		result_list.append(row)
		now = datetime.now()
		Iqry = "INSERT INTO `products`.inventory_products (`product_id`,`category_id`,\
					`quantity`,`price`,`datetime`,`pharmacist_id`,`order_status`) \
					values ({0},{1},{2},{3},'{4}','{5}','{6}')"\
					.format(row['product_id'],row['category_id'],15,row['price'],str(now.strftime("%Y-%m-%d %H:%M:%S")),0,'PO Raised')
		print(Iqry)
		cur.execute(Iqry)
		conn.commit()
		
	if len(result_list) > 0:
		sQry = "select * from `users`.customers where role = 'Vendor'"
		cur = conn.cursor()
		cur.execute(sQry)
		result = cur.fetchall()
		for row in result:
			send_mail(result_list,row['email'])