
from state import BlogState
import os 
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()
key1=os.getenv("GroqKEY")
llm=ChatGroq(model="openai/gpt-oss-20b",groq_api_key=key1,temperature=float(0.6))

research_prompt=ChatPromptTemplate.from_messages(
    [{
        "role":"system", "content":
        """
     You are a research agent .Given a blog topic and target audience ,produce a clear
     "1. 5-7 key points the blog should cover ",
     "2. Important facts,stats, or examples for each point",
     "3. Suggested angle or hook",
     "Be concise.Use bullet points. Do not write the full blog yet."
    """
    },
    { "role":"user", "content":"\n Blog Topic: {topic}\n Target Audience: {audience}\n,{revision_hints},Write the research outline now"}]   
)

def researcher_agent(state:BlogState,feedback:str=""):
    revision_hint=f"This feedback is provided by the human for the blog draft.Please address it :{feedback}"
    if not feedback:
        revision_hint="This is your first attempt"
    chain = research_prompt | llm
    response = chain.invoke({
        "topic": state.topic,
        "audience": state.audience,
        "revision_hints": state.research_state
    })
    return {"research": response.content,"research_state": revision_hint}



writer_prompt=ChatPromptTemplate.from_messages(
    [{
        "role":"system", "content":
        """
     You are a blog writing  agent. You will be provided with detailed research.
     Write a complete interesting blog post which will engage the readers.
     Rules:
        "Length: 500-800 words\n"
        "Write according to the topics which will suit the target audience,tone,feelings,emotions in it"
        "Do not add word count at the end"  
    """
    },
    { "role":"user", "content":"\n Blog Topic: {topic}\n, Target Audience: {audience}\n,Research:{research}\n,{revision_hints}\n.Write the draft now"}]   
)


def writer_agent(state:BlogState,feedback:str=""):
    revision_hint=f"This feedback is provided by the human for the blog draft.Please address it: {feedback}"
    if not feedback:
        revision_hint="This is your first attempt"
    chain = writer_prompt | llm
    response = chain.invoke({
        "topic": state.topic,
        "audience": state.audience,
        "research":state.research,
        "revision_hints": state.draft_state
    })
    return {"draft": response.content,"draft_state": revision_hint}

final_draft_prompt=ChatPromptTemplate.from_messages(
    [{
        "role":"system", "content":
        """
       You are an editing agent and you are going to take the draft  and make it a proper final blog out of it.
       Rules:
        "Fix grammer andd spelling and awkward phrases",
        "See if any bad word are there remove those away and replace it with some other words",
        "Proper spacing and formatting for the blog",
        "heading will be bold and italics and subheading will be in italics",
        "Make the blog engaging and interesting",
        "Output should final polished blog not the commentary"
        "blog should be in humanized way not like created by an AI Agent"
    """
    },
    { "role":"user", "content":" Blog Topic: {topic},draft:{draft},.Write the blog now"}]   
)


def final_draft(state:BlogState):
    chain = final_draft_prompt | llm
    response = chain.invoke({
        "topic": state.topic,
        "draft": state.draft
    })
    return {"final_draft": response.content}
