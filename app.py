from flask import Flask, render_template
from flask_pymongo import PyMongo
from scrape_mars import scrape

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/'
mongo = PyMongo(app)
client = mongo.cx

###
# Call the scrape() function from scrape_mars.py
# Store the returned value in Mongo as a Python dictionary
@app.route('/scrape')
def scrape_route():
    # Delete the existing document first to be safe
    client.drop_database('mars_db')
    db = client['mars_db']
    col = db['scrape']
    col.insert_one(scrape())
    return '<p>Successfully scraped data. <a href="/">Return to main page.</a></p>'


###
# Create a root route that will query the MongoDB and pass
# the data into an HTML template to display the data.
@app.route('/')
def root_route():
    db = client['mars_db']
    col = db['scrape']
    latest_scrape = col.find_one()
    return render_template("index.html", **latest_scrape)


if __name__ == '__main__':
    app.run(debug=True)