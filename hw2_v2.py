import tkinter as tk
from tkinter import filedialog, messagebox
import os
import jieba
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# 用來暫存做好的文字雲，給存檔功能使用
current_wc = None

def generate_action():
    global current_wc
    
    # 1. 讀取大腦指令：看使用者選了什麼語言
    lang = lang_var.get()
    text = text_area.get("1.0", tk.END).strip()
    word_frequencies = {}

    # 2. 雙語分流處理
    if lang == "en":
        # 【英文模式】
        words = text.split()
        for word in words:
            word = word.lower()
            if len(word) > 1 and word not in STOPWORDS:
                if word in word_frequencies:
                    word_frequencies[word] += 1
                else:
                    word_frequencies[word] = 1
        my_font = None # 英文不用特地挑字體

    else:
        # 【中文模式】
        words = jieba.lcut(text)
        zh_stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一個', '上', '也', '很', '到', '說', '要', '去', '你', '會', '著', '沒有', '看', '好', '自己', '這', '\n', ' ', '，', '。', '！', '？', '、'}
        
        for word in words:
            word = word.strip()
            if len(word) > 1 and word not in zh_stopwords:
                if word in word_frequencies:
                    word_frequencies[word] += 1
                else:
                    word_frequencies[word] = 1
        # 中文必須指定字體 (Windows 預設用微軟正黑體)
        my_font = "msjh.ttc" if os.name == 'nt' else "PingFang.ttc"

    # 防呆機制
    if not word_frequencies:
        messagebox.showwarning("警告", "沒有足夠的文字可以產生文字雲！")
        return

    # 印在終端機讓你檢查有沒有算對
    print(f"[{lang}] 過濾後的字數統計：", word_frequencies)

    # 3. 畫出文字雲
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

    # 4. 顯示圖片
    plt.figure(figsize=(6, 4))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()

def save_action():
    global current_wc
    if current_wc is None:
        messagebox.showwarning("警告", "請先產生文字雲再存檔喔！")
        return
        
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        title="儲存文字雲",
        filetypes=(("PNG 圖片", "*.png"), ("所有檔案", "*.*"))
    )
    if filepath:
        current_wc.to_file(filepath)
        messagebox.showinfo("成功", "太棒了，圖檔儲存成功！")


# ==========================================
# 底下是 GUI 介面設定區
# ==========================================
root = tk.Tk()
root.title("雙語文字雲產生器")
root.geometry("600x450")

# 文字輸入框
text_area = tk.Text(root, height=15, width=60)
text_area.pack(pady=10)

# 語言選擇區
lang_var = tk.StringVar(value="en")
lang_frame = tk.Frame(root)
lang_frame.pack(pady=5)
tk.Radiobutton(lang_frame, text="英文文字雲", variable=lang_var, value="en").pack(side=tk.LEFT, padx=10)
tk.Radiobutton(lang_frame, text="中文文字雲", variable=lang_var, value="zh").pack(side=tk.LEFT, padx=10)

# 按鈕區
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="產生文字雲", command=generate_action).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="儲存圖片", command=save_action).pack(side=tk.LEFT, padx=5)

root.mainloop()