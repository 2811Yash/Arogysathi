from django.shortcuts import render,redirect
from django.http import JsonResponse
import json
import google.generativeai as genai
from agno.agent import Agent
from agno.models.google import Gemini
# genai.configure(api_key=)
llm = genai.GenerativeModel('gemma-2.0-9b-it')

def chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_input = data.get("question", "")
        response = f"AI Response to: {user_input}"  # Replace with actual AI logic
        return JsonResponse({"response": response})
    return render(request,"index.html")
   
def nutrition(request):
    context = {}

    if request.method == "POST":
        action = request.POST.get("action")

        # IMAGE ANALYSIS
        if action == "analyze_and_chat" and request.FILES.get("image"):
            user_message = request.POST.get("message", "").strip()
            uploaded_image = request.FILES['image']
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            image_path = os.path.join(upload_dir, uploaded_image.name)

            with default_storage.open(image_path, 'wb+') as destination:
                for chunk in uploaded_image.chunks():
                    destination.write(chunk)

            image = Image.open(image_path)
            encoded_image = model.encode_image(image)
            moon_response = model.query(encoded_image, f"give the detailed nutrition analysis of that food from the image and answer this in detail {user_message}")
            image_url = settings.MEDIA_URL + 'uploads/' + uploaded_image.name
            try:
                health_agent = Agent(
                    name="Ayurvedic Nutrition Assistant",
                    role="You are a health and wellness assistant specializing in Ayurvedic and household remedies. You provide nutritional advice based on natural, plant-based, and holistic health approaches.",
                    model=Gemini(id="gemini-2.0-flash"),
                    instructions=[
                        "Never suggest any pharmaceutical or allopathic medicines (e.g., tablets, syrups).",
                        "You can suggest household remedies and Ayurvedic practices only.",
                        "Include nutritional advice and personalized suggestions based on the given context.",
                        f"Prefer the following context when replying: {moon_response}",
                        "Be kind, holistic, and clear in your response.",
                    ],
                    markdown=True
                )

                # Step 2: Generate response
                if user_message:
                    ai_reply = health_agent.run(user_message,stream=False)
                    print(ai_reply)
                    ai_reply = mark_safe(markdown.markdown(ai_reply.content))

                    return render(request, "nutrition.html", {
                        "ai_reply": ai_reply,
                        "user_message": user_message,
                        "image_url": image_url
                    })

            except Exception as e:
                print(f"Error: {e}")
                ai_reply = "Sorry, I am unable to process your request at the moment."
                return render(request, "nutrition.html", {"ai_reply": ai_reply})
    return render(request, "nutrition.html", context)


import moondream as md
from PIL import Image
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("moondream_api")

# Initialize the model
model = md.vl(api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlfaWQiOiJmOWFhNmE4NS1lZTAwLTQwN2QtYTU1OC1jYjZlMzMyZGQ4NDIiLCJpYXQiOjE3MzgwNTA1NDN9.8QYSLbRCCF_JFDUfPQwesCRcvkzwFdZlQHFj2Hm6Oco"
)
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from PIL import Image
import moondream
import os

def analyze_image(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']
        image_path = os.path.join(settings.MEDIA_ROOT, uploaded_image.name)

        # Save the image in media/uploads/
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)  # Ensure uploads folder exists

        image_path = os.path.join(upload_dir, uploaded_image.name)
        with default_storage.open(image_path, 'wb+') as destination:
            for chunk in uploaded_image.chunks():
                destination.write(chunk)

        # Process image with MoonDream API
        image = Image.open(image_path)
        encoded_image = model.encode_image(image)
        response = model.query(encoded_image, "give the full name of the plant given in image with breif description ")
        
        # context['response'] = response
        context['image_url'] = settings.MEDIA_URL + 'uploads/' + uploaded_image.name 
        medicinal_plant_agent = Agent(
            name="Ayurvedic Plant Wisdom",
            role="Specialized in explaining medicinal properties, benefits, and uses of plants in Ayurveda",
            model=Gemini(id="gemini-2.0-flash"),
            instructions=[
                "Focus exclusively on Ayurvedic knowledge and traditional remedies",
                "Structure responses with: 1) Primary Benefits 2) Medicinal Uses 3) Preparation Methods 4) Cautions",
                "Include relevant Sanskrit names and dosha effects (Vata/Pitta/Kapha)",
                "Suggest household formulations (teas, pastes, decoctions)",
                "Highlight nutritional compounds (e.g., 'contains curcuminoids' for turmeric)",
                "Never mention allopathic medicine or synthetic drugs",
                f"Contextualize all advice for: {response} (the plant being discussed)",
                "Use simple language with emoji markers for key points 🌿✨",
                "Cite classical texts like Charaka Samhita when possible"
            ],markdown=True) # Correct path
        ai_reply = medicinal_plant_agent.run("give some info about this plant",stream=False)
        print(ai_reply)
        ai_reply = mark_safe(markdown.markdown(ai_reply.content))
        context['response'] = ai_reply
        return render(request, 'analyze.html', context)

    return render(request, 'analyze.html', context)
import os
from groq import Groq
from dotenv import load_dotenv
import json

from django.utils.safestring import mark_safe
import markdown
def chat_bot(request):
    ai_reply = ""

    if request.method == "POST":
        try:
            user_message = request.POST.get("message", "").strip()
            print(user_message)

            health_agent1 = Agent(
                name="Ayurvedic Health Assistant",
                role="Expert Ayurvedic and natural health advisor focused on wellness using traditional remedies and household practices.",
                model=Gemini(id="gemini-2.0-flash"),
                instructions=[
                    "Do not suggest any allopathic or pharmaceutical medicines (e.g., tablets, capsules).",
                    "You may only recommend household remedies or Ayurvedic suggestions.",
                    "Use empathetic and reassuring language.",
                    "Keep responses clear and easy to follow.",
                ],
                markdown=True
            )

            if user_message:
                ai_reply = health_agent1.run(user_message,stream=False)
                print(ai_reply)
                ai_reply = mark_safe(markdown.markdown(ai_reply.content))
                return render(request, "chatbot.html", {"ai_reply": ai_reply, "user_message": user_message})

        except Exception as e:
            print(f"Error: {e}")  
            ai_reply = "Sorry, I am unable to process your request at the moment."
            return render(request, "chatbot.html", {"ai_reply": ai_reply})

    return render(request, "chatbot.html", {"ai_reply": ai_reply})

from django.utils.safestring import mark_safe
import markdown

def mental_health(request):
    # Initialize chat history in session
    if 'chat_history' not in request.session:
        request.session['chat_history'] = [
            {"sender": "bot", "message": "Hello! I’m here to support your mental well-being. How are you feeling today?"}
        ]

    chat_history = request.session['chat_history']

    if request.method == "POST":
        user_message = request.POST.get("message", "").strip()

        if user_message:
            # Append user's message
            chat_history.append({"sender": "user", "message": user_message})

            try:
                mental_health_agent = Agent(
                    name="Mental Health Support Bot",
                    role="Supportive mental health assistant who helps users reflect on their emotional well-being and detects possible signs of stress, anxiety, or depression from their responses.",
                    model=Gemini(id="gemini-2.0-flash"),
                    instructions=[
                        "Ask gentle, non-invasive questions to understand the user's mental state.",
                        "Do not diagnose or prescribe anything. You are not a medical professional.",
                        "Use empathetic and non-judgmental language.",
                        "Detect signs of stress, anxiety, or depression from the user's language and tone.",
                        "Offer emotional support, mindfulness tips, breathing techniques, or daily journaling practices.",
                        "Always suggest seeking help from a qualified mental health professional if signs of distress are found.",
                        "Avoid discussing medications or any form of treatment.",
                    ],
                    markdown=True
                )
                ai_reply = mental_health_agent.run(user_message,stream=False)
                ai_reply = markdown.markdown(ai_reply.content)
                print(ai_reply)
                chat_history.append({"sender": "bot", "message": ai_reply})

            except Exception as e:
                print(f"Error: {e}")
                ai_reply = "Sorry, I'm unable to process your request right now."
                ai_reply = markdown.markdown(ai_reply)
        else:
            ai_reply = "Hello! I’m here to support your mental well-being. How are you feeling today?"
            ai_reply = mark_safe(markdown.markdown(ai_reply))
        

            chat_history.append({"sender": "bot", "message": ai_reply})
            request.session['chat_history'] = chat_history 

    return render(request, "mental_healt.html", {"chat_history": chat_history})



def reset_chat(request):
    if 'chat_history' in request.session:
        del request.session['chat_history']
    return redirect('mental_health')  # make sure this matches your chat view name
