from utils import code, check_claude_output, insert_errors, parse_output

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from rerank import ReRankingAlgorithm

from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class TreeSequenceTool(metaclass=SingletonMeta):
    """
    """
    # Class Variables
    general_llm = ChatOpenAI(model_name='gpt-4o')
    retriever = ReRankingAlgorithm()

    def __init__():
        """
        """
        pass

    @classmethod
    def generatorTool(cls, messages, query):
        """
        """
        code_gen_prompt = ChatPromptTemplate.from_messages(
            [
                (
                "system",
                """You are a coding generator with expertise in using ts-kit toolkit for analysing tree-sequences. \n 
                Here is a relevant set of tskit documentation:  \n ------- \n  {context} \n ------- \n Answer the user 
                question based on the above provided documentation. Ensure any code you provide should be a callable function and can be executed \n 
                with all required imports and variables defined. Structure your answer with a description of the code solution. \n
                Then list the imports. And finally list the functioning code block. The function should return a string providing the answer. Here is the user question:""",
                ), 
                ("placeholder", "{messages}"),  
            ]
        )
        structured_code_llm = cls.general_llm.with_structured_output(code, include_raw=True)
        # Chain with output check
        code_chain_raw = (
            code_gen_prompt | structured_code_llm | check_claude_output
        )
        # This will be run as a fallback chain
        fallback_chain = insert_errors | code_chain_raw
        N = 3  # Max re-tries
        code_gen_chain_re_try = code_chain_raw.with_fallbacks(
            fallbacks=[fallback_chain] * N, exception_key="error"
        )
        code_gen_chain = code_gen_chain_re_try | parse_output
        
        # Retriever model
        final_rank = cls.retriever.retrieve_rerank(query)
        context = "\n\n------------------------------\n\n".join(
            rank['chunk'] for rank in final_rank[:5]) # Content

        # infer     
        code_solution = code_gen_chain.invoke( 
            {"context": context, "messages": messages}
        )
        return code_solution

    @classmethod
    def routerTool(cls, query):
        prompt_template = """
        Provide answer in 1 word (yes/no).
        If the question requires generating a code and using the given tressequence and tskit library in order to provide the answer, then respond with 'yes' else respond with 'no' 
        Respond appropriately based on the user's query: {query}
        """
        prompt = PromptTemplate(
            input_variables=['quert'], template=prompt_template
        )
        chain = prompt | cls.general_llm
        answer = chain.invoke(query)
        return answer

    @classmethod
    def generalInfoTool(cls, messages):
        """
        """
        prompt_template = """
        Here's the conversation as context: {conversation}
        Respond appropriately based on the user's last message: {question}
        """
        prompt = PromptTemplate(
            input_variables=["conversation", 'question'], template=prompt_template
        )
        chain = prompt | cls.general_llm
        query = {"conversation":messages[:-1], "question":messages[-1]}
        answer = chain.invoke(query)
        return answer
