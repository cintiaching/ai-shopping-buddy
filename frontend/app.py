# frontend.py

import gradio as gr
import time
from chatbots.shopping_buddy import shopping_buddy

# Create the Gradio Blocks interface
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages")  # Create a chatbot component
    msg = gr.Textbox()  # Create a textbox for user input
    clear = gr.ClearButton([msg, chatbot])  # Create a clear button
    chat_history = []
    thread_id = 1


    def respond(message, chat_history):  # Define the respond function
        global thread_id  # Use global thread_id
        if message.lower() == "clear":  # Check for clear command
            thread_id += 1  # Increment thread_id to clear memory
            chat_history.append(
                {"role": "assistant", "content": "Memory cleared. Starting a new thread."})  # Notify user
            return "", chat_history  # Return updated chat history

        bot_message = next(shopping_buddy(message, thread_id))  # Use shopping_buddy with thread_id
        if message != "":
            chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})  # Append bot message to history
        time.sleep(1)  # Simulate processing time
        return "", chat_history  # Return empty string for the message and updated chat history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])  # Set up the submit action

    # Trigger initial greeting by submitting an empty message on load
    demo.load(lambda: respond("", []), None, [msg, chatbot])

# Launch the interface
if __name__ == "__main__":
    demo.launch()  # Launch the Blocks interface
