import tkinter as tk
from tkinter import filedialog, messagebox

import os
import jieba
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# 定義我們的「文字雲產生器」類別 (Class) [cite: 197]
class WordCloudGenerator:
    
    # 建構函式 (Constructor)：建立物件時一定會呼叫到的函式 [cite: 184]
    def __init__(self, root):
        self.root = root
        self.root.title("雙語文字雲產生器 (物件導向版)")
        self.root.geometry("600x450")

        # 【重點】用物件層級的變數 (self.) 來取代 global！ [cite: 166]
        self.current_wc = None
        
        # --- 以下是把 UI 介面收納到建構函式裡 ---
        self.text_area = tk.Text(self.root, height=15, width=60)
        self.text_area.pack(pady=10)

        self.lang_var = tk.StringVar(value="en")
        lang_frame = tk.Frame(self.root)
        lang_frame.pack(pady=5)
        tk.Radiobutton(lang_frame, text="英文文字雲", variable=self.lang_var, value="en").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(lang_frame, text="中文文字雲", variable=self.lang_var, value="zh").pack(side=tk.LEFT, padx=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        # 注意這裡的 command 變成了呼叫「自己的方法 (self.generate_action)」
        tk.Button(btn_frame, text="產生文字雲", command=self.generate_action).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="儲存圖片", command=self.save_action).pack(side=tk.LEFT, padx=5)

    # 先做兩個空的方法 (Method) 放著，下一關我們再把大腦裝進去 [cite: 183]
    def generate_action(self):
        # 1. 抓取「我的」介面上的語言選擇和輸入的文字
        lang = self.lang_var.get()
        text = self.text_area.get("1.0", tk.END).strip()
        word_frequencies = {}

        # 2. 雙語分流處理 (這段邏輯跟之前完全一樣)
        if lang == "en":
            words = text.split()
            for word in words:
                word = word.lower()
                if len(word) > 1 and word not in STOPWORDS:
                    if word in word_frequencies:
                        word_frequencies[word] += 1
                    else:
                        word_frequencies[word] = 1
            my_font = None 

        else:
            words = jieba.lcut(text)
            zh_stopwords = set() 
            
            try:
                with open("stopwords_Traditional_Chinese.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        word = line.strip()
                        if word: 
                            zh_stopwords.add(word)
            except FileNotFoundError:
                messagebox.showwarning("找不到檔案", "找不到 'stopwords_Traditional_Chinese.txt'，將僅過濾基礎標點符號。")
                zh_stopwords = {'\n', ' ', '，', '。', '！', '？', '、'}
            
            for word in words:
                word = word.strip()
                if len(word) > 1 and word not in zh_stopwords:
                    if word in word_frequencies:
                        word_frequencies[word] += 1
                    else:
                        word_frequencies[word] = 1
            my_font = "msjh.ttc" if os.name == 'nt' else "PingFang.ttc"

        if not word_frequencies:
            messagebox.showwarning("警告", "過濾後沒有足夠的文字可以產生文字雲！")
            return

        print(f"[{lang}] 過濾後的字數統計：", word_frequencies)

        # 3. 畫出文字雲
        wc = WordCloud(
            font_path=my_font, 
            width=1200, 
            height=800, 
            background_color='white',
            max_words=50,
            colormap='plasma'
        )
        wc.generate_from_frequencies(word_frequencies)
        
        # 【重點】把做好的文字雲，存進「我的」肚子裡 (self.current_wc)
        self.current_wc = wc

        plt.figure(figsize=(12, 8))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis("off")
        plt.show()

    def save_action(self):
        # 存檔時，直接從「我的」肚子裡拿文字雲出來，不用再寫 global 了！
        if self.current_wc is None:
            messagebox.showwarning("警告", "請先產生文字雲再存檔喔！")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            title="儲存文字雲",
            filetypes=(("PNG 圖片", "*.png"), ("JPEG Image", "*.jpg"), ("所有檔案", "*.*"))
        )
        if filepath:
            self.current_wc.to_file(filepath)
            messagebox.showinfo("成功", "太棒了，圖檔儲存成功！")


# ==========================================
# 程式的真正進入點 (Main Program)
# ==========================================
if __name__ == "__main__":
    main_window = tk.Tk()
    
    # 實際建立出一個占用記憶體的物件實體 [cite: 198]
    app = WordCloudGenerator(main_window) 
    
    main_window.mainloop()