import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
import os

# 外部套件
from wordcloud import WordCloud, STOPWORDS
import jieba
import matplotlib.pyplot as plt

class WordCloudGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Article Word Cloud (Top 20 Words)")
        self.root.geometry("600x450")
        
        # 用來儲存產生的文字雲圖片物件，以便後續存檔
        self.current_wordcloud = None

        # --- UI 元件設定 ---
        tk.Label(root, text="Article Text:", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(10, 0))
        
        # 建立文字輸入框
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
        self.text_area.pack(padx=10, pady=5)
        
        # 建立按鈕框架
        btn_frame = tk.Frame(root)
        btn_frame.pack(anchor="w", padx=10, pady=5)
        
        # 三個主要功能按鈕
        tk.Button(btn_frame, text="Open .txt File", command=self.load_file).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Generate Word Cloud", command=self.generate_cloud).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save Word Cloud", command=self.save_cloud).pack(side=tk.LEFT, padx=5)

    def load_file(self):
        """讀取 txt 檔案並顯示在文字框中"""
        filepath = filedialog.askopenfilename(
            title="選擇純文字檔案",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if not filepath:
            return
            
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)  # 清空目前文字
                self.text_area.insert(tk.END, content) # 插入新文字
        except Exception as e:
            messagebox.showerror("錯誤", f"讀取檔案失敗:\n{e}")

    def generate_cloud(self):
        """核心邏輯：斷詞、Hash計算詞頻、畫文字雲"""
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "請先輸入或載入文字！")
            return

        # 1. 中英文斷詞處理 (加分項3：處理中文)
        # 使用 jieba 將一段話切分成詞彙陣列
        words = jieba.lcut(text)
        
        # 2. 定義 Stop words 與過濾條件 (加分項2：排除無意義字)
        # 結合 wordcloud 預設的英文 stopwords，並加入自訂的中英文標點與無意義字
        custom_stopwords = set(STOPWORDS)
        custom_stopwords.update(['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一個', '上', '也', '很', '到', '說', '要', '去', '你', '會', '著', '沒有', '看', '好', '自己', '這'])

        filtered_words = []
        for word in words:
            word = word.strip().lower() # 轉小寫並去空白
            # 排除長度為 1 的字（通常是單個標點或無意義單字）、排除數字、排除停用詞
            if len(word) > 1 and not word.isnumeric() and word not in custom_stopwords:
                # 使用 Regex 確保不是純標點符號
                if re.match(r'[^\W_]+', word): 
                    filtered_words.append(word)

        # 3. 運用 Hash (字典) 技巧找出高頻率文字
        # Python 的 Dict 底層即為 Hash Table，尋找與更新的時間複雜度為 O(1)
        word_frequencies = {}
        for word in filtered_words:
            if word in word_frequencies:
                word_frequencies[word] += 1
            else:
                word_frequencies[word] = 1

        if not word_frequencies:
            messagebox.showinfo("提示", "過濾後沒有足夠的文字可以產生文字雲。")
            return

        # 4. 產生文字雲
        # 注意：要顯示中文，必須指定中文字體路徑！
        # Windows 通常是 "msjh.ttc" (微軟正黑體)，Mac 通常是 "PingFang.ttc"
        font_path = "msjh.ttc" if os.name == 'nt' else "PingFang.ttc"
        
        try:
            # 設定前 n 個 (這裡是 20)
            wc = WordCloud(
                font_path=font_path,
                width=800, height=800, 
                background_color='white',
                max_words=20,           # 要求：前 n 個
                colormap='plasma',      # 讓顏色好看一點
                contour_width=3, 
                contour_color='steelblue'
            )
            
            # 將我們算好的 Hash 字典傳給 WordCloud
            wc.generate_from_frequencies(word_frequencies)
            self.current_wordcloud = wc
            
            # 使用 matplotlib 彈出視窗顯示圖片
            plt.figure(figsize=(6, 6))
            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")
            plt.title("Top 20 Words Cloud")
            plt.show()
            
        except OSError:
            messagebox.showerror("字體錯誤", f"找不到字體 '{font_path}'，若您要顯示中文，請在程式碼中修改 font_path 為您電腦中存在的中文字體路徑。")


    def save_cloud(self):
        """儲存文字雲成圖檔 (加分項1)"""
        if self.current_wordcloud is None:
            messagebox.showwarning("警告", "請先產生文字雲再存檔！")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            title="儲存文字雲圖檔",
            filetypes=(("PNG Image", "*.png"), ("JPEG Image", "*.jpg"))
        )
        if filepath:
            # 使用 wordcloud 內建的方法存檔
            self.current_wordcloud.to_file(filepath)
            messagebox.showinfo("成功", f"文字雲已成功儲存至:\n{filepath}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WordCloudGenerator(root)
    root.mainloop()