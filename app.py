import streamlit as st
from model import Model
from database import Database
from file_io import FileHandler
import os
from dotenv import load_dotenv
from streamlit_pdf_viewer import pdf_viewer
class ResumeProcessorApp:
    def __init__(self):
        self.db = Database()
        self.model = Model()
        self.file_handler = FileHandler()
    def format_dict_as_markdown(self, data):
        """Format dictionary into a Markdown-friendly string."""
        formatted = "\n".join(f"- **{key.capitalize()}**: {value}" for key, value in data.items())
        return formatted

    def process_resumes(self):
        """Handle file upload and resume processing"""
        st.sidebar.title("Upload Resumes Session")
        uploaded_files = st.sidebar.file_uploader("Upload Resume(s)", type=["pdf", "docx"], accept_multiple_files=True)
        if uploaded_files:
            
            for uploaded_file in uploaded_files:
                st.sidebar.write(f"Added {uploaded_file.name} to database successfully!")
                with st.sidebar.expander(f"Preview {uploaded_file.name}"):
                    binary_data = uploaded_file.getvalue()
                    pdf_viewer(input=binary_data, width=400)
                if st.sidebar.button(f"Summarize {uploaded_file.name}"):
                    extracted_data= self.file_handler.process_resume(uploaded_file)
                    if "messages" not in st.session_state:
                        st.session_state.messages = []

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Summary for {uploaded_file.name}:\n\n{self.format_dict_as_markdown(extracted_data)}"
                    })
                    st.sidebar.success(f"Summary for {uploaded_file.name} successfully!")
    def handle_chat(self):
        """Handle the chat section where users can ask questions"""
        st.header("Chat with the HR FAQ Bot")

        # Session state to store the chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display previous chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User input
        if prompt := st.chat_input("Ask a question about your application or resume"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get response from agent_sql_tool
            response = self.model.agent_sql_tool(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Display assistant's response
            with st.chat_message("assistant"):
                st.markdown(response)

    def run(self):
        """Run the Streamlit app"""
        self.process_resumes()
        self.handle_chat()

if __name__ == "__main__":
    load_dotenv()
    app = ResumeProcessorApp()
    app.run()