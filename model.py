import openai
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langsmith.wrappers import wrap_openai
import json
from database import Database
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

class Model:
    def __init__(self):
        self.client = wrap_openai(openai.Client())
        self.model = ChatOpenAI(model='gpt-3.5-turbo')
        self.db = Database()
        self.db_uri = "mysql+mysqlconnector://root:rootpassword@127.0.0.1:3306/ResumeDB"
        self.load_db = SQLDatabase.from_uri(self.db_uri)
    def process_with_openai(self, resume):
        template = """
            You are a HR manager at a company. You have received a resume from a candidate. You need to extract the information with the following database format:
            (name, email, phone, skills, experience, education, summary). More specific, the output must follow this format:
            {{
                "name": Name here,
                "email": email here,
                "phone": "phone number here,
                "skills": summarize skills here (string type only),
                "experience": summarize work experience here,
                "education": short summary of education here,
                "summary": short summary here.
            }}
            The resume you received is:
            {resume}
            """
        prompt_template = ChatPromptTemplate.from_template(template)
        prompt = prompt_template.invoke({"resume": resume})
        result = self.model.invoke(prompt)
        return(json.loads(result.content))
    
    def get_response(self, user_input):
        """Get the response from the chatbot model"""
        template = """
            You are a HR manager at a company. You are answering questions from job applicants. Here is the conversation:
            {conversation}
        """
        prompt_template = ChatPromptTemplate.from_template(template)
        prompt = prompt_template.invoke({"conversation": user_input})
        response =self.model.invoke(prompt)
        return response.content
    def get_chema(self, _):
        return self.load_db.get_table_info()
    def run_query(self, query):
        return self.load_db.run(query)
    def agent_sql_tool(self, user_input):
        template = """
        Based on the table schem below, write a SQL query that would help answer the user question:
        {schema}

        Question: {question}
        SQL Query:
        """
        prompt = ChatPromptTemplate.from_template(template)

        sql_chain= (
            RunnablePassthrough.assign(schema=self.get_chema)
            | prompt
            | self.model.bind(stop="\nSQL Result:")
            | StrOutputParser()
        )


        full_template = """
        Based on the table schem below, question, SQL query and SQL response, write a natural language response to the user question.
        {schema}

        Question: {question}
        SQL Query: {query}
        SQL Response: {response}
        """
        full_prompt = ChatPromptTemplate.from_template(full_template)
        full_chain = (
            RunnablePassthrough.assign(query=sql_chain).assign(
                schema=self.get_chema,
                response=lambda variables: self.run_query(variables["query"])
            )
            | full_prompt
            | self.model 
        )
        full_response = full_chain.invoke({"question": user_input})
        return full_response.content