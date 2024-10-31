# frontend.py

import gradio as gr
import time
from chatbots.shopping_buddy import shopping_buddy  # Import the shopping_buddy function

# Create the Gradio Blocks interface
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages")  # Create a chatbot component
    msg = gr.Textbox()  # Create a textbox for user input
    clear = gr.ClearButton([msg, chatbot])  # Create a clear button

    def respond(message, chat_history):  # Define the respond function
        bot_message = next(shopping_buddy(message))  # Use shopping_buddy to get the assistant's message
        chat_history.append({"role": "assistant", "content": bot_message})  # Append bot message to history
        time.sleep(1)  # Simulate processing time
        return "", chat_history  # Return empty string for the message and updated chat history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])  # Set up the submit action

# Launch the interface
if __name__ == "__main__":
    demo.launch()  # Launch the Blocks interface
