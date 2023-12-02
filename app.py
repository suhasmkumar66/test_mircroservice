import json,falcon,sys,re,uuid
import pymysql
from datetime import datetime
import base64

def conn_db():
	conn = pymysql.connect( 
			host='cs5721-project-suhasmkumar66-35d6.a.aivencloud.com', 
			user='avnadmin',  
			password = "AVNS_9ZVRUDfaIDQXFi0H9r1",  
			port=27477,
			cursorclass=pymysql.cursors.DictCursor
			)
	return conn
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
			print(sQry)
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
			print(result)
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
	def on_post(self,req,resp):
		conn = conn_db()
		data = json.loads(req.stream.read())
		random = str(uuid.uuid4()) 
		random = random.upper()
		random = random.replace("-","")
		order_number = random[0:10]
		for row in data:
			if 'category_id' in row and 'product_id' in row and 'customer_id' in row and 'quantity' in row and 'price' in row:
				Iqry = "INSERT INTO `orders`.cart_details (`customer_id`,`category_id`,`product_id`,\
					`order_number`,`quantity`,`price`) \
					values ({0},{1},{2},'{3}',{4},{5})"\
					.format(row['customer_id'],row['category_id'],row['product_id'],str(order_number),row['quantity'],row['price'])
				print(Iqry)
				cur = conn.cursor()
				cur.execute(Iqry)
				conn.commit()
				
		result = {"msg":"cart created sucessfully","OrderNo":str(order_number)}
		resp.status = falcon.HTTP_200
		resp.body = json.dumps(result)

class PlaceOrderClass:
	def on_post(self,req,resp):
		conn = conn_db()
		data = json.loads(req.stream.read())
		if 'order_number' in data and 'delivery_type' in data:
			sQry = "select * from `orders`.cart_details where order_number = '{0}'".format(data['order_number'])
			cur = conn.cursor()
			cur.execute(sQry)
			result = cur.fetchall()
			now = datetime.now()
			for row in result:
				Iqry = "INSERT INTO `orders`.order_details (`customer_id`,`product_id`,`category_id`,\
					`quantity`,`price`,`datetime`,`delivery_type`,`order_status`,`order_number`) \
					values ({0},{1},{2},{3},{4},'{5}','{6}','{7}','{8}')"\
					.format(row['customer_id'],row['product_id'],row['category_id'],row['quantity'],row['price'],now.strftime("%Y-%m-%d %H:%M:%S"),data['delivery_type'],'Order Confirmed',data['order_number'])
				print(Iqry)
				cur = conn.cursor()
				cur.execute(Iqry)
				conn.commit()
			#commented now for testing purpose
			# dQry = "delete from `orders`.cart_details where order_number = '{0}'".format(data['order_number'])
			# cur = conn.cursor()
			# cur.execute(dQry)
			# conn.commit()
			result = {"msg":"order created sucessfully","OrderNo":data['order_number'],'ordertime':now.strftime("%Y-%m-%d %H:%M:%S")}
			resp.status = falcon.HTTP_200
			resp.body = json.dumps(result)

api = falcon.API()
api.add_route('/register',RegisterClass())

api.add_route('/login',LoginClass())

api.add_route('/get-products', GetProductsClass())

api.add_route('/search-products', SearchProductsClass())

api.add_route('/addtocart', AddCartClass())

api.add_route('/placeOrder', PlaceOrderClass())