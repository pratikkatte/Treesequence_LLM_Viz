
import os
from typing import Annotated, List
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from tools import routerTool, generalInfoTool, generatorTool
from utils import execute_generated_code


from langgraph.checkpoint.memory import MemorySaver


# Max tries
max_iterations = 3

class GraphState(TypedDict):
    """
    """
    error: str
    messages: Annotated[List, add_messages]
    generation: str
    iterations: int
    result: str
    input_files: str
    next: str

def generate(state: GraphState):
    """
    """
    print("-- Generating Code -- ")

    # State
    messages = state["messages"]
    iterations = state['iterations']
    error = state["error"]

    if error != "no":
        question = state['messages'][-1].content + "\n" + error + "\n" + "Now, try again. Invoke the code tool to structure the output with a prefix, imports, and code block:"

        messages = [(
            "user",
            question
        )]
    else:
        question = state['messages'][-1].content

    code_solution = generatorTool(messages, question)
    
    messages = [
        (
            "assistant",
            f"{code_solution.prefix} \n Imports: {code_solution.imports} \n Code: {code_solution.code}",
        )
    ]
    iterations = iterations + 1

    return {"generation": code_solution, 
            "messages": messages, 
            "iterations": iterations,
            }

def execute_code(state: GraphState):

    print("--- checking code ---")
    messages = state['messages']
    iterations = state['iterations']
    code_solution = state['generation']
    input_files = state['input_files']
    generation = state['generation']
    error = state['error']

    try:
        result = execute_generated_code(generation, input_files)
    except Exception as e:
        print("-- code execution failed --")
        error_message = f"The solution failed the code execution test: {e}"
        
        if error_message not in error:
            error += "\n" + error_message
        return {
            "generation": code_solution,
            "messages": messages,
            "iterations": iterations,
            "error": error,
        }

    # no errors
    print(" -- no code failures --")

    # Log the result in messages
    result = f"Result: {result}"

    # Append result to messages (context)
    messages[-1].content += f"\nCode executed successfully. {result}"

    return {
        "generation": code_solution,
        "messages": messages,
        "error": None,
        "iterations": iterations,
        "result" : result
    }


def decide_to_finish(state: GraphState):
    """
    Determines whether to finish.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """
    error = state["error"]
    iterations = state["iterations"]
    max_iterations = 3

    if error == None or iterations == max_iterations:
        print("---DECISION: FINISH---")
        return "end"
    else:
        print("---DECISION: RE-TRY SOLUTION---")
        return "generate"

def router_call(state: GraphState):
    next = state['next']
    
    if next == 'no':
        return 'general_info'
    else:
        return 'generate'
    
def router(state: GraphState):
    """
    """
    # state
    
    question = state['messages'][-1].content

    query = {'query':question}
    answer = routerTool(query)

    return {
        "next": answer.content.lower()
    }

def general_info(state: GraphState):
    """
    """
    conversation = state['messages']

    answer = generalInfoTool(conversation)

    conversation = [(
            "assistant",
            f"{answer.content}",
        )]
    return {
        "result": answer.content,
        "error":None,
        "messages": conversation
    }

def create_graph():

    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("router", router)
    workflow.add_node("generate", generate) # generation solution
    workflow.add_node("execute_code", execute_code)  # execute code
    workflow.add_node("general_info", general_info)

    # Build graph
    workflow.add_edge(START, "router")
    workflow.add_edge("generate", "execute_code")    
    workflow.add_edge("general_info", END)
    
    workflow.add_conditional_edges(
        "execute_code", 
        decide_to_finish,
        {
            "end": END,
            "generate": "generate",
        },
    )
    workflow.add_conditional_edges(
        'router',
        router_call,
        {
            'generate':"generate",
            "general_info":"general_info"
        }
    )

    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app