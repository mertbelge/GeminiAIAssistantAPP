import os
import google.generativeai as genai
import pymysql
from dotenv import load_dotenv
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from datetime import datetime

def db_connection():
      
    load_dotenv()

    DATABASE_IP = os.getenv("DATABASE_IP")
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE = os.getenv("DATABASE")

    db_connection = pymysql.connect(
        host=DATABASE_IP,       
        user=DATABASE_USER,            
        password=DATABASE_PASSWORD,      
        database=DATABASE 
    )

    return db_connection

def model_start():

    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT API_KEY, Model FROM STAREX.AI_SetupMain")
    result = cursor.fetchall()

    API_KEY = result[0][0]
    model = result[0][1]

    api = os.environ["GOOGLE_API_KEY"] = API_KEY

    genai.configure(api_key=api)

    generation_config = {
      "temperature": 2,
      "top_p": 0.95,
      "top_k": 64,
      "max_output_tokens": 8192,
      "response_mime_type": "text/plain"
    }

    model = genai.GenerativeModel(model,
                                 generation_config=generation_config,)
    
    cursor.close()
    connection.close()
    
    return model

def system_prompt():
    
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT UserNameSurname, AI_Name FROM STAREX.AI_UserMain")
    result = cursor.fetchall()

    UserName = result[0][0]
    AI_Name = result[0][1]

    prompt = ('SİSTEM PROMPTU: Senin adın ' + AI_Name + ' ve seninle konuşan kişinin ismi' + UserName + 
            'birazdan sana geçmiş konuşmalarımız yüklenecek ve kullanıcın sana arada sırada geçmiş hakkında bilgi isteyebilir.' + 
            'Eğer sana ' + AI_Name + ' hitap edip ardında Not Ekle diye hitap edersem bana dümdüz 1 diye cevap ver.' + 
            'Eğer sana ' + AI_Name + ' hitap edip ardında Notlarımı Göster kibarcası yada kabacası olsun, hitap edersem bana dümdüz 2 diye cevap ver.' +
            'Eğer sana ' + AI_Name + ' hitap edip ardında Notlarımı Tamamlandıya Çek diye hitap edersem bana dümdüz 3 diye cevap ver.')
    
    cursor.close()
    connection.close()

    return prompt

def get_chat_history():
    
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT Role, Description FROM STAREX.AI_PromptMain")
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return [{'role': role, 'parts': [{'text': message}]} for role, message in result]

def get_AI_Name():
    
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT AI_Name FROM STAREX.AI_UserMain")
    result = cursor.fetchall()
    
    AI_Name = result[0][0]
    
    cursor.close()
    connection.close()
    
    return AI_Name

class AI_App(App):
        
    def build(self):
    
        self.note_add = 'Notunuz başarılı bir şekilde eklenmiştir!'
        self.note_not_exist = "Tarafınıza ait not bulunmamaktadır!"
        self.set_passive_complete = 'Notlarınız tamamlandıya çekilmiştir!'
        self.set_passive_fail = 'Notlarınız tamamlandıya çekildiği sıra hata meydana!'
        self.now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sys_prompt = system_prompt()

        self.history = [{'parts': [{'text':sys_prompt}], 'role': 'user'}] + get_chat_history()

        self.model = model_start()
        self.chat_session = self.model.start_chat( history = self.history)
        
        self.connection = db_connection()
        self.cursor = self.connection.cursor()

        main_layout = BoxLayout(orientation='vertical')

        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=[0, 0, 10, 15])
        self.label = Label(text="My Pocket Assistant", font_size=18, size_hint=(1, 0.1))

        exit_layout = RelativeLayout(size_hint=(None, None), size=(25, 25))

        self.exit_button = Button(size_hint=(1, 1), background_normal="", background_color=(1, 1, 1))
        self.exit_button.bind(on_press=self.on_exit)

        exit_icon = Image(source="img/x-icon.png", size_hint=(None, None), size=(15, 15),
                          pos_hint={"center_x": 0.5, "center_y": 0.5})
        
        exit_layout.add_widget(self.exit_button)
        exit_layout.add_widget(exit_icon)

        top_layout.add_widget(self.label)
        top_layout.add_widget(exit_layout)

        space_layout_1 = RelativeLayout(size_hint=(None, None), size=(10, 50))
        space_layout_2 = RelativeLayout(size_hint=(None, None), size=(5, 50))
        space_layout_3 = RelativeLayout(size_hint=(None, None), size=(5, 50))
        space_layout_4 = RelativeLayout(size_hint=(None, None), size=(5, 50))

        self.middle_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        bottom_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)
        self.text_input = TextInput(size_hint_x=0.9, multiline=True)

        listen_layout = RelativeLayout(size_hint=(None, None), size=(50, 50))

        self.listen_button = Button(size_hint=(1, 1), background_normal="", background_color=(1, 1, 1))
        self.listen_button.bind(on_press=self.on_record)

        listen_icon = Image(source="img/mic-icon.png", size_hint=(None, None), size=(30, 30),
                          pos_hint={"center_x": 0.5, "center_y": 0.5})
        
        listen_layout.add_widget(self.listen_button)
        listen_layout.add_widget(listen_icon)

        button_layout = RelativeLayout(size_hint=(None, None), size=(50, 50))

        self.send_button = Button(size_hint=(1, 1), background_normal="", background_color=(1, 1, 1))
        self.send_button.bind(on_press=self.on_enter)

        send_icon = Image(source="img/send-icon.png", size_hint=(None, None), size=(30, 30),
                          pos_hint={"center_x": 0.5, "center_y": 0.5})

        button_layout.add_widget(self.send_button)
        button_layout.add_widget(send_icon)
        
        bottom_layout.add_widget(space_layout_1)
        bottom_layout.add_widget(self.text_input)
        bottom_layout.add_widget(space_layout_2)
        bottom_layout.add_widget(listen_layout)
        bottom_layout.add_widget(space_layout_3)
        bottom_layout.add_widget(button_layout)
        bottom_layout.add_widget(space_layout_4)

        main_layout.add_widget(top_layout) 
        main_layout.add_widget(self.middle_layout)
        main_layout.add_widget(bottom_layout) 
        return main_layout
       
    def on_pause(self):

        self.cursor.close()
        self.connection.close()
        return 

    def on_resume(self):

        self.connection = db_connection()
        self.cursor = self.connection.cursor()
        return
    
    def on_exit(self, instance):

        App.get_running_app().stop()
        return 

    def on_record(self, instance):

        self.text_input.text = ""
      
    def on_enter(self, instance):
        
        prompt =  self.text_input.text.strip()
        self.text_input.text = ""
        self.middle_layout.clear_widgets()

        first_propmt = prompt

        if prompt != '':
                
            response = self.chat_session.send_message(prompt)
            response.resolve()

            if response.text == '1\n':

                self.cursor.callproc("SP_STAREX_AIAddNote", (prompt,))
                self.connection.commit()
                message = self.note_add

            elif response.text == '2\n':

                self.cursor.callproc("SP_STAREX_NoteGetList")
                result = self.cursor.fetchall()

                message = "\n".join([note[0] for note in result]) if result else self.note_not_exist

            elif response.text == '3\n':
                
                prompt = prompt.lower()
                prompt = prompt.split(' ',4)[-1]
                set_passive_id = prompt.split(" ve ")

                try:

                    for id_value in set_passive_id:

                        self.cursor.callproc("SP_STAREX_AINoteUpdate", (id_value,))
                        self.connection.commit()

                    message = self.set_passive_complete

                except:

                    message = self.set_passive_fail


            else:

                message = response.text
                self.cursor.callproc("SP_STAREX_AIChat", ('user', prompt))
                self.connection.commit()
                self.cursor.callproc("SP_STAREX_AIChat", ('assistant', message))
                self.connection.commit()  

            self.cursor.callproc("SP_STAREX_AILogInsert", ('user', first_propmt))
            self.connection.commit()
            self.cursor.callproc("SP_STAREX_AILogInsert", ('assistant', message))
            self.connection.commit() 

            self.cursor.callproc('SP_STAREX_GetCurrentChatHistory', (self.now,))
            self.connection.commit()
            result = self.cursor.fetchall()

            for row in result:

                role, description = row
            
                if role == 'user':
        
                    self.middle_layout.add_widget(Label(text=description, size_hint=(1, 0.5)))

                elif role == 'assistant':
            
                    self.middle_layout.add_widget(Label(text=description, size_hint=(1, 0.5)))

if __name__ == "__main__":
    AI_App().run()