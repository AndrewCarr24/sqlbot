import warnings
warnings.filterwarnings("ignore")
import langchain_core.tools
import dataclasses
from langchain_core.language_models import BaseChatModel
import typing
from typing import Optional
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool
import time
import json 


# LLMWithHistory 
@dataclasses.dataclass
class LLMWithHistory:
    """
    A class to represent a language model with history and tools.

    Attributes:
        llm (BaseChatModel): The language model.
        history (list[BaseMessage]): The history of messages.
        system_message (Optional[str]): An optional system message.
        tools (Optional[list[BaseTool]]): Optional list of tools.
        cost (float): The cost of the operations.
    """
    llm: BaseChatModel
    history: list[BaseMessage] = dataclasses.field(default_factory=list)
    system_message: Optional[str] = None  # Optional system message
    tools: typing.Optional[list[BaseTool]] = None
    cost: float = 0

    def add_cost(self, inp_msg: AIMessage) -> float: 
        """
        Add the cost of the input and output tokens to the total cost.
        Args:
            inp_msg (AIMessage): The AI message containing token usage information.
        Returns:
            float: The updated cost.
        """
        input_token_cost = inp_msg.additional_kwargs['usage'].get('prompt_tokens')*(3/1e6)
        output_token_cost = inp_msg.additional_kwargs['usage'].get('completion_tokens')*(15/1e6)
        self.cost += input_token_cost + output_token_cost
    
    def from_list(self, tool_list: list[langchain_core.tools.BaseTool]):
        """
        Create a dictionary of tools from a list of tools.
        Args:
            tool_list (list[BaseTool]): List of tools.
        """
        self.tool_dict = {t.name:t for t in tool_list}
    
    def __post_init__(self):
        """
        Post-initialization to bind tools if there are any.
        """
        if self.tools:
            self.llm = self.llm.bind_tools(self.tools)
            self.from_list(self.tools)

    def get_sql_query(self):
        """
        Retrieves the SQL queries from the chatbot's history.

        Returns:
            str: The SQL queries joined by newlines.
        """
        ai_msgs_with_tool_calls = [msg for msg in self.history if isinstance(msg, AIMessage) and msg.additional_kwargs.get('tool_calls')]

        if ai_msgs_with_tool_calls:
            sql_calls = [json.loads(call.get('function').get('arguments')).get('query') for call in ai_msgs_with_tool_calls[-1].additional_kwargs['tool_calls'] if call.get('function').get('name') == 'sql_db_query']
            if sql_calls:
                self.query_output = '\n\n'.join(sql_calls)
            else:
                self.query_output = ''
        else:
            self.query_output = ''
          
    def send_message_to_llm(self, message: str, print_response: bool = True):
        """
        Send a message to LLM and handle the response.
        Args:
            message (str): The message to send.
        """
        # Put system prompt at beginning if one has been provided 
        if not len(self.history):
            if self.system_message:
                self.history.append(SystemMessage(self.system_message))
        
        # Trim messages so that the number of human messages in history never exceeds three
        # (history will never be more than: system message + (human + other stuff) + (human + other stuff) + (human + whatever is in latest response)
        human_msg_lst = [type(msg) for msg in self.history if type(msg) == langchain_core.messages.human.HumanMessage]
        if len(human_msg_lst) > 2:
            human_msg_idx = [idx for idx, msg in enumerate(self.history) if type(msg) == langchain_core.messages.human.HumanMessage]
            self.history = self.history[:1] + self.history[human_msg_idx[-2]:]
            
        human_message = HumanMessage(message)
        
        # Append the human message to the history
        self.history.append(human_message)
        
        # Invoke the LLM with the current history
        response = self.llm.invoke(self.history)
        self.history.append(response)
        # self.add_cost(response)
        
        # If AIMessage with tool calls and print_response enabled, stream the response (for interim AI responses)
        if response.tool_calls and print_response and isinstance(response, AIMessage):
            for fake_token in response.content:
                print(fake_token, end="", flush=True)
                time.sleep(0.005)
            print("\n")

        # Handle tool calls if necessary
        # while response.response_metadata['finish_reason'] == "tool_calls":
        while response.tool_calls:

            # Build tool message, execute tool call, and append result to history 
            for tool_info in response.tool_calls:
                
                # Get tool name 
                tool_name = tool_info['name']
                # print(f"Running {tool_name} tool...\n")
                
                tool_args = tool_info['args']
                tool_output = self.tool_dict[tool_name].invoke(tool_args)
                # print("Delay to handle rate limit.")

                tool_response = ToolMessage(content=tool_output, 
                            tool_call_id=tool_info['id'])
                
                self.history.append(tool_response)
                
            response = self.llm.invoke(self.history)
            # self.add_cost(response)
            self.history.append(response)
                
        # Stream the response 
        if print_response:
            for fake_token in response.content:
                print(fake_token, end="", flush=True)
                time.sleep(0.005)
            print("\n")

         