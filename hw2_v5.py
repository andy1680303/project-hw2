# 圖形化介面模組
import tkinter as tk
from tkinter import filedialog, messagebox
# 處理英文
from wordcloud import WordCloud, STOPWORDS
# 繪圖模組
import matplotlib.pyplot as plt
# 處理中文
import os     # 用來判斷你的電腦是 Windows 還是 Mac，以決定抓什麼中文字體
import jieba  # 中文斷詞


# ==========================================
# 定義我們的「文字雲產生器」類別 (Class)
# 類別 (Class) 就像是定義物件的「藍圖」，我們在這裡設計好文字雲機器需要的所有變數與功能。
# ==========================================
class WordCloudGenerator:
    
    # 建構函式 (Constructor)：當我們建立這個類別的物件時，一定會優先自動呼叫這個函式
    # 負責初始化視窗大小、標題，以及將所有 UI 元件擺放到畫面上
    def __init__(self, root):
        self.root = root
        self.root.title("雙語文字雲產生器 (jieba版)") # 設定視窗標題
        self.root.geometry("600x450")                 # 設定視窗預設大小 (寬x高)

        # 【核心觀念：封裝與物件層級變數】
        # 使用 self.current_wc 宣告一個專屬於這個物件的變數，用來暫存做好的文字雲圖片。
        # 這樣就能完美取代過去使用的 global 全域變數，符合大型程式開發的規範。
        self.current_wc = None
        
        # --- UI 介面設計區 ---
        # 1. 建立文字輸入框 (供使用者貼上文章)
        self.text_area = tk.Text(self.root, height=15, width=60)
        self.text_area.pack(pady=10) # pack() 是將元件放入視窗，pady 控制上下間距

        # 2. 建立語言選擇區塊 (單選按鈕)
        self.lang_var = tk.StringVar(value="en") # 預設選擇 "en" (英文)
        lang_frame = tk.Frame(self.root)         # 建立一個隱形框架把按鈕包在一起
        lang_frame.pack(pady=5)
        # 綁定 variable 到 self.lang_var，這樣程式才能知道使用者選了哪一個
        tk.Radiobutton(lang_frame, text="英文文字雲", variable=self.lang_var, value="en").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(lang_frame, text="中文文字雲", variable=self.lang_var, value="zh").pack(side=tk.LEFT, padx=10)

        # 3. 建立功能按鈕區塊
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        # command=self.generate_action 代表點擊按鈕時，會去呼叫屬於自己的 generate_action 方法
        tk.Button(btn_frame, text="產生文字雲", command=self.generate_action).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="儲存圖片", command=self.save_action).pack(side=tk.LEFT, padx=5)

    # ==========================================
    # 核心方法：產生文字雲的大腦邏輯
    # ==========================================
    def generate_action(self):
        # 1. 讀取使用者的選擇與輸入的文字
        lang = self.lang_var.get()
        text = self.text_area.get("1.0", tk.END).strip()
        
        # 準備一個空的 Dictionary (字典) 來計算詞頻。
        # Dictionary 的底層實作即為 Hash Table，尋找與更新的時間複雜度為 O(1)，速度極快。
        word_frequencies = {}

        # 2. 雙語分流處理：根據選擇的語言執行不同的斷詞與過濾邏輯
        if lang == "en":
            # 【英文模式】
            words = text.split() # 英文直接以空白鍵作為切割依據
            for word in words:
                word = word.lower() # 統一轉為小寫，避免大小寫被視為不同單字
                # 過濾條件：長度須大於 1，且不能存在於 wordcloud 內建的 STOPWORDS (如 a, the, is) 中
                if len(word) > 1 and word not in STOPWORDS:
                    # Hash 技巧：統計出現次數
                    if word in word_frequencies:
                        word_frequencies[word] += 1
                    else:
                        word_frequencies[word] = 1
            my_font = None # 英文預設不需要特別指定字體路徑

        else:
            # 【中文模式】
            words = jieba.lcut(text) # 中文無空白，必須使用 jieba 斷詞套件根據語意切割
            zh_stopwords = set()     # 準備一個 Set (集合) 來存放中文停用詞，Set 底層也是 Hash，搜尋極快
            
            # 1. 取得目前這個 Python 腳本所在的資料夾絕對路徑
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # 2. 將資料夾路徑與檔案名稱組合起來，變成完整的絕對路徑
            stopword_path = os.path.join(current_dir, "stopwords_Traditional_Chinese.txt")

            # 動態讀取外部的中文停用詞檔案 (Stop Words Dictionary)
            try:
                # 必須指定 encoding="utf-8" 以正確讀取中文檔案內容，避免亂碼
                with open(stopword_path, "r", encoding="utf-8") as f:
                    for line in f:
                        word = line.strip()
                        if word: 
                            zh_stopwords.add(word) # 將檔案內的停用詞加入集合中
            except FileNotFoundError:
                # 若找不到檔案，則啟動防呆機制，跳出警告並僅提供基礎的標點符號過濾
                messagebox.showwarning("找不到檔案", "找不到 'stopwords_Traditional_Chinese.txt'，將僅過濾基礎標點符號。")
                zh_stopwords = {'\n', ' ', '，', '。', '！', '？', '、'}
            
            # 開始過濾與計算中文詞頻
            for word in words:
                word = word.strip()
                # 條件：長度大於 1，且不在我們剛剛建立的停用詞集合中
                if len(word) > 1 and word not in zh_stopwords:
                    if word in word_frequencies:
                        word_frequencies[word] += 1
                    else:
                        word_frequencies[word] = 1
            
            # 中文必須強制給予中文字體，否則會出現方塊亂碼 (豆腐塊)。自動判斷作業系統給予字體。
            my_font = "msjh.ttc" if os.name == 'nt' else "PingFang.ttc"

        # 3. 防呆機制：如果整篇文章都被過濾掉（例如全都是標點符號），則停止執行並警告
        if not word_frequencies:
            messagebox.showwarning("警告", "過濾後沒有足夠的文字可以產生文字雲！")
            return

        # 方便在終端機檢查 Hash 統計出來的結果
        print(f"[{lang}] 過濾後的字數統計：", word_frequencies)

        # 4. 呼叫外部函式庫產生文字雲圖形
        wc = WordCloud(
            font_path=my_font,        # 字體設定
            width=1200,               # 圖片寬度
            height=800,               # 圖片高度
            background_color='white', # 背景設為白色
            max_words=50,             # 限制最多只顯示頻率最高的前 50 個詞彙
            colormap='plasma'         # 套用好看的漸層色系
        )
        # 將我們算好的 Dictionary (Hash) 交給產生器
        wc.generate_from_frequencies(word_frequencies)
        
        # 【重點】將產生好的文字雲物件，儲存到「物件專屬的變數」中，讓 save_action 等一下可以拿來用
        self.current_wc = wc

        # 5. 使用 matplotlib 彈出視窗並顯示圖片
        plt.figure(figsize=(12, 8))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis("off") # 隱藏 X 軸與 Y 軸的刻度
        plt.show()

    # ==========================================
    # 儲存方法：將文字雲存成圖檔
    # ==========================================
    def save_action(self):
        # 檢查肚子裡 (self.current_wc) 有沒有已經做好的文字雲
        if self.current_wc is None:
            messagebox.showwarning("警告", "請先產生文字雲再存檔喔！")
            return
            
        # 彈出存檔對話框，讓使用者選擇存檔位置與格式
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            title="儲存文字雲",
            filetypes=(("PNG 圖片", "*.png"), ("JPEG Image", "*.jpg"), ("所有檔案", "*.*"))
        )
        
        # 若使用者有選擇路徑 (沒有按取消)，則呼叫 to_file 儲存圖檔
        if filepath:
            self.current_wc.to_file(filepath)
            messagebox.showinfo("成功", "太棒了，圖檔儲存成功！")


# ==========================================
# 程式的真正進入點 (Main Program)
# ==========================================
# 當這支程式被直接執行時，才會觸發底下的程式碼。
if __name__ == "__main__":
    # 建立 tkinter 的主視窗容器
    main_window = tk.Tk()
    
    # 實際建立出一個占用記憶體的「物件實體 (Object)」
    # 根據 WordCloudGenerator 這個藍圖，打造出名為 app 的實體，並把主視窗傳進去
    app = WordCloudGenerator(main_window) 
    
    # 啟動視窗的無窮迴圈，讓介面保持開啟狀態，等待使用者點擊按鈕
    main_window.mainloop()