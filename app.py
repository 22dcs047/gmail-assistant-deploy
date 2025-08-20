from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - Test</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 50px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 Gmail Assistant - Working!</h1>
        <p>Basic deployment successful. Now we can add features step by step.</p>
        <p>This confirms Vercel is working properly.</p>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
