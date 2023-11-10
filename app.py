import json,falcon

class RegisterClass:
    def on_post(self,req,resp):
        data = json.loads(req.stream.read())
        print(data)
        result = {"msg":"user registered sucessfully"}
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(result)

class LoginClass:
    def on_post(self,req,resp):
        data = json.loads(req.stream.read())
        if data['username'] == "suhas":
            result = {"username":"suhas","age":"27"}
            resp.status = falcon.HTTP_200
        else:
            result = {"error":"username not found"}
            resp.status = falcon.HTTP_400
        resp.body = json.dumps(result)
        



api = falcon.API()
api.add_route('/register',RegisterClass())

api.add_route('/login',LoginClass())