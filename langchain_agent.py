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
# apple music
#
from openai_function_applemusic import get_applemusic_info
from openai_function_applemusic import applemusic_function


class ApplemusicInfoInput(BaseModel):
    keyword: str = Field(keyword="keyword")


class ApplemusicInfo(BaseTool):
    name = "get_applemusic_info"
    description = "This is useful when you want to play songs or search for songs to be played on apple music by keywords related to songs, such as singer's name or song title."
    args_schema: Type[BaseModel] = ApplemusicInfoInput

    def _run(self, keyword: str):
        logging.info(f"get_applemusic_info({keyword})")
        # notify("applemusic\n")

        applemusic_url = get_applemusic_info(keyword)
        try:
            logging.info(f"applemusic_url:{applemusic_url}")
            notifyExternalUrl(applemusic_url)
        except Exception as e:
            print("error:", e)

        return f"Apple musicアプリを起動して{keyword}を再生します"

    def _arun(self, ticker: str):
        raise NotImplementedError("not support async")


#
# navi_destination
#
from openai_function_navi_destination import get_navi_destination_info
from openai_function_navi_destination import navi_destination_function
from typing import List


class NaviDestinationInfoInput(BaseModel):
    destinations: List[str] = Field(descption="destinations")


class NaviDestinationInfo(BaseTool):
    name = "get_navi_destination_info"
    description = "This is useful when you want to set intermediate points and destinations by landmark in the car navigation system."
    args_schema: Type[BaseModel] = NaviDestinationInfoInput

    def _run(self, destinations: List[str]):
        logging.info(f"get_navi_destination_info(destinations)")
        notify("目的地を設定しています\n")

        destinations = get_navi_destination_info(destinations)
        try:
            keyword = destinations[-1]
            logging.info(f"{keyword}")
            notifyMap(keyword)
        except Exception as e:
            print("error:", e)

        return destinations

    def _arun(self, ticker: str):
        raise NotImplementedError("not support async")


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
        logging.info(f"get_weather_info(latitude, longitude)")
        notify("Checking weather data.\n")
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
    	This is useful when you want to search the restaurant, ramen shops, Chinese restaurants, French cuisine and so on. 
     	Enter dictionary includes longitude, latitude, and restaurant genre keyword
    """
    args_schema: Type[BaseModel] = HotpepperInfoInput

    def _run(self, latitude: str, longitude: str, keyword: str, count: str):
        if int(count) > 1:
            count = 1
        keyword = translate_text(keyword, "ja")
        params = {
            "lat": latitude,
            "lng": longitude,
            "keyword": keyword,
            "count": count,
        }
        notify("ホットペッパーのレストラン情報を確認しています\n")
        logging.info(f"get_hotpepper_info(params=params)")

        response = get_hotpepper_info(params=params)

        try:
            data = json.loads(response)
            keyword = data[0]["name"] + " " + data[0]["address"]
            logging.info(f"{keyword}")
            notifyMap(keyword)
            data[0]["address"] = ""
            return json.dumps(data)
        except Exception as e:
            print("error:", e)

        return response

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
    	This is useful if you want to know how to use all of the car's equipment, how to use the car navigation system, or how to use the multimedia installed in the car.
     	Enter query.
    """
    args_schema: Type[BaseModel] = PDFInfoInput

    def _run(self, query: str):
        notify("取扱説明書を確認しています\n")
        logging.info(f"get_pdf_lexus_info(query)")
        response = get_pdf_lexus_info(query)
        notifyUrl(response.get("urls")[0])
        return json.dumps(response.get("content"), indent=2, ensure_ascii=False)

    def _arun(self, ticker: str):
        raise NotImplementedError("not support async")


class VieraInfo(BaseTool):
    name = "get_pdf_viera_info"
    description = """
        This is useful when you want to know instructions on how to operate Viera, a smart TV that can connect to the Internet.
        Search TV instruction manuals.Get how to operate Viera, a smart TV connected to the Internet.
    	Enter query.
    """
    args_schema: Type[BaseModel] = PDFInfoInput

    def _run(self, query: str):
        notify("checking the instruction manual.\n")
        logging.info(f"get_pdf_viera_info(query)")
        response = get_pdf_viera_info(query)
        notifyUrl(response.get("urls")[0])
        return json.dumps(response.get("content"), indent=2, ensure_ascii=False)

    def _arun(self, ticker: str):
        raise NotImplementedError("not support async")


tools = [
    WeatherInfo(),
    HotpepperInfo(),
    VieraInfo(),
    LexusInfo(),
    NaviDestinationInfo(),
    ApplemusicInfo(),
]


#
# Ugh!
#
memory = None


def OpenAIFunctionsAgent(tools=None, llm=None, verbose=False):
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    }
    #
    # Ugh!
    #
    global memory
    if memory is None:
        memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
        # Add the user's prompt to the memory if need
        #
        # prompt
        #
        prompt_init = """
        You are an AI assistant in an excellent car. You are the AI assistant in the car, and you are responsible for providing the user with an enjoyable driving experience by interacting with the user, adding supplementary information, and having a pleasant conversation as if you were spending time with your girlfriend. The following Markdown describes the rules, including the expected input and output formats, so please be sure to behave in accordance with the rules.
        ---
        # Instructions
        ## User input
        - User is in the driver or passenger seat of a car
        - User is driving to a destination in a car
        - If the user's intent is unclear, please ask a question
        - Supplementary information is always preceded by "Intent:"

        ## Output format
        - Answer in the user's language
        - If asked in Japanese, answer in Japanese
        - Answer in plain, short sentences.
        - Keep your answers short and conversational in a fast-paced, conversational manner.
        - If you don't know something, say you don't know it.
        - If you need to ask the user a question in order to answer, ask the question.
        - Whenever AI knows reference information, e.g. Websites, PDF files, and so on, it will add that information to the end of the sentence.

        ## Example of input/output
        I'm going on a business trip to Yokohama today. What is the weather like today?
        Intention: I want to know the weather in Yokohama.

        ## Example of output
        It's very sunny today in Yokohama, where I'm going on a business trip! But, you know, it's very hot because the sun is shining and the temperature is forecast to rise to 36 degrees Celsius. So please be careful of heat stroke. Please drink plenty of water, cool off a bit in the shade, and try not to get sick. Take care of your health and enjoy your wonderful business trip! Good luck!
        ---
        Again, you are an excellent car-mounted AI assistant. While interacting with the user, you should add supplementary information and make the user experience a pleasant drive with an enjoyable conversation, just like spending time with your girlfriend. The above Markdown describes the rules, including the expected input and output formats, so please be sure to behave according to the rules.
        Please note once again that you must follow the "## Output format" rule. However, at the time of explaining the rules, instruction has not yet started, so immediately after this message, please say only one word, "I understand," and exit the output. and finish the output.
        """

        prompt_answer = """
        AI must respond in 50 words or less whenever possible.
        AI must include their own suggestions in their responses.
        The AI will include witty and fun topics in its responses.
        Whenever AI has reference information, it will add that information to the end of the sentence. 
        """

        prompt_language = """
        AThe AI will respond in the same language as it recognized. 
        For example, if the AI understands that the input sentence is in English, it outputs the sentence in English.
        """

        prompts = [
            prompt_init,
            # prompt_language,
            # prompt_answer,
        ]
        for prompt in prompts:
            memory.save_context({"input": prompt}, {"ouput": "I understood!"})

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
        logging.warning(input_str)

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Run when tool ends running."""
        logging.warning(output)

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
import langid
from openai_translate import translate_text
from openai_translate import lang_name


def notify(input):
    if g_callback is not None:
        logging.warning(input)
        res = {"response": input, "type": "notification", "finish_reason": "false"}
        g_callback(json.dumps(res))


def notifyUrl(url):
    if g_callback is not None:
        logging.warning(url)
        res = {"response": url, "type": "url", "finish_reason": "false"}
        g_callback(json.dumps(res))


def notifyExternalUrl(url):
    if g_callback is not None:
        logging.warning(url)
        res = {"response": url, "type": "external_url", "finish_reason": "false"}
        g_callback(json.dumps(res))


def notifyMap(input):
    if g_callback is not None:
        logging.warning(input)
        res = {
            "response": input,
            "type": "map",
            "finish_reason": "false",
        }
        g_callback(json.dumps(res))


def search_viera_manual(input, callback):
    response = get_pdf_viera_info(input)
    res = {"response": response.get("content"), "finish_reason": "stop"}
    callback(json.dumps(res, ensure_ascii=False))
    notifyUrl(response.get("urls")[0])
    return response


g_callback = None
g_lang = None


def chat(input, callback=None, function=None):
    logging.info("chatstart")
    load_config()

    global g_callback, g_lang
    g_callback = callback
    # Determine the language used
    g_lang = langid.classify(input)[0]

    callback_manager = CallbackManager([MyCustomCallbackHandler(callback)])
    llm = ChatOpenAI(
        temperature=0,
        model=model_name,
        callback_manager=callback_manager,
        streaming=True,
    )
    agent_chain = OpenAIFunctionsAgent(tools=tools, llm=llm, verbose=True)

    suffix = f"AI must respond in {lang_name(g_lang)}."
    input = input + " " + suffix
    logging.warning(input)

    response = ""
    if function is None or function == "":
        response = agent_chain.run(input=input)
    elif function == "viera":
        response = search_viera_manual(input=input, callback=callback)

    cprint(f"response: {response}")
    g_callback = None
    g_lang = None


#
# test codes
#

queries = [
    ["尾崎豊のI love youを聴きたい", "get_applemusic_info"],
]

queries1 = [
    ["今日の横浜の天気は？", "get_weather_info"],
    ["What is the weather like in Yokohama today?", "get_weather_info"],
    ["横滨今天的天气如何？", "get_weather_info"],
]

queries4 = [
    ["横浜駅前の美味しいラーメン屋を3件教えて", "get_hotpepper_info"],
    ["イタリアンは？", "get_hotpepper_info"],
    ["中華は？", "get_hotpepper_info"],
]

queries0 = [
    ["カーナビの使い方をしりたい", "get_pdf_lexus_info"],
    ["カーナビに現在地を表示させたい", "get_pdf_lexus_info"],
    ["Webブラウザを起動させたい", "get_pdf_lexus_info"],
]

queries3 = [
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
    llm = ChatOpenAI(
        temperature=0,
        model=model_name,
        callback_manager=callback_manager,
        streaming=False,
    )
    # llm = ChatOpenAI(temperature=0, model=model_name)
    agent_chain = OpenAIFunctionsAgent(tools=tools, llm=llm, verbose=True)
    for query in queries:
        input = query[0]
        response = agent_chain.run(input=input)
        cprint(f"response: {response}")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(filename)s:%(funcName)s[%(lineno)d] - %(message)s",
    )
    test_langchain_support()


if __name__ == "__main__":
    main()
