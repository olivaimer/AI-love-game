import gradio as gr
from Handle import Handle
from Handle import history

class history():
    def __init__(self,date,scene):
        self.date=date
        self.scene=scene
        self.chat_history=[]
        self.diary=""
        self.user_inf={
            "username":"",
            "content":"",
            "instruction":"chat"
        }

    def history_append(self,chat):
        self.chat_history.append(chat)

class Centre:
    def __init__(self):
        self.date=""
        self.historys={"date_list":[]}
        self.mental=""
        self.suggestion=""
        self.user_inf={
            "username":"",
            "content":"",
            "instruction":"chat"
        }

    def load_data(self,date):
        global handle
        data=handle.data.copy()
        data["date"]=[date]
        data["scene"]=[self.historys[date].scene]
        data["history"]=self.historys[date].chat_history

        return data
        
    def change_date(self):
        lastdate=self.historys["date_list"][0]
        date_list=""
        for date in self.historys["date_list"]:
            if self.date==date:
                self.date=lastdate
                for date in self.historys["date_list"]:
                    if date==self.date:
                        date_list+=f"now!!{date} -> "
                    else:
                        date_list+=f"{date} -> "
                date_list=date_list[:-4]
                yield date_list,self.historys[self.date].scene,self.historys[self.date].chat_history,self.historys[self.date].diary  # 返回新的日期列表
            lastdate=date




    def load_user_inf(self,username,content):
        self.user_inf={
            "username":username,
            "content":content,
            "instruction":"chat"
        }

        return self.user_inf

    def chat(self,username,content):
        global handle
        txt_mental=""
        txt_suggestion_1=""
        data=self.load_data(self.date)
        print(1)
        user_inf=self.load_user_inf(username,content)
        """print("handle",handle)
        print(data,user_inf)"""
        print(handle.data)
        response=handle.chat_chuxue(data,user_inf)
        print(2)
        self.historys[self.date].history_append((content,f"{response}"))
        print(3)
        data=self.load_data(self.date)
        print(4)
        chatbox_chat=self.historys[self.date].chat_history
        yield txt_mental,chatbox_chat,txt_suggestion_1
        print("\n\n\n\n\nfffffffffff",handle.set_favorability(data,user_inf),"\n\n\n\n\n\n")
        handle.set_emotions(data,user_inf)
        handle.set_appraise(data,user_inf)
        """point=sum([handle.data["favorability"]["dependency"],handle.data["favorability"]["trustworthiness"],handle.data["favorability"]["familiarity"]])/3"""
        point=10
        identity=handle.data["favorability"]["identity"]
        emotions=handle.data["emotions"][-1]
        appraise=handle.data["appraise"][-1]
        txt_mental=f"初雪对{username}的好感度:{int(point)}\n初雪眼中你和她的关系:{identity}\n{emotions}\n初雪对{username}的评价：{appraise}"
        yield txt_mental,chatbox_chat,txt_suggestion_1

        handle.set_suggestion(data,user_inf)
        txt_suggestion_1=handle.data["suggestion"][-1]
        yield txt_mental,chatbox_chat,txt_suggestion_1

    def suggestion_2(self,content):
        self.user_inf["content"]=content
        data=self.load_data(self.date)
        user_inf=self.load_user_inf(username,content)
        suggestion=handle.set_suggestion2(data,user_inf)
        chatbox_suggestion=[(content,suggestion)]
        yield chatbox_suggestion

    def suggestion_3(self):
        data=self.load_data(self.date)
        user_inf=self.load_user_inf(username,content)
        txt_suggestion_3=handle.set_suggestion3(data,user_inf)
    
        yield txt_suggestion_3

    def date_scene_generate(self):
        global handle

        if self.historys["date_list"]==[]:
            date = handle.set_date(handle.data, self.user_inf)
            scene = handle.set_scene(handle.data, self.user_inf)

            self.historys["date_list"].append(date)
            self.historys[date] = self.history(date, scene)  # 确保新场景也被保存
            date_list=""
            self.date=date
            for date in self.historys["date_list"]:
                if date==self.date:
                    date_list+=f"now!!{date} -> "
                else:
                    date_list+=f"{date} -> "
            date_list=date_list[:-4]
            yield date_list,self.historys[self.date].scene,self.historys[self.date].chat_history,self.historys[self.date].diary  # 返回新的日期列表
        elif self.date==self.historys["date_list"][-1]:
            date = handle.set_date(handle.data, self.user_inf)
            scene = handle.set_scene(handle.data, self.user_inf)

            self.historys["date_list"].append(date)
            self.historys[date] = self.history(date, scene)  # 确保新场景也被保存
            date_list=""
            self.date=date
            for date in self.historys["date_list"]:
                if date==self.date:
                    date_list+=f"now!!{date} -> "
                else:
                    date_list+=f"{date} -> "
            date_list=date_list[:-4]
            yield date_list,self.historys[self.date].scene,self.historys[self.date].chat_history,self.historys[self.date].diary  # 返回新的日期列表

        else:
            for i in range(len(self.historys["date_list"])):
                if self.historys["date_list"][i]==self.date:
                    break
            self.date=self.historys["date_list"][i+1] 
            date_list=""
            for date in self.historys["date_list"]:
                if date==self.date:
                    date_list+=f"now!!{date} -> "
                else:
                    date_list+=f"{date} -> "
            date_list=date_list[:-4]
            yield date_list,self.historys[self.date].scene,self.historys[self.date].chat_history,self.historys[self.date].diary # 返回新的日期列表




    
    def get_date_list(self):
        return self.historys["date_list"]



    def diary(self):
        global handle
        if self.historys[self.date].diary=="":
            data=self.load_data(self.date)
            user_inf=self.load_user_inf(username,content)
            txt_diary=handle.set_diary(data,user_inf)
            self.historys[self.date].diary=txt_diary
            yield self.historys[self.date].diary
        else:
            yield self.historys[self.date].diary



    
    class history():
        def __init__(self,date,scene):
            self.date=date
            self.scene=scene
            self.chat_history=[]
            self.diary=""
            self.user_inf={
                "username":"",
                "content":"",
                "instruction":"chat"
            }

        def history_append(self,chat):
            self.chat_history.append(chat)

centre=Centre()





with gr.Blocks(css="style.css") as demo:
    with gr.Tab(label="初雪",elem_classes="gradio-container2"):
        with gr.Row(elem_classes="gradio-container6"):

            with gr.Column(scale=2,elem_classes="gradio-container3"):

                with gr.Group(elem_classes="gradio-container7"):
                    """dropdown_date=gr.Dropdown(centre.historys["date_list"],label="style1")"""
                    txt_date=gr.Textbox(lines=9,label="时间线",scale=1)
                  
                    """for date in centre.historys["date_list"]:
                            centre.buttons[date]=gr.Button(centre.historys[date].date)"""

                with gr.Row(elem_classes="gradio-container7"):
                    button_generate_date_scene=gr.Button("Next Day")
                    button_generate_change_date=gr.Button("Last Day")
                    
                """dropdown=gr.Dropdown(["1","2","3","4"],label="style1",scale=5)"""
                with gr.Group(elem_classes="gradio-container7"):
                    txt_mental=gr.Textbox(lines=12,label="初雪的情绪",scale=1)

            
            with gr.Column(scale=5,elem_classes="gradio-container3"):
                with gr.Tab(label="初雪",elem_classes="gradio-container7"):
                    with gr.Group(elem_classes="gradio-container5"):
                        txt_date_scene=gr.Textbox(lines=2,label="当前场景")
                    chatbox_chat=gr.Chatbot([],label="初雪聊天框")
                    with gr.Row(elem_classes="gradio-container5"):
                        username=gr.Textbox(lines=1,label="昵称",scale=3)
                        content=gr.Textbox(lines=1,label="对话内容",scale=7)
                    button_chat=gr.Button("快来和初雪聊天吧")
                with gr.Tab(label="初雪的日记",elem_classes="gradio-container7"):
                    txt_diary=gr.Textbox(lines=33,label="")
                    button_diary=gr.Button()
                with gr.Tab(label="头像生成",elem_classes="gradio-container7"):
                    pass
                



            with gr.Column(scale=2,elem_classes="gradio-container3"):
                with gr.Tab(label="实时小僚机",elem_classes="gradio-container7"):
                    with gr.Group(elem_classes="gradio-container5"):
                        txt_suggestion_1=gr.Textbox(lines=33,label="僚机启动")
                with gr.Tab(label="说爱鼓励师",elem_classes="gradio-container7"):
                    chatbox_suggestion=gr.Chatbot(label="说爱鼓励师",elem_classes="gradio-container5")
                    content_suggestion=gr.Textbox(lines=1,label="")
                    button_suggestion1=gr.Button("遇到困难了，问问军师吧")
                with gr.Tab(label="事后诸葛亮",elem_classes="gradio-container7"):
                    with gr.Group(elem_classes="gradio-container5"):
                        txt_suggestion_3=gr.Textbox(lines=30 , label="恋爱诸葛")
                    button_suggestion2=gr.Button("让大师来分析一波")
                    

        button_chat.click(fn=centre.chat,inputs=[username,content],outputs=[txt_mental,chatbox_chat,txt_suggestion_1])
        button_suggestion1.click(fn=centre.suggestion_2,inputs=[content_suggestion],outputs=[chatbox_suggestion])
        button_suggestion2.click(fn=centre.suggestion_3,outputs=[txt_suggestion_3])
        button_generate_date_scene.click(fn=centre.date_scene_generate,outputs=[txt_date,txt_date_scene,chatbox_chat,txt_diary])
        button_diary.click(fn=centre.diary,outputs=[txt_diary])
        button_generate_change_date.click(fn=centre.change_date,outputs=[txt_date,txt_date_scene,chatbox_chat,txt_diary])
    with gr.Tab(label="白露",elem_classes="gradio-container"):
        pass
    with gr.Tab(label="角色自定义",elem_classes="gradio-container"):
        pass
    with gr.Tab(label="群聊",elem_classes="gradio-container"):
        pass
        

    
                    

    """with gr.Group():
        txt1=gr.Textbox(lines=5,label="")
        txt1=gr.Textbox(lines=5,label="")
        txt1=gr.Textbox(lines=5,label="")
    with gr.Accordion():
        txt1=gr.Textbox(lines=5,label="")
        txt1=gr.Textbox(lines=5,label="")
        txt1=gr.Textbox(lines=5,label="")"""

if __name__ == "__main__":
    handle=Handle()

    history_list={}

    demo.queue().launch(share=True)