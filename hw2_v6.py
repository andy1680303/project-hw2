# ==========================================
# 外部模組與套件
# ==========================================
import tkinter as tk                       # 引入 Python 內建的圖形化介面 (GUI) 模組
from tkinter import filedialog, messagebox # 引入 tkinter 的子模組：檔案對話框與警告訊息視窗
import os                                  # 引入作業系統模組，用於判斷目前是 Windows 還是 Mac
from wordcloud import WordCloud, STOPWORDS # 引入文字雲產生器，以及內建的英文停用詞表 (無意義字)
import matplotlib.pyplot as plt            # 引入繪圖模組，用於將文字雲結果顯示在彈出視窗中

# 引入中研院 CKIP Transformers 的斷詞工具
# 這是一個基於深度學習 (Deep Learning) 的自然語言處理套件，精準度高
# 參考來源：https://github.com/ckiplab/ckip-transformers
# pip install -U ckip-transformers
from ckip_transformers.nlp import CkipWordSegmenter

# ==========================================
# 定義我們的「文字雲產生器」類別 (Class)
# 運用「物件導向」觀念，將介面、變數與功能整理在一起，並避免使用全域變數
# ==========================================
class WordCloudGenerator:
    
    # 建構函式 (Constructor)：當我們建立這個類別的物件實體時，會自動且優先執行的初始化設定
    def __init__(self, root):
        self.root = root
        self.root.title("雙語文字雲產生器 (CKIP 中研院 AI 版)") # 設定主視窗的標題
        self.root.geometry("600x450")                     # 設定主視窗的初始大小 (寬x高)

        # 【物件層級變數 (Instance Variable)】
        # 用 self.current_wc 來記錄目前產生好的文字雲，方便後續「存檔功能」讀取
        self.current_wc = None
        
        # ----------------------------------------------------
        # 【重要功能：預先載入 AI 模型】
        # 由於 AI 模型檔案較大，若每次按按鈕才載入會造成介面卡頓
        # 因此在建構函式中提早載入。選用 "albert-tiny" 模型因為它體積小、運算快，最適合桌面端程式
        # ----------------------------------------------------
        print("正在啟動 CKIP AI 引擎，請稍候...")
        self.ws_driver = CkipWordSegmenter(model="albert-tiny")
        print("CKIP 引擎載入完成！")
        
    
        # ==========================================
        # UI 介面設計區 (將所有元件放入主視窗中)
        # ==========================================
        # 1. 建立文字輸入框，供使用者貼上想分析的文章
        self.text_area = tk.Text(self.root, height=15, width=60)
        self.text_area.pack(pady=10) # pack() 是排版指令，pady=10 代表上下保留 10 像素的空白

        # 2. 建立語言選擇區塊 (單選按鈕)
        self.lang_var = tk.StringVar(value="en") # 預設選擇值為 "en" (英文)
        lang_frame = tk.Frame(self.root)         # 建立一個隱形框架，把兩個按鈕包在一起方便排版
        lang_frame.pack(pady=5)
        # 綁定 variable 到 self.lang_var，當使用者點擊時，程式就能知道目前選擇了哪種語言
        tk.Radiobutton(lang_frame, text="英文文字雲", variable=self.lang_var, value="en").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(lang_frame, text="中文文字雲", variable=self.lang_var, value="zh").pack(side=tk.LEFT, padx=10)

        # 3. 建立功能按鈕區塊
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        # 綁定 command：點擊按鈕時，會去呼叫物件內部的對應方法 (Method)
        tk.Button(btn_frame, text="產生文字雲", command=self.generate_action).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="儲存圖片", command=self.save_action).pack(side=tk.LEFT, padx=5)

    # ==========================================
    # 核心功能一：斷詞、過濾與產生文字雲大腦邏輯
    # ==========================================
    def generate_action(self):
        # 1. 讀取介面上的語言設定以及輸入框中的文字 (利用 strip() 移除前後多餘的空白或換行)
        lang = self.lang_var.get()
        text = self.text_area.get("1.0", tk.END).strip()
        
        # 【核心資料結構：Hash】
        # 建立一個空的 Dictionary 來統計詞頻。為 Python 的 Hash Table
        word_frequencies = {}

        # 2. 雙語分流處理：根據選擇的語言執行不同的切割與過濾邏輯
        if lang == "en":
            # 【英文模式】
            words = text.split() # 英文直接以「空白鍵」作為切割單字的依據
            for word in words:
                word = word.lower() # 將單字統一轉為小寫，避免 Apple 與 apple 被視為不同字
                
                # 過濾條件：長度須大於 1，且不能存在於 wordcloud 內建的 STOPWORDS 集合中
                if len(word) > 1 and word not in STOPWORDS:
                    # 利用 Hash Table 更新詞頻
                    if word in word_frequencies:
                        word_frequencies[word] += 1
                    else:
                        word_frequencies[word] = 1
            my_font = None # 英文不需要特地指定字體路徑

        else:
            # 【中文模式 - CKIP 深度學習斷詞】
            # CKIP 套件規定輸入格式必須是一個　List　，故用 [text] 包裝
            # 回傳的結果為巢狀list（兩層的list、二軸陣列），故取 [0] 提取出第一篇文章的斷詞結果陣列
            ws_result = self.ws_driver([text])
            words = ws_result[0]
            
            # 使用 Set (集合) 來存放中文停用詞，過濾時的比對速度快
            zh_stopwords = set()
            
            # 讀取外部的停用詞檔案：stopwords_Traditional_Chinese.txt
            # 1. 取得目前這個 Python 腳本所在的資料夾絕對路徑
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # 2. 將資料夾路徑與檔案名稱組合起來，變成完整的絕對路徑
            stopword_path = os.path.join(current_dir, "stopwords_Traditional_Chinese.txt")
            try:
                # 指定 encoding="utf-8" 以正確解碼中文字元，避免出現亂碼錯誤
                with open(stopword_path, "r", encoding="utf-8") as f:
                    for line in f:
                        word = line.strip()
                        if word: 
                            zh_stopwords.add(word) # 將檔案內每一行的詞彙加入 Set 集合中
            except FileNotFoundError:
                # 防呆：若資料夾中沒有該檔案，則跳出警告，並預設僅過濾基本的標點符號
                messagebox.showwarning("找不到檔案", "找不到 'stopwords_Traditional_Chinese.txt'，將僅過濾基礎標點符號。")
                zh_stopwords = {'\n', ' ', '，', '。', '！', '？', '、'}
            
            # 開始過濾並計算中文詞頻
            for word in words:
                word = word.strip()
                # 條件：長度大於 1，且不在我們建立的中文停用詞 Hash 集合中
                if len(word) > 1 and word not in zh_stopwords:
                    if word in word_frequencies:
                        word_frequencies[word] += 1
                    else:
                        word_frequencies[word] = 1
            
            # 中文必須強制給予中文字體路徑，否則文字雲會呈現方塊亂碼
            # 這裡利用 os 模組自動判斷：Windows ('nt') 用微軟正黑體，Mac 用蘋方體
            my_font = "msjh.ttc" if os.name == 'nt' else "PingFang.ttc"

        # 3. 執行前防呆：如果過濾後字典為空 (例如輸入全都是標點符號)，則中止執行並警告使用者
        if not word_frequencies:
            messagebox.showwarning("警告", "過濾後沒有足夠的文字可以產生文字雲！")
            return

        # 將 Hash 計算的結果印在終端機，方便開發者檢查資料正確性
        print(f"[{lang}] 過濾後的字數統計：", word_frequencies)

        # 4. 呼叫 WordCloud 套件產生圖片
        wc = WordCloud(
            font_path=my_font,        # 套用自動判斷的中/英文字體
            width=1200,               # 圖片寬度像素
            height=800,               # 圖片高度像素
            background_color='white', # 背景設定為白色
            max_words=50,             # 作業加分項：動態指定前 n 個最高頻率的文字 (此處設為 50)
            colormap='plasma'         # 套用 Python 內建的 plasma 漸層色系，提升美觀度
        )
        # 將我們算好的 Hash 字典交給文字雲產生器
        wc.generate_from_frequencies(word_frequencies)
        
        # 【重要封裝】將產生好的文字雲圖片，指派給物件層級變數，讓下方的 save_action 可以取得它
        self.current_wc = wc

        # 5. 使用 matplotlib 彈出視窗並顯示最終圖片
        plt.figure(figsize=(12, 8))
        plt.imshow(wc, interpolation='bilinear') # 使用雙線性插值法讓圖片邊緣更平滑
        plt.axis("off")                          # 隱藏預設的 X 與 Y 軸座標刻度
        plt.show()

    # ==========================================
    # 核心功能二：將文字雲結果儲存為圖檔
    # ==========================================
    def save_action(self):
        # 防呆機制：若使用者還沒產生文字雲就按存檔，self.current_wc 會是 None
        if self.current_wc is None:
            messagebox.showwarning("警告", "請先產生文字雲再存檔喔！")
            return
            
        # 彈出存檔對話框，讓使用者自行決定存檔路徑與副檔名格式
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            title="儲存文字雲",
            filetypes=(("PNG 圖片", "*.png"), ("JPEG Image", "*.jpg"), ("所有檔案", "*.*"))
        )
        
        # 若 filepath 不為空 (即使用者沒有按取消)，則呼叫內建的 to_file 方法存檔
        if filepath:
            self.current_wc.to_file(filepath)
            messagebox.showinfo("成功", "太棒了，圖檔儲存成功！")


# ==========================================
# 程式的真正進入點 (Main Program)
# 確保這支檔案被直接執行時，才會啟動視窗；若被其他檔案 import 則不會啟動
# ==========================================
if __name__ == "__main__":
    # 建立 tkinter 的主視窗容器
    main_window = tk.Tk()
    
    # 根據我們畫好的 WordCloudGenerator 藍圖，在記憶體中寫入一個名為 app 的物件實體 (Object)
    app = WordCloudGenerator(main_window) 
    
    # 啟動視窗的無窮迴圈 (Main Loop)，讓介面保持開啟狀態，等使用者的按鈕點擊事件
    main_window.mainloop()