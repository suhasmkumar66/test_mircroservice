import json,falcon,sys,re,uuid
import pymysql
from datetime import datetime
import base64
import os,ssl
from email.message import EmailMessage
import smtplib

def conn_db():
	conn = pymysql.connect( 
			host='cs5721-project-suhasmkumar66-35d6.a.aivencloud.com', 
			user='avnadmin',  
			password = "AVNS_9ZVRUDfaIDQXFi0H9r1",  
			port=27477,
			cursorclass=pymysql.cursors.DictCursor
			)
	return conn

def create_email_and_send(customer_id,order_status,order_number):
	conn = conn_db()
	#get customer mailing address
	UserQry = "select * from `users`.customers where id = '{0}'".format(int(customer_id))
	cur = conn.cursor()
	cur.execute(UserQry)
	cus_output = cur.fetchone()
	if cus_output is not None:
		subject = "Your order has been {0}".format(order_status)
		#do not change the allignment
		body = """
Dear Customer,

Your order has been {0} and your order Number is {1}

Regards,
Pharm-e-cart
""".format(order_status,order_number)
		toaddress = cus_output['email']
		send_mail(subject,body,toaddress)


def send_mail(subject,body,email_receiver):
	email_sender = "suhasmkumar66@gmail.com" #personal google account is set to send email
	email_password = 'mzal hfmd cvle vbft'
	em = EmailMessage()
	em['From'] = email_sender
	em['To'] = email_receiver
	em['Subject'] = subject
	em.set_content(body)

	context = ssl.create_default_context()

	with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
		smtp.login(email_sender,email_password)
		smtp.sendmail(email_sender,email_receiver,em.as_string())
	

class RegisterClass:
	def on_post(self,req,resp):
		conn = conn_db()
		data = json.loads(req.stream.read())
		if 'first_name' in data and 'last_name' in data and 'username' in data and 'password' in data and 'PPSN' in data and 'address' in data and 'eir_code' in data and 'email' in data:
			sQry = "select * from `users`.customers where username = '{0}'".format(data['username'])
			cur = conn.cursor()
			cur.execute(sQry)
			output = cur.fetchone()
			if output is not None:
				result = {'error':'username exists'}
				resp.status = falcon.HTTP_400
				resp.body = json.dumps(result)
				return
			sQry = "select * from `users`.customers where email = '{0}'".format(data['email'])
			cur.execute(sQry)
			output = cur.fetchone()
			if output is not None:
				result = {'error':'email exists'}
				resp.status = falcon.HTTP_400
				resp.body = json.dumps(result)
				return
			now = datetime.now()
			Iqry = "INSERT INTO `users`.customers (`first_name`,`last_name`,`username`,\
				`password`,`PPSN`,`address`,`eir_code`,`email`,`role`,`created_date`) \
				values ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')"\
				.format(data['first_name'],data['last_name'],data['username'],\
				data['password'],data['PPSN'],data['address'],data['eir_code'],\
				data['email'],'Customer',now.strftime("%Y-%m-%d %H:%M:%S"))
			cur.execute(Iqry)
			conn.commit()
	 
			result = {"msg":"user registered sucessfully"}
			resp.status = falcon.HTTP_200
			resp.body = json.dumps(result)
		else:
			result = {"error":"required params missing"}
			resp.status = falcon.HTTP_400
			resp.body = json.dumps(result)

class LoginClass:
	def on_post(self,req,resp):
		conn = conn_db()
		data = json.loads(req.stream.read())
		if 'username' in data and 'password' in data:
			sQry = "select * from `users`.customers where username = '{0}'".format(data['username'])
			cur = conn.cursor()
			cur.execute(sQry)
			output = cur.fetchone()
			if output is not None:
				if data['password'] == output['password']:
					result = {'id':output['id'],'first_name':output['first_name'],\
							'last_name':output['last_name'],'PPSN':output['PPSN'],\
								'address':output['address'],'eir_code':output['eir_code'],\
									'email':output['email'],'role':output['role']}
					
					resp.status = falcon.HTTP_200
					resp.body = json.dumps(result)
				else:
					result = {'error':'password is incorrect'}
					resp.status = falcon.HTTP_200
					resp.body = json.dumps(result)
			else:
				result = {'error':'username is incorrect'}
				resp.status = falcon.HTTP_400
				resp.body = json.dumps(result)
			
		else:
			result = {"error":"required params missing"}
			resp.status = falcon.HTTP_400
			resp.body = json.dumps(result)
		

class GetProductsClass:
	def on_post(self,req,resp):
		conn = conn_db()
		data = json.loads(req.stream.read())
		if 'category_id' in data:
			sQry = "select * from `products`.product_list where category_id = '{0}'".format(int(data['category_id']))
			cur = conn.cursor()
			cur.execute(sQry)
			result = cur.fetchall()
			result_list = []
			for row in result:
				result_list.append(row)
			
			resp.status = falcon.HTTP_200
			resp.body = json.dumps(result_list)
		else:
			result = {"error":"required params missing"}
			resp.status = falcon.HTTP_400
			resp.body = json.dumps(result)

class SearchProductsClass:
	def on_post(self,req,resp):
		conn = conn_db()
		data = json.loads(req.stream.read())
		if 'category_id' in data and 'search_key':
			sQry = "select * from `products`.product_list where category_id = '{0}'".format(int(data['category_id']))
			cur = conn.cursor()
			cur.execute(sQry)
			result = cur.fetchall()
			result_list = []
			for row in result:
				if re.search(data['search_key'], row['product_name'], re.IGNORECASE):
					result_list.append(row)
			resp.status = falcon.HTTP_200
			resp.body = json.dumps(result_list)
		else:
			result = {"error":"required params missing"}
			resp.status = falcon.HTTP_400
			resp.body = json.dumps(result)

class AddCartClass:
	def on_post(self, req, resp):
		conn = conn_db()
		data = json.loads(req.stream.read())
		random = str(uuid.uuid4())
		random = random.upper()
		random = random.replace("-", "")
		order_number = random[0:10]
		for row in data:
			if (
				"category_id" in row
				and "product_id" in row
				and "customer_id" in row
				and "quantity" in row
				and "price" in row
			):
				# validate whether quantity is invalid or not
				Qry = f"select quantity from `products`.product_list where category_id='{row['category_id']}' and product_id='{row['product_id']}' "
				cur = conn.cursor()
				cur.execute(Qry)
				result = cur.fetchall()
				for r_set in result:
					if int(r_set["quantity"]) < int(row["quantity"]):
						resp.status = falcon.HTTP_400
						resp.body = json.dumps({"msg": "selected quantity is invalid"})
						return
			Iqry = "INSERT INTO `orders`.cart_details (`customer_id`,`category_id`,`product_id`,\
					`order_number`,`quantity`,`price`) \
					values ({0},{1},{2},'{3}',{4},{5})".format(
				row["customer_id"],
				row["category_id"],
				row["product_id"],
				str(order_number),
				row["quantity"],
				row["price"],
			)
			cur = conn.cursor()
			cur.execute(Iqry)
			conn.commit()

		result = {"msg": "cart created sucessfully", "OrderNo": str(order_number)}
		resp.status = falcon.HTTP_200
		resp.body = json.dumps(result)

class PlaceOrderClass:
	def on_post(self,req,resp):
		conn = conn_db()
		data = json.loads(req.stream.read())
		if 'order_number' in data and 'delivery_type' in data and 'customer_id' in data:
			sQry = "select * from `orders`.cart_details where order_number = '{0}'".format(data['order_number'])
			cur = conn.cursor()
			cur.execute(sQry)
			result = cur.fetchall()
			now = datetime.now()
			for row in result:
				Iqry = "INSERT INTO `orders`.order_details (`customer_id`,`product_id`,`category_id`,\
					`quantity`,`price`,`datetime`,`delivery_type`,`order_status`,`order_number`) \
					values ({0},{1},{2},{3},{4},'{5}','{6}','{7}','{8}')"\
					.format(row['customer_id'],row['product_id'],row['category_id'],row['quantity'],row['price'],now.strftime("%Y-%m-%d %H:%M:%S"),data['delivery_type'],'Confirmed',data['order_number'])
				cur = conn.cursor()
				cur.execute(Iqry)
				conn.commit()

				#Reduce the product quantity from Products
				sPQry = "select * from `products`.product_list where product_id = '{0}'".format(row['product_id'])
				cur.execute(sPQry)
				output = cur.fetchone()
				if output is not None:
					curr_quantity = output['quantity']
					updated_quantity = curr_quantity - row['quantity']
					UptdQry = "Update `products`.product_list set quantity = '{0}' where product_id = '{1}'".format(int(updated_quantity),row['product_id'])
					cur.execute(UptdQry)
					conn.commit()


			dQry = "delete from `orders`.cart_details where order_number = '{0}'".format(data['order_number'])
			cur = conn.cursor()
			cur.execute(dQry)
			conn.commit()

			create_email_and_send(data['customer_id'],'Confirmed',data['order_number'])

			result = {"msg":"order created sucessfully","OrderNo":data['order_number'],'ordertime':now.strftime("%Y-%m-%d %H:%M:%S")}
			resp.status = falcon.HTTP_200
			resp.body = json.dumps(result)
		else:
			result = {"error":"required params missing"}
			resp.status = falcon.HTTP_400
			resp.body = json.dumps(result)

class UpdateOrderClass:
	def on_post(self,req,resp):
		conn = conn_db()
		data = json.loads(req.stream.read())
		if 'order_number' in data and 'order_status' in data and 'customer_id' in data:
			now = datetime.now()
			#update the status against order number
			Uqry = "Update `orders`.order_details set order_status = '{0}',datetime = '{1}' where order_number = '{2}'".format(data['order_status'],now.strftime("%Y-%m-%d %H:%M:%S"),data['order_number'])
			cur = conn.cursor()
			cur.execute(Uqry)
			conn.commit()

			create_email_and_send(data['customer_id'],data['order_status'],data['order_number'])
			result = {"msg":"order status updated sucessfully","OrderNo":data['order_number'],'updatetime':now.strftime("%Y-%m-%d %H:%M:%S")}
			resp.status = falcon.HTTP_200
			resp.body = json.dumps(result)
		else:
			result = {"error":"required params missing"}
			resp.status = falcon.HTTP_400
			resp.body = json.dumps(result)

class getCustomerOrdersClass:
	def on_post(self,req,resp):
		conn = conn_db()
		data = json.loads(req.stream.read())
		if 'customer_id' in data:
			sQry = "SELECT product_list.product_name,product_list.product_description,order_details.quantity,order_details.price,order_details.datetime,order_details.delivery_type,order_details.order_status,order_details.order_number FROM `orders`.order_details INNER JOIN `products`.product_list ON order_details.product_id=product_list.product_id where order_details.customer_id = {0} order by order_number".format(int(data['customer_id']))
			cur = conn.cursor()
			cur.execute(sQry)
			result = cur.fetchall()
			result_list = []
			for row in result:
				result_list.append(row)
			resp.status = falcon.HTTP_200
			resp.body = json.dumps(result)

		else:
			result = {"error":"required params missing"}
			resp.status = falcon.HTTP_400
			resp.body = json.dumps(result)

class updateInventoryClass:
	def on_post(self,req,resp):
		conn = conn_db()
		data = json.loads(req.stream.read())
		if 'order_number' in data:
			sQry = "select * from `orders`.order_details where order_number = '{0}'".format(data['order_number'])
			cur = conn.cursor()
			cur.execute(sQry)
			result = cur.fetchall()
			for row in result:
				sPQry = "select * from `products`.product_list where product_id = '{0}'".format(row['product_id'])
				cur.execute(sPQry)
				output = cur.fetchone()
				if output is not None:
					curr_quantity = output['quantity']
					updated_quantity = int(curr_quantity) + int(row['quantity'])
					UptdQry = "Update `products`.product_list set quantity = '{0}' where product_id = '{1}'".format(int(updated_quantity),row['product_id'])
					cur.execute(UptdQry)
					conn.commit()
			result = {"msg":"Inventory updated sucessfully","OrderNo":data['order_number']}
			resp.status = falcon.HTTP_200
			resp.body = json.dumps(result)
			
		else:
			result = {"error":"required params missing"}
			resp.status = falcon.HTTP_400
			resp.body = json.dumps(result)


class getInventoryProductsClass:
	def on_post(self,req,resp):
		conn = conn_db()
		sQry = "SELECT product_list.product_name,product_list.product_description,inventory_products.quantity,inventory_products.price,inventory_products.datetime,inventory_products.order_status FROM `products`.inventory_products INNER JOIN `products`.product_list ON inventory_products.product_id=product_list.product_id where inventory_products.order_status = 'PO Raised'"	
		cur = conn.cursor()
		cur.execute(sQry)
		result = cur.fetchall()
		result_list = []
		for row in result:
			result_list.append(row)
		resp.status = falcon.HTTP_200
		resp.body = json.dumps(result)


api = falcon.API()
api.add_route('/register',RegisterClass())

api.add_route('/login',LoginClass())

api.add_route('/get-products', GetProductsClass())

api.add_route('/search-products', SearchProductsClass())

api.add_route('/addtocart', AddCartClass())

api.add_route('/placeOrder', PlaceOrderClass())

api.add_route('/updateOderStatus', UpdateOrderClass())

api.add_route('/getCustomerOrders', getCustomerOrdersClass())

api.add_route('/updateInventory', updateInventoryClass())

api.add_route('/getInventoryProducts', getInventoryProductsClass())