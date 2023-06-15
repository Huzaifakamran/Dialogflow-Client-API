from flask import Flask, request, jsonify,render_template
# from google.cloud import dialogflow
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
import os
import openai
import psycopg2
from datetime import datetime

app = Flask(__name__)
CORS(app)

load_dotenv()

def realtorScrap(address):
    # print(address)
    my_dict = {}
    addressComponents = address['address']['address_components']
    for record in addressComponents:
        if 'street_number' in record['types']:
            my_dict['street_number'] = record['short_name']
            continue
        if 'route' in record['types']:
            my_dict['route'] = record['long_name']
            continue
        if 'locality' in record['types']:
            my_dict['locality'] = record['short_name']
            continue
        if 'administrative_area_level_1' in record['types']:
            my_dict['areaLevelOne'] = record['short_name']
            break
    # print(my_dict)
    locality = my_dict['locality'].replace(' ','-')
    print(locality)
    areaLevelOne = my_dict['areaLevelOne']
    print(areaLevelOne)
    o={}
    target_url = f"https://www.realtor.com/realestateandhomes-search/{locality}_{areaLevelOne}"
    head={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
    resp = requests.get(target_url, headers=head)
    soup = BeautifulSoup(resp.text, 'html.parser')
    allData = soup.find_all("div",{"class":"property-wrap"})
    route = my_dict['route'].split(' ')[0]
    print('route',route)
    inputAddress = my_dict['street_number'] + ' ' + route
    print('input',inputAddress)
    # print(allData)
    for i in range(0, len(allData)):
        address = allData[i].find("div",{"data-label":"pc-address"}).text
        # print(address)
        if inputAddress in address:
            print('under if')
            o["price"]=allData[i].find("span",{"data-label":"pc-price"}).text
            metaData = allData[i].find("ul",{"class":"property-meta"})
            allMeta = metaData.find_all("li")
            for x in range(0, len(allMeta)):
                try:
                    o["bed"]=allMeta[0].text
                except:
                    o["bed"]=None
                try:
                    o["bath"]=allMeta[1].text
                except:
                    o["bath"]=None
                try:
                    o["size-sqft"]=allMeta[2].text
                except:
                    o["size-sqft"]=None
                try:
                    o["size-acre"]=allMeta[3].text
                except:
                    o["size-acre"]=None
            o["address"]=allData[i].find("div",{"data-label":"pc-address"}).text
            o['status'] = True
            # print(o)
            return json.dumps(o)
        
    return json.dumps({
                "status":False,
                "message":"property details unavailable please manually enter property details"
                })

@app.route('/', methods = ['GET'])
def main():
    return 'Please add user id at the end of the url'

@app.route('/<int:id>', methods=['GET'])
def home(id):
    return render_template('index.html',id=id)

@app.route('/address', methods=['POST'])
def address():
    address = request.json
    # formattedAddress = address['address']['formatted_address']
    result = realtorScrap(address)
    print(result)
    return result
    
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json
    address = user_message['address']
    price = user_message['price']
    bed = user_message['bed']
    bath = user_message['bath']
    sizeSqft = user_message['sizeSqft']
    status = request.args.get('status')
    openai.api_key = os.getenv("OPEN_API_KEY")
    if(status == '1'):
        print('under status')
        firstPrompt = f'''
        act as a copywriter specializing in creating listing descriptions for homes for sale. 
        Your objective is to create two unique an engaging and persuasive listing description 
        free of grammatical errors for a property for sale. This description will be read by 
        potential buyers of the property who want to read more and schedule a showing. 
        Make this description no less than 750 characters and more than 1,500 characters. 
        You must only use true and factual data. Highlight the location of the primary suite 
        if there is one. Make the description flow as if the reader is walking room to room in the home. 
        Use all of the following data no more than once to create the descriptions.
        address = {address}\n
        price = {price}\n
        bed = {bed}\n
        bath = {bath}\n
        sizeSqft = {sizeSqft}
        '''
        response = openai.Completion.create(
        model="text-davinci-003", 
        prompt=firstPrompt, 
        temperature=0, 
        max_tokens=1500
        )
        firstResponse = response['choices'][0]['text']
        # print(firstResponse)
        print("GET FIRST RESPONSE")
        return jsonify({
        # "firstResponse":firstResponse
        "firstResponse":firstResponse
        # "secondResponse":secondResponse
    })
    else:
        secondPrompt = f'''
        Act as a social media marketer with an expertise in writing captions for homes for sale. 
        Your objective is to create captions for a facebook post, instagram post, and twitter post using the data below. 
        You must stay in the character limits of each application for each post. The goal is to create an engaging enough caption to 
        entice a potential buyer to click on the link provided for more info. You must include a placeholder for the link to the property. 
        You must include relevant emojis. You must include up to 9 hashtags that are relevant and heavily used in the real estate industry. 
        Layout the caption as such:

        [Headline - Example - Hot New Listing Alert ]
        [Address - {address}]
        [Price - {price}]
        [Bedroom count - {bed}]
        [bathroom count - {bath}]
        [square footage - {sizeSqft}]

        [closing lines, insert link to property, and hashtags]

    '''
        response = openai.Completion.create(
        model="text-davinci-003", 
        prompt=secondPrompt, 
        temperature=0, 
        max_tokens=1500
        )
        secondResponse = response['choices'][0]['text']
        return jsonify({
            "secondResponse":secondResponse
        })

    # return jsonify(response['choices'][0]['text'])
    # print(user_id)
    # user_id = request.args.get('user_id')

    # Send user message to Dialogflow and get response
    # response = detect_intent(user_id, user_message)

    # Return bot response
    # return jsonify({'message': response})

@app.route('/saveChat', methods =['POST'])
def saveChat():
    try:
        print('reached here')
        chatdata = request.json
        status = request.args.get('status')
        # print(type(status))
        uID = request.args.get('id')
        print(uID)
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print('before if')
        if(status == '1'):
            print('under status 1')
            formattedAddress = chatdata[0]['formattedAddress']
            price = chatdata[0]['price']
            bed = chatdata[0]['bed']
            bath = chatdata[0]['bath']
            sizeSqft = chatdata[0]['sizeSqft']
            sizeAcre = chatdata[0]['sizeAcre']
            propertyType = chatdata[0]['propertyType']
            yearBuilt = chatdata[0]['yearBuilt']
            architecturalStyle = chatdata[0]['architecturalStyle']
            bedBathDist = chatdata[0]['bedBathDist']
            commName = chatdata[0]['commName']
            schoolDist = chatdata[0]['schoolDist']
            keyFeatures = chatdata[0]['keyFeatures']
            EEASF = chatdata[0]['EEASF']
            HOA = chatdata[0]['HOA']
            additionalComments = chatdata[0]['additionalComments']
            print(additionalComments)
            datetime_str = chatdata[0]['dateTime']
            datetime_obj = datetime.strptime(datetime_str, '%m/%d/%Y, %I:%M:%S %p')
            dateTime = datetime_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
            query1 = conn.cursor()
            query1.execute("INSERT INTO public.users ( User_id, Created_date,Property_address, Property_type, Listing_price, Number_of_bedrooms, Number_of_bathrooms, Square_footage, Lot_size, Year_built, Architectural_style, Bed_bath_dist, Community_name, School_district, Key_features, Energy_efficiency, Hoa_info, Additional_comments) Values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",(uID,dateTime,formattedAddress,propertyType,price,bed,bath,sizeSqft,sizeAcre,yearBuilt,architecturalStyle,bedBathDist,commName,schoolDist,keyFeatures,EEASF,HOA,additionalComments))
            users_id = query1.fetchone()[0]
            query1.close()
            for record in chatdata[1 : ]:
                sender = record['sender']
                message = record['message']
                user_id = users_id
                datetime_str = record['dateTime']
                datetime_obj = datetime.strptime(datetime_str, '%m/%d/%Y, %I:%M:%S %p')
                dateTime = datetime_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                query2 = conn.cursor()
                query2.execute("INSERT INTO public.chat_history (Message, User_id, Created_date,Sender) Values (%s,%s,%s,%s)",(message,user_id,dateTime,sender))
                query2.close()
            conn.commit()
            return jsonify({
                "status":"Data Saved Successfully"
            })
        elif status == '2':       
            openai.api_key = os.getenv("OPEN_API_KEY")
            botList = []
            # print(botList)
            # print(chatdata)
            for rec in chatdata[1 : ]:
                if rec['sender'] == 'bot':
                    botList.append(rec['message'])
            botResponse = '\n'.join(botList)
            print(botResponse)
            message = chatdata[-1]
            custMessage = message['message']
            response = openai.Completion.create(
            model="text-davinci-003", 
            prompt=f"{botResponse}\nAbove is the response please answer below question by considering the above response and make sure do not give extra spaces at the begining\n{custMessage}", 
            temperature=0, 
            max_tokens=1500
            )
            Response = response['choices'][0]['text']
            return jsonify({
                'response': Response
            })
    except Exception as e:
        print(e)
    finally:
        conn.close()

@app.route('/viewList', methods = ['GET'])
def viewList():
    try:
        uID = request.args.get('id')
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        query1 = conn.cursor()
        query1.execute("Select Property_address,Created_date from public.users where User_id = %s",(uID,))
        data = query1.fetchall()
        query1.close()
        myList = []
        for address,createdDate in data:
            my_dict = {
                'address':address,
                'createdDate': createdDate
            }
            myList.append(my_dict)
        return jsonify(myList)
    except Exception as e:
        print(e)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)