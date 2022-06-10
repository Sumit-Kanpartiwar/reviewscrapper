from flask import Flask, request, jsonify, render_template
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo

logging.basicConfig(filename='ineuron_scrapper.log', level=logging.DEBUG)

app = Flask(__name__)

@app.route("/xyz", methods=['POST','GET']) # route to show the courses data in a web UI
@cross_origin()
def test():
    if request.method =='GET':
        try:
            logging.info("trying to go to website 'https://www.ccbp.in' and obtain the beautiful soup html parser object for all the reviews available")
            website_url = "https://www.ccbp.in"
            uClient = uReq(website_url)
            webpage = uClient.read()
            uClient.close()
            webpage_html = bs(webpage, "html.parser")
            bigboxes = webpage_html.findAll("nav", {"class": "nav-menu-home-3 w-nav-menu"})
            rlink = list(bigboxes[0])[4]['href']
            reviewslink = website_url + rlink
            reviews = requests.get(reviewslink)
            reviews.encoding = 'utf-8'
            reviews_html = bs(reviews.text, "html.parser")
            big = reviews_html.find_all("div", {"class": "collection-tems w-dyn-item"})
        except Exception as e:
            print('An error occured while parsing the reviews from the website')
            logging.error('An error occured while parsing the reviews from the website')
            logging.exception(f"the error is: {e}")
        try:
            review = []
            for r in range(len(big)):
                try:
                    Name = big[r].div.div.div.div.text
                except:
                    Name = "No Name"

                try:
                    Designation = list(big[r].div.div)[1].div.text
                except:
                    Designation = "Not mentioned"

                try:
                    Comment = list(big[r].div.div)[2].p.text
                except:
                    Comment = "No comments"

                mydict = {"Name": Name, "Designation": Designation, "Comment": Comment}
                review.append(mydict)
        except Exception as e:
            print(f'An error occured while parsing the reviews from the website{e}')
            logging.error('An error occured while extracting the students data and storing it in csv file')
            logging.exception(f"the error is: {e}")

        try:
            logging.info("trying to store the students data in NoSQL- Mongo DB")
            client = pymongo.MongoClient(f"mongodb+srv://mongodb:mongodb@cluster0.nlmjr.mongodb.net/?retryWrites=true&w=majority")
            db1 = client['ineuronscrapper']
            collect = db1['NxtWave_reviews']
            collect.insert_many(review)
            return jsonify("done")
        except Exception as e:
            print(f"{e}")
            logging.error('An error occured while storing the students data in mongo DB')
            logging.exception(f"the error is: {e}")


if __name__=='__main__':
    app.run()

