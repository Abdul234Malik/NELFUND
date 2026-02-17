from app.core.config import OPENAI_API_KEY  # noqa: F401
from app.agents.qa_chain import answer_question

result = answer_question("Who is eligible for the NELFUND student loan?")
print(result)
