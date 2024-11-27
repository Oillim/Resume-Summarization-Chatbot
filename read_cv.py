
from PyPDF2 import PdfReader
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langsmith.wrappers import wrap_openai
import openai
# Load the PDF file
pdf_path = "data/CV-NguyenMinhVu-HYRED.pdf"
reader = PdfReader(pdf_path)

# Extract text from each page
resume_docs = reader.pages[0].extract_text()

load_dotenv()

client = wrap_openai(openai.Client())
model = ChatOpenAI(model='gpt-3.5-turbo')


template = """
You are a HR manager at a company. You have received a resume from a candidate. You need to summarize the important information from the resume. Here is the resume:
{resume}
"""

prompt_template = ChatPromptTemplate.from_template(template)
prompt = prompt_template.invoke({"resume": resume_docs})
result = model.invoke(prompt)
print(result.content)