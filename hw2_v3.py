import tkinter as tk
from tkinter import filedialog, messagebox
import os
import jieba
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

current_wc = None

def generate_action():
    global current_wc
    
    lang = lang_var.get()
    text = text_area.get("1.0", tk.END).strip()
    word_frequencies = {}

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
        my_font = None 

    else:
        # 【中文模式】
        words = jieba.lcut(text)
        zh_stopwords = set() # 先準備一個空的集合來裝停用詞
        
        # ★ 新增：動態讀取外部的停用詞檔案
        try:
            # 嘗試打開同一個資料夾下的 txt 檔 (注意 encoding='utf-8' 避免中文亂碼)
            with open("stopwords_Traditional_Chinese.txt", "r", encoding="utf-8") as f:
                for line in f:
                    # 把每一行前後的空白或換行符號去掉，然後加進集合裡
                    word = line.strip()
                    if word: 
                        zh_stopwords.add(word)
        except FileNotFoundError:
            # 如果資料夾裡沒放這個 txt 檔，就跳出警告，並使用最基礎的預設名單
            messagebox.showwarning("找不到檔案", "找不到 'stopwords_Traditional_Chinese.txt'，將僅過濾基礎標點符號。請確認檔案與程式放在同一資料夾！")
            zh_stopwords = {'\n', ' ', '，', '。', '！', '？', '、'}
        
        # 開始算字數與過濾
        for word in words:
            word = word.strip()
            # 條件：字長度大於1，且「不能」在你提供的停用詞表裡面
            if len(word) > 1 and word not in zh_stopwords:
                if word in word_frequencies:
                    word_frequencies[word] += 1
                else:
                    word_frequencies[word] = 1
                    
        my_font = "msjh.ttc" if os.name == 'nt' else "PingFang.ttc"

    # 防呆機制
    if not word_frequencies:
        messagebox.showwarning("警告", "過濾後沒有足夠的文字可以產生文字雲！")
        return

    print(f"[{lang}] 過濾後的字數統計：", word_frequencies)

    # 畫出文字雲
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

    # 顯示圖片
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
# 底下是 GUI 介面設定區 (維持不變)
# ==========================================
root = tk.Tk()
root.title("雙語文字雲產生器")
root.geometry("600x450")

text_area = tk.Text(root, height=15, width=60)
text_area.pack(pady=10)

lang_var = tk.StringVar(value="en")
lang_frame = tk.Frame(root)
lang_frame.pack(pady=5)
tk.Radiobutton(lang_frame, text="英文文字雲", variable=lang_var, value="en").pack(side=tk.LEFT, padx=10)
tk.Radiobutton(lang_frame, text="中文文字雲", variable=lang_var, value="zh").pack(side=tk.LEFT, padx=10)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="產生文字雲", command=generate_action).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="儲存圖片", command=save_action).pack(side=tk.LEFT, padx=5)

root.mainloop()