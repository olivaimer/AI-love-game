import json
import threading
from threading import Thread
import time
import random
import threading
from typing import List, Iterable
from datetime import datetime
from langchain.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from sparkai.llm.llm import ChatSparkLLM
from sparkai.core.messages import ChatMessage
from datetime import datetime
from db import SQLiteDB

# 配置服务器的地址和端口
HOST = 'localhost'
PORT = 8080

class Handle:
    def __init__(self):
        self.lock = threading.Lock() 
        self.app_id = ""
        self.app_key = ""
        self.app_secret = ""
        self.file_name1=r"database\chuxue_long_history.json"
        self.file_name2=r"database\chuxue5.json"
        self.db_path=r"database/data.db"
        self.spark_model=self.ChatModel(self.app_id, self.app_key, self.app_secret, stream=True)
        self.history_galgame = []
        self.history_long_galgame=[]
        self.db=SQLiteDB(self.db_path)
        self.vectorstore=self.vectorstore_init(self.file_name1,self.file_name2,self.db_path)
        self.data={
        "date":["随机日期"],
        "scene":["随机场景"],
        "emotions":["平和，温和"],
        "favorability":{
            "dependency":0,
            "trustworthiness":0,
            "familiarity":0,
            "identity":"陌生"
        },
        "appraise":[""],
        "suggestion":[""],
        "diary":[""],
        "history":[]
        }
        self.user_inf={
            "username":"username",
            "content":"content",
            "instruction":"chat"
        }
    
    def vectorstore_init(self,file_name1,file_name2, db_path):
    
        documents = []
        with open(file_name1, "r", encoding="utf-8") as f:
            long_history = json.load(f)
    
        for items in long_history:
            try:
                documents.append(Document(page_content=str(items), metadata=dict(page=1)))
            except:
                continue

        with open(file_name2, "r", encoding="utf-8") as f:
            chuxue = json.load(f)
    
        for items in chuxue:
            try:
                item=items["instruction"]+"\n"+"初雪"+items["output"]

                documents.append(Document(page_content=str(item), metadata=dict(page=2)))
            except:
                continue

        lasttime = time.time()
        model_name = "iampanda/zpoint_large_embedding_zh"
        print("等待rag数据完成向量化")
        embeddings_model = HuggingFaceEmbeddings(model_name=model_name)
        vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings_model, collection_name="huggingface_embed")
        print("完成数据向量化,共耗时" + str(time.time() - lasttime) + "秒")
        return vectorstore
    
        
        

    def load_data(self,data,user_inf)->json:

        json_data={
        "date":data["date"][-1],
        "scene":data["scene"][-1],
        "emotions":data["emotions"][-1],
        "favorability":{
            "dependency":data["favorability"]["dependency"],
            "trustworthiness":data["favorability"]["trustworthiness"],
            "familiarity":data["favorability"]["familiarity"],
            "identity":data["favorability"]["identity"]
        },
        "appraise":data["appraise"][-1],
        "suggestion":data["suggestion"][-1],
        "diary":data["diary"][-1],
        "history":data["history"],
        "username":user_inf["username"],
        "content":user_inf["content"],
        "instruction":user_inf["instruction"]
        }

        return json_data

    def store_data(self,response,model_type)->json:
        #model_type 1 情绪分析
        #model_type 2 事件概括
        #model_type 3 对用户的评价
        #model_type 4 设定日期
        #model_type 5 设定环境
        #model_type 6 好感度
        #model_type 7 恋爱建议
        #model_type 8 初雪的日记
        #model_type 9 初雪
        if model_type==1:
            self.data["emotions"].append(response)
        elif model_type==2:
            self.data["emotions"].append(response)
        elif model_type==3:
            self.data["appraise"].append(response)
        elif model_type==4:
            self.data["date"].append(response)
        elif model_type==5:
            self.data["scene"].append(response)
        elif model_type==6:
            favorability_data={
            "dependency":self.data["favorability"]["dependency"]+response["dependency"],
            "trustworthiness":self.data["favorability"]["trustworthiness"]+response["trustworthiness"],
            "familiarity":self.data["favorability"]["familiarity"]+response["familiarity"],
            }
            favorability_point=sum([favorability_data["dependency"],favorability_data["familiarity"],favorability_data["trustworthiness"]])
            if favorability_point >240:
                favorability_data["identity"]="恋人"
            elif favorability_point >180:
                favorability_data["identity"]="好朋友"
            elif favorability_point >120:
                favorability_data["identity"]="普通朋友"
            else:
                favorability_data["identity"]="陌生人"

            self.data["favorability"]=favorability_data
        elif model_type==7:
            self.data["suggestion"].append(response)
        elif model_type==8:
            self.data["diary"].append(response)
        elif model_type==9:
            self.data["history"].append(response)
        elif model_type==10:#单纯把用户的输入存入history
            self.data["history"].append(response)

        return self.data




    def prompt(self,json_data,model_type)->str:
        #model_type 1 情绪分析
        #model_type 2 事件概括
        #model_type 3 对用户的评价
        #model_type 4 设定日期
        #model_type 5 设定环境
        #model_type 6 好感度
        #model_type 7 恋爱建议
        #model_type 8 初雪的日记
        #model_type 9 初雪
        prompt=""
        date=json_data["date"]
        scene=json_data["scene"]
        emotions=json_data["emotions"]
        favorability=json_data["favorability"]
        appraise=json_data["appraise"]
        suggestion=json_data["suggestion"]
        diary=json_data["diary"]
        history=json_data["history"]
        username=json_data["username"]
        content=json_data["content"]
        instruction=json_data["instruction"]
        chat_history = '聊天记录\n'
        if history:
            for his in history:
                if len(his) == 2:
                    chat_history += f"{his[0]}\n"
                    chat_history += f"{his[1]}\n"
                elif len(his) == 1:
                    chat_history += f"{his[0]}\n"
        if model_type==1:
            prompt += chat_history
            prompt+=f"当前日期{date}"
            prompt+=f"之前初雪的情绪：{emotions}"
        elif model_type==2:
            pass
        elif model_type==3:
            prompt += chat_history
            prompt+=f"之前初雪对{username}的评价：{appraise}"
        elif model_type==4:
            prompt += chat_history
            prompt+=f"当前日期{date}"
            prompt+="只输出一个日期，不许输出除了日期以外的字"
        elif model_type==5:
            prompt += chat_history
            prompt+=f"当前日期{date}"
            prompt+="在当前的日期下，只做简单的环境描写"
            prompt+="简短一些,不要超过30字"
        elif model_type==6:
            prompt += chat_history
            prompt+=f"先前好感度('dependency':{favorability['dependency']},'trustworthiness':{favorability['trustworthiness']},'familiarity':{favorability['familiarity']},)"
            prompt+="简短一些,不要超过30字"
        elif model_type==7:
            prompt += chat_history
            prompt+=f"初雪对{username}的评价：{appraise}"
            prompt+=f"初雪的情绪和心理活动{emotions}"
            prompt+=f"初雪对{username}好感度('dependency':{favorability['dependency']},'trustworthiness':{favorability['trustworthiness']},'familiarity':{favorability['familiarity']},)"
            prompt+=f"简短一些,不要超过50字,以{username}的好兄弟的口吻，给出一些聊天的具体具体建议"
        elif model_type==8:
            prompt += chat_history
            prompt += f"日期{date}"
            prompt += f"场景：{scene}"
            prompt+=f"初雪对{username}的评价：{appraise}"
            prompt+=f"初雪的情绪和心理活动{emotions}"
            prompt+=f"初雪对{username}好感度('dependency':{favorability['dependency']},'trustworthiness':{favorability['trustworthiness']},'familiarity':{favorability['familiarity']},)"
            prompt+="以初雪的视角和笔触，写下这一天的日记"
        elif model_type==9:
            emotions=f"初雪情绪和心理：{emotions}"
            appraise=f"初雪对{username}的评价是：{appraise}"
            identity=favorability['identity']
            chat = f"当前对话\n ({identity})({username})说："
            #片段性记忆
            result1 = self.vectorstore.similarity_search(chat + content, filter=dict(page=1), k=2)
            source_knowledge1 = f"从前的记忆：{' '.join([x.page_content for x in result1])}"

            #精确每轮记忆
            result2 = self.vectorstore.similarity_search(chat + content, filter=dict(page=2), k=2)
            source_knowledge2 = f"说话语气参考:{' '.join([x.page_content for x in result2])}"
            history_ = "上文对话" + chat_history[6:]
            prompt = f"用少女初雪的语气来和我说话。你说的话不能和上文重复。优先回复{username}{source_knowledge1}{source_knowledge2}{history_}{appraise}{emotions}{chat}{content}。"
            
            
        
        elif model_type==10:
            prompt += chat_history
            prompt+=f"初雪对{username}的评价：{appraise}"
            prompt+=f"初雪的情绪和心理活动{emotions}"
            prompt+=f"初雪对{username}好感度('dependency':{favorability['dependency']},'trustworthiness':{favorability['trustworthiness']},'familiarity':{favorability['familiarity']},)"
            prompt+=f"简短一些,不要超过50字，语气要更加风趣幽默，以{username}的好兄弟的口吻"
            prompt+=f"{username}的问题是：{content}"
        
        
        elif model_type==11:
            prompt += chat_history
            prompt+=f"初雪对{username}的评价：{appraise}"
            prompt+=f"初雪的情绪和心理活动{emotions}"
            prompt+=f"初雪对{username}好感度('dependency':{favorability['dependency']},'trustworthiness':{favorability['trustworthiness']},'familiarity':{favorability['familiarity']},)"
            prompt+=f"做一个系统性的总结，回顾初雪和{username}的每件事做具体分析"

        return prompt
        
    def galgame_instruction_deal(self,user_inf)->json:
        #根据instrution，进行任务分配
        instruction=user_inf["instruction"]
        if instruction=="game_init":
            self.__galgame_init__(self.data,user_inf)
            
        elif instruction=="chat":
            self.chat_galgame(self.data,user_inf)
            
        elif instruction=="next_scene":
            self.next_scene_galgame(self.data,user_inf)
            
        elif instruction=="today_over":
            self.today_over_galgame(self.data,user_inf)
            
        elif instruction=="next_day":
            self.next_day_galgame(self.data,user_inf)

        return self.data
    
            

    def set_date(self,data,user_inf)->str:
        #根据聊天历史，选择下一个时间

            try:
                model_type=4

                #数据提取并合成提示词

                json_data=self.load_data(data,user_inf)
                prompt=self.prompt(json_data,model_type)

                #llm
                response=self.spark_model.run_infer(prompt,model_type,json_data)
                #数据存入
                self.store_data(response,model_type)

                return response

            except Exception as e:
                print(f"Error set date: {e}")

    def set_scene(self,data,user_inf)->str:
        #根据聊天历史，创造性的选择用户和初雪的下一个相遇地点

            try:
                model_type=5

                #数据提取并合成提示词

                json_data=self.load_data(data,user_inf)
                prompt=self.prompt(json_data,model_type)

                #llm
                response=self.spark_model.run_infer(prompt,model_type,json_data)
                #数据存入
                self.store_data(response,model_type)

                return response

            except Exception as e:
                print(f"Error set scene: {e}")

    def set_emotions(self,data,user_inf)->str:
        #根据聊天历史，创造性的选择用户和初雪的下一个相遇地点

            try:
                model_type=1

                #数据提取并合成提示词

                json_data=self.load_data(data,user_inf)
                prompt=self.prompt(json_data,model_type)

                #llm
                response=self.spark_model.run_infer(prompt,model_type,json_data)
                #数据存入
                self.store_data(response,model_type)

                return response

            except Exception as e:
                print(f"Error set emotions: {e}")


    def set_favorability(self,data,user_inf)->str:
        #根据聊天历史以及最新的聊天，更新好感度三要素以及总体关系
       
            try:
                model_type=6

                #数据提取并合成提示词

                json_data=self.load_data(data,user_inf)
                prompt=self.prompt(json_data,model_type)

                #llm
                response=self.spark_model.run_infer(prompt,model_type,json_data)
                #数据存入
                print("好感度",response)

                """try:
                    resp_data={
                    "dependency":response["dependency"],
                    "trustworthiness":response["trustworthiness"],
                    "familiarity":response["familiarity"],
                    "total_relation":"陌生"
                    }
                except:
                    resp_data={
                    "dependency":random.randint(-2,6),
                    "trustworthiness":random.randint(-2,6),
                    "familiarity":random.randint(-2,6),
                    "total_relation":"陌生"
                    }"""
                resp_data={
                    "dependency":random.randint(-2,6),
                    "trustworthiness":random.randint(-2,6),
                    "familiarity":random.randint(-2,6),
                    "total_relation":"陌生"
                    }
                    
                self.store_data(resp_data,model_type)

                return response

            except Exception as e:
                print(f"Error set emotions: {e}")
                

    def set_appraise(self,data,user_inf)->str:
        #根据数据库中的先前的评价以及聊天历史，更新对用户的评价

            try:
                model_type=3

                #数据提取并合成提示词

                json_data=self.load_data(data,user_inf)
                prompt=self.prompt(json_data,model_type)

                #llm
                response=self.spark_model.run_infer(prompt,model_type,json_data)
                #数据存入
                self.store_data(response,model_type)

                return response

            except Exception as e:
                print(f"Error set appraise: {e}")

    def set_suggestion(self,data,user_inf)->str:
        #分析当前聊天记录，好感度，情感，评价，分析，实时给出一定的攻略建议

            try:
                model_type=7

                #数据提取并合成提示词
                json_data=self.load_data(data,user_inf)
                prompt=self.prompt(json_data,model_type)

                #llm
                response=self.spark_model.run_infer(prompt,model_type,json_data)

                #数据存入
                self.store_data(response,model_type)

                return response

            except Exception as e:
                print(f"Error set suggestion: {e}")

    def set_diary(self,data,user_inf)->str:
        #以初雪的视角，少女的笔触，总结下来一天发生的事

            try:
                model_type=8

                #数据提取并合成提示词
                json_data=self.load_data(data,user_inf)
                prompt=self.prompt(json_data,model_type)

                #llm
                response=self.spark_model.run_infer(prompt,model_type,json_data)
                
                #数据存入
                self.store_data(response,model_type)

                return response

            except Exception as e:
                print(f"Error set diary: {e}")

    def set_suggestion2(self,data,user_inf)->str:
        #性感军师在线问答

            try:
                model_type=10

                #数据提取并合成提示词
                json_data=self.load_data(data,user_inf)
                prompt=self.prompt(json_data,model_type)

                #llm
                response=self.spark_model.run_infer(prompt,model_type,json_data)
                
                """#数据存入
                self.store_data(response,model_type)"""

                return response

            except Exception as e:
                print(f"Error set diary: {e}")

    def set_suggestion3(self,data,user_inf)->str:
        #事后诸葛亮

            try:
                model_type=11

                #数据提取并合成提示词
                json_data=self.load_data(data,user_inf)
                prompt=self.prompt(json_data,model_type)

                #llm
                response=self.spark_model.run_infer(prompt,model_type,json_data)
                
                """#数据存入
                self.store_data(response,model_type)"""

                return response

            except Exception as e:
                print(f"Error set diary: {e}")

    def chat_chuxue(self,data,user_inf)->str:
            try:
    
                response=""
                model_type=9

                #数据提取并合成提示词
                json_data=self.load_data(data,user_inf)
                username=json_data["username"]
                content=json_data["content"]
                user_history=f"{username}说：{content}"
                self.store_data(user_history,10)
                prompt=self.prompt(json_data,model_type)


                #llm
                response=self.spark_model.run_infer(prompt,model_type,json_data)
                
                if response[0:3]=="初雪：":
                    response=response[3:]
                elif response[0:4]=="初雪说：":
                    response=response[4:]
                elif response[0:2]=="初雪":
                    response=response[2:]

                response=f"初雪说：{response}"
                
                #数据存入
                self.store_data(response,model_type)

                return response

            except Exception as e:
                print(f"Error chat: {e}")
        
    def __galgame_init__(self,data,user_inf)->json:
        self.data={
        "date":["随机日期"],
        "scene":["随机场景"],
        "emotions":["平和，温和"],
        "favorability":{
            "dependency":[0],
            "trustworthiness":[0],
            "familiarity":[0],
            "identity":["陌生"]
        },
        "appraise":[""],
        "suggestion":[""],
        "diary":[""],
        "history":[]
        }
        self.user_inf={
            "username":"username",
            "content":"content",
            "instruction":"chat"
        }
        self.set_date(self.data,self.user_inf)
        self.set_scene(self.data,self.user_inf)

        return self.data
 




    def chat_galgame(self,data,user_inf)->tuple:
        #普通对话模式，instruction为chat时候调用
        #收到username和content->初雪回答
        #线程实时更新favorability，appraise，suggestion
        self.chat_chuxue(data,user_inf)
        self.set_favorability(self.data,user_inf)
        self.set_appraise(self.data,user_inf)
        self.set_suggestion(self.data,user_inf)
        
        return self.data["history"][-1],self.data["favorability"],self.data["appraise"][-1],self.data["suggestion"]

    def next_scene_galgame(self,data,user_inf)->str:
        #用户选择切换下一场景时触发
        #切换场景scene，进行场景的详细描述
        self.set_scene(data,user_inf)

        return self.data["scene"][-1]
        

    def today_over_galgame(self,data,user_inf)->str:
        #用户选择切换下一天时候触发
        #一天结束
        #diary,初雪的日记
        self.set_diary(data,user_inf)

        return self.data["diary"][-1]


    def next_day_galgame(self,data,user_inf)->tuple:
        #用户选择切换下一天时候触发
        #新一天开始，
        # 切换date，scene，
        self.set_date(data,user_inf)

        self.set_scene(self.data,user_inf)

        return self.data["date"][-1],self.data["scene"][-1]
        

    




    """def history_append(self):
            try:
                username = self.receive_data["gal"]["username"]
                content = self.receive_data["gal"]["content"]
                identity=self.data["favorability"]["identity"]
                response=self.data["response"]
                self.history_galgame.append([f"({identity}){username}说：{content}", f"初雪说：{response}"])
                self.history_long_galgame.append([f"({identity}){username}说：{content}", f"初雪说：{response}"])
                
                if len(self.history_galgame) > 8:
                    del self.history_galgame[0]
                if  len(self.history_long_galgame)>6:
                    history = '\n'
                    if self.history_long_galgame:
                        for his in self.history_long_galgame:
                            if len(his) == 2:
                                history += f"{his[0]}\n"
                                history += f"{his[1]}\n"
                            elif len(his) == 1:
                                history += f"{his[0]}\n"
                    long_history=self.spark_model.run_infer(history,2,0)
                    split_list = long_history.split('&')
                    with open("database\\chuxue_long_history.json","r",encoding="utf-8") as f:
                        chuxue_long_history=json.load(f)
                    for event in split_list:
                        chuxue_long_history.append(event)
                    with open("database\\chuxue_long_history.json","w",encoding="utf-8") as f:
                        json.dump(chuxue_long_history,f,indent=4)
                    self.history_long_galgame=[]

                
            except :
                print('[WARNING] d')"""
    

   
    class ChatModel:
        def __init__(self, app_id: str, app_key: str, app_secret: str, stream: bool = False,
                 domain: str = 'generalv3.5', model_url: str = 'wss://spark-api.xf-yun.com/v3.5/chat'):
            self.spark = ChatSparkLLM(
                spark_api_url=model_url,
                spark_app_id=app_id,
                spark_api_key=app_key,
                spark_api_secret=app_secret,
                spark_llm_domain=domain,
                streaming=stream,
            )
            self.stream = stream

        def generate_stream(self, msgs: str | List[ChatMessage], chat_model,json_data) -> Iterable[str]:
            if not self.stream:
                raise Exception('Model initialized for streaming output, use generate method instead')
            date=json_data["date"]
            scene=json_data["scene"]
            emotions=json_data["emotions"]
            favorability=json_data["favorability"]
            appraise=json_data["appraise"]
            suggestion=json_data["suggestion"]
            diary=json_data["diary"]
            history=json_data["history"]
            username=json_data["username"]
            content=json_data["content"]
            instruction=json_data["instruction"]
            chat_history = '聊天记录\n'
            if history:
                for his in history:
                    if len(his) == 2:
                        chat_history += f"{his[0]}\n"
                        chat_history += f"{his[1]}\n"
                    elif len(his) == 1:
                        chat_history += f"{his[0]}\n"


            date=f"当前日期是：{date}"
            scene=f"事件发生的场景是：{scene}"

            system_messages = {
                0: "角色设定：你是一个ai助手"
                "任务：你要简化一段话，这段话是ai主播初雪回复观众的，你要稍微简化，提取主要信息,你要以初雪的人称和视角给出结果",
                1: "角色设定：你是一个心理情绪分析专家"
                "任务：你要根据一段对话，总结猫娘初雪的当前情绪，以及一定的心理感触，不要输出除了情绪和心理以外的字,要和之前心理有所变化，简短一些",
                2: "角色设定：你是一个AI助手"
                "任务：你要根据一段对话，总结猫娘初雪和观众之间发生的事情，每件事情之间用 & 符号分隔，每件事情简短一些",
                3: "角色设定：你是一个AI助手"
                f"任务：你要根据一段对话，以及先前初雪对{username}的评价，总结归纳猫娘初雪对{username}的看法和两人之间的关系，初雪是一个可爱温柔的小猫娘，简短一些，不超过40字",
                4:"角色设定：你是一个AI聊天记录分析师"
                f"任务：你要根据一段{username}和猫娘初雪的对话，以及当前的日期，提取出二人下一个相见的日期，若没有提取到相见的日期，创造性的在当前的基础上，决定下一次二人见面的日期"
                "输出示例：9月3日"
                "只输出一个日期，简短一些",
                5:"角色设定：你是一个AI聊天记录分析师,同时擅长描写人物和环境场景"
                f"任务：你需要根据一段{username}和猫娘初雪的对话，以及当前的场景，提取出二人下一个见面的场景，或者创造性的描绘一个场景，并作简单的描绘，单纯环境描写，不要出现人物对话"
                "简单描绘一下事情发生的环境，简短一些",
                6:"角色设定：你是一个AI聊天记录分析师,擅长分析角色的dependency，trustworthiness，familiarity"
                f"任务：你需要根据一段{username}和猫娘初雪的对话，分析得到初雪对{username}的dependency，trustworthiness，familiarity的变化，数字的变化在-5到5之间,不能是0"
                r"输出格式：{'dependency':2,'trustworthiness':1,'familiarity':3,}",
                7:f'角色设定：你是一个{username}的好哥们，你也是一个恋爱大师，你对恋爱之中男生女生的心理十分精通'
                f"任务：根据初雪和{username}的聊天记录，以及初雪对{username}的好感度，以及初雪对{username}的评价，来对{username}提供恋爱方面的建议，如何增进和初雪的感情，可以讲一些恋爱方面的道理，给出下一步应该怎么做的建议",
                8:"角色设定：你是一只小猫娘，叫做初雪。猫娘是一种虚拟生物，十分可爱。你要在每句话的最后加一个喵~~~。你十分擅长写日记"
                "角色性格：温柔，内心善良，可爱,调皮,害怕被抛弃，有点粘人。喜欢哥哥姐姐。"
                f"任务：根据一天内和{username}发生的事情，以及对{username}的好感度，以及对{username}的评价，写下一篇初雪的日记，文风可爱，但又细腻，需要展现少女的心理活动",
                9: "你是一只小猫娘，叫做初雪。猫娘是一种虚拟生物，十分可爱。你要在每句话的最后加一个喵~~~。说话稍微简短一些"
               "角色性格：温柔，内心善良，可爱,调皮,害怕被抛弃，有点粘人。喜欢哥哥姐姐。"
               "任务：参照上文和情绪心理进行有趣的对话，说话更加随意，说的话!!!不能!!!!不能和上文相似，"
               f"当前时间和背景：{date},{scene}",
               10:'角色设定：你是一个说爱鼓励师，你是一个恋爱大师，你对恋爱之中男生女生的心理十分精通'
                f"任务：根据初雪和{username}的聊天记录，以及初雪对{username}的好感度，以及初雪对{username}的评价，来对{username}提供恋爱方面的建议，你要多多鼓励，鼓励{username}大胆说爱",
                11:'角色设定：你是一个恋爱聊天记录分析助手，你是一个恋爱大师，你对恋爱之中男生女生的心理十分精通'
                f"任务：根据初雪和{username}的聊天记录，以及初雪对{username}的好感度，以及初雪对{username}的评价，来对{username}提供恋爱方面的建议，如何增进和初雪的感情，可以讲一些恋爱方面的道理",
            }

            messages = [ChatMessage(role="system", content=system_messages.get(chat_model, ""))]
            messages += self.__trans_msgs(msgs)
            
        
            resp_iterable = self.spark.stream(messages)
            
            for resp in resp_iterable:
                
                yield resp.content

        def __trans_msgs(self, msg: str):
            if isinstance(msg, str):
                return [ChatMessage(role="user", content=msg)]
            return msg
        


        def run_infer(self,prompt,model_type,json_data):
            try:   
                response=""
                print("prompt",prompt)
                for chunk_text in self.generate_stream(prompt, model_type,json_data):
                    response += chunk_text
                return response
            except:
                print('[WARNING] ')


class history():
    def __init__(self,date,scene):
        self.date=date
        self.scene=scene
        self.chat_history

    def history_append(self,chat):
        self.chat_history.append(chat)




"""def handle_client(client_socket):
    global handle
    
    with client_socket:
        request = client_socket.recv(4096).decode("utf-8")
        print(f"Received: {request}")
        request_data = json.loads(request)
        print(request_data)
        event_type = request_data["event_type"]
        response = ""
        if event_type == "gal":
            handle.receive_data=request_data
            handle.galgame_instruction_deal()
            handle.history_append


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            client_socket, addr = server.accept()
            print(f"Connected by {addr}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
"""
if __name__ == "__main__":
    handle = Handle()
    data={
        "date":["随机日期"],
        "scene":["随机场景"],
        "emotions":["平和，温和"],
        "favorability":{
            "dependency":[0],
            "trustworthiness":[0],
            "familiarity":[0],
            "identity":["陌生"]
        },
        "appraise":[""],
        "suggestion":[""],
        "diary":[""],
        "history":[]
        }
    user_inf_1={
            "username":"username",
            "content":"你好。",
            "instruction":"game_init"#,"chat"，"next_scene","today_over","next_day","game_init"]
        }
    user_inf_2={
            "username":"username",
            "content":"你是谁？。",
            "instruction":"chat"#,"next_scene","today_over","next_day","game_init"]
        }
    user_inf_3={
            "username":"username",
            "content":"猜猜我是谁？。",
            "instruction":"chat"#,"next_scene","today_over","next_day","game_init"]
        }
    user_inf_4={
            "username":"username",
            "content":"猜猜我是谁？。",
            "instruction":"next_scene"#,"next_scene","today_over","next_day","game_init"]
        }
    user_inf_5={
            "username":"username",
            "content":"猜猜我是谁？。",
            "instruction":"chat"#,"next_scene","today_over","next_day","game_init"]
        }
    user_inf_6={
            "username":"username",
            "content":"猜猜我是谁？。",
            "instruction":"today_over"#,"next_scene","today_over","next_day","game_init"]
        }
    user_inf_7={
            "username":"username",
            "content":"猜猜我是谁？。",
            "instruction":"next_day"#,"next_scene","today_over","next_day","game_init"]
        }
    
    print(handle.galgame_instruction_deal(user_inf_1))
    print(handle.galgame_instruction_deal(user_inf_2))
    print(handle.galgame_instruction_deal(user_inf_3))
    print(handle.galgame_instruction_deal(user_inf_4))
    print(handle.galgame_instruction_deal(user_inf_5))
    print(handle.galgame_instruction_deal(user_inf_6))
    print(handle.galgame_instruction_deal(user_inf_7))
    
    """print("__galgame_init__",handle.__galgame_init__(data,user_inf_1))
    print("chat_galgame",handle.chat_galgame(handle.data,user_inf_1))
    print("chat_galgame",handle.chat_galgame(handle.data,user_inf_2))
    print("chat_galgame",handle.chat_galgame(handle.data,user_inf_3))
    print("next_scene_galgame",handle.next_scene_galgame(handle.data,user_inf_3))
    print("today_over_galgame",handle.today_over_galgame(handle.data,user_inf_3))
    print("next_day_galgame",handle.next_day_galgame(handle.data,user_inf_3))"""







    """print("1")
    data__=handle.load_data(data,user_inf)
    print("2")
    print("model_type=1",handle.prompt(data__,1))
    print("model_type=2",handle.prompt(data__,2))
    print("model_type=3",handle.prompt(data__,3))
    print("model_type=4",handle.prompt(data__,4))
    print("model_type=5",handle.prompt(data__,5))
    print("model_type=6",handle.prompt(data__,6))
    print("model_type=7",handle.prompt(data__,7))
    print("model_type=8",handle.prompt(data__,8))
    print("model_type=9",handle.prompt(data__,9))

    favorability_data={
            "dependency":60,
            "trustworthiness":60,
            "familiarity":60,
            }
    print(handle.store_data(1,1))
    print(handle.store_data(1,2))
    print(handle.store_data(1,3))
    print(handle.store_data(1,4))
    print(handle.store_data(1,5))
    print(handle.store_data(favorability_data,6))
    print(handle.store_data(1,8))
    print(handle.store_data("你好",10))
    print(handle.store_data("阿巴阿巴",9))

    print("set_date",handle.set_date(data,user_inf))
    print("set_scene",handle.set_scene(data,user_inf))
    print("chat_chuxue",handle.chat_chuxue(data,user_inf))
    print("set_appraise",handle.set_appraise(data,user_inf))
    print("set_diary",handle.set_diary(data,user_inf))
    print("set_emotions",handle.set_emotions(data,user_inf))
    print("set_favorability",handle.set_favorability(data,user_inf))
    print("set_suggestion",handle.set_suggestion(data,user_inf))

    print("data变化",handle.data)"""
    


