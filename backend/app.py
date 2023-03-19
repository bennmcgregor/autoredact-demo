from flask import Flask, request
app = Flask(__name__)
	
@app.route('/redactor', methods = ['POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      return 'file uploaded successfully'
		
if __name__ == '__main__':
   app.run(debug = True)