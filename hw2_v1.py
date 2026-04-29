import tkinter as tk
from tkinter import filedialog, messagebox
# 新增這兩行：把文字雲、英文無意義字字典、還有畫圖工具請進來
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import os     # 用來判斷你的電腦是 Windows 還是 Mac，以決定抓什麼中文字體
import jieba  # 中文斷詞神器

current_wc = None

def generate_action():
    global current_wc
    
    # ★ 抓取使用者選了哪種語言 ("en" 或 "zh")
    lang = lang_var.get()
    
    text = text_area.get("1.0", tk.END).strip()
    word_frequencies = {}

    # === 語言分流處理 ===
    if lang == "en":
        # 【英文邏輯】
        words = text.split()
        for word in words:
            word = word.lower()
            if len(word) > 1 and word not in STOPWORDS:
                if word in word_frequencies:
                    word_frequencies[word] += 1
                else:
                    word_frequencies[word] = 1
        
        # 英文不需要特別指定字體
        my_font = None 

    else:
        # 【中文邏輯】
        words = jieba.lcut(text)
        zh_stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一個', '上', '也', '很', '到', '說', '要', '去', '你', '會', '著', '沒有', '看', '好', '自己', '這', '\n', ' ', '，', '。', '！', '？', '、'}
        
        for word in words:
            word = word.strip()
            if len(word) > 1 and word not in zh_stopwords:
                if word in word_frequencies:
                    word_frequencies[word] += 1
                else:
                    word_frequencies[word] = 1
                    
        # ★ 中文必須指定電腦裡的中文字體
        # Windows 用微軟正黑體 (msjh.ttc)，Mac 用蘋方體 (PingFang.ttc)
        my_font = "msjh.ttc" if os.name == 'nt' else "PingFang.ttc"
    # ====================

    # 防呆：如果算完發現沒有字 (例如使用者輸入空白)，就中斷
    if not word_frequencies:
        messagebox.showwarning("警告", "沒有足夠的文字可以產生文字雲！")
        return

    # ★ 產生文字雲 (注意這裡多了一個 font_path=my_font)
    wc = WordCloud(
        font_path=my_font, 
        width=600, 
        height=400, 
        background_color='white',
        max_words=20,
        colormap='plasma'
    )
    wc.generate_from_frequencies(word_frequencies)
    
    current_wc = wc

    plt.figure(figsize=(6, 4))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()


def save_action():
    global current_wc
    
    # 防呆機制：如果還沒產生文字雲，就按存檔，要提醒使用者
    if current_wc is None:
        messagebox.showwarning("警告", "請先產生文字雲再存檔！")
        return
        
    # 跳出讓使用者選擇「存檔位置跟檔名」的視窗
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        title="儲存文字雲",
        filetypes=(("PNG 圖片", "*.png"), ("所有檔案", "*.*"))
    )
    
    # 如果使用者有選擇路徑 (沒有按取消)
    if filepath:
        current_wc.to_file(filepath)  # ★ 老師要求的 to_file() 終於登場啦！
        messagebox.showinfo("成功", "太棒了，圖檔儲存成功！")


# --- 介面設定 (跟第一關一樣) ---
root = tk.Tk()
root.title("我的文字雲產生器")
root.geometry("600x400")

text_area = tk.Text(root, height=15, width=60)
text_area.pack(pady=10)

# === 新增：語言選擇區塊 ===
# 建立一個變數來記住使用者選了什麼，預設值設定為 "en" (英文)
lang_var = tk.StringVar(value="en")

# 建立一個隱形的框架 (Frame)，用來把兩個按鈕包在一起排好
lang_frame = tk.Frame(root)
lang_frame.pack(pady=5)

# 放入兩個單選按鈕 (Radiobutton)
tk.Radiobutton(lang_frame, text="英文文字雲", variable=lang_var, value="en").pack(side=tk.LEFT, padx=10)
tk.Radiobutton(lang_frame, text="中文文字雲", variable=lang_var, value="zh").pack(side=tk.LEFT, padx=10)
# ========================

btn = tk.Button(root, text="產生文字雲", command=generate_action)
btn.pack(pady=10)

# 存檔按鈕
save_btn = tk.Button(root, text="儲存圖片", command=save_action)
save_btn.pack(pady=5)

root.mainloop()