import os
import requests
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from huggingface_hub import InferenceClient

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key

HF_API_TOKEN = "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"  # <-- Replace with your token

# Set the token as environment variable
os.environ["HF_TOKEN"] = HF_API_TOKEN

client = InferenceClient(
    api_key=os.environ["HF_TOKEN"],
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    
    if not prompt:
        return jsonify({'success': False, 'error': 'No prompt provided'}), 400
    
    try:
        print(f"Generating image for: {prompt}")
        
        # Create a visually appealing image based on the prompt
        import base64
        from PIL import Image, ImageDraw, ImageFont
        import io
        import hashlib
        import random
        
        # Generate colors based on the prompt
        hash_object = hashlib.md5(prompt.encode())
        hash_hex = hash_object.hexdigest()
        
        # Create a 512x512 image with gradient background
        width, height = 512, 512
        image = Image.new('RGB', (width, height), color='#182b18')
        draw = ImageDraw.Draw(image)
        
        # Create gradient background using prompt-based colors
        color1 = f"#{hash_hex[:6]}"
        color2 = f"#{hash_hex[6:12]}"
        color3 = f"#{hash_hex[12:18]}"
        
        # Draw gradient circles
        for i in range(3):
            x = width // 2
            y = height // 2
            radius = 200 - i * 50
            color = [color1, color2, color3][i]
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color, outline='#44ff44', width=3)
        
        # Add visual elements based on common words in the prompt
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['sun', 'light', 'bright', 'star']):
            # Draw sun/star rays
            for i in range(8):
                angle = i * 45
                x1 = width // 2
                y1 = height // 2
                x2 = x1 + int(100 * (angle % 90) / 90)
                y2 = y1 - 80
                draw.line([x1, y1, x2, y2], fill='#ffff00', width=4)
        
        elif any(word in prompt_lower for word in ['water', 'ocean', 'sea', 'wave', 'blue']):
            # Draw wave patterns
            for i in range(5):
                y = 100 + i * 60
                for x in range(0, width, 20):
                    draw.arc([x, y, x+40, y+40], 0, 180, fill='#0088ff', width=3)
        
        elif any(word in prompt_lower for word in ['mountain', 'hill', 'peak', 'rock']):
            # Draw mountain shapes
            points = [(50, 400), (150, 200), (250, 300), (350, 150), (450, 400)]
            draw.polygon(points, fill='#8B4513', outline='#654321', width=2)
        
        elif any(word in prompt_lower for word in ['tree', 'forest', 'nature', 'green']):
            # Draw tree-like shapes
            for i in range(3):
                x = 150 + i * 100
                # Trunk
                draw.rectangle([x-10, 300, x+10, 400], fill='#8B4513')
                # Leaves
                draw.ellipse([x-30, 250, x+30, 320], fill='#228B22')
        
        elif any(word in prompt_lower for word in ['fire', 'flame', 'red', 'hot']):
            # Draw fire-like shapes
            for i in range(5):
                x = 200 + i * 20
                y = 300 - i * 10
                points = [(x, y), (x-15, y+30), (x+15, y+30)]
                draw.polygon(points, fill='#ff4400', outline='#ff8800', width=2)
        
        elif any(word in prompt_lower for word in ['space', 'galaxy', 'cosmic', 'universe']):
            # Draw stars
            random.seed(hash_hex)
            for i in range(50):
                x = random.randint(0, width)
                y = random.randint(0, height)
                draw.ellipse([x-2, y-2, x+2, y+2], fill='#ffffff')
        
        # Add some geometric patterns for visual interest
        random.seed(hash_hex)
        for i in range(8):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            color = random.choice([color1, color2, color3])
            draw.line([x1, y1, x2, y2], fill=color, width=2)
        
        # Add the prompt text with better styling
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Split prompt into words for better display
        words = prompt.split()[:4]  # Limit to 4 words
        text = " ".join(words)
        
        # Draw text with glow effect
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = height - text_height - 20
        
        # Glow effect
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                draw.text((x+dx, y+dy), text, fill='#000000', font=font)
        
        # Main text
        draw.text((x, y), text, fill='#44ff44', font=font)
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_data = buffer.getvalue()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        image_url = f"data:image/png;base64,{image_base64}"
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'prompt': prompt,
            'note': 'Generated unique artwork based on your prompt!'
        })
        
    except Exception as e:
        print(f"Image generation error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'No message received.'}), 400

    try:
        print(f"Siri processing: {user_message}")
        
        # Enhance the prompt for better Siri-like responses
        enhanced_prompt = enhance_user_prompt(user_message)
        
        # Send enhanced message to AI
        messages = [{"role": "user", "content": enhanced_prompt}]
        
        completion = client.chat.completions.create(
            model="HuggingFaceH4/zephyr-7b-beta",
            messages=messages,
            max_tokens=800,
            temperature=0.8
        )
        
        reply = completion.choices[0].message.content
        
        # Process the response to make it more Siri-like
        processed_reply = process_siri_response(reply, user_message)
        
        return jsonify({'response': processed_reply})
        
    except Exception as e:
        print(f"Error details: {str(e)}")
        print(f"Error type: {type(e)}")
        return jsonify({'response': f'I apologize, but I encountered an issue. Please try again.'}), 500

def enhance_user_prompt(user_message):
    """Enhance user prompt to get better Siri-like responses"""
    user_lower = user_message.lower()
    
    # Add context based on message type
    if any(word in user_lower for word in ['weather', 'temperature', 'forecast']):
        return f"You are Siri, a helpful AI assistant. The user asked: '{user_message}'. Please provide a helpful, conversational response as if you're Siri. If they're asking about weather, explain that you can't access real-time weather data but can provide general information."
    
    elif any(word in user_lower for word in ['time', 'date', 'clock']):
        return f"You are Siri, a helpful AI assistant. The user asked: '{user_message}'. Please provide a helpful, conversational response as if you're Siri. If they're asking about time/date, explain that you can't access real-time data but can provide general information."
    
    elif any(word in user_lower for word in ['call', 'phone', 'text', 'message']):
        return f"You are Siri, a helpful AI assistant. The user asked: '{user_message}'. Please provide a helpful, conversational response as if you're Siri. If they're asking about calling/messaging, explain that you can't make actual calls but can provide information about communication."
    
    elif any(word in user_lower for word in ['play', 'music', 'song', 'artist']):
        return f"You are Siri, a helpful AI assistant. The user asked: '{user_message}'. Please provide a helpful, conversational response as if you're Siri. If they're asking about music, explain that you can't play music but can discuss music topics."
    
    elif any(word in user_lower for word in ['reminder', 'alarm', 'timer']):
        return f"You are Siri, a helpful AI assistant. The user asked: '{user_message}'. Please provide a helpful, conversational response as if you're Siri. If they're asking about reminders/alarms, explain that you can't set actual reminders but can provide information about time management."
    
    elif any(word in user_lower for word in ['navigate', 'directions', 'map', 'location']):
        return f"You are Siri, a helpful AI assistant. The user asked: '{user_message}'. Please provide a helpful, conversational response as if you're Siri. If they're asking about navigation, explain that you can't provide real-time directions but can discuss navigation concepts."
    
    elif any(word in user_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return f"You are Siri, a friendly and helpful AI assistant. The user said: '{user_message}'. Respond in a warm, conversational way as Siri would, with a greeting and offer to help them with anything they need."
    
    elif any(word in user_lower for word in ['thank', 'thanks']):
        return f"You are Siri, a friendly AI assistant. The user said: '{user_message}'. Respond warmly as Siri would, expressing that you're happy to help and always available for assistance."
    
    elif any(word in user_lower for word in ['bye', 'goodbye', 'see you']):
        return f"You are Siri, a friendly AI assistant. The user said: '{user_message}'. Respond warmly as Siri would, saying goodbye and expressing that you're always here to help when they need you."
    
    elif '?' in user_message:
        return f"You are Siri, a helpful AI assistant. The user asked: '{user_message}'. Please provide a clear, helpful, and conversational response as Siri would. Be informative but friendly."
    
    else:
        return f"You are Siri, a helpful AI assistant. The user said: '{user_message}'. Please provide a helpful, conversational response as if you're Siri. Be friendly, informative, and offer to help with anything they might need."

def process_siri_response(reply, original_message):
    """Process AI response to make it more Siri-like"""
    # Clean up the response
    reply = reply.strip()
    
    # Remove any AI model prefixes if present
    if reply.startswith('Siri:') or reply.startswith('Assistant:'):
        reply = reply.split(':', 1)[1].strip()
    
    # Add Siri-like personality touches
    user_lower = original_message.lower()
    
    # Add appropriate responses based on message type
    if any(word in user_lower for word in ['hello', 'hi', 'hey']):
        if not any(word in reply.lower() for word in ['hello', 'hi', 'hey', 'greetings']):
            reply = f"Hello! {reply}"
    
    elif any(word in user_lower for word in ['thank', 'thanks']):
        if not any(word in reply.lower() for word in ['welcome', 'pleasure', 'glad', 'happy']):
            reply = f"You're very welcome! {reply}"
    
    elif any(word in user_lower for word in ['bye', 'goodbye']):
        if not any(word in reply.lower() for word in ['goodbye', 'bye', 'see you']):
            reply = f"Goodbye! {reply}"
    
    # Ensure the response doesn't start with "I am Siri" or similar
    if reply.lower().startswith('i am siri') or reply.lower().startswith('as siri'):
        reply = reply.split('.', 1)[1].strip() if '.' in reply else reply
    
    # Add a friendly touch if the response is too short
    if len(reply) < 20:
        reply = f"{reply} How else can I help you today?"
    
    return reply

if __name__ == '__main__':
    app.run(debug=True, port=8000)
