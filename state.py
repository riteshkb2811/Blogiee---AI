from pydantic import BaseModel
       


class BlogState(BaseModel):
    topic:str=""
    audience:str=""

    research:str=""
    research_state:str=""

    draft:str=""
    draft_state:str=""

    final_draft:str=""

    revision_count:int=0