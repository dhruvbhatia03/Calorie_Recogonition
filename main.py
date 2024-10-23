from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from PIL import Image
from keras.preprocessing.image import load_img, img_to_array
import numpy as np
from keras.models import load_model
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image

genai.configure(api_key=os.getenv("Google_API_Key"))



model = load_model('FV.h5')
labels = {0 : 'apple', 1 : 'banana', 2 : 'beetroot', 3 : 'bell pepper', 4 : 'cabbage', 5 : 'capsicum', 6 : 'carrot',
          7 : 'cauliflower', 8 : 'chilli pepper', 9 : 'corn', 10 : 'cucumber', 11 : 'eggplant', 12 : 'garlic', 13 : 'ginger',
          14 : 'grapes', 15 : 'jalepeno', 16 : 'kiwi', 17 : 'lemon', 18 : 'lettuce', 19 : 'mango', 20 : 'onion',
          21 : 'orange', 22 : 'paprika', 23 : 'pear', 24 : 'peas', 25 : 'pineapple', 26 : 'pomegranate', 27 : 'potato',
          28 : 'raddish', 29 : 'soy beans', 30 : 'spinach', 31 : 'sweetcorn', 32 : 'sweetpotato', 33 : 'tomato',
          34 : 'turnip', 35 : 'watermelon'}

fruits = ['Apple', 'Banana', 'Bello Pepper', 'Chilli Pepper', 'Grapes', 'Jalepeno', 'Kiwi', 'Lemon', 'Mango', 'Orange',
          'Paprika', 'Pear', 'Pineapple', 'Pomegranate', 'Watermelon']
vegetables = ['Beetroot', 'Cabbage', 'Capsicum', 'Carrot', 'Cauliflower', 'Corn', 'Cucumber', 'Eggplant', 'Ginger',
              'Lettuce', 'Onion', 'Peas', 'Potato', 'Raddish', 'Soy Beans', 'Spinach', 'Sweetcorn', 'Sweetpotato',
              'Tomato', 'Turnip']

input_prompt="""
You are an expert in nutritionist where you need to see the food items from the image and calculate the total calories, also provide the details of every food items with calories intake is below format
    1. Item 1: no of calories
    2. Item 2:  no of calories
    and so on

    and also tell the nutritional facts and benefits of it.
"""

def home():
    st.title("Welcome to our application .....")
    st.markdown("<p style='font-size:20px;'>Our team has developed an innovative platform aimed at simplifying your wellness journey. Using cutting-edge technologies like calorie recognition through image recognition and an intelligent chatbot powered by Google Gemini, our website provides you with personalized health insights. Track your daily nutritional intake, calculate your BMI, and much more — all from the convenience of our user-friendly interface. Explore the future of health monitoring with our smart solutions designed to keep you on track with your fitness goals!</p>", unsafe_allow_html=True)
    st.image(Image.open("home_image.jpg").resize((700, 350)))

def fetch_calories(prediction):
    try:
        url = 'https://www.google.com/search?&q=calories in ' + prediction
        req = requests.get(url).text
        soup = BeautifulSoup(req, 'html.parser')
        calories = soup.find("div", class_="BNeawe iBp4i AP7Wnd").text
        return calories
    
    except Exception as e:
        st.error("Error! \nUnable able to fetch the Calories")
        print(e)


def processed_img(img_path):
    img = load_img(img_path, target_size=(224, 224, 3))
    img = img_to_array(img)
    img = img / 255
    img = np.expand_dims(img, [0])
    answer = model.predict(img)
    y_class = answer.argmax(axis=-1)
    print(y_class)
    y = " ".join(str(x) for x in y_class)
    y = int(y)
    res = labels[y]
    print(res)
    return res.capitalize()

def get_gemini_repsonse(image,prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([image[0], prompt])
    return response.text

def input_image_setup(img_file):
    bytes_data = img_file.getvalue()

    image_parts = [
        {
            "mime_type": img_file.type,  # Get the mime type of the uploaded file
            "data": bytes_data
        }
    ]
    return image_parts

def get_gemini_nutrition(food):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([f"You are an expert nutritionist where you need to tell me about nutritional facts and benefits of {food}."])
    return response.text


def calculate_bmi(weight, height):
    height_in_meters = height / 100

    bmi = weight / (height_in_meters ** 2)
    return round(bmi, 2)

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"
    
def calorie_recogonition():
    st.title("Calorie Recogonition System")
    img_file = st.file_uploader("Choose an Image", type=["jpg", "png"])
    if img_file is not None:
        img = Image.open(img_file).resize((250, 250))
        st.image(img, use_column_width=False)
        save_image_path = './upload_images/' + img_file.name
        with open(save_image_path, "wb") as f:
            f.write(img_file.getbuffer())

        # if st.button("Predict"):
        if img_file is not None:
            result = processed_img(save_image_path)
            print(result)
            if result in vegetables:
                st.info('**Category : Vegetables**')
            else:
                st.info('**Category : Fruit**')
            st.success("**Predicted : " + result + '**')
            cal = fetch_calories(result)
            if cal:
                st.warning('**' + cal + '(100 grams)**')

        if st.button("Wrong Item Detected ?"):
            image_data=input_image_setup(img_file)
            response=get_gemini_repsonse(image_data,input_prompt)
            st.subheader("The Response is")
            st.write(response)
        
        if st.button("Get nutritional facts about the food item"):
            st.subheader("Nutritional Facts:")
            st.write(get_gemini_nutrition(result))

def bmi_calculator():
    st.title("Body-Mass-Index (BMI) Calculator")
    weight = st.number_input("Enter your weight (in kg)", min_value=0.0, format="%.2f")
    height = st.number_input("Enter your height (in cm)", min_value=0.0, format="%.2f")

    if st.button("Calculate BMI"):
        if weight > 0 and height > 0:
            bmi = calculate_bmi(weight, height)
            category = bmi_category(bmi)
            st.success(f"Your BMI is {bmi} ({category})")
        else:
            st.error("Please enter valid values for weight and height.")

def get_answer(user_input):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([f"You are an expert nutritionist chatbot you have to answer the question: {user_input} and please try to answer to some extent(Don't give very big answers)"])
        return response.text
    except Exception as e:
        return "Error: Unable to generate a response."

def nutritionist_chatbot():
    st.title("Our Nutritionist Chatbot")

    # Chat history placeholder
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    user_input = st.text_input("You: ", placeholder="Ask me anything...")

    if user_input:
        
        response = get_answer(user_input)
            
        st.session_state['chat_history'].append(("Bot", response))
        st.session_state['chat_history'].append(("You", user_input))

    for sender, message in st.session_state['chat_history'][::-1]:
        if sender == "Bot":
            st.write(f"**{sender}:** {message}")
        else:
            st.info(f"**{sender}:** {message}")

      

def about():
    pass

def contact_us():
    st.title("THE MPR TEAM .......")
    st.subheader("1. Aditya Rawat : dhruv04814902022@msijanakpuri.com")
    st.subheader("2. Dhruv Bhatia : dhruv04814902022@msijanakpuri.com")
    st.subheader("3. Supriyo Nath : Supriyo02014902022@msijanakpuri.com")
    st.markdown("<p style='font-size:25px;'>BCA 3rd Year<br>Section:- B (Morning Shift)</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:40px;'>Maharaja Surajmal Institute</p>", unsafe_allow_html=True)

def run():
    
    st.sidebar.title("Health Estimo")
    logo = Image.open("logo.png").resize((100, 100))
    st.sidebar.image(logo)
    

    nav = st.sidebar.radio("Navigate From Here ...", ["Home", "Calorie Recogonition", "BMI Calculator", "Nutritionist ChatBOT", "About", "Contact Us"])
    

    if nav == "Home":
        home()
    elif nav == "Calorie Recogonition":
        calorie_recogonition()
    elif nav == "BMI Calculator":
        bmi_calculator()
    elif nav == "Nutritionist ChatBOT":
        nutritionist_chatbot()
    elif nav == "About":
        about()
    elif nav == "Contact Us":
        contact_us()




run()