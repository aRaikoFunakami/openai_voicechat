import json
import os, logging
from typing import Any
from typing import Type
from pydantic import BaseModel, Field

#
# LangChain related test codes
#
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool


model_name = "gpt-3.5-turbo-16k"
# model_name = "gpt-3.5-turbo-0613"
# model_name = "gpt-4-0613"

# default_persist_directory = "./chroma_split_documents"
default_persist_directory = "./chroma_load_and_split"


# load config
def load_config():
    config_file = os.path.dirname(__file__) + "/config.json"
    config = None
    with open(config_file, "r") as file:
        config = json.load(file)
    os.environ["OPENAI_API_KEY"] = config["openai_api_key"]
    return config


#
# Weather
#
from openai_function_weather import get_weather_info
from openai_function_weather import weather_function


class WeatherInfoInput(BaseModel):
    latitude: int = Field(descption="latitude")
    longitude: int = Field(descption="longitude")


class WeatherInfo(BaseTool):
    name = "get_weather_info"
    description = "This is useful when you want to know the weather forecast. Enter longitude in the latitude field and latitude in the longitude field."
    args_schema: Type[BaseModel] = WeatherInfoInput

    def _run(self, latitude: int, longitude: int):
        return get_weather_info(latitude, longitude)

    def _arun(self, ticker: str):
        raise NotImplementedError("not support async")


#
# ホットペッパーでレストラン情報を取得する
#
from openai_function_hotpepper import get_hotpepper_info


class HotpepperInfoInput(BaseModel):
    latitude: str = Field(descption="latitude")
    longitude: str = Field(descption="longitude")
    keyword: str = Field(descption="Restaurant Genres")
    count: str = Field(descption="Maximum number of restaurants to search and find")


class HotpepperInfo(BaseTool):
    name = "get_hotpepper_info"
    description = """
    	This is useful when you want to know the restaurant information. 
     	Enter dictionary includes longitude, latitude, and restaurant genre keyword
    """
    args_schema: Type[BaseModel] = HotpepperInfoInput

    def _run(self, latitude: str, longitude: str, keyword: str, count: str):
        params = {
            "lat": latitude,
            "lng": longitude,
            "keyword": keyword,
            "count": count,
        }
        return get_hotpepper_info(params=params)

    def _arun(self, ticker: str):
        raise NotImplementedError("not support async")


#
# カーナビとTVについての問い合わせに
#
from openai_function_pdf import get_pdf_lexus_info
from openai_function_pdf import get_pdf_viera_info


class PDFInfoInput(BaseModel):
    query: str = Field(descption="query")


class LexusInfo(BaseTool):
    name = "get_pdf_lexus_info"
    description = """
    	This is useful when you want to Explanation of all the car's equipment including options, explanation of the functions of the car navigation system, and handling of the multimedia installed in the car.
     	Enter query.
    """
    args_schema: Type[BaseModel] = PDFInfoInput

    def _run(self, query: str):
        return get_pdf_lexus_info(query)

    def _arun(self, ticker: str):
        raise NotImplementedError("not support async")


class VieraInfo(BaseTool):
    name = "get_pdf_viera_info"
    description = """
    	This is useful when you want to know instructions on how to operate Viera, a smart TV that can connect to the Internet.
    	Enter query.
    """
    args_schema: Type[BaseModel] = PDFInfoInput

    def _run(self, query: str):
        return get_pdf_viera_info(query)

    def _arun(self, ticker: str):
        raise NotImplementedError("not support async")


tools = [
    WeatherInfo(),
    HotpepperInfo(),
    VieraInfo(),
    LexusInfo(),
]


def OpenAIFunctionsAgent(tools=None, llm=None, verbose=False):
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    }
    memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

    # Add the user's prompt to the memory if need
    prompt = """
    The following is a friendly conversation between a human and an AI. 
    The AI is talkative and provides lots of specific details from its context. 
    If the AI does not know the answer to a question, it truthfully says it does not know.
    """
    memory.save_context({"input": prompt}, {"ouput": "understand!"})

    return initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=verbose,
        agent_kwargs=agent_kwargs,
        memory=memory,
    )


# Streaming対応
# ref: https://python.langchain.com/en/latest/modules/callbacks/getting_started.html
# ref: https://ict-worker.com/ai/langchain-stream.html
from typing import Any, Dict, List, Optional, Union
from langchain.schema import AgentAction, AgentFinish, LLMResult
from langchain.callbacks.manager import CallbackManager, BaseCallbackHandler


class MyCustomCallbackHandler(BaseCallbackHandler):
    def __init__(self, callback):
        self.callback = callback

    """Custom CallbackHandler."""

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""

    def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Run on new LLM token. Only available when streaming is enabled."""
        if self.callback is not None:
            res = {"response": token, "finish_reason": ""}
            self.callback(json.dumps(res, ensure_ascii=False))
            # self.callback(token)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Run when LLM ends running."""
        if self.callback is not None:
            res = {"response": "", "finish_reason": "stop"}
            self.callback(json.dumps(res, ensure_ascii=False))

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when LLM errors."""

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        """Run when chain starts running."""

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Run when chain ends running."""

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when chain errors."""

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Run when tool ends running."""

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""

    def on_text(self, text: str, **kwargs: Any) -> Any:
        """Run on arbitrary text."""
				
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""


    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run on agent end."""


#
# called by app
#
llm = None
agent_chain = None
callback_manager = None

def chat(input, callback=None):
    logging.info("chatstart")
    load_config()

    global llm, agent_chain, callback_manager
    if llm is None or agent_chain is None:
        callback_manager = CallbackManager([MyCustomCallbackHandler(callback)])
        llm = ChatOpenAI(
            temperature=0,
            model=model_name,
            callback_manager=callback_manager,
            streaming=True,
		)
        agent_chain = OpenAIFunctionsAgent(tools=tools, llm=llm, verbose=True)

    response = agent_chain.run(input=input)
    cprint(f"response: {response}")


#
# test codes
#

suffix = """
参照先を含めてアナウンサー口調で50文字以内で答えよ。
"""

queries2 = [
    ["今日の東京の天気はどうですか？", "get_weather_info"],
    ["北海道は？。", "get_weather_info"],
    ["明日は？。", "get_weather_info"],
]

queries3 = [
    ["横浜駅前の美味しいラーメン屋を3件教えて", "get_hotpepper_info"],
    ["イタリアンは？", "get_hotpepper_info"],
    ["中華は？", "get_hotpepper_info"],
]

queries4 = [
    ["カーナビの使い方をしりたい", "get_pdf_lexus_info"],
    ["カーナビに現在地を表示させたい", "get_pdf_lexus_info"],
    ["Webブラウザを起動させたい", "get_pdf_lexus_info"],
]

queries = [
    ["テレビでハイブリッドキャストの設定方法をしりたい", "get_pdf_viera_info"],
    ["録画のやりかたは？", "get_pdf_viera_info"],
    ["YouTubeを見たい", "get_pdf_viera_info"],
]


def cprint(text):
    return print("\033[34m" + text + "\033[0m")


def dummy_callback(input):
    print(input)
    return


def test_langchain_support():
    load_config()
    callback_manager = CallbackManager([MyCustomCallbackHandler(dummy_callback)])
    llm = ChatOpenAI(temperature=0, model=model_name, callback_manager=callback_manager, streaming=True)
    # llm = ChatOpenAI(temperature=0, model=model_name)
    agent_chain = OpenAIFunctionsAgent(tools=tools, llm=llm, verbose=True)
    for query in queries:
        input = query[0] + suffix
        response = agent_chain.run(input=input)
        cprint(f"response: {response}")


def main():
    logging.basicConfig(
        level=logging.WARN,
        format="%(asctime)s - %(filename)s:%(funcName)s[%(lineno)d] - %(message)s",
    )
    test_langchain_support()


if __name__ == "__main__":
    main()
