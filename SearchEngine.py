from flask import Flask, render_template, request
import queryindex2

app = Flask(__name__)

@app.route('/')
def student():
   return render_template('student.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      #n = request.args.get('Name')
      n = request.form['Name']
      resultlist = queryindex2.output(n)
      return render_template("result.html", Data = resultlist)

if __name__ == '__main__':
   app.run(debug = True)