# importing json to import jason data into python dictionary
import json

# urllib.request for makinga api call
import urllib.request,requests
# importing flask
from flask import Flask,render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisakey'
db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    

    def __repr__(self) -> str:
        return '<City %r>' % self.name
def get_weather_data(city):
    url =f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&appid=af97f81de56e7b88f2921c9427df533f'
    r = requests.get(url).json()
    return r

@app.route("/")
def index_get():
    cities = City.query.all()
    
    weather_data = []

    for city in cities:

        r = get_weather_data(city.name)
        weather = {
            'city': city.name,
            'temprature': r['main']['temp'] ,
            'desc': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'], 
        }
        
        weather_data.insert(0,weather)
    
    return render_template('weather.html',weather_data=weather_data)

@app.route("/",methods =['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city')

    if new_city:
        exist_city = City.query.filter_by(name = new_city).first()

        if not exist_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)

                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'city does not exist'

            
        else:
            err_msg = 'city already exist!'

    if err_msg:
        flash(err_msg,'error')
    else:
        flash('city added sucessfully')
    return redirect(url_for('index_get'))
    # return render_template('weather.html',weather_data=weather_data)

@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'successfully delete {city.name}', 'sucesss')
    return redirect(url_for('index_get')) 

if __name__ == '__main__':
  app.run(debug=True)
        